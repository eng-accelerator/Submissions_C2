# agents/execution.py

import subprocess
import sys
import os
import tempfile
import textwrap


def execute_script(script_code: str):
    """
    Execute the given Playwright script code in an isolated Python process.

    Returns:
        {
            "success": bool,
            "log": str,
            "screenshot_path": str | None
        }
    """
    # Basic validation
    if not script_code or not script_code.strip():
        return {
            "success": False,
            "log": "No script code provided.",
            "screenshot_path": None,
        }

    # Write script to a temporary file
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".py", mode="w", encoding="utf-8"
        ) as tmp:
            # Normalize indentation a bit and ensure trailing newline
            tmp.write(textwrap.dedent(script_code).strip() + "\n")
            tmp_path = tmp.name
    except Exception as e:
        return {
            "success": False,
            "log": f"Failed to create temporary script file: {e}",
            "screenshot_path": None,
        }

    try:
        env = os.environ.copy()

        # Run the script as a subprocess
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        combined_log = (stdout + ("\n" + stderr if stderr else "")).strip()

        # Determine screenshot path: prefer success screenshot, else error screenshot
        screenshot_path = None
        if os.path.exists("run_result.png"):
            screenshot_path = "run_result.png"
        elif os.path.exists("run_error.png"):
            screenshot_path = "run_error.png"

        return {
            "success": proc.returncode == 0,
            "log": combined_log,
            "screenshot_path": screenshot_path,
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "log": f"Execution timed out: {e}",
            "screenshot_path": None,
        }
    except Exception as e:
        return {
            "success": False,
            "log": f"Execution failed: {e}",
            "screenshot_path": None,
        }
    finally:
        # Always try to clean up the temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass
