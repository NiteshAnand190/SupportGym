TASK_CONFIG = {
    "task_id":    "easy",
    "difficulty": "easy",
    "description": "Simple FAQ resolution — customer forgot their password",
    "max_steps": 3,

    "ticket_text": (
        "Hi there, I forgot my password and I can't log into my account. "
        "I've tried the login page but I don't see a reset option anywhere. "
        "Can you help me get back in? My email is john.doe@example.com"
    ),

    "customer_history": [
        "Account created 6 months ago",
        "No previous support tickets",
        "Verified customer — email confirmed",
    ],

    "context": {
        "knowledge_base": {
            "password_reset": (
                "Go to login page → click 'Forgot Password' → enter your email "
                "→ check inbox for reset link (valid for 24 hours)"
            ),
            "account_locked": (
                "After 5 failed login attempts the account locks for 30 minutes automatically"
            ),
        },
        "policy": {
            "response_time_target": "under 2 minutes",
            "escalation_threshold": "only if account is suspected compromised",
        },
    },

    "ground_truth": {
        "correct_decision":       "resolve",
        "must_contain_keywords":  ["password", "reset", "email", "link"],
        "must_not_contain":       ["refund", "escalate", "supervisor", "cannot help"],
        "tone_markers": [
            "happy to help", "please", "let me know", "thank you",
            "hi", "hello", "glad", "certainly", "of course", "sure",
        ],
    },
}
