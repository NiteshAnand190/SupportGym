---
title: SupportGym
emoji: 🤖
colorFrom: yellow
colorTo: blue
sdk: docker
app_file: main.py
pinned: false
---

# SupportGym

SupportGym is an **OpenEnv-compatible reinforcement learning environment** designed to train and evaluate AI agents on realistic **customer support workflows**.

Unlike toy environments, SupportGym simulates real-world decision-making where agents must balance **policy compliance, customer satisfaction, and business constraints**.

---

## Why SupportGym?

Customer support is one of the most common and complex real-world applications of AI. Effective handling requires:

* Understanding and applying policies (with exceptions)
* Managing emotionally charged conversations
* Making correct decisions under uncertainty
* Avoiding harmful or unauthorized commitments

SupportGym provides a structured environment where agents can **learn, act, and be evaluated** on these exact challenges.

---

## Key Features

* OpenEnv-compliant (`reset`, `step`, `state`)
* Real-world task simulation (not synthetic or game-based)
* Multi-step reasoning with partial observability
* Deterministic, interpretable reward signals
* Progressive difficulty: easy → medium → hard
* Fully reproducible baseline evaluation

---

## Environment Overview

| Property    | Value                                                   |
| ----------- | ------------------------------------------------------- |
| Task type   | Text-based decision making                              |
| Observation | Ticket text, customer history, policy context           |
| Action      | Reply + decision (resolve/refund/escalate/request_info) |
| Reward      | Continuous (0.0–1.0), never binary                      |
| Tasks       | 3 (easy → medium → hard)                                |
| Max steps   | 3 / 5 / 8                                               |
| Runtime     | < 2 min per task, < 20 min total                        |

---

## Action Space

```json
{
  "reply": "Customer-facing response",
  "decision": "resolve | refund | escalate | request_info",
  "reason": "Optional explanation"
}
```

---

## Observation Space

```json
{
  "task_id": "easy",
  "ticket_text": "Customer message...",
  "customer_history": ["..."],
  "context": { "policy": {...}, "order": {...} },
  "step_count": 1,
  "max_steps": 3,
  "previous_replies": [],
  "done": false
}
```

---

## Tasks

### 🟢 Easy — FAQ Resolution

Customer forgot their password.

* **Goal:** Provide correct instructions with professional tone
* **Skills:** clarity, accuracy, basic empathy
* **Scoring:** decision (50%) + tone (30%) + accuracy (20%)
* **Baseline score:** **1.000**

---

### 🟡 Medium — Refund Handling

Customer received the wrong item and is frustrated.

* **Goal:** Apply policy correctly and de-escalate
* **Skills:** policy reasoning, empathy, action correctness
* **Scoring:** policy (40%) + tone (30%) + action (30%)
* **Baseline score:** **0.9625**

---

### 🔴 Hard — Complex Escalation

Defective product outside return window, within warranty, customer threatens chargeback.

* **Goal:** Recognize exception and escalate appropriately
* **Skills:** judgment under pressure, policy exceptions, risk handling
* **Scoring:** escalation (35%) + tone (25%) + no_promises (20%) + awareness (20%)
* **Baseline score:** **0.98**

---

## Baseline Performance

Model: `meta-llama/Meta-Llama-3-8B-Instruct`

| Task    | Score      |
| ------- | ---------- |
| easy    | 1.000      |
| medium  | 0.9625     |
| hard    | 0.9800     |
| **avg** | **0.9808** |

---

## Reward Design

SupportGym uses **composite, non-binary rewards**:

* Decision correctness
* Policy adherence
* Tone and empathy
* Keyword/issue coverage
* Penalties for unsafe responses
* Minimum quality threshold

---

## Setup & Usage

### Run locally

```bash
git clone https://github.com/YOUR_USERNAME/supportgym
cd supportgym
pip install -r requirements.txt
uvicorn main:app --port 7860
```

---

### Run with Docker

```bash
docker build -t supportgym .
docker run -p 7860:7860 supportgym
```

---

### Run baseline agent

```bash
set HF_TOKEN=your_token_here
set MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
set API_BASE_URL=https://router.huggingface.co/v1
set ENV_URL=https://niteshanand-supportgym.hf.space

python inference.py
```

---

## API

| Method | Endpoint | Description    |
| ------ | -------- | -------------- |
| POST   | /reset   | Start new task |
| POST   | /step    | Submit action  |
| GET    | /state   | Current state  |
| GET    | /tasks   | List tasks     |
| GET    | /health  | Health check   |

---

## Design Notes

* Single-session environment (evaluation simplicity)
* Deterministic grading
* Designed for real-world agent behavior

---

## Environment Variables

| Variable     | Description         |
| ------------ | ------------------- |
| HF_TOKEN     | HuggingFace API key |
| API_BASE_URL | LLM endpoint        |
| MODEL_NAME   | Model identifier    |
| ENV_URL      | Environment URL     |

---

## License

Apache 2.0
