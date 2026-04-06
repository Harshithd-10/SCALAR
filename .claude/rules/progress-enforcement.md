# progress-enforcement.md
## Mandatory Rule: progress.md Lifecycle

This rule is non-negotiable. It applies to every coding session without exception.

---

## The Two Immutable Laws

### Law 1 — Before Writing Any Code
Read `_context/progress.md` completely.

Specifically:
- Find every task marked `IN PROGRESS` — continue from the notes column
- Find the first task marked `NOT STARTED` in the current phase — that is your next task
- Do not touch any file owned by a task marked `DONE`
- If `progress.md` does not exist, stop and tell the human before proceeding

If you skip this step and write code without reading progress.md first,
you risk overwriting working implementations and duplicating logic that already exists.

### Law 2 — After Every Successful Implementation
Update `progress.md` immediately, before waiting for the next human prompt.

Specifically, update:
1. The task's `Status` column: `IN PROGRESS` → `DONE`
2. The task's `Test` column: confirm tests pass or note what's pending
3. The task's `Notes` column: brief note on anything non-obvious
4. The `What Currently Exists and Works` section: one-line summary of the new module
5. The `Session Log`: append an entry for this session
6. The `File Ownership Map`: mark the file's status as DONE

Do not end a session without updating progress.md.
If you completed a task but tests have not been run yet, mark it `NEEDS REVIEW`, not `DONE`.

---

## What DONE Means

A task is `DONE` if and only if:
- The code is written
- `pytest tests/unit/test_[module].py` passes
- The file is saved

A task is NOT `DONE` if:
- The code runs but has no test
- The code is written but throws warnings
- You "think" it works but haven't run the test

---

## Blocked Tasks

If you cannot complete a task due to a dependency, missing information, or error you
cannot resolve in 2 attempts:
1. Mark the task `BLOCKED` in progress.md
2. Fill in the `Active Blockers` table with what is blocking it
3. Stop working on that task
4. Move to the next `NOT STARTED` task if one exists
5. If nothing can proceed, tell the human and reference progress.md

Do not loop on a blocked task. Escalate via `_context/debug_handoff.md`.

---

## Why This Rule Exists

Without it: on session 2, you re-read `_context/claude.md`, see a complete blueprint,
and cannot distinguish what is already built from what is not. You will overwrite
working code, create duplicate implementations, or implement things in the wrong order.

`progress.md` is your only reliable state between sessions. Treat it as such.
