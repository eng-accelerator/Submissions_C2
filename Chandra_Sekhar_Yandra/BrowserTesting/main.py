# main.py

import os
import streamlit as st

from agents.flow_discovery import discover_flow
from agents.script_generator import generate_script
from agents.execution import execute_script
from agents.error_diagnosis import diagnose
from agents.adaptive_repair import self_heal
from agents.regression_monitor import describe as regression_describe  # optional

# Import new features
from chatbot import chat_with_llm, get_available_models, format_search_results_html
from price_comparison import compare_prices


# ------------------ Session defaults ------------------

if "target_url_input" not in st.session_state:
    st.session_state["target_url_input"] = ""
if "goal_prompt_input" not in st.session_state:
    st.session_state["goal_prompt_input"] = ""
if "last_script" not in st.session_state:
    st.session_state["last_script"] = ""
# Chatbot session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


# ------------------ Helpers ------------------

def use_example(url: str, goal: str):
    """Set the Target URL and Goal/Prompt from an example scenario."""
    st.session_state["target_url_input"] = url
    st.session_state["goal_prompt_input"] = goal


def _normalize_execution_result(result):
    """
    Normalize execute_script(...) return into (success: bool, log: str, screenshot_path: str|None).

    Supports:
      - dict: {'success': bool, 'log': str|list, 'screenshot_path': str}
      - tuple/list: (success, log), (success, log, screenshot_path), or similar.
      - log may be a string, list of lines, or anything str()-able.
    """
    success = False
    log = ""
    screenshot_path = None

    # Dict shape
    if isinstance(result, dict):
        success = bool(result.get("success"))
        raw_log = result.get("log", "")
        if isinstance(raw_log, (list, tuple)):
            log = "\n".join(str(x) for x in raw_log)
        else:
            log = str(raw_log or "")
        screenshot_path = result.get("screenshot_path")

    # Tuple or list shape
    elif isinstance(result, (tuple, list)):
        if len(result) >= 1:
            success = bool(result[0])

        if len(result) >= 2:
            raw_log = result[1]
            if isinstance(raw_log, (list, tuple)):
                log = "\n".join(str(x) for x in raw_log)
            else:
                log = str(raw_log or "")

        if len(result) >= 3:
            screenshot_path = result[2]

    # Fallback: anything else
    else:
        log = str(result or "")

    return success, log, screenshot_path


# ------------------ Page layout ------------------

st.set_page_config(
    page_title="Browser Automation AI Agent",
    layout="wide",
)

st.title("🧠 Browser Automation AI Agent")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["🤖 Browser Testing", "💬 AI Chatbot", "💰 Price Comparison"])

# Tab 1: Original Browser Testing Feature
with tab1:

    with st.expander("Overview / About", expanded=False):
        st.markdown(
            """
    This app showcases an **AI-native browser automation agent** that turns a natural
    language goal into an executable, self-healing browser test.

    **Agents in the loop:**

    1. **Flow Discovery** – understands your goal and proposes key user steps.
    2. **Script Generator** – uses an LLM to generate only the test steps while a fixed
       Playwright harness (imports, `run()`, browser lifecycle) is controlled by us.
    3. **Execution** – runs the script, captures logs and screenshots.
    4. **Error Diagnosis** – explains why a run failed.
    5. **Adaptive Repair** – proposes fixes (selectors, waits) by editing only the test body.
    6. **Regression Monitor (optional)** – compares screenshots across runs.

    Describe **what** you want; the agents figure out **how** to do it in the browser.
    """
        )


# ------------------ Example scenarios (scrollable) ------------------

    with st.expander("Example scenarios"):
        st.markdown(
            """
            <style>
            .examples-scroll {
                max-height: 420px;      /* fixed height -> vertical scroll kicks in */
                overflow-y: auto;       /* enable vertical scrolling */
                overflow-x: hidden;     /* hide horizontal scroll */
                padding-right: 8px;
                width: 100%;
                box-sizing: border-box;
            }
            .examples-scroll code {
                font-size: 0.8rem;
            }
            </style>
            <div class="examples-scroll">
            """,
            unsafe_allow_html=True,
        )

        # ---- Row 1 ----
        c1, c2 = st.columns(2)

        with c1:
            ex_url = "https://www.saucedemo.com/"
            ex_goal = "Login with standard_user and verify the products page is visible"
            st.markdown("**SauceDemo – Verify Products Page**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_sauce_products",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        with c2:
            ex_url = "https://www.saucedemo.com/"
            ex_goal = (
                "Login with standard_user, add the Sauce Labs Bike Light to the cart, "
                "then open the cart page and verify it is listed"
            )
            st.markdown("**SauceDemo – Add Bike Light to Cart**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_sauce_bikelight",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        st.markdown("---")

        # ---- Row 2 ----
        c3, c4 = st.columns(2)

        with c3:
            ex_url = "https://www.saucedemo.com/"
            ex_goal = (
                "Login with standard_user, sort products by Price (low to high), "
                "add the cheapest item to the cart, then verify that item is present in the cart"
            )
            st.markdown("**SauceDemo – Cheapest Item via Sorting**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_sauce_cheapest",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        with c4:
            ex_url = "https://www.saucedemo.com/"
            ex_goal = (
                "Login with standard_user, add Sauce Labs Backpack to the cart, "
                "complete checkout with test user details, and verify the order "
                "confirmation page is shown"
            )
            st.markdown("**SauceDemo – Backpack Checkout Flow**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_sauce_checkout",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        st.markdown("---")

        # ---- Row 3 ----
        c5, c6 = st.columns(2)

        with c5:
            ex_url = "https://the-internet.herokuapp.com/login"
            ex_goal = (
                "Open the login page, log in with username 'tomsmith' and "
                "password 'SuperSecretPassword!', and verify the success message is displayed"
            )
            st.markdown("**The Internet – Valid Login**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_ti_login_success",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        with c6:
            ex_url = "https://www.demoblaze.com/"
            ex_goal = (
                "Open the home page, navigate to 'Samsung galaxy s6' product details, "
                "add it to the cart, then open the cart page and verify "
                "'Samsung galaxy s6' is listed"
            )
            st.markdown("**Demoblaze – Add Samsung Galaxy S6 to Cart**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_demoblaze_s6",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        st.markdown("---")

        # ---- Row 4 ----
        c7, c8 = st.columns(2)

        with c7:
            ex_url = "https://www.saucedemo.com/"
            ex_goal = (
                "Login with standard_user, add Sauce Labs Backpack and "
                "Sauce Labs Bolt T-Shirt to the cart, then open the cart page and "
                "verify both items and their prices are visible"
            )
            st.markdown("**SauceDemo – Multi-item Cart Verification**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_sauce_multi_cart",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        with c8:
            ex_url = (
                "https://opensource-demo.orangehrmlive.com/"
                "web/index.php/auth/login"
            )
            ex_goal = (
                "Open the OrangeHRM demo login page, log in with username 'Admin' "
                "and password 'admin123', and verify that the dashboard page is displayed"
            )
            st.markdown("**OrangeHRM Demo – Admin Login**")
            st.code(f"URL:  {ex_url}", language="text")
            st.code(f"Goal: {ex_goal}", language="text")
            st.button(
                "Use this example",
                key="ex_orangehrm_login",
                on_click=use_example,
                args=(ex_url, ex_goal),
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------ Configure run ------------------

    st.subheader("Configure Your Run")

    cols = st.columns([3, 4, 2])

    with cols[0]:
        target_url = st.text_input(
            "Target URL",
            key="target_url_input",
        )

    with cols[1]:
        goal_prompt = st.text_input(
            "Goal / Prompt",
            key="goal_prompt_input",
        )

    with cols[2]:
        engine = st.selectbox(
            "Automation Engine",
            ["Playwright (Python)"],
            index=0,
        )

    run_button = st.button("🚀 Generate & Run", use_container_width=True)
# Clear inputs button (outside expander so it's always available)
    st.button(
        "🧹 Clear inputs",
        key="ex_clear",
        on_click=use_example,
        args=("", ""),
        use_container_width=True,
    )

# ------------------ Agent orchestration UI ------------------

    st.markdown("---")
    st.markdown("## 🔄 Agent Orchestration & Results")

# Progress / status rows
    step_flow = st.empty()
    step_script = st.empty()
    step_exec = st.empty()
    step_diag = st.empty()

    st.markdown("---")

# Detailed panels
    flow_col, exec_col = st.columns([1.2, 2.0])

    with flow_col:
        st.markdown("### 🔍 Flow Discovery Agent")
        flow_steps_box = st.empty()

    with exec_col:
        st.markdown("### ▶️ Execution Agent")
        exec_status = st.empty()
        exec_log_box = st.empty()
        exec_screenshot_box = st.empty()

    st.markdown("---")
    st.markdown("### 🧾 Script Generator Agent")
    script_box = st.empty()

    st.markdown("---")
    st.markdown("### 🩻 Error Diagnosis & Adaptive Repair")
    diag_box = st.empty()
    repair_box = st.empty()


# ------------------ Generate & Run pipeline ------------------

    if run_button:
        if not target_url.strip() or not goal_prompt.strip():
            st.error("Please provide both Target URL and Goal / Prompt.")
        else:
            clean_url = target_url.strip()
            clean_goal = goal_prompt.strip()

            # 1) Flow Discovery
            step_flow.markdown("**Step 1/4 – Flow Discovery:** ⏳ running...")
            with st.spinner("Flow Discovery Agent is analyzing your goal..."):
                steps = discover_flow(clean_url, clean_goal)

            if not steps:
                step_flow.markdown("**Step 1/4 – Flow Discovery:** ⚠️ no steps discovered")
                flow_steps_box.warning(
                    "No steps discovered. Try making the goal more explicit "
                    "(e.g. 'Login with X, navigate to Y, verify Z')."
                )
                # Skip rest of pipeline cleanly
                step_script.markdown("**Step 2/4 – Script Generation:** ⏹ skipped")
                step_exec.markdown("**Step 3/4 – Execution:** ⏹ skipped")
                step_diag.markdown("**Step 4/4 – Diagnosis & Self-Heal:** ⏹ skipped")
                st.stop()
            else:
                step_flow.markdown("**Step 1/4 – Flow Discovery:** ✅ completed")
                flow_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
                flow_steps_box.markdown(flow_md)

            # 2) Script Generation
            step_script.markdown("**Step 2/4 – Script Generation:** ⏳ running...")
            with st.spinner("Script Generator Agent is creating a Playwright script..."):
                script_code = generate_script(clean_url, steps, engine, clean_goal)
                st.session_state["last_script"] = script_code
            step_script.markdown("**Step 2/4 – Script Generation:** ✅ completed")
            script_box.code(script_code, language="python")

            # Optionally persist to disk
            try:
                with open("generated_test.py", "w", encoding="utf-8") as f:
                    f.write(script_code)
            except Exception:
                pass

            # 3) Execution Agent
            step_exec.markdown("**Step 3/4 – Execution:** ⏳ running...")
            with st.spinner("Execution Agent is running the script..."):
                raw_result = execute_script(script_code)

            success, log, screenshot_path = _normalize_execution_result(raw_result)

            if success:
                step_exec.markdown("**Step 3/4 – Execution:** ✅ passed")
                exec_status.success("Run successful ✅ The flow completed as expected.")
            else:
                step_exec.markdown("**Step 3/4 – Execution:** ❌ failed")
                exec_status.error("Run failed ❌ The flow did not complete successfully.")

            if log:
                exec_log_box.code(log, language="text")

            if screenshot_path and isinstance(screenshot_path, str) and os.path.exists(screenshot_path):
                exec_screenshot_box.image(
                    screenshot_path,
                    caption="Captured Screenshot",
                    use_column_width=True,
                )

            # 4) Diagnosis & Adaptive Repair (only on failure)
            if not success:
                step_diag.markdown("**Step 4/4 – Diagnosis & Self-Heal:** ⏳ running...")
                with st.spinner("Error Diagnosis Agent is analyzing the failure..."):
                    diagnosis = diagnose(log)
                diag_box.markdown(f"**Diagnosis:** {diagnosis}")

                with st.spinner("Adaptive Repair Agent is proposing a fix..."):
                    repaired_script, note = self_heal(script_code, log)

                if repaired_script and repaired_script != script_code:
                    step_diag.markdown("**Step 4/4 – Diagnosis & Self-Heal:** ✅ fix proposed")
                    repair_box.markdown(f"**Adaptive Repair Note:** {note}")
                    repair_box.code(repaired_script, language="python")
                else:
                    step_diag.markdown(
                        "**Step 4/4 – Diagnosis & Self-Heal:** ⚠️ no safe automatic fix"
                    )
                    repair_box.info(
                        note
                        or "No safe automatic fix was found. Please adjust the script manually."
                    )
            else:
                step_diag.markdown(
                    "**Step 4/4 – Diagnosis & Self-Heal:** ✅ skipped (execution passed)"
                )

# ------------------ New Feature: AI Chatbot ------------------

with tab2:
    from feature_chatbot_ui import render_chatbot_tab
    render_chatbot_tab()

# ------------------ New Feature: Price Comparison ------------------

with tab3:
    from feature_price_comparison_ui import render_price_comparison_tab
    render_price_comparison_tab()
