# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 24
next_cycle: 25

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 19; local state is now synced through cycle 22.
- Cycle 21 tightened git global-option validation so malformed `-c` and `--config-env` values fail closed instead of exposing a later subcommand.
- Cycle 22 focused on regression depth: keep the git global-flag sweep honest by covering already-supported boolean globals and valid `-c` override paths.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.
- Cycle 24 closed a heredoc gap where `cat > file <<'EOF' ... EOF` and `cat <<'EOF' > file` bypassed redirect content inspection and were allowed inside the project.

Cycle 24 closed:
- Extract heredoc bodies from raw shell stages and carry them into redirect classification without weakening existing path checks
- Reuse redirect content scanning for heredoc-backed writes so private keys and destructive script payloads escalate before write approval
- Add regression coverage for both `cat > file <<'EOF'` and `cat <<'EOF' > file` secret/destructive payload writes
- Re-run the full pytest suite to confirm the heredoc fix stays stable across the classifier

Next scan ideas:
- Probe more heredoc and here-string combinations where shell wrappers or redirects may hide executable/destructive payloads
- Fuzz command wrappers where global flags or redirects can hide a destructive inner subcommand
- Continue credential-store/path coverage for less common developer tooling
