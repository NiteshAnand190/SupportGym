from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class Decision(str, Enum):
    resolve      = "resolve"
    refund       = "refund"
    escalate     = "escalate"
    request_info = "request_info"


class Action(BaseModel):
    reply:    str            = Field(..., description="Text reply to send to the customer")
    decision: Decision       = Field(..., description="Action decision: resolve/refund/escalate/request_info")
    reason:   Optional[str]  = Field(None, description="Optional reasoning for the decision")


class Observation(BaseModel):
    task_id:          str             = Field(..., description="Active task ID")
    ticket_text:      str             = Field(..., description="The customer support ticket text")
    customer_history: List[str]       = Field(..., description="Customer account history")
    context:          Dict[str, Any]  = Field(..., description="Policies, order info, knowledge base")
    step_count:       int             = Field(..., description="Current step number")
    max_steps:        int             = Field(..., description="Maximum steps allowed")
    previous_replies: List[str]       = Field(..., description="Agent replies so far this episode")
    done:             bool            = Field(..., description="Whether episode is finished")


class StepResult(BaseModel):
    observation: Observation
    reward:      float            = Field(..., ge=0.0, le=1.0)
    done:        bool
    info:        Dict[str, Any]


class ResetRequest(BaseModel):
    task_id: str = Field(default="easy", description="Task ID: easy | medium | hard")


class StateResponse(BaseModel):
    task_id:      Optional[str]
    step_count:   int
    total_reward: float
    done:         bool
    history:      List[Dict[str, Any]]
