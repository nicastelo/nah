# nah

Context-aware safety guard for Claude Code. Guards all tools (Bash, Read, Write, Edit, Glob, Grep), not just shell commands. Deterministic, zero tokens, milliseconds.

**Tagline:** "A permission system you control."

## Project Structure

- `src/nah/` — Python package (pip-installable, CLI entry point: `nah`)
- `docs/PLAN.md` — Full technical plan (architecture, tool handlers, build phases)
- `docs/features/` — Feature design tracking (FD system)

## Conventions

- **Python 3.10+**, zero external dependencies for the core hook (stdlib only)
- **LLM layer** uses `urllib.request` (stdlib) — no `requests` dependency
- **Commit format**: `FD-XXX: Brief description` for feature work
- **Entry point**: `nah` CLI via `nah.cli:main`
- **Config format**: YAML (`~/.config/nah/config.yaml` + `.nah.yaml` per project)
- **Hook script**: `~/.claude/hooks/nah_guard.py` (installed read-only, chmod 444)

---

## Feature Design (FD) Management

Features are tracked in `docs/features/`. Each FD has a dedicated file (`FD-XXX_TITLE.md`) and is indexed in `FEATURE_INDEX.md`.

### FD Lifecycle

| Stage | Description |
|-------|-------------|
| **Planned** | Identified but not yet designed |
| **Design** | Actively designing (exploring code, writing plan) |
| **Open** | Designed and ready for implementation |
| **In Progress** | Currently being implemented |
| **Pending Verification** | Code complete, awaiting verification |
| **Complete** | Verified working, ready to archive |
| **Deferred** | Postponed (low priority or blocked) |
| **Closed** | Won't implement (superseded or not needed) |

### Slash Commands

| Command | Purpose |
|---------|---------|
| `/fd-new` | Create a new feature design |
| `/fd-explore` | Explore project - overview, FD history, recent activity |
| `/fd-deep` | Deep parallel analysis — 4 agents explore a hard problem from different angles, verify claims, synthesize |
| `/fd-status` | Show active FDs with status and grooming |
| `/fd-verify` | Post-implementation: commit, proofread, verify |
| `/fd-close` | Complete/close an FD, archive file, update index, update changelog |

### Conventions

- **FD files**: `docs/features/FD-XXX_TITLE.md` (XXX = zero-padded number)
- **Commit format**: `FD-XXX: Brief description`
- **Numbering**: Next number = highest across all index sections + 1
- **Source of truth**: FD file status > index (if discrepancy, file wins)
- **Archive**: Completed FDs move to `docs/features/archive/`

### Managing the Index

The `FEATURE_INDEX.md` file has four sections:

1. **Active Features** — All non-complete FDs, sorted by FD number
2. **Completed** — Completed FDs, newest first
3. **Deferred / Closed** — Items that won't be done
4. **Backlog** — Low-priority or blocked items parked for later

### Inline Annotations (`%%`)

Lines starting with `%%` in any file are **inline annotations from the user**. When you encounter them:
- Treat each `%%` annotation as a direct instruction — answer questions, develop further, provide feedback, or make changes as requested
- Address **every** `%%` annotation in the file; do not skip any
- After acting on an annotation, remove the `%%` line from the file
- If an annotation is ambiguous, ask for clarification before acting

### Changelog

- **Format**: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- **Updated by**: `/fd-close` (complete disposition only) adds entries under `[Unreleased]`
- **FD references**: Entries end with `(FD-XXX)` for traceability
- **Subsections**: Added, Changed, Fixed, Removed
- **Releasing**: Rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`, add fresh `[Unreleased]` header
