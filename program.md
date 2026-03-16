# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 26
next_cycle: 27

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 24; continue from the activity ledger while keeping the branch head fixes in view.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.
- Cycle 24 closed a heredoc gap where `cat > file <<'EOF' ... EOF` and `cat <<'EOF' > file` bypassed redirect content inspection and were allowed inside the project.
- Cycle 25 closed flagged and glued here-string gaps where `cat -n<<<'payload'`, `cat --<<<'payload'`, and shell-wrapper forms like `bash -s <<< 'echo payload' > file` or `bash --noprofile -s<<<'echo payload' > file` skipped payload inspection or fell back to unknown writes.
- Cycle 26 closes shell-wrapper `-c` redirect gaps where `bash -c`, `sh -c`, leading shell flags, and `command bash -c` allowed secret or destructive literal writes inside the project without content inspection.

Cycle 26 closed:
- Reuse single-stage inner-command parsing for redirect literal extraction so shell-wrapper `-c` payloads feed existing secret/destructive write scans
- Strip `command` before redirect literal extraction so `command bash -c ... > file` inherits the same content inspection as plain shell wrappers
- Add regression coverage for `bash/sh -c`, leading wrapper flags, and `command bash -c` secret/destructive redirect writes
- Re-run the full pytest suite to confirm redirect guard behavior stays stable across the classifier

Next scan ideas:
- Probe combined shell short-option clusters like `bash -lc/-cl/-cecho` to decide when `-c` should unwrap versus fail closed
- Probe `env`, `nice`, and other prefix wrappers around shell `-c`/stdin forms to see whether safe wrapper stripping can preserve redirect payload inspection
- Continue credential-store/path coverage for less common developer tooling
