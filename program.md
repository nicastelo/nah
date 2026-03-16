# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 27
next_cycle: 28

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 24; continue from the activity ledger while keeping the branch head fixes in view.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.
- Cycle 24 closed a heredoc gap where `cat > file <<'EOF' ... EOF` and `cat <<'EOF' > file` bypassed redirect content inspection and were allowed inside the project.
- Cycle 25 closed flagged and glued here-string gaps where `cat -n<<<'payload'`, `cat --<<<'payload'`, and shell-wrapper forms like `bash -s <<< 'echo payload' > file` or `bash --noprofile -s<<<'echo payload' > file` skipped payload inspection or fell back to unknown writes.
- Cycle 26 closes shell-wrapper `-c` redirect gaps where `bash -c`, `sh -c`, leading shell flags, and `command bash -c` allowed secret or destructive literal writes inside the project without content inspection.
- Cycle 27 closes `stdbuf` passthrough gaps where buffered shell wrappers like `stdbuf -oL bash -c ... > file` and `command stdbuf --output=L bash -lc ... > file` fell back to unknown instead of preserving safe inner classification or redirect payload inspection.

Cycle 27 closed:
- Strip `stdbuf` wrapper layers before recursive classification and redirect-literal extraction so safe inner commands keep their underlying action type.
- Support short `-i/-o/-e` and long `--input/--output/--error` buffer-mode flags, including attached-value forms, while failing closed on unknown options.
- Add regression coverage for safe wrapped `git status` plus secret/destructive `bash -c` redirect payloads through `stdbuf` and `command stdbuf` forms.
- Re-run the full pytest suite to confirm passthrough-wrapper behavior stays stable across the classifier.

Next scan ideas:
- Probe other safe prefix wrappers like `setsid` or `stdbuf --` nesting around shell `-c` / stdin forms to decide whether more passthrough stripping is justified without weakening fail-closed behavior.
- Probe wrappers with side effects like `nohup`, `timeout`, or `ionice` to document which ones should stay fail-closed versus classify through to the inner command.
- Continue credential-store/path coverage for less common developer tooling.
