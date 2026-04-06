TASK_CONFIG = {
    "task_id":    "medium",
    "difficulty": "medium",
    "description": "Refund handling — wrong item delivered, customer is angry, within 30-day policy window",
    "max_steps": 5,

    "ticket_text": (
        "I ordered a blue shirt (Order #45821) two weeks ago and received a green one instead. "
        "I specifically needed the blue one for an important event this weekend. "
        "I want a FULL REFUND immediately. This is completely unacceptable — "
        "how does your warehouse even make this kind of mistake?!"
    ),

    "customer_history": [
        "Premium member for 2 years",
        "Order #45821 placed 14 days ago — Blue Formal Shirt Size M — $49.99",
        "3 previous successful orders",
        "No prior complaints or returns",
    ],

    "context": {
        "order": {
            "order_id":       "45821",
            "item_ordered":   "Blue Formal Shirt - Size M",
            "item_received":  "Green Casual Shirt - Size M",
            "order_date":     "14 days ago",
            "amount":         "$49.99",
            "payment_method": "Visa ending 4242",
        },
        "policy": {
            "refund_window_days":  30,
            "days_since_purchase": 14,
            "wrong_item_policy":   "Full refund OR free replacement — customer's choice, no return required",
            "processing_time":     "3-5 business days",
            "return_required":     False,
        },
    },

    "ground_truth": {
        "correct_decision":       "refund",
        "must_contain_keywords":  ["wrong", "refund", "apologi", "sorry"],
        "must_not_contain":       ["cannot refund", "no refund", "your fault", "nothing we can do"],
        "tone_markers": [
            "apologize", "sorry", "understand", "certainly",
            "absolutely", "inconvenience", "mistake",
        ],
        "eligible_for_refund":    True,
        "within_policy_window":   True,
    },
}
