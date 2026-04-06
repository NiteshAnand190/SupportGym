# SupportGym

An OpenEnv-compatible reinforcement learning environment for training AI agents on real-world **customer support** tasks.

---

## What is SupportGym?

Every company in the world runs a customer support queue. Handling tickets well requires:
- Understanding policy and knowing when rules have exceptions
- De-escalating angry customers without making promises you can't keep
- Deciding when to resolve, refund, or escalate — with partial information

SupportGym gives AI agents a standardised training ground for exactly this skill, with 3 difficulty-graded tasks and a meaningful partial-reward signal.

---

## Environment Overview

| Property       | Value                                                    |
|----------------|----------------------------------------------------------|
| Task type      | Text-based decision making                               |
| Observation    | Ticket text, customer history, policy context            |
| Action         | Reply text + decision (resolve/refund/escalate/request_info) |
| Reward         | 0.0 – 1.0 composite score (never binary)                |
| Tasks          | 3 (easy → medium → hard)                                |
| Max steps      | 3 / 5 / 8 per task                                      |
| Runtime        | < 2 min per task, < 20 min total                         |

---

## Action Space

```json
{
  "reply":    "Your full text response to the customer",
  "decision": "resolve | refund | escalate | request_info",
  "reason":   "Optional one-sentence reasoning"
}
```

## Observation Space

```json
{
  "task_id":          "easy",
  "ticket_text":      "Customer message...",
  "customer_history": ["Account created 6 months ago", "..."],
  "context":          { "policy": {...}, "order": {...} },
  "step_count":       1,
  "max_steps":        3,
  "previous_replies": [],
  "done":             false
}
```

---

## Tasks

### Task 1 — Easy: FAQ Resolution
**Scenario:** Customer forgot their password and can't log in.  
**What agent must do:** Provide correct reset instructions, professional tone.  
**Grading:** decision (50%) + tone (30%) + accuracy (20%)  
**Baseline score:** ~0.72

### Task 2 — Medium: Refund Handling
**Scenario:** Customer received the wrong item, is angry, order is 14 days old (within 30-day window).  
**What agent must do:** Approve refund, de-escalate, follow policy correctly.  
**Grading:** policy adherence (40%) + de-escalation (30%) + correct action (30%)  
**Baseline score:** ~0.61

### Task 3 — Hard: Complex Escalation
**Scenario:** Premium customer, product broke after 2 uses, 56 days ago (outside return window but within warranty), threatening chargeback.  
**What agent must do:** Stay professional, recognise warranty exception, escalate — never flat-reject or make promises.  
**Grading:** escalation decision (35%) + tone under pressure (25%) + no bad promises (20%) + awareness (20%)  
**Baseline score:** ~0.48

---

## Baseline Scores (Mistral-7B-Instruct-v0.3)

| Task   | Score |
|--------|-------|
| easy   | 0.720 |
| medium | 0.610 |
| hard   | 0.480 |
| **avg**| **0.603** |

---

## Setup & Usage

### Option A — Run locally

```bash
git clone https://github.com/YOUR_USERNAME/supportgym
cd supportgym

pip install -r requirements.txt

uvicorn main:app --reload --port 7860
# → open http://localhost:7860/docs to test all endpoints
```

### Option B — Run with Docker

```bash
docker build -t supportgym .
docker run -p 7860:7860 supportgym
```

### Run the baseline agent

```bash
export HF_TOKEN=hf_your_token_here
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
export ENV_URL=http://localhost:7860

python inference.py
```

---

## API Reference

| Method | Endpoint  | Body                        | Returns               |
|--------|-----------|-----------------------------|------------------------|
| POST   | /reset    | `{ "task_id": "easy" }`     | Observation            |
| POST   | /step     | Action object               | StepResult (reward)    |
| GET    | /state    | —                           | Current episode state  |
| GET    | /tasks    | —                           | List of available tasks|
| GET    | /health   | —                           | Server health          |
| GET    | /docs     | —                           | Interactive API docs   |

---

## Reward Function Design

Rewards are never binary. Every response gets partial credit:

- **Decision matching** — did the agent choose the objectively correct action?
- **Tone scoring** — does the reply contain professional, empathetic language markers?
- **Keyword coverage** — does the reply address the core issue?
- **Forbidden phrase penalty** — is the agent making promises it shouldn't, or dismissing the customer?
- **Reply length** — is the response substantive enough to actually help?

This means an agent that picks the wrong decision but responds professionally still earns ~0.3, giving meaningful learning signal throughout training.

---

## Environment Variables

| Variable      | Description                              | Default                                    |
|---------------|------------------------------------------|--------------------------------------------|
| `HF_TOKEN`    | Your HuggingFace access token            | required for inference.py                  |
| `API_BASE_URL`| LLM API endpoint                         | `https://router.huggingface.co/v1`         |
| `MODEL_NAME`  | Model identifier                         | `mistralai/Mistral-7B-Instruct-v0.3`       |
| `ENV_URL`     | SupportGym server URL                    | `http://localhost:7860`                    |

---

## License

Apache 2.0
