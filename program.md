# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 23
next_cycle: 24

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 19; local state is now synced through cycle 22.
- Cycle 20 stripped `git --no-lazy-fetch` before builtin and override matching so later destructive subcommands are still classified correctly.
- Cycle 21 tightened git global-option validation so malformed `-c` and `--config-env` values fail closed instead of exposing a later subcommand.
- Cycle 22 focused on regression depth: keep the git global-flag sweep honest by covering already-supported boolean globals and valid `-c` override paths.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.

Cycle 23 closed:
- Route literal payload scanning through stdout-capturing `&>` / `&>>` redirects instead of only plain `>` / `1>` forms
- Preserve leading-dash `printf` literals during best-effort redirect extraction so secret-like payloads still trigger content inspection
- Add regression coverage for `echo` / `printf` secret writes via `&>` / `&>>` inside the project
- Re-run the full pytest suite to confirm redirect handling stays stable

Next scan ideas:
- Probe more redirect/content combinations where literal extraction may diverge from shell output semantics
- Fuzz command wrappers where global flags or redirects can hide a destructive inner subcommand
- Continue credential-store/path coverage for less common developer tooling
