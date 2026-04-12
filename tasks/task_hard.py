TASK_CONFIG = {
    "task_id":    "hard",
    "difficulty": "hard",
    "description": (
        "Complex escalation — product broke after 2 uses, 56 days since purchase "
        "(outside 30-day return window), customer threatening chargeback, demands manager"
    ),
    "max_steps": 8,

    "ticket_text": (
        "I bought your premium blender 8 weeks ago and it COMPLETELY stopped working after just 2 uses. "
        "TWO USES. I paid $120 for this garbage. I want a full refund RIGHT NOW. "
        "Your 30-day return policy is an absolute JOKE. If you don't sort this out TODAY "
        "I will dispute this charge with my bank, leave 1-star reviews on every platform I can find, "
        "and make sure everyone I know hears about how terrible your company is. "
        "I demand to speak to a manager immediately."
    ),

    "customer_history": [
        "Order #78234 placed 56 days ago",
        "Item: Premium Blender Pro — $120.00",
        "No previous returns or complaints",
        "Loyalty tier: GOLD — Total lifetime spend: $840",
    ],

    "context": {
        "order": {
            "order_id":   "78234",
            "item":       "Premium Blender Pro",
            "order_date": "56 days ago",
            "amount":     "$120.00",
        },
        "policy": {
            "standard_return_window_days": 30,
            "days_since_purchase":         56,
            "outside_standard_window":     True,
            "manufacturer_warranty_days":  365,
            "warranty_status":             "ACTIVE — product is within 1-year manufacturer warranty",
            "exceptional_case_policy": (
                "Product defect within warranty period qualifies for escalation review regardless of return window. "
                "Gold loyalty members with defect claims must be escalated — never outright rejected."
            ),
            "chargeback_guidance": (
                "Do NOT make refund promises. Acknowledge concern, empathise, escalate to senior team. "
                "Outright rejection increases chargeback risk."
            ),
        },
    },

    "ground_truth": {
        "correct_decision": "escalate",
        "must_contain_keywords": [
            "understand", "escalat", "warrant", "defect", "team",
        ],
        "must_not_contain": [
            "cannot help you", "nothing we can do", "your problem",
            "too bad", "policy is final", "not eligible",
        ],
        "forbidden_promises": [
            "full refund", "definitely refund", "guaranteed refund",
            "100% refund", "immediately refund", "refund right now",
        ],
        "tone_markers": [
            "understand your frustration", "sincerely apologize", "sorry",
            "take this seriously", "important to us", "value you",
            "escalate", "senior", "specialist",
        ],
    },
}
