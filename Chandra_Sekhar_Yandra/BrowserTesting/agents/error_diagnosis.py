# agents/error_diagnosis.py

def diagnose(error_logs: str):
    """
    Error Diagnosis Agent:
    Look at logs/error text, return explanation + probable root cause.
    """
    if "#login-btn" in error_logs or "Element '#login-btn' not found" in error_logs:
        explanation = (
            "The script failed looking for '#login-btn', "
            "which is missing in the current DOM."
        )
        root_cause = "Outdated selector for Login button."
    else:
        explanation = "The script encountered an error. Further analysis required."
        root_cause = "Unknown yet."

    return explanation, root_cause
