import streamlit as st
from datetime import datetime

# Import "agents" (each in its own file inside agents/)
from agents.flow_discovery import discover_flow
from agents.script_generator import generate_script
from agents.execution import execute_script
from agents.error_diagnosis import diagnose
from agents.adaptive_repair import self_heal
from agents.regression_monitor import describe as regression_describe

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Browser Automation AI Agent",
    layout="wide"
)

st.title("🧠 Browser Automation AI Agent")
st.caption("From natural language → to browser flows → to runnable, self-healing automation scripts.")

# =========================
# OVERVIEW / ABOUT (EXPANDABLE)
# =========================

with st.expander("ℹ️ Overview / How this tool works", expanded=True):
    st.markdown(
        """
### What is this?

This is an **AI-powered Browser Automation Agent** that:
- Takes a **URL** and a **natural language goal** (e.g., *"Test login flow"*, *"Add item to cart"*)
- **Discovers** the expected user journey
- **Generates** an executable Playwright script
- **Runs** it automatically
- On failure, **diagnoses** the issue and attempts a **self-healing fix**

### Why is it useful?

Traditional browser tests are:
- Manual to create ✅
- Fragile when the UI changes ❌
- Expensive to maintain ❌

This agent:
- Reduces repetitive manual testing / scripting work
- Keeps tests more stable via **adaptive repairs**
- Exposes real code (no black box): teams can review, version, and trust it

### How to use this demo

1. **Enter Target URL** – the web app you want to interact with.
2. **Describe the Goal** – what flow should be run? (e.g., login, basic checkout, form submit)
3. Click **“Generate & Run”**.
4. Watch the agents:
   - 🔍 *Flow Discovery* – human-readable steps
   - 🧾 *Script Generator* – real Playwright code
   - ▶️ *Execution* – run log + screenshot
   - 🩺 *Error Diagnosis* – why it failed (if it fails)
   - 🔁 *Adaptive Repair* – proposed self-healing patch
5. (Optional) Check the **Regression Monitor** note at the bottom for future visual diff support.

This layout is intentionally transparent so you can see every step the AI takes.
        """
    )

st.markdown("---")

# =========================
# INPUTS: URL + GOAL + ENGINE
# =========================

st.subheader("🔧 Configure Your Run")

col1, col2, col3, col4 = st.columns([3, 4, 2, 2])

with col1:
    url = st.text_input(
        "Target URL",
        value="https://example-ecommerce.com",
        help="The site or app where the browser flow should run."
    )

with col2:
    goal = st.text_input(
        "Goal / Prompt",
        value="Test login flow with valid user",
        help="Describe the scenario: e.g. 'Test login', 'Search product and add to cart', 'Submit contact form'."
    )

with col3:
    engine = st.selectbox(
        "Automation Engine",
        ["Playwright (Python)"],
        index=0,
        help="For this demo we use Playwright Python. Others can be plugged in later."
    )

with col4:
    run_clicked = st.button(
        "🚀 Generate & Run",
        use_container_width=True,
        help="Run the full pipeline: discover → generate script → execute → analyze → (self-heal if needed)."
    )

st.markdown("---")

# Layout for main content
left_col, right_col = st.columns([2, 3])

# =========================
# MAIN EXECUTION LOGIC
# =========================

if run_clicked and url and goal:

    # ---------------------------------
    # 1) FLOW DISCOVERY AGENT
    # ---------------------------------
    with left_col:
        st.subheader("🔍 Flow Discovery Agent")
        st.caption(
            "Understands your goal and suggests the key user steps. "
            "In a full version, this would also inspect the live DOM."
        )

        steps = discover_flow(url, goal)

        # Display steps nicely
        for i, step in enumerate(steps, start=1):
            st.write(f"**{i}.** {step}")

        # ---------------------------------
        # 2) SCRIPT GENERATOR AGENT
        # ---------------------------------
        st.subheader("🧾 Script Generator Agent")
        st.caption(
            "Turns the discovered steps into a concrete Playwright script. "
            "This script is real automation code you can run in CI/CD."
        )

        script_code = generate_script(url, steps, engine)
        st.code(script_code, language="python")

    # ---------------------------------
    # 3) EXECUTION AGENT
    # ---------------------------------
    with right_col:
        st.subheader("▶️ Execution Agent")
        st.caption(
            "Runs the generated script, then reports pass/fail, logs, and screenshots. "
            "In a real deployment, this could run headless in your pipeline or on a grid."
        )

        status_placeholder = st.empty()

        with st.spinner("Running browser flow in Playwright..."):
            status_placeholder.info("Execution in progress...")
            success, logs, screenshot_path = execute_script(script_code)

        # Update status after run
        if success:
            status_placeholder.success("Execution completed successfully.")
        else:
            status_placeholder.error("Execution finished with errors.")


        st.text(f"Run ID: DEMO-{datetime.now().strftime('%H%M%S')}")
        st.text(f"Engine: {engine}")

        if success:
            st.success("Run successful ✅ The flow completed as expected.")
        else:
            st.error("Run failed ❌ The flow did not complete successfully.")

        st.markdown("**Run Log**")
        if logs:
            st.text("\n".join(logs))
        else:
            st.text("No logs captured.")

        if screenshot_path:
            st.markdown("**Captured Screenshot**")
            st.image(
                screenshot_path,
                caption="Final page state from this run",
                use_column_width=True
            )
        else:
            st.caption("No screenshot available for this run.")

    # =========================
    # 4) ERROR DIAGNOSIS + SELF-HEAL
    # =========================

    st.markdown("---")
    st.subheader("🩺 Error Diagnosis & 🔁 Adaptive Repair")
    st.caption(
        "If the run fails, the agents try to explain why and propose a safe, reviewable fix to the script."
    )

    if success:
        st.info(
            "The last run passed. No self-healing required. "
            "If a future UI change breaks this flow, this section will guide the fix automatically."
        )
    else:
        # Reconstruct error text from logs
        error_text = "\n".join(logs) if logs else ""

        # ---------- Error Diagnosis Agent ----------
        explanation, root_cause = diagnose(error_text)

        st.markdown("**Diagnosis**")
        st.write(explanation)
        st.write(f"**Likely Root Cause:** {root_cause}")

        # ---------- Adaptive Repair Agent ----------
        repaired_code, note = self_heal(script_code, error_text)

        st.markdown("**Proposed Self-Healing Fix**")
        st.write(note)

        col_old, col_new = st.columns(2)
        with col_old:
            st.caption("Original Script")
            st.code(script_code, language="python")
        with col_new:
            st.caption("Self-Healed Script (Proposed)")
            st.code(repaired_code, language="python")

        # Button to simulate / trigger rerun with repaired script
        if st.button("✅ Apply Fix & Rerun (Demo)"):
            success2, logs2, screenshot2 = execute_script(repaired_code)

            if success2:
                st.success("Self-healed run passed ✅ This shows how the agent adapts to UI changes.")
            else:
                st.error("Self-healed run still failing ❌ Further manual review needed.")

            st.markdown("**New Run Log**")
            st.text("\n".join(logs2))

            if screenshot2:
                st.image(
                    screenshot2,
                    caption="Page state after self-heal attempt",
                    use_column_width=True
                )

else:
    # When no run yet: guide the user softly
    with left_col:
        st.subheader("👟 Quick Start")
        st.write("1. Enter the **Target URL** of your web app.")
        st.write("2. Describe what you want, e.g.:")
        st.code('Test login with valid user', language="text")
        st.code('Search for "shoes" and add first result to cart', language="text")
        st.code('Submit contact form and verify success message', language="text")
        st.write("3. Click **“🚀 Generate & Run”** to see the agents in action.")

    with right_col:
        st.subheader("🔎 What each Agent does (Conceptually)")
        st.markdown("""
- **Flow Discovery Agent** – Reads your goal, maps it into clear user steps.
- **Script Generator Agent** – Converts those steps into Playwright code.
- **Execution Agent** – Runs the script, captures logs & screenshots.
- **Error Diagnosis Agent** – Explains failures in human terms.
- **Adaptive Repair Agent** – Suggests non-breaking fixes (e.g., better selectors).
- **Regression Monitor Agent** – (Future) Compares screenshots over time to catch UI/layout drift.
        """)

# =========================
# REGRESSION MONITOR (CONCEPT)
# =========================

st.markdown("---")
st.subheader("🖼️ Regression Monitor (Concept / Future Work)")
st.caption(
    "This would track screenshots from previous successful runs and compare them with new runs "
    "to detect unintended UI changes (disappearing buttons, layout shifts, etc.)."
)
st.write(regression_describe())
