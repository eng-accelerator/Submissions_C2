import os
import streamlit as st

from agents.flow_discovery import discover_flow
from agents.script_generator import generate_script
from agents.execution import execute_script
from agents.error_diagnosis import diagnose
from agents.adaptive_repair import self_heal


# ===================== Session State =====================


def _init_state():
    st.session_state.setdefault("target_url_input", "")
    st.session_state.setdefault("goal_prompt_input", "")
    st.session_state.setdefault("last_script", "")
    st.session_state.setdefault("repaired_script", None)
    st.session_state.setdefault("last_run_label", "")


_init_state()


# ===================== Page Config =====================


st.set_page_config(
    page_title="AI Browser Automation Lab",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Browser Automation Lab")
st.caption(
    "Playwright + Agents. All LLM/OpenRouter logic is centralized in the llm/ package."
)

st.markdown(
    """
Pipeline:
1. **Flow Discovery** – understand your goal & app.
2. **Script Generation** – create a runnable Playwright script.
3. **Execution** – run in an isolated subprocess with screenshot capture.
4. **Diagnosis & Self-Heal** – explain failures & propose fixes (Demoblaze demo).
"""
)


# ===================== Helpers =====================


def _use_example(url: str, goal: str):
    st.session_state["target_url_input"] = url
    st.session_state["goal_prompt_input"] = goal


def _cleanup_screenshots():
    """Remove old screenshots so we never reuse stale images across runs."""
    for name in ("run_result.png", "run_error.png"):
        try:
            if os.path.exists(name):
                os.remove(name)
        except Exception:
            pass


def _normalize_execution_result(result):
    """
    Normalize execute_script(...) into:
        (success: bool, log: str, screenshot_path: str | None)
    """
    success = False
    log = ""
    screenshot_path = None

    if isinstance(result, dict):
        success = bool(result.get("success"))
        raw_log = result.get("log", "")
        if isinstance(raw_log, (list, tuple)):
            log = "\n".join(str(x) for x in raw_log)
        else:
            log = str(raw_log or "")
        screenshot_path = result.get("screenshot_path")

    elif isinstance(result, (tuple, list)):
        if len(result) > 0:
            success = bool(result[0])
        if len(result) > 1:
            raw_log = result[1]
            if isinstance(raw_log, (list, tuple)):
                log = "\n".join(str(x) for x in raw_log)
            else:
                log = str(raw_log or "")
        if len(result) > 2:
            screenshot_path = result[2]

    else:
        log = str(result)

    return success, log, screenshot_path


def _is_valid_playwright_script(script_code: str) -> bool:
    """
    Only execute real harness-based scripts, not error messages.
    """
    if not script_code:
        return False

    s = script_code.strip()

    if s.startswith("# Script generation failed"):
        return False

    if "from playwright.sync_api import sync_playwright" not in s:
        return False

    if "def run():" not in s:
        return False

    return True


def _run_execution(script_code: str, step_exec, log_box, label: str):
    """
    Execute script, render results, and return (success, log, screenshot_path).
    """
    _cleanup_screenshots()

    st.session_state["last_run_label"] = label
    step_exec.markdown(f"**Step 3/4 – {label}:** ⏳ running...")

    with st.spinner(f"{label} Agent is running the script..."):
        try:
            raw = execute_script(script_code)
        except Exception as e:
            success = False
            log = f"Exception while executing script:\n{e}"
            screenshot_path = None
        else:
            success, log, screenshot_path = _normalize_execution_result(raw)

    if success:
        step_exec.markdown(f"**Step 3/4 – {label}:** ✅ passed")
    else:
        step_exec.markdown(f"**Step 3/4 – {label}:** ❌ failed")

    log_box.markdown("**Execution Log:**")
    log_box.code(log or "(no log output)", language="bash")

    if screenshot_path and os.path.exists(screenshot_path):
        st.image(
            screenshot_path,
            caption=f"{label} screenshot",
            use_container_width=True,
        )

    return success, log, screenshot_path


def _run_diagnosis_and_repair(
    script_code: str,
    log: str,
    step_diag,
    diag_box,
    repair_box,
):
    """
    Run diagnosis + adaptive repair.
    If a valid repaired script is produced, store it in session and show it.
    """
    step_diag.markdown("**Step 4/4 – Diagnosis & Self-Heal:** ⏳ running...")

    # Diagnosis
    with st.spinner("Error Diagnosis Agent is analyzing the failure..."):
        try:
            diagnosis = diagnose(log)
        except Exception as e:
            diagnosis = f"Diagnosis error: {e}"

    diag_box.markdown(f"**Diagnosis:** {diagnosis}")

    # Self-heal
    with st.spinner("Adaptive Repair Agent is proposing a fix..."):
        try:
            repaired_script, note = self_heal(script_code, log)
        except Exception as e:
            repaired_script, note = None, f"Self-heal error: {e}"

    if (
        repaired_script
        and repaired_script.strip()
        and repaired_script.strip() != script_code.strip()
        and _is_valid_playwright_script(repaired_script)
    ):
        st.session_state["repaired_script"] = repaired_script
        step_diag.markdown(
            "**Step 4/4 – Diagnosis & Self-Heal:** ✅ fix proposed"
        )
        repair_box.markdown(f"**Adaptive Repair Note:** {note}")
        repair_box.code(repaired_script, language="python")
    else:
        st.session_state["repaired_script"] = None
        step_diag.markdown(
            "**Step 4/4 – Diagnosis & Self-Heal:** ⚠️ no automatic fix applied"
        )
        repair_box.info(
            note
            or "No automatic self-heal applied. The failure likely requires manual adjustment."
        )


# ===================== Example Scenarios =====================


with st.expander("Example scenarios"):
    st.markdown(
        """
        <style>
        .examples-scroll {
            max-height: 420px;
            overflow-y: auto;
            overflow-x: hidden;
            padding-right: 8px;
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

    # 1) Login
    st.markdown("#### 1️⃣ Login – the-internet.herokuapp.com")
    u = "https://the-internet.herokuapp.com/login"
    g = (
        "Open the login page, log in with username 'tomsmith' and "
        "password 'SuperSecretPassword!', then verify the secure area."
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2:
        st.button("Use this", key="ex_login", on_click=_use_example, args=(u, g))

    st.markdown("---")

    # 2) Demoblaze checkout – self-heal demo
    st.markdown("#### 2️⃣ Demoblaze checkout – Self-heal demo")
    u = "https://www.demoblaze.com"
    g = (
        "Go to Laptops, add 'Sony vaio i5' to cart, open cart, place order, fill details, "
        "complete purchase, and verify purchase confirmation."
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2:
        st.button("Use this", key="ex_demoblaze", on_click=_use_example, args=(u, g))

    st.markdown("---")

    # 3) AutomationExercise – Signup
    st.markdown("#### 3️⃣ AutomationExercise – Signup")
    u = "https://automationexercise.com"
    g = (
        "Open the homepage, click 'Signup / Login', register a new user with a random email, "
        "and verify account creation."
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2:
        st.button("Use this", key="ex_signup", on_click=_use_example, args=(u, g))

    st.markdown("---")

    # 4) AutomationExercise – Contact Us
    st.markdown("#### 4️⃣ AutomationExercise – Contact Us")
    u = "https://automationexercise.com"
    g = (
        "Open the homepage, navigate to 'Contact us', fill the contact form with a sample "
        "message, submit it, and verify the success confirmation."
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2:
        st.button("Use this", key="ex_contact", on_click=_use_example, args=(u, g))

    st.markdown("</div>", unsafe_allow_html=True)


# ===================== Inputs =====================


st.markdown("---")
cols = st.columns([3, 5, 2])

with cols[0]:
    target_url = st.text_input("Target URL", key="target_url_input")

with cols[1]:
    goal_prompt = st.text_input("Goal / Prompt", key="goal_prompt_input")

with cols[2]:
    engine = st.selectbox(
        "Automation Engine",
        ["Playwright (Python)"],
        index=0,
        help="Currently using Playwright Python harness.",
    )

run_button = st.button("🚀 Generate & Run", use_container_width=True)


# ===================== Layout Placeholders =====================


st.markdown("---")
step_cols = st.columns(4)
step_flow = step_cols[0].empty()
step_script = step_cols[1].empty()
step_exec = step_cols[2].empty()
step_diag = step_cols[3].empty()

st.markdown("### 🧭 Discovered Flow")
flow_box = st.empty()

st.markdown("### 🧪 Generated Script")
script_box = st.empty()

st.markdown("### 📜 Execution Log")
log_box = st.empty()

st.markdown("### 🩻 Diagnosis & Self-Heal")
diag_box = st.empty()
repair_box = st.empty()


# ===================== Main Pipeline =====================


if run_button:
    # New run: clear any previous repair script
    st.session_state["repaired_script"] = None

    if not target_url.strip() or not goal_prompt.strip():
        st.warning("Please provide both a **Target URL** and a **Goal / Prompt**.")
    else:
        url = target_url.strip()
        goal = goal_prompt.strip()

        # ---- Step 1: Flow Discovery ----
        step_flow.markdown("**Step 1/4 – Flow Discovery:** ⏳ running...")
        with st.spinner("Flow Discovery Agent is analyzing your goal & app..."):
            try:
                flow = discover_flow(url, goal)
            except Exception as e:
                flow = [f"Flow discovery failed: {e}"]

        step_flow.markdown("**Step 1/4 – Flow Discovery:** ✅ completed")

        if isinstance(flow, (list, tuple)):
            flow_str = "\n".join(f"- {s}" for s in flow)
        else:
            flow_str = str(flow)

        flow_box.markdown("**Discovered Flow:**")
        flow_box.code(flow_str, language="markdown")

        # ---- Step 2: Script Generation ----
        step_script.markdown("**Step 2/4 – Script Generation:** ⏳ running...")
        with st.spinner("Script Generation Agent is producing a Playwright script..."):
            try:
                script_code = generate_script(url, goal)
            except Exception as e:
                script_code = f"# Script generation failed: {e}"

        if not isinstance(script_code, str):
            script_code = str(script_code)

        st.session_state["last_script"] = script_code

        if _is_valid_playwright_script(script_code):
            step_script.markdown("**Step 2/4 – Script Generation:** ✅ completed")
        else:
            step_script.markdown("**Step 2/4 – Script Generation:** ❌ failed")

        script_box.markdown("**Generated Script:**")
        script_box.code(script_code, language="python")

        # ---- Step 3 & 4: Execution + Self-Heal ----
        if not _is_valid_playwright_script(script_code):
            step_exec.markdown(
                "**Step 3/4 – Execution:** ⏭️ skipped (no runnable script)"
            )
            step_diag.markdown(
                "**Step 4/4 – Diagnosis & Self-Heal:** ⏭️ skipped"
            )
        else:
            success, log, _ = _run_execution(
                script_code,
                step_exec=step_exec,
                log_box=log_box,
                label="Execution",
            )

            if not success:
                _run_diagnosis_and_repair(
                    script_code, log, step_diag, diag_box, repair_box
                )
            else:
                step_diag.markdown(
                    "**Step 4/4 – Diagnosis & Self-Heal:** ✅ skipped (execution passed)"
                )


# ===================== Apply Repaired Script =====================


if st.session_state.get("repaired_script"):
    st.markdown("---")
    st.markdown("### 🔁 Apply Adaptive Repair")

    if st.button("✅ Apply Fix & Re-Run", use_container_width=True, key="apply_fix"):
        repaired_script = st.session_state.get("repaired_script")

        if repaired_script and _is_valid_playwright_script(repaired_script):
            # Reuse flow; show that we’re using the repaired script
            step_flow.markdown(
                "**Step 1/4 – Flow Discovery:** ♻️ reused from previous run"
            )
            step_script.markdown(
                "**Step 2/4 – Script Generation:** ♻️ using repaired script from Adaptive Repair"
            )

            success, log, _ = _run_execution(
                repaired_script,
                step_exec=step_exec,
                log_box=log_box,
                label="Re-run (Repaired Script)",
            )

            if success:
                step_diag.markdown(
                    "**Step 4/4 – Diagnosis & Self-Heal:** ✅ repaired script passed"
                )
                st.session_state["repaired_script"] = None
            else:
                _run_diagnosis_and_repair(
                    repaired_script, log, step_diag, diag_box, repair_box
                )
        else:
            st.warning("Repaired script is not runnable; please review it manually.")
