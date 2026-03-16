# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 25
next_cycle: 26

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 24; continue from the activity ledger while keeping the branch head fixes in view.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.
- Cycle 24 closed a heredoc gap where `cat > file <<'EOF' ... EOF` and `cat <<'EOF' > file` bypassed redirect content inspection and were allowed inside the project.
- Cycle 25 closed flagged and glued here-string gaps where `cat -n<<<'payload'`, `cat --<<<'payload'`, and shell-wrapper forms like `bash -s <<< 'echo payload' > file` or `bash --noprofile -s<<<'echo payload' > file` skipped payload inspection or fell back to unknown writes.

Cycle 25 closed:
- Split glued here-string operators during stage decomposition so `cmd<<<'payload'` tokenizes like `cmd <<< 'payload'`
- Reuse here-string literal extraction after leading wrapper flags so shell wrappers still surface redirect payloads for content scanning
- Add regression coverage for flagged/glued `cat` here-strings and flagged `bash` here-string redirect writes carrying secret or destructive payloads
- Re-run the full pytest suite to confirm the here-string hardening stays stable across the classifier

Next scan ideas:
- Probe shell-wrapper `-c` and stdin-script combinations where leading flags or option terminators may still hide write payloads
- Fuzz mixed here-string plus redirect compositions for other wrappers (`env`, `command`, nested shells) that may bypass literal extraction
- Continue credential-store/path coverage for less common developer tooling
