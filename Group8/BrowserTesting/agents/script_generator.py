# agents/script_generator.py

def generate_script(url: str, steps, engine: str = "Playwright (Python)"):
    """
    Script Generator Agent:
    Turn discovered steps into executable automation code.
    For now: generate Playwright Python script.
    """
    if "Python" in engine:
        return f'''\
from playwright.sync_api import sync_playwright
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Auto-generated steps
            page.goto("{url}")
            # TODO: refine selectors based on real DOM/LLM
            # Example for login flow:
            page.get_by_role("button", name="Login").click()
            page.get_by_placeholder("Email").fill("test@example.com")
            page.get_by_placeholder("Password").fill("Password123!")
            page.get_by_role("button", name="Sign in").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="run_result.png")
        except Exception as e:
            page.screenshot(path="run_error.png")
            print(f"ERROR: {{e}}")
            browser.close()
            sys.exit(1)

        browser.close()
        sys.exit(0)

if __name__ == "__main__":
    run()
'''
    else:
        # You can add TS/JS engines here if needed
        return "// TODO: implement other engines"
