"""Manual harness for invoking the persona suite pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from agents.persona_suite import run_persona_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the persona suite on local assets.")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Image paths to analyse.",
    )
    parser.add_argument(
        "--brief",
        default="",
        help="Optional design brief or context string.",
    )
    parser.add_argument(
        "--task",
        action="append",
        default=[],
        dest="tasks",
        help="Task(s) to validate (repeat flag for multiple).",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print markdown report in addition to JSON summary.",
    )
    return parser.parse_args()


def run(paths: Dict[str, str], brief: str, tasks: list[str], markdown: bool) -> None:
    result = run_persona_batch(paths, brief=brief, tasks_to_validate=tasks)

    print("=== Persona Suite JSON Summary ===")
    print(json.dumps(result["report"], indent=2, ensure_ascii=False))

    if markdown:
        print("\n=== Persona Suite Markdown Report ===")
        print(result["report_markdown"])


def main() -> None:
    args = parse_args()
    files = {}
    for path in args.paths:
        abs_path = Path(path).expanduser()
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: {abs_path}")
        files[str(abs_path)] = str(abs_path)

    run(files, args.brief, args.tasks, args.markdown)


if __name__ == "__main__":
    main()


