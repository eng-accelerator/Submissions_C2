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
        success = proc.returncode == 0

        # Decide screenshot based on success/failure.
        result_exists = os.path.exists("run_result.png")
        error_exists = os.path.exists("run_error.png")

        screenshot_path = None
        if success:
            if result_exists:
                screenshot_path = "run_result.png"
            elif error_exists:
                screenshot_path = "run_error.png"
        else:
            if error_exists:
                screenshot_path = "run_error.png"
            elif result_exists:
                screenshot_path = "run_result.png"

        return {
            "success": success,
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
        try:
            os.remove(tmp_path)
        except Exception:
            pass
