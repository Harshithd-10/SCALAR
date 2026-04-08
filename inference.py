"""
inference.py — HuggingFace Spaces entry point
PR Review & Security Audit OpenEnv Environment

HF Spaces requires this file at the repo root. It imports and launches
the FastAPI app defined in app/main.py via uvicorn on port 7860.

Do NOT add business logic here. All routing, environment state, and
grader logic lives under app/. This file is a thin launcher only.
"""

import uvicorn

from app.main import app  # noqa: F401  — re-exported for HF Spaces auto-detection


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7860,
        log_level="info",
        # Single worker: environment state is in-process (asyncio.Lock guarded).
        # Multi-worker would require an external state store — out of scope per CLAUDE.md §1.
        workers=1,
    )
