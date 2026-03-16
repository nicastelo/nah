# nah autoresearch program

run_tag: hackathon
branch: autoresearch/hackathon
status: active
current_cycle: 31
next_cycle: 32

Context:
- Fresh clone of `autoresearch/hackathon` surfaced newer upstream code while the tracked local run ledger still stopped at cycle 24; continue from the activity ledger while keeping the branch head fixes in view.
- Cycle 23 tightened redirect content inspection so stdout-capturing `&>` / `&>>` writes still scan literal `echo` / `printf` payloads, including leading-dash secrets.
- Cycle 24 closed a heredoc gap where `cat > file <<'EOF' ... EOF` and `cat <<'EOF' > file` bypassed redirect content inspection and were allowed inside the project.
- Cycle 25 closed flagged and glued here-string gaps where `cat -n<<<'payload'`, `cat --<<<'payload'`, and shell-wrapper forms like `bash -s <<< 'echo payload' > file` or `bash --noprofile -s<<<'echo payload' > file` skipped payload inspection or fell back to unknown writes.
- Cycle 26 closes shell-wrapper `-c` redirect gaps where `bash -c`, `sh -c`, leading shell flags, and `command bash -c` allowed secret or destructive literal writes inside the project without content inspection.
- Cycle 27 closes `stdbuf` passthrough gaps where buffered shell wrappers like `stdbuf -oL bash -c ... > file` and `command stdbuf --output=L bash -lc ... > file` fell back to unknown instead of preserving safe inner classification or redirect payload inspection.
- Cycle 28 closes `setsid` passthrough gaps where detached shell wrappers like `setsid bash -c ...`, `setsid --wait bash -lc ...`, and `command setsid -w bash -c ...` fell back to unknown instead of preserving safe inner classification or redirect payload inspection.
- Cycle 29 closes `timeout` passthrough gaps where duration-prefixed wrappers like `timeout 5 bash -c ...`, `timeout -s KILL 5 bash -c ...`, and `command timeout -p 5 bash -c ...` fell back to unknown instead of preserving safe inner classification or redirect payload inspection.
- Cycle 30 closes `ionice` passthrough gaps where scheduling wrappers like `ionice -c 3 bash -c ...`, `ionice --class idle bash -c ...`, and `command ionice -t -c 3 bash -c ...` fell back to unknown instead of preserving safe inner classification or redirect payload inspection while process-targeting forms stay fail-closed.
- Cycle 31 closes `timeout` clustered short-option gaps where forms like `timeout -vp 5 bash -c ...`, `timeout -vk 1s 5 bash -c ...`, `timeout -vs KILL 5 bash -c ...`, and glued argument variants like `timeout -vk1s ...` or `timeout -vsKILL ...` fell back to unknown instead of preserving passthrough unwrapping or redirect payload inspection.

Cycle 29 closed:
- Strip `timeout` wrapper layers before recursive classification and redirect-literal extraction so safe inner commands keep their underlying action type.
- Support exact timeout no-arg flags `-f`, `-p`, `-v`, `--foreground`, `--preserve-status`, and `--verbose` plus `-k`/`-s` and `--kill-after=`/`--signal=` argument forms while failing closed on unknown options.
- Treat the first non-flag token as the timeout duration, then classify the remaining inner command so wrapped `bash -c` redirects still inspect literal secret/destructive payloads.
- Add regression coverage for safe wrapped `git status` plus secret/destructive `bash -c` redirect payloads through `timeout`, `/usr/bin/timeout`, and `command timeout` forms.
- Re-run the full pytest suite to confirm passthrough-wrapper behavior stays stable across the classifier.


Cycle 30 closed:
- Strip `ionice` wrapper layers before recursive classification and redirect-literal extraction so safe inner commands keep their underlying action type.
- Support command-mode `ionice` flags `-t`/`--ignore`, `-c`/`--class`, and `-n`/`--classdata` including glued short and `--flag=value` forms while failing closed on process-targeting flags like `-p`, `-P`, `-u`, `--pid`, `--pgid`, and `--uid`.
- Add regression coverage for safe wrapped `git status` plus secret/destructive `bash -c` redirect payloads through `ionice`, `/usr/bin/ionice`, and `command ionice` forms.
- Re-run the full pytest suite to confirm passthrough-wrapper behavior stays stable across the classifier.

Cycle 31 closed:
- Extend `timeout` passthrough stripping to parse clustered GNU short options so no-arg combinations like `-vp` / `-vf` and arg-taking forms like `-vk 1s`, `-vs KILL`, `-vk1s`, and `-vsKILL` preserve inner-command classification.
- Keep fail-closed behavior for malformed or unknown clustered short options instead of guessing through ambiguous syntax.
- Add regression coverage for plain, `/usr/bin/timeout`, and `command timeout` clustered forms plus malformed timeout clusters that must stay `unknown`.
- Re-run the full pytest suite to confirm passthrough-wrapper behavior stays stable across the classifier.

Next scan ideas:
- Probe wrappers with side effects like `nohup` to document which ones should stay fail-closed versus classify through to the inner command.
- Continue credential-store/path coverage for less common developer tooling.
- Audit other passthrough wrappers for clustered short-option parsing inconsistencies.
