# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 19
next_cycle: 20

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code, but local loop state still last closed cycle 16.
- Cycle 18 extended git global-option stripping to cover valid `--config-env` and equals-joined `--exec-path=...` forms without weakening fail-closed handling for malformed or ambiguous inputs.
- Cycle 19 continued the git global-flag sweep and closed another pathspec global that could hide a real subcommand behind an unnecessary `unknown` classification.

Cycle 19 closed:
- Strip `git --icase-pathspecs ...` before builtin and trusted global override matching
- Restore expected classification for safe and destructive subcommands hidden behind the pathspec global
- Extend regression coverage so `status` stays safe and `push --force` stays history-rewrite when prefixed with `--icase-pathspecs`
- Keep the loop focused on genuine git global-option parsing gaps instead of broader wrapper fuzzing for this cycle

Next scan ideas:
- Probe more git global-option edge cases, especially optional-argument flags and malformed value handling that could accidentally expose a later subcommand
- Fuzz command wrappers where global flags can hide a destructive inner subcommand
- Continue credential-store/path coverage for less common developer tooling
