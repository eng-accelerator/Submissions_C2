# agents/error_diagnosis.py

def diagnose(log: str):
    """
    Light-weight error diagnosis: looks at the execution log / traceback
    and returns a human readable summary.
    """
    if not log:
        return "No log output captured. Unable to determine the cause."

    lower = log.lower()

    if "timeout" in lower and "waiting for selector" in lower:
        return "Likely selector or timing issue: element did not appear before timeout."

    if "no such element" in lower or "cannot find" in lower:
        return "Selector issue: the script is looking for an element that does not exist."

    if "403" in lower or "401" in lower:
        return "Authentication or permission issue."

    if "navigation" in lower and "failed" in lower:
        return "Navigation failed; target URL might be unreachable or redirecting unexpectedly."

    if "sony vaio i5" in lower and "demoblaze" in lower:
        return "Demoblaze flow failed around product/cart/checkout; selectors or waits may need adjustment."

    return "The script encountered an error. Further analysis required."
