# PROGRESS.MD — [PROJECT NAME]
## Phase 5 Live Execution State
### Last updated: [TIMESTAMP] | Updated by: Antigravity

---

## ⚠️ ANTIGRAVITY: READ THIS BEFORE WRITING ANY CODE

This file is your memory across sessions. Before doing anything:

1. Read the full task table below
2. Only work on tasks marked `NOT STARTED`
3. If a task is `DONE` — do not touch that file under any circumstance
4. If a task is `IN PROGRESS` — read the notes column, continue from there
5. When you finish a task, update its row in the table before ending the session
6. Never mark a task `DONE` unless its tests pass

If you are unsure what to do next: read `_context/claude.md` Section 7 (Phase-Wise Build Plan), then come back here and find the first `NOT STARTED` task in the current phase.

---

## Current Phase

**Active**: Phase [ ] — [Phase Name]
**Previous phases**: All complete / Phase N complete

---

## Task Registry

| # | Module | Task | Status | File(s) | Test | Notes |
|---|--------|------|--------|---------|------|-------|
| 1 | shared | Config loader | NOT STARTED | src/shared/config.py | tests/unit/test_config.py | — |
| 2 | shared | Logger setup | NOT STARTED | src/shared/logger.py | tests/unit/test_logger.py | — |
| 3 | [module] | [task] | NOT STARTED | src/[module]/[file].py | tests/unit/test_[file].py | — |

**Status values**: `NOT STARTED` · `IN PROGRESS` · `DONE` · `BLOCKED` · `NEEDS REVIEW`

---

## What Currently Exists and Works

[Antigravity updates this section as tasks complete.
Plain language. One line per completed module.]

- Nothing yet.

---

## Active Blockers

[Tasks that are stuck and why. Antigravity fills this in.]

| # | Task | Blocked by | Escalated? |
|---|------|-----------|-----------|
| — | — | — | — |

---

## Session Log

[One entry per Antigravity session. Append, never overwrite.]

### Session 1 — [DATE]
- Started: task #N
- Completed: —
- Left off at: —
- Next session should start with: task #N

---

## File Ownership Map

[Which file belongs to which task. Prevents duplicate implementations.]

| File | Owner Task # | Status |
|------|-------------|--------|
| src/shared/config.py | #1 | NOT STARTED |
| src/shared/logger.py | #2 | NOT STARTED |

---

*Updated by Antigravity at end of every session.*
*Never manually edited by human — this is the agent's working memory.*
