import os
import re
import streamlit as st

from agents.flow_discovery import discover_flow
from agents.script_generator import generate_script
from agents.execution import execute_script
from agents.error_diagnosis import diagnose
from agents.adaptive_repair import self_heal
from agents.regression_monitor import run_visual_check

# ===== CHATBOT INTEGRATION - NEW IMPORT =====
try:
    from agents.llm.IChatbot import Chatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    Chatbot = None
# ============================================


def _init_state():
    st.session_state.setdefault("target_url_input", "")
    st.session_state.setdefault("goal_prompt_input", "")
    st.session_state.setdefault("last_script", "")
    st.session_state.setdefault("repaired_script", None)
    st.session_state.setdefault("last_run_label", "")
    
    # ===== CHATBOT INTEGRATION - INITIALIZE CHATBOT =====
    if CHATBOT_AVAILABLE and "chatbot" not in st.session_state:
        st.session_state.chatbot = Chatbot()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # ===================================================

_init_state()


st.set_page_config(page_title="AI Browser Automation Lab", page_icon="🧪", layout="wide")

st.markdown("""
<style>
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
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

/* Checkboxes */
.stCheckbox>label {
    color: #1e293b;
    font-weight: 500;
}

/* Progress bars */
.stProgress>div>div>div>div {
    background-color: #0d9488;
}

/* Dividers */
hr {
    border-color: #cbd5e1;
    margin: 2rem 0;
}

/* Example subtitle styling */
.example-subtitle {
    color: #64748b;
    font-size: 0.95rem;
    margin-top: 0.25rem;
    margin-bottom: 0.75rem;
}

/* Chat message styling */
.chat-message {
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    line-height: 1.5;
}

.chat-message.user {
    background-color: #eff6ff;
    border-left: 3px solid #0d9488;
}

.chat-message.assistant {
    background-color: #f8fafc;
    border-left: 3px solid #2563eb;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    padding: 1rem;
}

[data-testid="stSidebar"] .stButton>button {
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
}

[data-testid="stSidebar"] h2 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

/* Pulse animation for AI Assistant button */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(13, 148, 136, 0); }
    100% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0); }
}

.pulse-button {
    animation: pulse 2s infinite;
}

/* AI Assistant badge */
.ai-badge {
    background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 4px rgba(13, 148, 136, 0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("🧪 AI Browser Automation Lab")
st.markdown('<p class="example-subtitle">Your AI-powered testing companion with Self-Healing & Visual Regression Guard</p>', unsafe_allow_html=True)

# ===== CHATBOT INTEGRATION - ADD VISIBLE "ASK AI" BUTTON =====
if CHATBOT_AVAILABLE:
    col_title, col_ai_button = st.columns([4, 1])
    with col_ai_button:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("💬 Ask AI Assistant", use_container_width=True, type="primary", help="Get help from AI", key="ask_ai_btn"):
            # Add welcome message to chat if empty
            if not st.session_state.chat_history:
                welcome_msg = "👋 Hi! I'm your AI assistant. I can help you with browser automation, test failures, examples, and more. What would you like to know?"
                st.session_state.chat_history.append(("assistant", welcome_msg))
            st.rerun()
else:
    st.markdown("")
# =================================================================

def _use_example(url_val: str, goal_val: str):
    st.session_state["target_url_input"] = url_val
    st.session_state["goal_prompt_input"] = goal_val
    st.session_state["repaired_script"] = None

def _is_valid_playwright_script(code):
    if not isinstance(code, str): return False
    code_l = code.lower()
    if "# script generation failed" in code_l or "# error" in code_l: return False
    if "from playwright" in code_l or "sync_playwright" in code_l: return True
    return False

def _run_execution(script_code, step_marker, log_box, label="Execution"):
    step_marker.markdown(f"**Stage 3/5 — {label}:** ⏳ running...")
    with st.spinner(f"{label} Agent is executing the Playwright script..."):
        try:
            result = execute_script(script_code)
        except Exception as e:
            result = {"success": False, "log": f"Execution error: {e}", "screenshot_path": None}
    success = result.get("success", False)
    log = result.get("log", "")
    screenshot_path = result.get("screenshot_path")
    if success: step_marker.markdown(f"**Stage 3/5 — {label}:** ✅ passed")
    else: step_marker.markdown(f"**Stage 3/5 — {label}:** ❌ failed")
    log_box.markdown(f"**{label} Log:**")
    if success: log_box.success(f"Test passed! ✅\n\n```\n{log}\n```")
    else: log_box.error(f"Test failed. ❌\n\n```\n{log}\n```")
    if screenshot_path and os.path.exists(screenshot_path):
        st.image(screenshot_path, caption=f"{label} Screenshot", use_container_width=True)
    return success, log, screenshot_path

def _run_diagnosis_and_repair(script_code, error_log, step_marker, diag_box, repair_box):
    step_marker.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⏳ running...")
    with st.spinner("Diagnosis Agent is analyzing the error..."):
        try:
            diagnosis_msg = diagnose(error_log)
        except Exception as e:
            diagnosis_msg = f"Diagnosis error: {e}"
    diag_box.markdown("**Diagnosis:**")
    diag_box.warning(diagnosis_msg)
    with st.spinner("Adaptive Repair Agent is attempting to fix the script..."):
        try:
            healed_script, heal_note = self_heal(script_code, error_log)
        except Exception as e:
            healed_script, heal_note = None, f"Self-heal error: {e}"
    if healed_script:
        step_marker.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ repair available")
        repair_box.markdown("**Adaptive Repair Result:**")
        repair_box.info(f"🔧 {heal_note}")
        repair_box.code(healed_script, language="python")
        st.session_state["repaired_script"] = healed_script
    else:
        step_marker.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⭕ no auto-repair")
        repair_box.markdown("**Adaptive Repair Result:**")
        repair_box.info(f"ℹ️ {heal_note}")

def _get_visual_ids(url, goal):
    test_id = re.sub(r"[^\w\-]", "_", (url + " " + goal).lower())[:100]
    baseline_id = None
    create_baseline_only = False
    goal_l = (goal or "").lower()
    if "intentionally" in goal_l or "demonstrate visual regression" in goal_l:
        baseline_id = re.sub(r"[^\w\-]", "_", (url + " saucedemo_baseline").lower())[:100]
    return test_id, baseline_id, create_baseline_only

def _run_visual_guard(url, goal, screenshot_path, step_visual, vr_box):
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
    
    # ===== CHATBOT INTEGRATION - RETURN VISUAL RESULT FOR CONTEXT =====
    return result
    # ==================================================================

with st.expander("📋 Example Test Scenarios", expanded=False):
    st.info("💡 **Tip:** These are pre-built examples, but you can test **any website**! Just enter your own URL and goal below. The AI will generate a custom test script for you.")
    st.markdown("---")
    
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

run_button = st.button("🚀 Generate & Run", use_container_width=True)

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
    
    # ===== CHATBOT INTEGRATION - INITIALIZE TEST CONTEXT TRACKING =====
    test_context = {
        'success': False,
        'log': '',
        'screenshot_path': None,
        'visual_check': None,
        'self_heal_applied': None,
        'scenario': None,
        'error_diagnosis': None
    }
    # ==================================================================
    
    if not target_url.strip() or not goal_prompt.strip():
        st.warning("Please provide both a Target URL and a Goal / Prompt.")
    else:
        url = target_url.strip()
        goal = goal_prompt.strip()
        
        # ===== CHATBOT INTEGRATION - SET SCENARIO NAME =====
        test_context['scenario'] = f"{url} - {goal[:50]}"
        # ===================================================
        
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
            
            # ===== CHATBOT INTEGRATION - UPDATE TEST CONTEXT =====
            test_context['success'] = success
            test_context['log'] = log
            test_context['screenshot_path'] = screenshot_path
            # =====================================================
            
            if not success:
                # Run diagnosis and repair
                step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⏳ running...")
                with st.spinner("Diagnosis Agent is analyzing the error..."):
                    try:
                        diagnosis_msg = diagnose(log)
                        test_context['error_diagnosis'] = diagnosis_msg  # CHATBOT INTEGRATION
                    except Exception as e:
                        diagnosis_msg = f"Diagnosis error: {e}"
                        test_context['error_diagnosis'] = diagnosis_msg  # CHATBOT INTEGRATION
                diag_box.markdown("**Diagnosis:**")
                diag_box.warning(diagnosis_msg)
                
                with st.spinner("Adaptive Repair Agent is attempting to fix the script..."):
                    try:
                        healed_script, heal_note = self_heal(script_code, log)
                        if healed_script:
                            test_context['self_heal_applied'] = heal_note  # CHATBOT INTEGRATION
                    except Exception as e:
                        healed_script, heal_note = None, f"Self-heal error: {e}"
                
                if healed_script:
                    step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ repair available")
                    repair_box.markdown("**Adaptive Repair Result:**")
                    repair_box.info(f"🔧 {heal_note}")
                    repair_box.code(healed_script, language="python")
                    st.session_state["repaired_script"] = healed_script
                else:
                    step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⭕ no auto-repair")
                    repair_box.markdown("**Adaptive Repair Result:**")
                    repair_box.info(f"ℹ️ {heal_note}")
                
                step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped (test failed)")
                vr_box.info("Visual regression guard skipped because the test run failed.")
            else:
                step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ skipped (execution passed)")
                visual_result = _run_visual_guard(url, goal, screenshot_path, step_visual, vr_box)
                test_context['visual_check'] = visual_result  # CHATBOT INTEGRATION
        
        # ===== CHATBOT INTEGRATION - INJECT CONTEXT INTO CHATBOT =====
        if CHATBOT_AVAILABLE and st.session_state.get("chatbot"):
            st.session_state.chatbot.set_test_context(test_context)
        # =============================================================

if st.session_state.get("repaired_script"):
    st.markdown("---")
    st.markdown("### 🔧 Apply Adaptive Repair")
    if st.button("✅ Apply Fix & Re-Run", use_container_width=True, key="apply_fix"):
        repaired_script = st.session_state.get("repaired_script")
        if repaired_script and _is_valid_playwright_script(repaired_script):
            # ===== CHATBOT INTEGRATION - TRACK RE-RUN CONTEXT =====
            rerun_context = {
                'success': False,
                'log': '',
                'screenshot_path': None,
                'visual_check': None,
                'self_heal_applied': 'Re-running with repaired script',
                'scenario': 'Re-run with repaired script',
                'error_diagnosis': None
            }
            # =====================================================
            
            step_flow.markdown("**Stage 1/5 — Flow Discovery:** ♻️ reused from previous run")
            step_script.markdown("**Stage 2/5 — Script Generation:** ♻️ using repaired script from Adaptive Repair")
            success, log, screenshot_path = _run_execution(repaired_script, step_exec, log_box, "Re-run (Repaired Script)")
            
            # ===== CHATBOT INTEGRATION - UPDATE RE-RUN CONTEXT =====
            rerun_context['success'] = success
            rerun_context['log'] = log
            rerun_context['screenshot_path'] = screenshot_path
            # =======================================================
            
            if success:
                step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ repaired script passed")
                visual_result = _run_visual_guard(st.session_state.get("target_url_input", ""), st.session_state.get("goal_prompt_input", ""), screenshot_path, step_visual, vr_box)
                rerun_context['visual_check'] = visual_result  # CHATBOT INTEGRATION
                st.session_state["repaired_script"] = None
            else:
                # Re-run diagnosis for failed repair
                with st.spinner("Analyzing repaired script failure..."):
                    try:
                        diagnosis_msg = diagnose(log)
                        rerun_context['error_diagnosis'] = diagnosis_msg  # CHATBOT INTEGRATION
                    except Exception as e:
                        diagnosis_msg = f"Diagnosis error: {e}"
                        rerun_context['error_diagnosis'] = diagnosis_msg  # CHATBOT INTEGRATION
                
                with st.spinner("Attempting second repair..."):
                    try:
                        healed_script, heal_note = self_heal(repaired_script, log)
                        if healed_script:
                            rerun_context['self_heal_applied'] = f"Second repair: {heal_note}"  # CHATBOT INTEGRATION
                    except Exception as e:
                        healed_script, heal_note = None, f"Self-heal error: {e}"
                
                if healed_script:
                    step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ✅ second repair available")
                    repair_box.markdown("**Adaptive Repair Result (Second Attempt):**")
                    repair_box.info(f"🔧 {heal_note}")
                    repair_box.code(healed_script, language="python")
                    st.session_state["repaired_script"] = healed_script
                else:
                    step_diag.markdown("**Stage 4/5 — Diagnosis & Self-Heal:** ⭕ no further repair")
                    repair_box.markdown("**Adaptive Repair Result:**")
                    repair_box.info(f"ℹ️ {heal_note}")
                
                step_visual.markdown("**Stage 5/5 — Visual Regression Guard:** ⭕ skipped (repaired test failed)")
                vr_box.info("Visual regression guard skipped because the repaired run failed.")
            
            # ===== CHATBOT INTEGRATION - INJECT RE-RUN CONTEXT =====
            if CHATBOT_AVAILABLE and st.session_state.get("chatbot"):
                st.session_state.chatbot.set_test_context(rerun_context)
            # =======================================================
        else:
            st.warning("Repaired script is not runnable; please review it manually.")

# ===== CHATBOT INTEGRATION - ADD CHAT INTERFACE IN SIDEBAR =====
if CHATBOT_AVAILABLE:
    with st.sidebar:
        st.markdown('<div class="ai-badge">✨ AI-Powered</div>', unsafe_allow_html=True)
        st.markdown("## 💬 AI Assistant")
        st.markdown('<p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">Your automation expert, always ready to help!</p>', unsafe_allow_html=True)
        
        # Chat display area with scrollable container
        st.markdown("---")
        
        # Display chat history
        if st.session_state.chat_history:
            for role, message in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f'<div class="chat-message user"><strong>You:</strong><br>{message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant"><strong>🤖 Assistant:</strong><br>{message}</div>', unsafe_allow_html=True)
        else:
            st.info("👋 Hi! I'm your AI assistant. Ask me about:\n- How features work\n- Test failures\n- Which examples to try\n- Playwright tips")
        
        st.markdown("---")
        
        # Chat input with Enter key support
        user_input = st.chat_input("Ask a question... (Press Enter to send)")
        
        # Handle send (triggered by Enter or clicking send)
        if user_input and user_input.strip():
            # Add user message immediately
            st.session_state.chat_history.append(("user", user_input.strip()))
            
            # Show typing indicator
            with st.spinner("🤖 Assistant is typing..."):
                response = st.session_state.chatbot.reply(user_input.strip())
            
            # Add assistant response
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        
        # Clear button
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("")  # Spacing
        with col2:
            clear_button = st.button("Clear Chat 🗑️", use_container_width=True)
        
        # Handle clear
        if clear_button:
            st.session_state.chatbot.clear_history()
            st.session_state.chat_history = []
            st.rerun()
        
        # Quick help buttons
        st.markdown("---")
        st.markdown("**Quick Questions:**")
        
        if st.button("💡 How does self-heal work?", use_container_width=True):
            response = st.session_state.chatbot.reply("How does self-heal work?")
            st.session_state.chat_history.append(("user", "How does self-heal work?"))
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        
        if st.button("📸 What is visual regression?", use_container_width=True):
            response = st.session_state.chatbot.reply("What is visual regression?")
            st.session_state.chat_history.append(("user", "What is visual regression?"))
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        
        if st.button("🎯 Which example should I try?", use_container_width=True):
            response = st.session_state.chatbot.reply("Which example should I try?")
            st.session_state.chat_history.append(("user", "Which example should I try?"))
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        
        if st.button("📚 Show all examples", use_container_width=True):
            response = st.session_state.chatbot.reply("List all examples")
            st.session_state.chat_history.append(("user", "List all examples"))
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
        
        # Contextual help if test just ran
        if st.session_state.chatbot.last_test_result:
            st.markdown("---")
            test_result = st.session_state.chatbot.last_test_result
            if not test_result.get('success'):
                st.warning("⚠️ Last test failed. Ask me why!")
            elif test_result.get('visual_check', {}).get('status') == 'failed':
                st.warning("👁️ Visual regression detected!")
            elif test_result.get('self_heal_applied'):
                st.success("🔧 Self-heal was applied!")

else:
    with st.sidebar:
        st.markdown("## 💬 AI Assistant")
        st.info("💬 AI Assistant is not available. Install the chatbot module to enable this feature.")
# =====================================================