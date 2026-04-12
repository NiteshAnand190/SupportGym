"""
SupportGym — FastAPI server
OpenEnv-compatible: POST /reset · POST /step · GET /state
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from models import Action, Observation, StepResult, ResetRequest
from environment import SupportGymEnv

app = FastAPI(
    title="SupportGym",
    description=(
        "An OpenEnv-compatible reinforcement-learning environment "
        "for training AI agents on customer support tasks."
    ),
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One global env instance — stateful, one episode at a time
env = SupportGymEnv()


# ── OpenEnv required endpoints ────────────────────────────────────────────────

@app.post("/reset", response_model=Observation)
def reset(request: ResetRequest = None) -> Observation:
    """
    Start a new episode.
    Returns the initial Observation for the requested task.
    Accepts: { "task_id": "easy" | "medium" | "hard" }
    """
    task_id = (request.task_id if request else None) or "easy"
    try:
        return env.reset(task_id=task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResult)
def step(action: Action) -> StepResult:
    """
    Submit an action. Returns StepResult with observation, reward (0.0–1.0), done, info.
    action: { "reply": "...", "decision": "resolve|refund|escalate|request_info", "reason": "..." }
    """
    try:
        return env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state() -> Dict[str, Any]:
    """Return current episode state."""
    return env.state()


# ── helper endpoints ──────────────────────────────────────────────────────────

@app.get("/tasks")
def list_tasks():
    """List all available tasks."""
    return {
        "tasks": [
            {
                "task_id":     "easy",
                "difficulty":  "easy",
                "description": "Simple FAQ resolution — customer forgot password",
                "max_steps":   3,
            },
            {
                "task_id":     "medium",
                "difficulty":  "medium",
                "description": "Refund handling — wrong item, customer is angry, within policy",
                "max_steps":   5,
            },
            {
                "task_id":     "hard",
                "difficulty":  "hard",
                "description": "Complex escalation — out-of-window defect claim + chargeback threat",
                "max_steps":   8,
            },
        ]
    }


@app.get("/health")
def health():
    """Health check — always returns 200."""
    return {"status": "ok", "environment": "SupportGym", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "name": "SupportGym",
        "description": "Customer Support RL Environment",
        "docs": "/docs",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/health"],
    }
