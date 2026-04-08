"""
Baseline inference script.

Runs an OpenAI agent against all three task difficulties and records scores.
Requires the environment server to be running (local or HuggingFace Spaces).

Usage:
    export API_BASE_URL=http://localhost:7860
    export MODEL_NAME=gpt-4o
    export HF_TOKEN=your_hf_token_here          # optional
    export LOCAL_IMAGE_NAME=pr-review-env        # optional, only if using from_docker_image()
    export OPENAI_API_KEY=your_key_here

    python baseline/run_baseline.py

Output: baseline/results.json
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx
from openai import OpenAI, RateLimitError

# ---------------------------------------------------------------------------
# Environment variables
# API_BASE_URL and MODEL_NAME have defaults; HF_TOKEN does not.
# LOCAL_IMAGE_NAME is optional — only needed when using from_docker_image().
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

DIFFICULTIES = ["easy", "medium", "hard"]
RESULTS_PATH = Path(__file__).parent / "results.json"

SYSTEM_PROMPT = """You are a senior software engineer performing code review and security auditing.

IMPORTANT: Lines are numbered starting at 1. Count each line of code carefully.
The first line of the code snippet is line 1, the second is line 2, and so on.
Empty lines and comment lines count toward line numbering.

Analyze the provided code carefully and respond ONLY with a valid JSON object in this exact format:
{
  "flagged_lines": [<list of integer line numbers (1-indexed) where bugs exist>],
  "findings": [
    { "type": "<vulnerability type, e.g. sql_injection, hardcoded_secret, xss>", "description": "<explanation>" }
  ],
  "review_text": "<structured code review: include severity labels (critical/high/medium/low), line references (line N or LN), actionable recommendations (should/must/recommend), and category labels (bug/security/vulnerability/style/performance)>"
}

For flagged_lines: flag the exact line numbers where bugs or errors occur.
For findings: use snake_case type names like sql_injection, hardcoded_secret, xss, path_traversal, insecure_deserialization.
For review_text: always reference specific line numbers, assign severity, use actionable language, and categorize issues.

Respond with JSON only. No markdown, no explanation, no code fences."""


def build_user_prompt(observation: dict) -> str:
    """Prepend line numbers to code so the model can reference them accurately."""
    code_lines = observation["code_snippet"].splitlines()
    numbered = "\n".join(f"{i + 1}: {line}" for i, line in enumerate(code_lines))
    return (
        f"Task: {observation['instructions']}\n\n"
        f"Code (line numbers shown for reference):\n{numbered}"
    )


def call_agent(client: OpenAI, observation: dict, max_retries: int = 5) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(observation)},
    ]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip()

            # Strip markdown code fences if model adds them anyway
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            return json.loads(raw)

        except RateLimitError as e:
            if attempt == max_retries - 1:
                print("[ERROR] Max retries reached. API quota may be exhausted.", flush=True)
                raise e

            wait_time = 45
            print(
                f"[WARN] Rate limit hit. Sleeping {wait_time}s before retry "
                f"(attempt {attempt + 1}/{max_retries})...",
                flush=True,
            )
            time.sleep(wait_time)

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse failed on attempt {attempt + 1}: {e}", flush=True)
            if attempt == max_retries - 1:
                raise

    return {"flagged_lines": [], "findings": [], "review_text": ""}


def run_baseline() -> None:
    # ------------------------------------------------------------------
    # START — structured log block
    # ------------------------------------------------------------------
    print("[START]", flush=True)
    print(f"[START] api_base_url={API_BASE_URL}", flush=True)
    print(f"[START] model={MODEL_NAME}", flush=True)
    print(f"[START] hf_token_present={'yes' if HF_TOKEN else 'no'}", flush=True)
    if LOCAL_IMAGE_NAME:
        print(f"[START] local_image_name={LOCAL_IMAGE_NAME}", flush=True)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("[ERROR] OPENAI_API_KEY environment variable is not set.", flush=True)
        sys.exit(1)

    # All LLM calls use the OpenAI client configured via these variables
    client = OpenAI(api_key=openai_api_key)

    results = []

    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as http:
        health = http.get("/")
        if health.status_code != 200:
            print(f"[ERROR] Environment at {API_BASE_URL} is not responding.", flush=True)
            sys.exit(1)
        print(f"[START] environment_healthy=true", flush=True)

        for i, difficulty in enumerate(DIFFICULTIES):
            # ------------------------------------------------------------------
            # STEP — one block per difficulty
            # ------------------------------------------------------------------
            print(f"[STEP] difficulty={difficulty}", flush=True)

            reset_resp = http.post("/reset", json={"task_difficulty": difficulty})
            reset_resp.raise_for_status()
            observation = reset_resp.json()
            print(f"[STEP] task_id={observation['task_id']}", flush=True)

            try:
                action = call_agent(client, observation)
            except Exception as e:
                print(f"[STEP] agent_error={e}", flush=True)
                action = {"flagged_lines": [], "findings": [], "review_text": ""}

            step_resp = http.post("/step", json=action)
            step_resp.raise_for_status()
            result = step_resp.json()

            reward = result["reward"]
            info = result.get("info", {})
            print(f"[STEP] reward={reward:.4f} info={info}", flush=True)

            results.append({
                "difficulty": difficulty,
                "task_id": observation["task_id"],
                "reward": reward,
                "info": info,
                "action": action,
            })

            if i < len(DIFFICULTIES) - 1:
                print("[STEP] sleeping 15s (rate limit guard)...", flush=True)
                time.sleep(15)

    # ------------------------------------------------------------------
    # END — structured log block
    # ------------------------------------------------------------------
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[END] results_path={RESULTS_PATH}", flush=True)
    for r in results:
        print(
            f"[END] difficulty={r['difficulty']} task_id={r['task_id']} reward={r['reward']:.4f}",
            flush=True,
        )
    print("[END]", flush=True)


if __name__ == "__main__":
    run_baseline()
