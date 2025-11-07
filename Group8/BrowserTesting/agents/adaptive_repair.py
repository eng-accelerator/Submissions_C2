# agents/adaptive_repair.py

def self_heal(script_code: str, error_logs: str):
    """
    Adaptive Repair Agent:
    Demo rule:
    - If waiting for get_by_role("button", name="Login") timed out,
      try a more generic 'Sign in' text-based locator.
    """
    repaired = script_code
    note = "No automatic fix available. Please review manually."

    if 'get_by_role("button", name="Login")' in script_code and "Timeout 30000ms" in error_logs:
        repaired = script_code.replace(
            'page.get_by_role("button", name="Login").click()',
            'page.get_by_text("Sign in").click()  # self-healed selector'
        )
        note = (
            "Updated Login locator from role-based 'Login' button to a text-based "
            "'Sign in' locator, assuming the site uses a different label."
        )

    return repaired, note
