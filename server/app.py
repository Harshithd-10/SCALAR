"""
server/app.py — Required by openenv validate for multi-mode deployment discovery.

The canonical app lives in app/main.py (per CLAUDE.md §4 module map).
This file is a thin re-export so the OpenEnv validator can find `app` and
`start` at the path it expects (server/app.py) without duplicating any logic.

Do NOT add business logic here.
"""

from app.main import app, start  # noqa: F401 — re-exported for openenv validator

__all__ = ["app", "start"]
