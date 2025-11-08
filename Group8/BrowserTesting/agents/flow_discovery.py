# agents/flow_discovery.py

from urllib.parse import urlparse


def discover_flow(target_url: str, goal: str):
    """
    Very small, deterministic "Flow Discovery" that turns the selected example
    (URL + goal) into a list of high-level steps. This is intentionally
    template-based so the hackathon demo is stable.
    """
    url = (target_url or "").strip().lower()
    goal_l = (goal or "").strip().lower()
    domain = urlparse(url).netloc

    steps = []

    # 1) Login & check homepage  (the-internet.herokuapp.com)
    if "the-internet.herokuapp.com" in domain and "login" in goal_l:
        steps = [
            "Open the login page",
            "Enter valid username",
            "Enter valid password",
            "Click the Login button",
            "Verify the secure area page is displayed",
        ]

    # 2) Add to cart  (saucedemo.com)
    elif "saucedemo.com" in domain and "backpack" in goal_l:
        steps = [
            "Open SauceDemo login page",
            "Enter standard_user credentials",
            "Click Login",
            "Add 'Sauce Labs Backpack' to cart",
            "Open cart page",
            "Verify 'Sauce Labs Backpack' is listed",
        ]

    # 3) Contact us form (automationexercise.com)
    elif "automationexercise.com" in domain and "contact" in goal_l:
        steps = [
            "Open Contact Us page",
            "Fill name, email, subject, and message",
            "Submit the form",
            "Verify success message is displayed",
        ]

    # 4) Checkout until payment (demoblaze.com)
    elif "demoblaze.com" in domain and ("place order" in goal_l or "payment" in goal_l):
        steps = [
            "Open Demoblaze home page",
            "Select 'Laptops' category",
            "Open 'Sony vaio i5' product details",
            "Add product to cart and accept alert",
            "Open cart page",
            "Click 'Place Order'",
            "Fill order form",
            "Submit and verify confirmation/purchase dialog",
        ]

    # Fallback: minimal generic flow
    if not steps and url:
        steps = [
            f"Open {target_url}",
            "Attempt to follow the goal described by the user",
        ]

    return steps
