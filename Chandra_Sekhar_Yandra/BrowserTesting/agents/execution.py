# agents/execution.py

import subprocess
import textwrap
import os
import sys  # 👈 IMPORTANT

def execute_script(script_code: str, script_path: str = "generated_test.py"):
    """
    Execution Agent:
    - Writes script to file
    - Runs it with the SAME Python interpreter as Streamlit (sys.executable)
    - Returns success flag, logs, screenshot path
    """
    # Write script to file
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    # Use the current interpreter, not plain "python"
    result = subprocess.run(
        [sys.executable, script_path],   # 👈 this is the key change
        capture_output=True,
        text=True
    )

    success = (result.returncode == 0)
    logs = textwrap.dedent(result.stdout + "\n" + result.stderr).strip()

    # Pick screenshot file based on what the script produced
    screenshot_path = None
    if os.path.exists("run_result.png") and success:
        screenshot_path = "run_result.png"
    elif os.path.exists("run_error.png"):
        screenshot_path = "run_error.png"

    return success, logs.splitlines() if logs else [], screenshot_path
