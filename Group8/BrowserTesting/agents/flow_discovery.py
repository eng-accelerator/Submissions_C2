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

    # 1) Login & check homepage (the-internet.herokuapp.com)
    if "the-internet.herokuapp.com" in domain and "login" in goal_l:
        steps = [
            "Open the login page",
            "Enter valid username",
            "Enter valid password",
            "Click the Login button",
            "Verify the secure area page is displayed",
        ]

    # 2) Add to cart (saucedemo.com)
    elif "saucedemo.com" in domain and "backpack" in goal_l:
        steps = [
            "Open SauceDemo login page",
            "Enter standard_user credentials",
            "Click Login",
            "Add 'Sauce Labs Backpack' to cart",
            "Open cart page",
            "Verify 'Sauce Labs Backpack' is listed",
        ]

    # 3) Visual regression (saucedemo.com)
    elif "saucedemo.com" in domain and ("intentionally" in goal_l or "visual regression" in goal_l):
        steps = [
            "Login to SauceDemo",
            "Add item to cart",
            "Alternate between cart and inventory views",
            "Capture screenshot for comparison",
            "Detect visual differences on subsequent runs",
        ]

    # 4) Contact us form (automationexercise.com)
    elif "automationexercise.com" in domain and "contact" in goal_l:
        steps = [
            "Open Contact Us page",
            "Fill name, email, subject, and message",
            "Submit the form",
            "Verify success message is displayed",
        ]

    # 5) Checkout until payment (demoblaze.com)
    elif "demoblaze.com" in domain and ("place order" in goal_l or "payment" in goal_l or "sony vaio" in goal_l):
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

    # 6) Dynamic content (the-internet.herokuapp.com)
    elif "the-internet.herokuapp.com" in domain and "dynamic" in goal_l:
        steps = [
            "Navigate to dynamic content page",
            "Wait for content to load",
            "Verify dynamic elements are present",
            "Capture screenshot",
        ]

    # 7) Drag and drop (the-internet.herokuapp.com)
    elif "the-internet.herokuapp.com" in domain and "drag" in goal_l:
        steps = [
            "Navigate to drag and drop page",
            "Locate source and target elements",
            "Perform drag and drop action",
            "Verify elements have swapped positions",
        ]

    # 8) File upload (the-internet.herokuapp.com)
    elif "the-internet.herokuapp.com" in domain and "upload" in goal_l:
        steps = [
            "Navigate to file upload page",
            "Create a temporary test file",
            "Select file for upload",
            "Click upload button",
            "Verify file was uploaded successfully",
        ]

    # 9) Dropdown selection (the-internet.herokuapp.com)
    elif "the-internet.herokuapp.com" in domain and "dropdown" in goal_l:
        steps = [
            "Navigate to dropdown page",
            "Locate dropdown element",
            "Select an option from dropdown",
            "Verify selected value",
        ]

    # 10) Multiple windows (the-internet.herokuapp.com)
    elif "the-internet.herokuapp.com" in domain and "window" in goal_l:
        steps = [
            "Navigate to multiple windows page",
            "Click to open new window",
            "Switch to new window context",
            "Verify new window content",
            "Return to original window",
        ]

    # Fallback: minimal generic flow
    if not steps and url:
        steps = [
            f"Open {target_url}",
            "Attempt to follow the goal described by the user",
        ]

    return steps