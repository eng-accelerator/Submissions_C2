# agents/script_generator.py

from urllib.parse import urlparse
import textwrap

# Centralized LLM helpers (OpenRouter etc.) live under agents.llm.
# Fallbacks keep the app running even if LLM is not configured.
try:
    from agents.llm.llm_client import llm_chat
    from agents.llm.llm_utils import clean_llm_code
except ImportError:
    try:
        from llm.llm_client import llm_chat  # alt layout
        from llm.llm_utils import clean_llm_code
    except ImportError:
        def llm_chat(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
            return ""

        def clean_llm_code(text: str) -> str:
            return text


# ==================== Shared Playwright Harness ====================

HARNESS_HEADER = """\
from playwright.sync_api import sync_playwright
import sys


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
"""

HARNESS_FOOTER = """\
        except Exception as e:
            print("ERROR:", e)
            try:
                page.screenshot(path="run_error.png", full_page=True)
            except Exception:
                pass
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    run()
"""


def _indent(code: str, spaces: int = 12) -> str:
    return textwrap.indent(code.strip("\n"), " " * spaces)


# ==================== Hand-crafted Scenario Scripts ====================


def _script_login_internet(url: str) -> str:
    body = f"""
page.goto("{url}")
page.fill("#username", "tomsmith")
page.fill("#password", "SuperSecretPassword!")
page.click("button.radius")
page.wait_for_selector("div.flash.success", timeout=5000)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_saucedemo_backpack(url: str) -> str:
    body = f"""
page.goto("{url}", wait_until="load")
page.fill("#user-name", "standard_user")
page.fill("#password", "secret_sauce")
page.click("#login-button")

page.wait_for_selector(".inventory_item", timeout=5000)
page.click("button#add-to-cart-sauce-labs-backpack")

page.click("a.shopping_cart_link")
page.wait_for_selector(".cart_item", timeout=5000)

page.click("button#checkout")
page.fill("#first-name", "Test")
page.fill("#last-name", "User")
page.fill("#postal-code", "12345")
page.click("input#continue")
page.click("button#finish")

page.wait_for_selector("h2.complete-header:has-text('THANK YOU')", timeout=5000)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_contact_form(url: str) -> str:
    """
    Robust AutomationExercise Contact Us:
    - Close consent overlay if present
    - Navigate via Contact Us link
    - Fill form
    - Handle optional alert
    - Assert real success message
    """
    body = f"""
page.goto("{url}", wait_until="load")

# Try to close any cookie/consent overlays that might block clicks
try:
    page.wait_for_timeout(1000)
    overlay = page.locator("div.fc-dialog-overlay, div.fc-consent-root").first
    if overlay.is_visible():
        for sel in [
            "button.fc-cta-consent",
            "button.fc-cta-do-not-consent",
            "button:has-text('Accept')",
            "button:has-text('Allow')",
            "button:has-text('OK')",
            "button:has-text('Got it')",
            "div.fc-close",
        ]:
            btn = page.locator(sel).first
            if btn.is_visible():
                btn.click()
                break
        # Fallback: hard-remove overlay if still present
        if overlay.is_visible():
            page.evaluate(
                "document.querySelectorAll('div.fc-dialog-overlay,div.fc-consent-root')"
                ".forEach(e => e.remove())"
            )
except Exception:
    pass

# Navigate to Contact Us
try:
    page.click("a[href='/contact_us']")
except Exception:
    page.click("a:has-text('Contact us')")

page.wait_for_selector("h2:has-text('Get In Touch')", timeout=8000)

# Name
try:
    page.fill("input[data-qa='name']", "Test User")
except Exception:
    page.fill("input[name='name']", "Test User")

# Email
try:
    page.fill("input[data-qa='email']", "test@example.com")
except Exception:
    page.fill("input[name='email']", "test@example.com")

# Subject
try:
    page.fill("input[data-qa='subject']", "Test Subject")
except Exception:
    page.fill("input[name='subject']", "Test Subject")

# Message
try:
    page.fill("textarea[data-qa='message']", "This is a test message from the AI agent demo.")
except Exception:
    page.fill("textarea[name='message']", "This is a test message from the AI agent demo.")

# Submit
page.click("input[type='submit'][name='submit'], input[data-qa='submit-button']")

# Optional alert
try:
    dialog = page.wait_for_event("dialog", timeout=5000)
    dialog.accept()
except Exception:
    pass

# Assert success
page.wait_for_selector(
    "div:has-text('Success! Your details have been submitted successfully.')",
    timeout=8000,
)

page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_demoblaze_checkout_v1(url: str) -> str:
    """
    Intentionally BROKEN Demoblaze checkout script for the self-heal demo.

    It completes the flow but asserts on a WRONG confirmation string so it always fails.
    self_heal() will replace this with _script_demoblaze_checkout_v2.
    """
    body = f"""
page.goto("{url}", wait_until="load")

page.click("a:has-text('Laptops')")
page.click("a:has-text('Sony vaio i5')")
page.click("a:has-text('Add to cart')")

# Very naive alert handling
try:
    page.wait_for_event("dialog", timeout=3000).accept()
except Exception:
    pass

page.click("#cartur")
page.click("button:has-text('Place Order')")

page.fill("#name", "Test User")
page.fill("#country", "Testland")
page.fill("#city", "Test City")
page.fill("#card", "4111111111111111")
page.fill("#month", "12")
page.fill("#year", "2030")
page.click("button:has-text('Purchase')")

# INTENTIONALLY WRONG ASSERTION -> will timeout / fail
page.wait_for_selector("text=Thank you for your purchase!!!", timeout=5000)

page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_demoblaze_checkout_v2(url: str) -> str:
    """
    Hardened Demoblaze checkout flow (correct script).
    """
    body = f"""
page.goto("{url}", wait_until="load")

page.click("a:has-text('Laptops')")
page.wait_for_timeout(1000)

page.click("a:has-text('Sony vaio i5')")
page.wait_for_selector("h2.name", timeout=5000)

page.click("a:has-text('Add to cart')")
try:
    dialog = page.wait_for_event("dialog", timeout=8000)
    dialog.accept()
except Exception:
    pass

page.click("#cartur")
page.wait_for_selector("table tbody tr", timeout=8000)

page.click("button:has-text('Place Order')")
page.wait_for_selector("#orderModal", timeout=5000)

page.fill("#name", "Test User")
page.fill("#country", "Testland")
page.fill("#city", "Test City")
page.fill("#card", "4111111111111111")
page.fill("#month", "12")
page.fill("#year", "2030")

page.click("button:has-text('Purchase')")

page.wait_for_selector("text=Thank you for your purchase", timeout=8000)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


# ==================== Generic / LLM-assisted Script ====================


def _script_generic(url: str, goal: str) -> str:
    """
    Generic script:
      - Ask LLM for Playwright body (via llm_chat) if available.
      - Else use deterministic skeleton.
    """
    system_prompt = (
        "You are a senior QA engineer generating Playwright sync code. "
        "You ONLY write Python code that uses an existing `page` object."
    )

    user_prompt = (
        f"URL under test: {url}\n"
        f"Test goal: {goal}\n\n"
        "Write ONLY Python code using Playwright sync API on `page`.\n"
        "Rules:\n"
        "- Do NOT import anything.\n"
        "- Do NOT start sync_playwright or create browser/context.\n"
        "- Do NOT define run() or main().\n"
        f"- Start by calling page.goto(\"{url}\", wait_until=\"load\").\n"
        "- Add reasonable waits before interacting/asserting.\n"
        "- On success, call: page.screenshot(path=\"run_result.png\", full_page=True).\n"
    )

    body = ""
    raw = llm_chat(system_prompt, user_prompt, max_tokens=1200)
    if raw:
        cleaned = clean_llm_code(raw)
        if (
            "page.goto" in cleaned
            and "sync_playwright" not in cleaned
            and "def run" not in cleaned
        ):
            body = cleaned

    if not body:
        body = f"""
# TODO: Implement steps for: {goal!r}
page.goto("{url}", wait_until="load")
page.wait_for_timeout(2000)
# Add interactions & assertions here.
page.screenshot(path="run_result.png", full_page=True)
"""

    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


# ==================== Public Entry ====================


def generate_script(url: str, goal: str) -> str:
    """
    Used by main.py.
    Deterministic for known demos; generic/LLM-backed otherwise.
    """
    url = (url or "").strip()
    goal = (goal or "").strip()
    parsed = urlparse(url)
    domain = (parsed.netloc or "").lower()
    goal_l = goal.lower()

    if "the-internet.herokuapp.com" in domain:
        return _script_login_internet(url)

    if "saucedemo.com" in domain and "backpack" in goal_l:
        return _script_saucedemo_backpack(url)

    if "automationexercise.com" in domain and "contact" in goal_l:
        return _script_contact_form(url)

    if "demoblaze.com" in domain and (
        "sony vaio i5" in goal_l or "place order" in goal_l or "payment" in goal_l
    ):
        # Always start with intentionally broken version for self-heal demo
        return _script_demoblaze_checkout_v1(url)

    return _script_generic(url, goal)


__all__ = ["generate_script", "_script_demoblaze_checkout_v2"]
