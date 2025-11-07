# agents/flow_discovery.py

def discover_flow(url: str, goal: str):
    """
    Flow Discovery Agent:
    Given a URL + natural language goal, return high-level steps.
    For hackathon: keyword-based / simple logic is enough.
    """
    goal_lower = goal.lower()

    if "login" in goal_lower:
        return [
            f"Open '{url}'",
            "Click on 'Login' button",
            "Enter email",
            "Enter password",
            "Click 'Sign in'",
            "Verify user lands on dashboard or sees 'Welcome'"
        ]
    # add more patterns (search, checkout, etc.) if you like

    # fallback generic flow
    return [
        f"Open '{url}'",
        "Verify page loads successfully"
    ]
