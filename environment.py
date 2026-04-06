"""
SupportGymEnv — stateful episode manager.
Wraps the task registry and graders behind the OpenEnv step/reset/state interface.
"""
from typing import Optional, Dict, Any, List

from models import Observation, Action, StepResult
from graders import grade
from tasks import TASK_REGISTRY


class SupportGymEnv:
    def __init__(self):
        self.task_id:         Optional[str]       = None
        self.config:          Optional[Dict]       = None
        self.step_count:      int                  = 0
        self.best_reward:     float                = 0.0
        self.done:            bool                 = False
        self.history:         List[Dict[str, Any]] = []
        self.previous_replies: List[str]           = []

    # ── reset ────────────────────────────────────────────────────────────────

    def reset(self, task_id: str = "easy") -> Observation:
        if task_id not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task_id '{task_id}'. "
                f"Available: {list(TASK_REGISTRY.keys())}"
            )

        self.task_id          = task_id
        self.config           = TASK_REGISTRY[task_id]
        self.step_count       = 0
        self.best_reward      = 0.0
        self.done             = False
        self.history          = []
        self.previous_replies = []

        return self._build_observation()

    # ── step ─────────────────────────────────────────────────────────────────

    def step(self, action: Action) -> StepResult:
        if self.done:
            raise RuntimeError("Episode is finished. Call reset() to start a new episode.")
        if self.task_id is None:
            raise RuntimeError("No active episode. Call reset() first.")

        self.step_count += 1

        # Grade the action
        score_breakdown = grade(self.task_id, action, self.config)
        reward          = float(score_breakdown["total"])

        # Track the best reward achieved this episode
        self.best_reward = max(self.best_reward, reward)

        # Record the agent's reply
        self.previous_replies.append(action.reply)

        # Episode ends when agent commits to a terminal decision OR max steps hit
        TERMINAL = {"resolve", "refund", "escalate"}
        is_terminal  = action.decision.value in TERMINAL
        reached_max  = self.step_count >= self.config["max_steps"]
        self.done    = is_terminal or reached_max

        # Append to history
        self.history.append({
            "step":       self.step_count,
            "action":     action.model_dump(),
            "reward":     reward,
            "breakdown":  score_breakdown,
            "done":       self.done,
        })

        return StepResult(
            observation=self._build_observation(),
            reward=reward,
            done=self.done,
            info={
                "breakdown":       score_breakdown,
                "step":            self.step_count,
                "best_reward":     self.best_reward,
                "task_difficulty": self.config["difficulty"],
            },
        )

    # ── state ────────────────────────────────────────────────────────────────

    def state(self) -> Dict[str, Any]:
        return {
            "task_id":      self.task_id,
            "step_count":   self.step_count,
            "best_reward":  self.best_reward,
            "done":         self.done,
            "history":      self.history,
        }

    # ── internal ─────────────────────────────────────────────────────────────

    def _build_observation(self) -> Observation:
        return Observation(
            task_id=          self.task_id,
            ticket_text=      self.config["ticket_text"],
            customer_history= self.config["customer_history"],
            context=          self.config["context"],
            step_count=       self.step_count,
            max_steps=        self.config["max_steps"],
            previous_replies= list(self.previous_replies),
            done=             self.done,
        )
