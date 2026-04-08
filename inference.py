"""
inference.py — HuggingFace Spaces entry point
PR Review & Security Audit OpenEnv Environment

HF Spaces requires this file at the repo root. It imports and launches
the FastAPI app defined in app/main.py via uvicorn on port 7860.

Do NOT add business logic here. All routing, environment state, and
grader logic lives under app/. This file is a thin launcher only.
"""

import json
from pathlib import Path

# Pre-flight: validate all episode files before starting the server
_DATA_DIR = Path("data/tasks")
_FILES = ["task1_episodes.json", "task2_episodes.json", "task3_episodes.json"]

for _fname in _FILES:
    _fpath = _DATA_DIR / _fname
    if not _fpath.exists():
        print(f"[WARN] Missing episode file: {_fpath}", flush=True)
        continue
    try:
        with open(_fpath) as _f:
            _episodes = json.load(_f)
        print(f"[OK] {_fname}: {len(_episodes)} episodes loaded", flush=True)
    except json.JSONDecodeError as _e:
        print(f"[FATAL] Malformed JSON in {_fpath}: {_e}", flush=True)
        raise SystemExit(1)

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