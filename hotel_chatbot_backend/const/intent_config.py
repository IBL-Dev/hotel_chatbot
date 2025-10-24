# ---- All supported intents and their keyword triggers ----
INTENTS = {
    "booking": [
        "book", "reservation", "reserve", "check-in", "check in",
        "check out", "room", "booking", "stay", "availability"
    ],
    "service": [
        "spa", "restaurant", "menu", "taxi", "transport",
        "service", "housekeeping", "clean", "food", "laundry"
    ],
    "complaint": [
        "complain", "problem", "issue", "dirty", "delay",
        "bad service", "not working", "broken"
    ],
    "how_to_use": [
        "how to", "help", "guide", "explain", "instructions"
    ]
}

DEFAULT_INTENT = "unknown"
