import os
import re
import streamlit as st

from agents.flow_discovery import discover_flow
from agents.script_generator import generate_script
from agents.execution import execute_script
from agents.error_diagnosis import diagnose
from agents.adaptive_repair import self_heal
from agents.regression_monitor import run_visual_check

# Import chatbot UI
try:
    from chatbot_ui import render_chatbot_ui, initialize_chatbot_state
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("Warning: Chatbot not available. Install langgraph and langchain to enable.")


def _init_state():
    st.session_state.setdefault("target_url_input", "")
    st.session_state.setdefault("goal_prompt_input", "")
    st.session_state.setdefault("last_script", "")
    st.session_state.setdefault("repaired_script", None)
    st.session_state.setdefault("last_run_label", "")
    st.session_state.setdefault("show_chatbot", False)

    # Initialize chatbot state if available
    if CHATBOT_AVAILABLE:
        initialize_chatbot_state()

_init_state()

st.set_page_config(page_title="AI Browser Automation Lab", page_icon="🧪", layout="wide")

st.markdown("""
<style>
/* Professional theme inspired by BrowserStack */
.stApp { 
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #1a1f36;
}

.block-container { 
    padding-top: 2rem; 
    padding-bottom: 2rem; 
    max-width: 1400px;
}

/* Headers with professional styling */
h1 { 
    color: #1a1f36;
    font-weight: 700;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

h2 { 
    color: #2563eb;
    font-weight: 600;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
    margin-top: 2rem;
}

h3 { 
    color: #1e40af;
    font-weight: 600;
}

h4 { 
    color: #475569;
    font-weight: 600;
}

/* Professional buttons with teal/green gradient - better contrast */
.stButton>button {
    background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
    color: #ffffff;
    border-radius: 8px;
    border: none;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(13, 148, 136, 0.3);
    font-size: 1rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.stButton>button:hover {
    background: linear-gradient(135deg, #0f766e 0%, #115e59 100%);
    box-shadow: 0 6px 12px rgba(13, 148, 136, 0.4);
    transform: translateY(-2px);
}

.stButton>button:active {
    transform: translateY(0px);
}

/* Code blocks with Claude-like light styling */
.stCodeBlock {
    background-color: #fafafa !important;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* Code content styling - light background with good syntax visibility */
.stCodeBlock pre {
    background-color: #fafafa !important;
    color: #1a1a1a !important;
}

.stCodeBlock code {
    background-color: #fafafa !important;
    color: #1a1a1a !important;
    font-family: 'SF Mono', 'Monaco', 'Menlo', 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* Inline code */
code {
    background-color: #f5f5f5 !important;
    color: #1e293b !important;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    font-family: 'SF Mono', 'Monaco', 'Menlo', 'Courier New', monospace;
}

/* Python syntax highlighting approximation */
.stCodeBlock .hljs-keyword { color: #0550ae; font-weight: 600; }
.stCodeBlock .hljs-string { color: #0a3069; }
.stCodeBlock .hljs-comment { color: #57606a; font-style: italic; }
.stCodeBlock .hljs-function { color: #8250df; }
.stCodeBlock .hljs-number { color: #0550ae; }
.stCodeBlock .hljs-built_in { color: #0550ae; }

/* Text inputs with professional styling */
.stTextInput>div>div>input {
    background-color: #ffffff;
    border: 2px solid #cbd5e1;
    color: #1e293b;
    border-radius: 8px;
    padding: 0.75rem;
    transition: all 0.3s ease;
    font-size: 0.95rem;
}

.stTextInput>div>div>input:focus {
    border-color: #0d9488;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1);
    outline: none;
}

/* Select boxes */
.stSelectbox>div>div>select {
    background-color: #ffffff;
    border: 2px solid #cbd5e1;
    color: #1e293b;
    border-radius: 8px;
    padding: 0.75rem;
}

/* Alert boxes with clean styling */
.stAlert {
    border-radius: 8px;
    background-color: #eff6ff;
    border-left: 4px solid #0d9488;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 1rem;
}

/* Expanders with card styling */
.streamlit-expanderHeader {
    background-color: #ffffff;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    padding: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.streamlit-expanderHeader:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Images with clean borders */
img {
    border-radius: 8px;
    border: 2px solid #e5e7eb;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

img:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    transform: scale(1.01);
}

/* Dividers */
hr {
    border-color: #e5e7eb;
    margin: 2rem 0;
}

/* Text styling */
p, li, span {
    color: #475569;
}

strong {
    color: #1e293b;
    font-weight: 600;
}

/* Caption text */
.caption {
    color: #64748b;
    font-size: 0.9rem;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #0d9488 !important;
}

/* Success messages */
.success {
    background-color: #f0fdf4;
    border-left-color: #10b981;
}

/* Error messages */
.error {
    background-color: #fef2f2;
    border-left-color: #ef4444;
}

/* Warning messages */
.warning {
    background-color: #fffbeb;
    border-left-color: #f59e0b;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* Example subtitle styling */
.example-subtitle {
    color: #64748b;
    font-size: 0.85rem;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

st.title("🧪 AI Browser Automation Lab")
st.caption("Multi-agent browser testing with Playwright. Powered by AI for intelligent test generation and self-healing.")
st.markdown("**Pipeline:** Flow Discovery → Script Generation → Execution → Diagnosis & Self-Heal → Visual Regression Guard")

def _use_example(url: str, goal: str):
    st.session_state["target_url_input"] = url
    st.session_state["goal_prompt_input"] = goal

def _cleanup_screenshots():
    for name in ("run_result.png", "run_error.png"):
        try:
            if os.path.exists(name):
                os.remove(name)
        except Exception:
            pass

def _normalize_execution_result(result):
    success, log, screenshot_path = False, "", None
    if isinstance(result, dict):
        success = bool(result.get("success"))
        raw_log = result.get("log", "")
        log = "\n".join(str(x) for x in raw_log) if isinstance(raw_log, (list, tuple)) else str(raw_log or "")
        screenshot_path = result.get("screenshot_path")
    elif isinstance(result, (tuple, list)):
        if len(result) > 0: success = bool(result[0])
        if len(result) > 1:
            raw_log = result[1]
            log = "\n".join(str(x) for x in raw_log) if isinstance(raw_log, (list, tuple)) else str(raw_log or "")
        if len(result) > 2: screenshot_path = result[2]
    else:
        log = str(result)
    return success, log, screenshot_path

def _is_valid_playwright_script(script_code: str) -> bool:
    if not script_code: return False
    s = script_code.strip()
    if s.startswith("# Script generation failed"): return False
    return "from playwright.sync_api import sync_playwright" in s and "def run():" in s

def _get_test_id_from_url_goal(url: str, goal: str) -> str:
    u = (url or "").lower()
    if "the-internet.herokuapp.com" in u:
        if "login" in goal.lower(): return "herokuapp_login"
        if "dynamic" in goal.lower(): return "herokuapp_dynamic"
        if "dropdown" in goal.lower(): return "herokuapp_dropdown"
        if "upload" in goal.lower(): return "herokuapp_upload"
    if "saucedemo.com" in u:
        g = goal.lower()
        if "intentionally" in g or "demonstrate visual regression" in g: return "saucedemo_visual_regression"
        if "backpack" in g: return "saucedemo_backpack"
        return "saucedemo_checkout"
    if "demoblaze.com" in u: return "demoblaze_checkout"
    raw = url or ""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", raw).strip("_").lower()
    return slug[:80] or "default_scenario"

def _get_visual_ids(url: str, goal: str):
    test_id = _get_test_id_from_url_goal(url, goal)
    print(f"\n{'='*60}\n[Visual IDs] Self-Baseline Mode\n  Test ID: {test_id}\n  - First run: CREATE baseline\n  - Subsequent runs: COMPARE against baseline\n{'='*60}\n")
    return test_id, None, False

def _run_execution(script_code: str, step_exec, log_box, label: str):
    _cleanup_screenshots()
    st.session_state["last_run_label"] = label
    step_exec.markdown(f"**Stage 3/5 — {label}:** ⏳ running...")
    with st.spinner(f"{label} Agent is running the script..."):
        try:
            raw = execute_script(script_code)
        except Exception as e:
            success, log, screenshot_path = False, f"Exception while executing script:\n{e}", None
        else:
            success, log, screenshot_path = _normalize_execution_result(raw)
    step_exec.markdown("**Stage 3/5 — Execution:** ✅ passed" if success else "**Stage 3/5 — Execution:** ❌ failed")
    log_box.markdown("**Execution Log:**")
    log_box.code(log or "(no log output)", language="bash")
    if screenshot_path and os.path.exists(screenshot_path):
        st.image(screenshot_path, caption=f"{label} screenshot", use_container_width=True)
    return success, log, screenshot_path

def _run_diagnosis_and_repair(script_code, log, step_diag, diag_box, repair_box):
    step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⏳ running...")
    with st.spinner("Error Diagnosis Agent is analyzing the failure..."):
        try:
            diagnosis = diagnose(log)
        except Exception as e:
            diagnosis = f"Diagnosis error: {e}"
    diag_box.markdown(f"**Diagnosis:** {diagnosis}")
    with st.spinner("Adaptive Repair Agent is proposing a fix..."):
        try:
            repaired_script, note = self_heal(script_code, log)
        except Exception as e:
            repaired_script, note = None, f"Self-heal error: {e}"
    if repaired_script and repaired_script.strip() and repaired_script.strip() != script_code.strip() and _is_valid_playwright_script(repaired_script):
        st.session_state["repaired_script"] = repaired_script
        step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ fix proposed")
        repair_box.empty()
        repair_box.markdown(f"**Adaptive Repair Note:** {note}")
        repair_box.code(repaired_script, language="python")
        diag_box.info("A self-healed script has been generated. Click **Apply Fix & Re-Run** below to execute the repaired test.")
    else:
        st.session_state["repaired_script"] = None
        step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⚠️ no automatic fix applied")
        repair_box.info(note or "No automatic self-heal applied. The failure likely requires manual adjustment.")

def _run_visual_guard(url: str, goal: str, screenshot_path: str, step_visual, vr_box):
    step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⏳ running...")
    if not screenshot_path or not os.path.exists(screenshot_path):
        step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped (no screenshot)")
        vr_box.info("No screenshot available for visual regression check.")
        return
    test_id, baseline_id, create_baseline_only = _get_visual_ids(url, goal)
    with st.spinner("Visual Regression Guard is comparing screenshots..."):
        result = run_visual_check(test_id=test_id, screenshot_path=screenshot_path, baseline_dir="screenshots", baseline_id=baseline_id, create_baseline_only=create_baseline_only)
    status = result.get("status")
    message = result.get("message", "")
    diff_path = result.get("diff_path")
    if status == "baseline_created": step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ✅ baseline created")
    elif status == "passed": step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ✅ passed")
    elif status == "failed": step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ❌ failed")
    else: step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⚠️ unavailable")
    id_info = f"test_id={test_id}"
    if baseline_id: id_info += f", baseline_id={baseline_id}"
    vr_box.markdown(f"*Visual IDs:* `{id_info}`")
    if status == "baseline_created": vr_box.success(message)
    elif status == "passed": vr_box.success(message)
    elif status == "failed":
        vr_box.error(message)
        if diff_path and os.path.exists(diff_path):
            st.image(diff_path, caption="Visual difference vs baseline", use_container_width=True)
    else: vr_box.info(message)

with st.expander("📋 Example Test Scenarios", expanded=False):
    
    st.markdown("#### 1. **Herokuapp Login** - Basic Form Interaction ✅")
    st.markdown('<p class="example-subtitle">Test standard login flow with form validation</p>', unsafe_allow_html=True)
    u = "https://the-internet.herokuapp.com/login"
    g = "Open the login page, log in with username 'tomsmith' and password 'SuperSecretPassword!', then verify the secure area."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_login", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 2. **Saucedemo Cart** - E-commerce Flow ✅")
    st.markdown('<p class="example-subtitle">Add product to cart and verify checkout process</p>', unsafe_allow_html=True)
    u = "https://www.saucedemo.com"
    g = "Log in with 'standard_user'/'secret_sauce', add 'Sauce Labs Backpack' to cart, open cart and verify the item is listed."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_sauce_base", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 3. **Saucedemo Visual Regression** - Visual Testing Demo 📸")
    st.markdown('<p class="example-subtitle">Automatically detect UI changes between test runs</p>', unsafe_allow_html=True)
    u = "https://www.saucedemo.com"
    g = "Log in with 'standard_user'/'secret_sauce', add 'Sauce Labs Backpack' to cart. This scenario intentionally produces different screenshots on each run to demonstrate visual regression detection."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_sauce_vr", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 4. **Demoblaze Self-Heal** - Broken Script → Auto-fix 🔧")
    st.markdown('<p class="example-subtitle">AI automatically fixes broken test selectors</p>', unsafe_allow_html=True)
    u = "https://www.demoblaze.com"
    g = "Go to Laptops, add 'Sony vaio i5' to cart, open cart, place order, fill details, complete purchase, and verify confirmation."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_demo", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 5. **Dropdown Selection** - UI Component Testing 🎯")
    st.markdown('<p class="example-subtitle">Test dropdown menus and select options</p>', unsafe_allow_html=True)
    u = "https://the-internet.herokuapp.com/dropdown"
    g = "Navigate to dropdown page, select Option 1 from dropdown, and verify selection."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_dropdown", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 6. **File Upload** - File Handling Test 📁")
    st.markdown('<p class="example-subtitle">Create temp file, upload it, and verify success</p>', unsafe_allow_html=True)
    u = "https://the-internet.herokuapp.com/upload"
    g = "Navigate to file upload page, create a test file, upload it, and verify successful upload."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_upload", on_click=_use_example, args=(u, g))
    st.markdown("---")
    
    st.markdown("#### 7. **Dynamic Content** - Wait & Load Testing ⏱️")
    st.markdown('<p class="example-subtitle">Handle dynamically loaded content with smart waits</p>', unsafe_allow_html=True)
    u = "https://the-internet.herokuapp.com/dynamic_content"
    g = "Navigate to dynamic content page, wait for content to load, and capture screenshot."
    c1, c2 = st.columns([3, 1])
    with c1: st.code(f"URL: {u}\nGoal: {g}", language="text")
    with c2: st.button("Use this", key="ex_dynamic", on_click=_use_example, args=(u, g))

st.markdown("---")
cols = st.columns([3, 5, 2])
with cols[0]: target_url = st.text_input("Target URL", key="target_url_input", placeholder="https://example.com")
with cols[1]: goal_prompt = st.text_input("Goal / Prompt", key="goal_prompt_input", placeholder="Describe what you want to test...")
with cols[2]: engine = st.selectbox("Automation Engine", ["Playwright (Python)"], index=0)

# Add buttons row with Generate & Run and AI Assistant
button_cols = st.columns([3, 1])
with button_cols[0]:
    run_button = st.button("🚀 Generate & Run", use_container_width=True)
with button_cols[1]:
    if CHATBOT_AVAILABLE:
        chatbot_button = st.button("🤖 AI Assistant", use_container_width=True)
        if chatbot_button:
            st.session_state.show_chatbot = not st.session_state.show_chatbot
    else:
        st.button("🤖 AI Assistant", use_container_width=True, disabled=True, help="Install langgraph and langchain to enable")

# Show chatbot in sidebar or modal if activated
if CHATBOT_AVAILABLE and st.session_state.show_chatbot:
    with st.sidebar:
        st.markdown("---")
        render_chatbot_ui()

st.markdown("---")
step_cols = st.columns(5)
step_flow = step_cols[0].empty()
step_script = step_cols[1].empty()
step_exec = step_cols[2].empty()
step_diag = step_cols[3].empty()
step_visual = step_cols[4].empty()

st.markdown("### 🧭 Discovered Flow")
flow_box = st.empty()
st.markdown("### 🧪 Generated Script")
script_box = st.empty()
st.markdown("### 📜 Execution Log")
log_box = st.empty()
st.markdown("### 🩹 Diagnosis & Self-Heal")
diag_box = st.empty()
repair_box = st.empty()
st.markdown("### 👁️ Visual Regression Guard")
vr_box = st.empty()

if run_button:
    st.session_state["repaired_script"] = None
    if not target_url.strip() or not goal_prompt.strip():
        st.warning("Please provide both a Target URL and a Goal / Prompt.")
    else:
        url = target_url.strip()
        goal = goal_prompt.strip()
        
        step_flow.markdown("**Stage 1/5 — Flow Discovery:** ⏳ running...")
        with st.spinner("Flow Discovery Agent is analyzing your goal & app..."):
            try:
                flow = discover_flow(url, goal)
            except Exception as e:
                flow = [f"Flow discovery failed: {e}"]
        step_flow.markdown("**Stage 1/5 — Flow Discovery:** ✅ completed")
        flow_str = "\n".join(f"- {s}" for s in flow) if isinstance(flow, (list, tuple)) else str(flow)
        flow_box.markdown("**Discovered Flow:**")
        flow_box.code(flow_str, language="markdown")
        
        step_script.markdown("**Stage 2/5 — Script Generation:** ⏳ running...")
        with st.spinner("Script Generation Agent is producing a Playwright script..."):
            try:
                script_code = generate_script(url, goal)
            except Exception as e:
                script_code = f"# Script generation failed: {e}"
        if not isinstance(script_code, str): script_code = str(script_code)
        st.session_state["last_script"] = script_code
        if _is_valid_playwright_script(script_code):
            step_script.markdown("**Stage 2/5 — Script Generation:** ✅ completed")
        else:
            step_script.markdown("**Stage 2/5 — Script Generation:** ❌ failed")
        script_box.markdown("**Generated Script:**")
        script_box.code(script_code, language="python")
        
        if not _is_valid_playwright_script(script_code):
            step_exec.markdown("**Stage 3/5 — Execution:** ⭕ skipped (no runnable script)")
            step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⭕ skipped")
            step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped")
            vr_box.info("Visual regression guard skipped (no runnable script).")
        else:
            success, log, screenshot_path = _run_execution(script_code, step_exec, log_box, "Execution")
            if not success:
                _run_diagnosis_and_repair(script_code, log, step_diag, diag_box, repair_box)
                step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped (test failed)")
                vr_box.info("Visual regression guard skipped because the test run failed.")
            else:
                step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ skipped (execution passed)")
                _run_visual_guard(url, goal, screenshot_path, step_visual, vr_box)

if st.session_state.get("repaired_script"):
    st.markdown("---")
    st.markdown("### 🔧 Apply Adaptive Repair")
    if st.button("✅ Apply Fix & Re-Run", use_container_width=True, key="apply_fix"):
        repaired_script = st.session_state.get("repaired_script")
        if repaired_script and _is_valid_playwright_script(repaired_script):
            step_flow.markdown("**Stage 1/5 — Flow Discovery:** ♻️ reused from previous run")
            step_script.markdown("**Stage 2/5 — Script Generation:** ♻️ using repaired script from Adaptive Repair")
            success, log, screenshot_path = _run_execution(repaired_script, step_exec, log_box, "Re-run (Repaired Script)")
            if success:
                step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ repaired script passed")
                _run_visual_guard(st.session_state.get("target_url_input", ""), st.session_state.get("goal_prompt_input", ""), screenshot_path, step_visual, vr_box)
                st.session_state["repaired_script"] = None
            else:
                _run_diagnosis_and_repair(repaired_script, log, step_diag, diag_box, repair_box)
                step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped (repaired test failed)")
                vr_box.info("Visual regression guard skipped because the repaired run failed.")
        else:
            st.warning("Repaired script is not runnable; please review it manually.")