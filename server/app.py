"""
server/app.py — OpenEnv multi-mode deployment entry point.

Required by `openenv validate`:
  - Exposes `app` (the FastAPI instance)
  - Exposes `main()` as a named, directly callable function
  - Has `if __name__ == '__main__': main()` guard

All business logic lives in app/main.py per CLAUDE.md §4.
This file is the validator-facing launcher only.
"""

import uvicorn

from app.main import app  # noqa: F401 — re-exported for OpenEnv discovery

__all__ = ["app", "main"]


def main() -> None:
    """
    Primary server entry point discovered by openenv validate.
    Registered in pyproject.toml [project.scripts] as `serve = "server.app:main"`.
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7860,
        log_level="info",
        workers=1,  # Single worker — in-process state + asyncio.Lock. See CLAUDE.md §1.
    )


if __name__ == "__main__":
    main()
