# agents/script_generator.py

import textwrap
import os
from urllib.parse import urlparse

try:
    from agents.llm.llm_client import llm_chat
    from agents.llm.llm_utils import clean_llm_code
except ImportError:
    try:
        from llm.llm_client import llm_chat
        from llm.llm_utils import clean_llm_code
    except ImportError:
        def llm_chat(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
            return ""

        def clean_llm_code(text: str) -> str:
            return text


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


# ==================== Herokuapp Examples ====================

def _script_login_internet(url: str) -> str:
    body = f"""\
# Scenario: Herokuapp login
page.goto("{url}")
page.fill("#username", "tomsmith")
page.fill("#password", "SuperSecretPassword!")
page.click("button.radius")
page.wait_for_selector("div.flash.success", timeout=5000)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_dynamic_content(url: str) -> str:
    body = f"""\
# Scenario: Dynamic Content
page.goto("{url}")
page.wait_for_selector("div#content", timeout=5000)
page.wait_for_timeout(1000)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_dropdown(url: str) -> str:
    body = f"""\
# Scenario: Dropdown Selection
page.goto("{url}")
page.select_option("#dropdown", "1")
page.wait_for_timeout(500)
page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _script_file_upload(url: str) -> str:
    body = f"""\
# Scenario: File Upload
import tempfile
import os

page.goto("{url}")

# Create a temporary test file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
    tmp.write("Test file for upload")
    tmp_path = tmp.name

try:
    page.set_input_files("#file-upload", tmp_path)
    page.click("#file-submit")
    page.wait_for_selector("#uploaded-files", timeout=5000)
    page.screenshot(path="run_result.png", full_page=True)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


# ==================== Saucedemo Examples ====================

def _script_saucedemo_checkout_baseline(url: str) -> str:
    body = f"""\
# Scenario: Saucedemo Add to Cart
page.goto("{url}", wait_until="load")

page.fill("#user-name", "standard_user")
page.fill("#password", "secret_sauce")
page.click("#login-button")

page.wait_for_selector(".inventory_item", timeout=5000)
page.click("button#add-to-cart-sauce-labs-backpack")

page.click("a.shopping_cart_link")
page.wait_for_selector(".cart_item", timeout=5000)

page.screenshot(path="run_result.png", full_page=True)
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def _get_visual_regression_counter():
    """Track how many times Example 3 has been run using a counter file."""
    counter_file = "visual_regression_counter.txt"
    
    try:
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                count = int(f.read().strip())
        else:
            count = 0
    except Exception:
        count = 0
    
    try:
        with open(counter_file, 'w') as f:
            f.write(str(count + 1))
    except Exception:
        pass
    
    return count


def _script_saucedemo_visual_regression_demo(url: str) -> str:
    run_count = _get_visual_regression_counter()
    is_cart_view = (run_count % 2 == 0)
    
    print(f"\n{'='*60}")
    print(f"[Script Generator] Visual Regression Demo")
    print(f"  Run count: {run_count}")
    print(f"  View: {'CART' if is_cart_view else 'INVENTORY'}")
    print(f"{'='*60}\n")
    
    if is_cart_view:
        body = f"""\
# Scenario: Saucedemo Visual Regression Demo (CART VIEW - Run {run_count})
print("\\n=== VISUAL REGRESSION: Generating CART view ===\\n")

page.goto("{url}", wait_until="load")
page.fill("#user-name", "standard_user")
page.fill("#password", "secret_sauce")
page.click("#login-button")

page.wait_for_selector(".inventory_item", timeout=5000)
page.click("button#add-to-cart-sauce-labs-backpack")

page.click("a.shopping_cart_link")
page.wait_for_selector(".cart_item", timeout=5000)

print("\\n=== Screenshot: CART page with items ===\\n")
page.screenshot(path="run_result.png", full_page=True)
"""
    else:
        body = f"""\
# Scenario: Saucedemo Visual Regression Demo (INVENTORY VIEW - Run {run_count})
print("\\n=== VISUAL REGRESSION: Generating INVENTORY view ===\\n")

page.goto("{url}", wait_until="load")
page.fill("#user-name", "standard_user")
page.fill("#password", "secret_sauce")
page.click("#login-button")

page.wait_for_selector(".inventory_item", timeout=5000)
page.click("button#add-to-cart-sauce-labs-backpack")

page.wait_for_timeout(500)

print("\\n=== Screenshot: INVENTORY page ===\\n")
page.screenshot(path="run_result.png", full_page=True)
"""
    
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


# ==================== Demoblaze Examples ====================

def _script_demoblaze_checkout_v1(url: str) -> str:
    body = f"""\
# Scenario: Demoblaze Checkout (Intentionally Broken)
page.goto("{url}", wait_until="load")

page.click("a:has-text('Laptops')")
page.wait_for_timeout(1000)

page.click("a:has-text('Sony vaio i5')")
page.wait_for_selector("h2.name", timeout=5000)

# Wrong selector to trigger failure & self-heal
page.click("a:has-text('Add cart')")
"""
    return HARNESS_HEADER + _indent(body) + "\n" + HARNESS_FOOTER


def script_demoblaze_checkout_fixed(url: str) -> str:
    body = f"""\
# Scenario: Demoblaze Checkout (Self-Heal Fixed)
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


def _script_demoblaze_checkout_v2(url: str) -> str:
    return script_demoblaze_checkout_fixed(url)


# ==================== Generic LLM ====================

def _script_generic(url: str, goal: str) -> str:
    system_prompt = "You are a senior QA engineer generating Playwright sync code. You ONLY write Python code that uses an existing `page` object."
    user_prompt = f"URL under test: {url}\nTest goal: {goal}\n\nWrite ONLY Python code using Playwright sync API on `page`.\nRules:\n- Do NOT import anything or start Playwright.\n- Do NOT define run() or main().\n- Start with page.goto(\"{url}\", wait_until=\"load\").\n- Add waits where appropriate.\n- On success, call page.screenshot(path=\"run_result.png\", full_page=True).\n"

    code = ""
    raw = llm_chat(system_prompt, user_prompt, max_tokens=1200)
    if raw:
        cleaned = clean_llm_code(raw)
        if "page.goto" in cleaned and "sync_playwright" not in cleaned and "def run" not in cleaned:
            code = cleaned

    if not code:
        code = f"""\
# Scenario: Generic fallback
page.goto("{url}", wait_until="load")
page.wait_for_timeout(2000)
page.screenshot(path="run_result.png", full_page=True)
"""

    return HARNESS_HEADER + _indent(code) + "\n" + HARNESS_FOOTER


# ==================== Router ====================

def generate_script(url: str, goal: str) -> str:
    url = (url or "").strip()
    goal = (goal or "").strip()
    parsed = urlparse(url)
    domain = (parsed.netloc or "").lower()
    goal_l = goal.lower()

    # Herokuapp examples
    if "the-internet.herokuapp.com" in domain:
        if "login" in goal_l:
            return _script_login_internet(url)
        elif "dynamic" in goal_l:
            return _script_dynamic_content(url)
        elif "dropdown" in goal_l:
            return _script_dropdown(url)
        elif "upload" in goal_l:
            return _script_file_upload(url)

    # Saucedemo examples
    if "saucedemo.com" in domain:
        if "intentionally" in goal_l or "demonstrate visual regression" in goal_l:
            return _script_saucedemo_visual_regression_demo(url)
        return _script_saucedemo_checkout_baseline(url)

    # Demoblaze self-heal
    if "demoblaze.com" in domain and "sony vaio i5" in goal_l:
        return _script_demoblaze_checkout_v1(url)

    return _script_generic(url, goal)


__all__ = ["generate_script", "script_demoblaze_checkout_fixed", "_script_demoblaze_checkout_v2"]