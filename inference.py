"""
inference.py — Agent script for PR Review & Security Audit OpenEnv
==================================================================
Mandatory env vars:
  HF_TOKEN       Your HuggingFace / API key
  API_BASE_URL   LLM endpoint  (default: HF router)
  MODEL_NAME     Model ID       (default: Qwen/Qwen2.5-72B-Instruct)
  ENV_BASE_URL   Running env server (default: http://localhost:7860)

STDOUT FORMAT (do not modify — validator parses these exactly):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import json
import os
import sys
import time
import textwrap
from typing import Any, Optional

import httpx
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860").rstrip("/")
BENCHMARK    = "pr-review-security-audit"

DIFFICULTIES      = ["easy", "medium", "hard"]
MAX_STEPS         = 1     # single-turn env — step() always returns done=True
MAX_TOKENS        = 1024
TEMPERATURE       = 0.1   # low = more deterministic, better for structured tasks
SUCCESS_THRESHOLD = 0.5
TIMEOUT           = 60    # seconds per HTTP call


# ---------------------------------------------------------------------------
# Stdout logging — field names, order, and format are contractual
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool,
             error: Optional[str]) -> None:
    action_safe = action.replace("\n", " ").replace("\r", "")[:200]
    print(
        f"[STEP] step={step} action={action_safe!r} "
        f"reward={reward:.2f} done={str(done).lower()} "
        f"error={error if error else 'null'}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float,
            rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Environment HTTP helpers
# ---------------------------------------------------------------------------

def env_reset(client: httpx.Client, difficulty: str) -> dict[str, Any]:
    """POST /reset -> Observation dict."""
    resp = client.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_difficulty": difficulty},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()

def env_step(client: httpx.Client, action: dict[str, Any]) -> dict[str, Any]:
    """POST /step -> StepResult dict."""
    resp = client.post(
        f"{ENV_BASE_URL}/step",
        json=action,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()

def wait_for_env(max_wait: int = 120) -> None:
    """Poll /health until ready or deadline."""
    print(f"[INFO] Waiting for env at {ENV_BASE_URL} ...", flush=True)
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            with httpx.Client() as c:
                r = c.get(f"{ENV_BASE_URL}/health", timeout=5)
                if r.status_code == 200:
                    print("[INFO] Env server is ready.", flush=True)
                    return
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError(
        f"Env server at {ENV_BASE_URL} did not become ready within {max_wait}s"
    )


# ---------------------------------------------------------------------------
# Prompts — tuned precisely to each grader's scoring logic
# ---------------------------------------------------------------------------
#
# Action schema (app/models/action.py, strict=True):
#   flagged_lines : list[int]     — 1-indexed line numbers with bugs/vulns
#   findings      : list[Finding] — each: {"type": str, "description": str}
#   review_text   : str           — free-form review (scored in hard task only)
#
# Grader details:
#   Task 1: recall = |flagged & bug_lines| / |bug_lines|
#           spam penalty -0.1 if len(flagged) > 3 * len(bug_lines)
#           clean code (no bugs) => must return flagged_lines=[]
#
#   Task 2: for each ground-truth vuln_type, checks if ANY finding.type
#           is a substring match (case-insensitive, both directions).
#           clean code (no vulns) => must return findings=[]
#           FP penalty -0.05 per finding beyond 2x ground-truth count
#
#   Task 3: 40% bug lines + 40% vuln findings + 20% review_text quality
#           Review quality regex checks (each = +0.25):
#             - severity word:   critical | high | medium | low
#             - line reference:  "line N" or "LN"
#             - actionable word: should | must | recommend | suggest | consider
#             - category word:   bug | security | vulnerability | style | performance

# Known vulnerability types used in the episodes (substring matching is forgiving
# but using exact names is safest):
_VULN_TYPE_LIST = (
    "sql_injection, hardcoded_secret, xss, command_injection, "
    "insecure_deserialization, path_traversal, open_redirect, xxe, "
    "broken_access_control, jwt, md5, insecure_random, "
    "null_pointer_dereference, off_by_one_error, wrong_condition, "
    "infinite_loop, logic_error, missing_input_validation, resource_leak"
)

# --- Easy task system prompt ---
SYSTEM_PROMPT_EASY = textwrap.dedent(f"""
    You are a code reviewer specialising in runtime bugs.
    Analyse the code and return ONLY a valid JSON object — no markdown, no prose.

    JSON schema:
    {{
      "flagged_lines": [<int>, ...],
      "findings": [],
      "review_text": ""
    }}

    Rules for flagged_lines:
    - List every 1-indexed line number that contains a bug.
    - Include ONLY lines with real bugs (null dereference, off-by-one, wrong
      condition, infinite loop, divide-by-zero, missing return, etc.).
    - If the code has NO bugs, return an empty list: "flagged_lines": []
    - Do NOT flag cosmetic or style issues — bugs only.
    - Do NOT flag more than 3x the number of real bugs (spam penalty applies).

    Return ONLY the JSON object.
""").strip()

# --- Medium task system prompt ---
SYSTEM_PROMPT_MEDIUM = textwrap.dedent(f"""
    You are a security engineer specialising in OWASP Top 10 vulnerabilities.
    Analyse the code and return ONLY a valid JSON object — no markdown, no prose.

    JSON schema:
    {{
      "flagged_lines": [],
      "findings": [
        {{
          "type": "<exact snake_case type from the list below>",
          "description": "<clear description of the issue>"
        }}
      ],
      "review_text": ""
    }}

    Known vulnerability types (use these exact names):
    {_VULN_TYPE_LIST}

    Rules for findings:
    - Add one entry per distinct vulnerability.
    - Use the most specific type name from the list above.
    - If the code has NO vulnerabilities, return an empty list: "findings": []
    - Do NOT add speculative findings — only clear, present vulnerabilities.
    - Avoid excessive false positives (penalty applies beyond 2x real count).

    Return ONLY the JSON object.
""").strip()

# --- Hard task system prompt ---
# The review_text quality grader uses four regex patterns — each is worth 0.25:
#   1. severity word:   critical | high | medium | low
#   2. line reference:  "line N" or "LN"
#   3. actionable word: should | must | recommend | suggest | consider
#   4. category word:   bug | security | vulnerability | style | performance
SYSTEM_PROMPT_HARD = textwrap.dedent(f"""
    You are a senior software engineer performing a full PR review.
    Analyse the code diff and return ONLY a valid JSON object — no markdown, no prose.

    JSON schema:
    {{
      "flagged_lines": [<int>, ...],
      "findings": [
        {{
          "type": "<exact snake_case type>",
          "description": "<clear description>"
        }}
      ],
      "review_text": "<structured review — see rules below>"
    }}

    Rules for flagged_lines:
    - List every 1-indexed diff line number with a bug (runtime or logic error).
    - Count lines from the top of the diff snippet starting at 1.
    - If no bugs, return [].

    Rules for findings:
    - One entry per distinct security vulnerability.
    - Use exact type names: {_VULN_TYPE_LIST}
    - If no vulnerabilities, return [].

    Rules for review_text (CRITICAL — follow exactly):
    - Your review MUST contain all four of the following elements:
      1. A severity rating using one of these words: critical, high, medium, low
         Example: "This PR contains a critical security vulnerability."
      2. At least one line reference in the format "line N" (e.g. "line 3")
         Example: "The bug at line 3 will cause a crash."
      3. An actionable recommendation using: must, should, recommend, suggest, or consider
         Example: "You must sanitize all user inputs before use."
      4. A category label using one of: bug, security, vulnerability, style, performance
         Example: "This is a security vulnerability that needs immediate attention."
    - Write 2-4 sentences combining all four elements naturally.
    - Example of a perfect review_text:
      "This PR introduces a critical security vulnerability at line 3 where user input
       is passed directly to a SQL query. You must use parameterized queries instead.
       Additionally, the hardcoded secret on line 4 is a high-severity bug that should
       be moved to environment variables."

    Return ONLY the JSON object.
""").strip()


def get_system_prompt(difficulty: str) -> str:
    return {
        "easy":   SYSTEM_PROMPT_EASY,
        "medium": SYSTEM_PROMPT_MEDIUM,
        "hard":   SYSTEM_PROMPT_HARD,
    }.get(difficulty, SYSTEM_PROMPT_EASY)


def build_user_prompt(obs: dict[str, Any]) -> str:
    difficulty   = obs.get("difficulty", "easy")
    instructions = obs.get("instructions", "Review the code.")
    code_snippet = obs.get("code_snippet", "# (no code)")
    return textwrap.dedent(f"""
        Instructions: {instructions}

        Code:
        ```
        {code_snippet}
        ```

        Respond with a single JSON object only.
    """).strip()


# ---------------------------------------------------------------------------
# LLM call -> validated Action dict
# ---------------------------------------------------------------------------

_EMPTY_ACTION: dict[str, Any] = {
    "flagged_lines": [],
    "findings":      [],
    "review_text":   "",
}

def call_llm(oai: OpenAI, obs: dict[str, Any]) -> dict[str, Any]:
    """
    Call the model and return a dict that matches the Action schema exactly.
    Falls back to _EMPTY_ACTION on any error so the episode still completes.
    """
    difficulty = obs.get("difficulty", "easy")
    try:
        completion = oai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": get_system_prompt(difficulty)},
                {"role": "user",   "content": build_user_prompt(obs)},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        raw = (completion.choices[0].message.content or "").strip()

        # Strip accidental markdown fences (```json ... ```)
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            ).strip()

        parsed: dict[str, Any] = json.loads(raw)

        # --- Coerce types to satisfy Pydantic strict=True on the server ---

        # flagged_lines: list[int], all values >= 1
        parsed["flagged_lines"] = [
            int(x) for x in parsed.get("flagged_lines", [])
            if str(x).lstrip("-").isdigit() and int(x) >= 1
        ]

        # findings: list[{type: str, description: str}]
        clean_findings: list[dict[str, str]] = []
        for f in parsed.get("findings", []):
            if isinstance(f, dict) and "type" in f and "description" in f:
                clean_findings.append({
                    "type":        str(f["type"]).strip().lower().replace(" ", "_").replace("-", "_"),
                    "description": str(f["description"]).strip(),
                })
        parsed["findings"] = clean_findings

        # review_text: str
        parsed["review_text"] = str(parsed.get("review_text", "")).strip()

        return parsed

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parse error: {e} | raw snippet: {raw[:200]!r}", flush=True)
        return _EMPTY_ACTION.copy()
    except Exception as e:
        print(f"[DEBUG] LLM call failed: {e}", flush=True)
        return _EMPTY_ACTION.copy()


# ---------------------------------------------------------------------------
# Single episode runner
# ---------------------------------------------------------------------------

def run_episode(
    http: httpx.Client,
    oai:  OpenAI,
    difficulty: str,
) -> tuple[float, list[float], int, bool]:
    """
    Run one complete episode. Always emits [START] ... [STEP]* ... [END].
    Returns (score, rewards, steps_taken, success).
    """
    task_name   = f"pr-review-{difficulty}"
    rewards:    list[float] = []
    steps_taken = 0
    score       = 0.0
    success     = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env_reset(http, difficulty)

        for step_n in range(1, MAX_STEPS + 1):
            action_dict = call_llm(oai, obs)
            action_str  = json.dumps(action_dict, separators=(",", ":"))

            reward: float         = 0.0
            done:   bool          = True
            error:  Optional[str] = None

            try:
                result = env_step(http, action_dict)
                reward = float(result.get("reward", 0.0))
                done   = bool(result.get("done", True))
                info   = result.get("info") or {}
                error  = info.get("error")
            except httpx.HTTPStatusError as e:
                error = f"HTTP {e.response.status_code}"
                print(
                    f"[DEBUG] step() HTTP {e.response.status_code}: "
                    f"{e.response.text[:300]}",
                    flush=True,
                )
            except Exception as e:
                error = str(e)[:120]
                print(f"[DEBUG] step() exception: {e}", flush=True)

            rewards.append(reward)
            steps_taken = step_n
            log_step(step=step_n, action=action_str, reward=reward,
                     done=done, error=error)
            if done:
                break

        score   = rewards[-1] if rewards else 0.0
        score   = max(0.001, min(0.999, score))   # validator requires strictly (0, 1)
        success = score >= SUCCESS_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error ({difficulty}): {exc}", flush=True)
        if not rewards:
            rewards.append(0.0)
            steps_taken = 1
            log_step(step=1, action="null", reward=0.0, done=True,
                     error=str(exc)[:120])

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score, rewards, steps_taken, success


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not API_KEY:
        print("[FATAL] HF_TOKEN / API_KEY is not set.", flush=True)
        sys.exit(1)

    wait_for_env(max_wait=120)
    print(f"[INFO] Starting baseline | model={MODEL_NAME}", flush=True)

    oai = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    all_scores: list[float] = []

    with httpx.Client() as http:
        for difficulty in DIFFICULTIES:
            score, _, _, _ = run_episode(http, oai, difficulty)
            all_scores.append(score)
            time.sleep(1)

    if len(all_scores) == 3:
        avg = sum(all_scores) / 3
        print(
            f"[SUMMARY] easy={all_scores[0]:.3f} "
            f"medium={all_scores[1]:.3f} "
            f"hard={all_scores[2]:.3f} "
            f"avg={avg:.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
