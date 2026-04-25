#!/usr/bin/env python3
"""
Task Router - Integrates classifier with context loading and model selection.
Used by automation scripts to automatically route tasks to optimal configuration.
"""

import sys
import json
from pathlib import Path
from enum import Enum

# Import classifier inline since it's in same directory
sys.path.insert(0, str(Path(__file__).parent))

# Load task_classifier module (note: hyphen in filename)
import importlib.util

spec = importlib.util.spec_from_file_location(
    "task_classifier", Path(__file__).parent / "task-classifier.py"
)
tc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc_module)
TaskClassifier = tc_module.TaskClassifier
TaskComplexity = tc_module.TaskComplexity

COMPLEXITY_TO_AGENT_TYPE = {
    "SIMPLE": "research",
    "MEDIUM": "research",
    "COMPLEX": "coding",
}

COMPLEXITY_TO_PRIORITY = {
    "SIMPLE": 3,
    "MEDIUM": 5,
    "COMPLEX": 7,
}


class TaskRouter:
    """
    Complete routing system: classify → select model → load context → set thinking.
    """

    WORKSPACE = Path.home() / ".openclaw" / "workspace"

    # Context files for SIMPLE tasks (Haiku — minimal)
    SIMPLE_CONTEXT = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "USER.md": WORKSPACE / "USER.md",
    }

    # Context files for MEDIUM tasks (Sonnet — standard)
    MEDIUM_CONTEXT = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "USER.md": WORKSPACE / "USER.md",
        "MEMORY.md": WORKSPACE / "MEMORY.md",
    }

    # Context files for COMPLEX tasks (Opus — full)
    COMPLEX_CONTEXT = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "USER.md": WORKSPACE / "USER.md",
        "MEMORY.md": WORKSPACE / "MEMORY.md",
        "TOOLS.md": WORKSPACE / "TOOLS.md",
        "today_memory": None,  # Set dynamically
    }

    @staticmethod
    def route(user_input: str, verbose: bool = False) -> dict:
        """
        Complete routing decision.

        Returns dict with:
        - complexity: SIMPLE or COMPLEX
        - model: Recommended model
        - thinking: Recommended thinking level
        - context_level: minimal or full
        - context_files: List of files to load
        - reasoning: Human-readable explanation
        """

        # Step 1: Classify
        complexity, reasoning = TaskClassifier.classify(user_input)

        # Step 2: Select model
        model = TaskClassifier.get_model(complexity)

        # Step 3: Set thinking level
        thinking = TaskClassifier.get_thinking(complexity)

        # Step 4: Determine context level
        context_level = TaskClassifier.get_context_level(complexity)

        # Step 5: Load context files
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        today_file = TaskRouter.WORKSPACE / "memory" / f"{today}.md"

        if context_level == "minimal":
            context_files = list(TaskRouter.SIMPLE_CONTEXT.keys())
        elif context_level == "standard":
            context_files = list(TaskRouter.MEDIUM_CONTEXT.keys())
        else:  # full
            context_files = list(TaskRouter.COMPLEX_CONTEXT.keys())
            if today_file.exists():
                context_files.append(f"memory/{today}.md")

        # Step 6: Calculate expected response time
        expected_time_map = {
            TaskComplexity.SIMPLE: "0.3-0.7s",
            TaskComplexity.MEDIUM: "0.5-1s",
            TaskComplexity.COMPLEX: "1-2s",
        }
        expected_time = expected_time_map.get(complexity, "1-2s")

        result = {
            "task": user_input,
            "complexity": complexity.value,
            "model": model,
            "thinking": thinking,
            "context_level": context_level,
            "context_files": context_files,
            "expected_time": expected_time,
            "reasoning": reasoning,
        }

        if verbose:
            print(json.dumps(result, indent=2))

        # Submit to coordinator (non-blocking — never breaks routing)
        try:
            import subprocess, os as _os

            _coord = _os.path.join(_os.path.dirname(__file__), "agent_coordinator.py")
            _complexity_val = (
                complexity.value if hasattr(complexity, "value") else str(complexity)
            )
            _agent_type = COMPLEXITY_TO_AGENT_TYPE.get(_complexity_val, "coding")
            _priority = COMPLEXITY_TO_PRIORITY.get(_complexity_val, 5)
            _coord_result = subprocess.run(
                [
                    "python3",
                    _coord,
                    "submit",
                    "--task",
                    user_input[:200],
                    "--type",
                    _agent_type,
                    "--priority",
                    str(_priority),
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            import json as _json

            result["coordinator_task_id"] = _json.loads(_coord_result.stdout).get(
                "task_id"
            )
        except Exception:
            result["coordinator_task_id"] = None

        return result

    @staticmethod
    def should_use_subagent(user_input: str) -> bool:
        """Check if task should be delegated to subagent (coding tasks)."""
        coding_keywords = ["code", "build", "debug", "implement", "test", "refactor"]
        text = user_input.lower()
        return any(kw in text for kw in coding_keywords)


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: task_router.py '<user input>' [--verbose]")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:]).replace("--verbose", "").strip()
    verbose = "--verbose" in sys.argv

    result = TaskRouter.route(user_input, verbose=verbose)

    if not verbose:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
