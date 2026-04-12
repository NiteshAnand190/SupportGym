"""
Graders for SupportGym.
Each grader returns a dict with sub-scores and a 'total' key (0.0 – 1.0).
All scoring is deterministic — same input always produces same output.
"""
from typing import Dict, Any
from models import Action, Decision

def _invalid_reply(reply: str) -> bool:
    return (not reply) or (len(reply.strip()) < 10)

# ── helpers ──────────────────────────────────────────────────────────────────

def _tone_score(reply: str, markers: list) -> float:
    """Fraction of tone markers present, capped at 1.0."""
    if not markers:
        return 1.0
    low = reply.lower()
    hits = sum(1 for m in markers if m.lower() in low)
    # Require at least 30% of markers for any credit
    threshold = max(1, int(len(markers) * 0.3))
    return min(1.0, hits / threshold) if hits >= 1 else 0.0


def _keyword_score(reply: str, keywords: list) -> float:
    """Fraction of required keywords present."""
    if not keywords:
        return 1.0
    low = reply.lower()
    hits = sum(1 for kw in keywords if kw.lower() in low)
    return hits / len(keywords)


def _forbidden_penalty(reply: str, forbidden: list) -> float:
    """1.0 if none present, reduced by 0.4 per hit, floor 0.0."""
    if not forbidden:
        return 1.0
    low = reply.lower()
    hits = sum(1 for f in forbidden if f.lower() in low)
    return max(0.0, 1.0 - hits * 0.4)


def _reply_length_ok(reply: str, min_words: int = 20) -> float:
    """Penalise trivially short replies."""
    words = len(reply.split())
    if words >= min_words:
        return 1.0
    return words / min_words


# ── task graders ─────────────────────────────────────────────────────────────

def grade_easy(action: Action, config: Dict[str, Any]) -> Dict[str, float]:
    """
    Task 1 — FAQ password reset.
    Weights: correct_decision 50% | tone 30% | no_hallucination 20%
    """
    gt = config["ground_truth"]

    if _invalid_reply(action.reply):
        return {"decision": 0.0, "tone": 0.0, "accuracy": 0.0, "total": 0.0}

    # Decision (50%)
    decision_base = 1.0 if action.decision == Decision.resolve else 0.0
    keyword_cov   = _keyword_score(action.reply, gt["must_contain_keywords"])
    decision_score = decision_base * 0.6 + keyword_cov * 0.4  # blend

    # Tone (30%)
    tone_score = _tone_score(action.reply, gt["tone_markers"])

    # No hallucination / forbidden content (20%)
    accuracy_score = (
        _forbidden_penalty(action.reply, gt["must_not_contain"]) * 0.7
        + _reply_length_ok(action.reply, min_words=20) * 0.3
    )

    breakdown = {
        "decision": round(decision_score * 0.50, 4),
        "tone":     round(tone_score     * 0.30, 4),
        "accuracy": round(accuracy_score * 0.20, 4),
    }
    breakdown["total"] = round(sum(breakdown.values()), 4)
    return breakdown


def grade_medium(action: Action, config: Dict[str, Any]) -> Dict[str, float]:
    """
    Task 2 — Wrong item refund.
    Weights: policy_adherence 40% | de_escalation 30% | correct_action 30%
    """
    gt = config["ground_truth"]
    
    if _invalid_reply(action.reply):
        return {"policy": 0.0, "tone": 0.0, "action": 0.0, "total": 0.0}

    # Policy adherence (40%)
    if action.decision == Decision.refund:
        policy_score = 1.0
    elif action.decision == Decision.escalate:
        policy_score = 0.5   # acceptable but suboptimal
    elif action.decision == Decision.request_info:
        policy_score = 0.25  # unnecessary — all info is available
    else:
        policy_score = 0.0   # resolve without addressing refund = wrong

    # De-escalation / empathy (30%)
    tone_score = _tone_score(action.reply, gt["tone_markers"])

    # Correct action details (30%)
    keyword_score  = _keyword_score(action.reply, gt["must_contain_keywords"])
    forbidden_ok   = _forbidden_penalty(action.reply, gt["must_not_contain"])
    length_ok      = _reply_length_ok(action.reply, min_words=30)
    action_score   = keyword_score * 0.5 + forbidden_ok * 0.3 + length_ok * 0.2

    breakdown = {
        "policy": round(policy_score * 0.40, 4),
        "tone":   round(tone_score   * 0.30, 4),
        "action": round(action_score * 0.30, 4),
    }
    breakdown["total"] = round(sum(breakdown.values()), 4)
    return breakdown


def grade_hard(action: Action, config: Dict[str, Any]) -> Dict[str, float]:
    """
    Task 3 — Out-of-window defective product, chargeback threat.
    Weights: escalation_decision 35% | tone_under_pressure 25% | no_bad_promises 20% | awareness 20%
    """
    gt = config["ground_truth"]

    if _invalid_reply(action.reply):
        return {
            "escalation": 0.0,
            "tone": 0.0,
            "no_promises": 0.0,
            "awareness": 0.0,
            "total": 0.0
        }

    # Escalation decision (35%)
    if action.decision == Decision.escalate:
        escalation_score = 1.0
    elif action.decision == Decision.request_info:
        escalation_score = 0.35  # at least not a hard no
    elif action.decision == Decision.refund:
        escalation_score = 0.15  # made a promise it shouldn't
    else:  # resolve — dismissing the customer entirely
        escalation_score = 0.0

    # Tone under pressure (25%)
    tone_score = _tone_score(action.reply, gt["tone_markers"])

    # No bad promises (20%)
    no_promises_score = _forbidden_penalty(action.reply, gt["forbidden_promises"])

    # Awareness — mentions warranty / escalation path / doesn't outright reject (20%)
    awareness_kw      = _keyword_score(action.reply, gt["must_contain_keywords"])
    no_rejection      = _forbidden_penalty(action.reply, gt["must_not_contain"])
    length_ok         = _reply_length_ok(action.reply, min_words=40)
    awareness_score   = awareness_kw * 0.5 + no_rejection * 0.35 + length_ok * 0.15

    breakdown = {
        "escalation":  round(escalation_score  * 0.35, 4),
        "tone":        round(tone_score        * 0.25, 4),
        "no_promises": round(no_promises_score  * 0.20, 4),
        "awareness":   round(awareness_score    * 0.20, 4),
    }
    breakdown["total"] = round(sum(breakdown.values()), 4)
    return breakdown


# ── public interface ──────────────────────────────────────────────────────────

GRADER_MAP = {
    "easy":   grade_easy,
    "medium": grade_medium,
    "hard":   grade_hard,
}


def grade(task_id: str, action: Action, config: Dict[str, Any]) -> Dict[str, float]:
    grader = GRADER_MAP.get(task_id)
    if not grader:
        raise ValueError(f"No grader for task_id '{task_id}'. Available: {list(GRADER_MAP)}")
    return grader(action, config)
