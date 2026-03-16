# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 17
next_cycle: 18

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code, but local loop state still last closed cycle 16.
- Cycle 17 closed a git global-option stripping gap where valid global flags obscured the real subcommand and fell through to `unknown`.
- The fix preserves both builtin git classification and trusted global override matching after stripping these globals.

Cycle 17 closed:
- Strip equals-joined git global value flags like `--git-dir=/x`, `--work-tree=/x`, and `--namespace=ns` before subcommand classification
- Strip additional git global boolean flags `-p` / `--paginate`, `-P` / `--no-pager`, and `--no-advice`
- Restore expected classification for safe and destructive commands hidden behind those globals
- Add regression coverage for both builtin classification and global override lookup paths

Next scan ideas:
- Probe more git global-option edge cases, especially `--config-env`, `--exec-path`, and missing-value fail-closed behavior
- Fuzz command wrappers where global flags can hide a destructive inner subcommand
- Continue credential-store/path coverage for less common developer tooling
