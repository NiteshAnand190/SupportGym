"""
SupportGym Baseline Inference Script
=====================================
Runs an LLM agent against all 3 SupportGym tasks and reports scores.

Required environment variables:
  API_BASE_URL  — LLM API base URL  (default: HuggingFace router)
  HF_TOKEN      — your HuggingFace token (free at huggingface.co)
  MODEL_NAME    — model to use        (default: Mistral-7B-Instruct)
  ENV_URL       — SupportGym server   (default: localhost:7860)

Usage:
  python inference.py
"""
import os
import json
import sys
import requests
from openai import OpenAI

# ── config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "hf_dummy"
MODEL_NAME   = os.getenv("MODEL_NAME") or "mistralai/Mistral-7B-Instruct-v0.3"
ENV_URL      = os.getenv("ENV_URL") or "http://localhost:7860"
MAX_STEPS    = 8

VALID_DECISIONS = {"resolve", "refund", "escalate", "request_info"}

SYSTEM_PROMPT = """You are an expert customer support agent. Your job is to handle customer tickets professionally.

Given a ticket, respond ONLY with a valid JSON object — no markdown, no explanation, just raw JSON:
{
  "reply": "<your full reply to the customer — empathetic, helpful, professional>",
  "decision": "<one of: resolve | refund | escalate | request_info>",
  "reason": "<one sentence explaining your decision>"
}

Decision guide:
- resolve      → you can fix it now with information or instructions
- refund       → customer is clearly eligible for a refund per policy
- escalate     → case needs a senior agent, manager, or specialist team
- request_info → you need more details before deciding

Rules:
- Always be empathetic and professional, even with angry customers
- Never make refund promises you are not authorized to make
- If outside return window but product is defective within warranty → escalate, never flat reject
- Keep replies clear and helpful — aim for 3–5 sentences minimum"""

# ── env client ────────────────────────────────────────────────────────────────

def env_call(method: str, endpoint: str, data: dict = None) -> dict:
    url = f"{ENV_URL}{endpoint}"
    try:
        if method == "POST":
            r = requests.post(url, json=data or {}, timeout=30)
        else:
            r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[ERROR] Environment call failed: {e}")
        sys.exit(1)


# ── llm client ────────────────────────────────────────────────────────────────

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def ask_llm(ticket: str, history: list, context: dict, step: int, max_steps: int) -> dict:
    user_message = f"""Customer ticket:
{ticket}

Customer history:
{json.dumps(history, indent=2)}

Relevant policy and context:
{json.dumps(context, indent=2)}

This is step {step} of maximum {max_steps}.
Reply with JSON only."""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.3,
            max_tokens=512,
        )
        raw = completion.choices[0].message.content or "{}"
    except Exception as e:
        print(f"  [LLM error] {e} — using fallback action")
        return {
            "reply":    "I sincerely apologize for the inconvenience. I will escalate this to our specialist team right away to ensure it gets the attention it deserves.",
            "decision": "escalate",
            "reason":   "LLM call failed — safe fallback",
        }

    # Clean and parse JSON
    clean = raw.strip()
    for fence in ["```json", "```"]:
        clean = clean.replace(fence, "")
    clean = clean.strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract JSON substring
        start = clean.find("{")
        end   = clean.rfind("}") + 1
        if start != -1 and end > start:
            try:
                parsed = json.loads(clean[start:end])
            except Exception:
                parsed = {}
        else:
            parsed = {}

    # Validate and sanitise
    if parsed.get("decision") not in VALID_DECISIONS:
        parsed["decision"] = "request_info"
    if not parsed.get("reply"):
        parsed["reply"] = raw[:500]

    return {
        "reply":    str(parsed.get("reply", "")),
        "decision": parsed["decision"],
        "reason":   str(parsed.get("reason", "")),
    }


# ── run one task ──────────────────────────────────────────────────────────────

def run_task(task_id: str) -> float:
    print(f"\n{'─'*55}")
    print(f"  Task: {task_id.upper()}")
    print(f"{'─'*55}")

    obs = env_call("POST", "/reset", {"task_id": task_id})
    print(f"  Ticket preview: {obs['ticket_text'][:90]}...")

    best_reward = 0.0

    for step_num in range(1, MAX_STEPS + 1):
        if obs.get("done"):
            break

        action = ask_llm(
            ticket    = obs["ticket_text"],
            history   = obs["customer_history"],
            context   = obs["context"],
            step      = obs["step_count"],
            max_steps = obs["max_steps"],
        )

        result      = env_call("POST", "/step", action)
        obs         = result["observation"]
        reward      = result["reward"]
        best_reward = max(best_reward, reward)
        breakdown   = result["info"]["breakdown"]

        print(
            f"  Step {step_num}: decision={action['decision']:12s} | "
            f"reward={reward:.3f} | breakdown={breakdown}"
        )

        if result["done"]:
            break

    print(f"  Best reward for '{task_id}': {best_reward:.3f}")
    return best_reward


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  SupportGym — Baseline Inference")
    print("=" * 55)
    print(f"  Model  : {MODEL_NAME}")
    print(f"  API    : {API_BASE_URL}")
    print(f"  Env    : {ENV_URL}")

    # Verify server is up
    health = env_call("GET", "/health")
    print(f"  Server : {health.get('status', 'unknown')}")

    scores: dict = {}
    for task_id in ["easy", "medium", "hard"]:
        try:
            scores[task_id] = run_task(task_id)
        except Exception as e:
            print(f"  [FAILED] {task_id}: {e}")
            scores[task_id] = 0.0

    avg = sum(scores.values()) / len(scores)

    print(f"\n{'='*55}")
    print("  FINAL SCORES")
    print(f"{'─'*55}")
    for task_id, score in scores.items():
        bar   = "█" * int(score * 20)
        print(f"  {task_id:8s}: {score:.3f}  {bar}")
    print(f"{'─'*55}")
    print(f"  {'average':8s}: {avg:.3f}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
