# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 18
next_cycle: 19

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code, but local loop state still last closed cycle 16.
- Cycle 17 closed a git global-option stripping gap where valid global flags obscured the real subcommand and fell through to `unknown`.
- Cycle 18 extended git global-option stripping to cover valid `--config-env` and equals-joined `--exec-path=...` forms without weakening fail-closed handling for malformed or ambiguous inputs.

Cycle 18 closed:
- Strip valid `git --config-env NAME=ENVVAR ...` and `git --config-env=NAME=ENVVAR ...` forms before subcommand classification
- Strip valid equals-joined `git --exec-path=/path ...` before builtin and trusted global override matching
- Preserve fail-closed behavior for malformed `--config-env` values and bare `--exec-path`, which does not execute a hidden subcommand
- Add regression coverage for builtin classification and trusted global override matching across the new flag forms

Next scan ideas:
- Probe more git global-option edge cases, especially optional-argument flags and malformed value handling that could accidentally expose a later subcommand
- Fuzz command wrappers where global flags can hide a destructive inner subcommand
- Continue credential-store/path coverage for less common developer tooling
