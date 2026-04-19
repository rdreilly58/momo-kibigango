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
spec = importlib.util.spec_from_file_location("task_classifier", Path(__file__).parent / "task-classifier.py")
tc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc_module)
TaskClassifier = tc_module.TaskClassifier
TaskComplexity = tc_module.TaskComplexity

class TaskRouter:
    """
    Complete routing system: classify → select model → load context → set thinking.
    """
    
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    
    # Context files for SIMPLE tasks (minimal)
    SIMPLE_CONTEXT = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "USER.md": WORKSPACE / "USER.md",
    }
    
    # Context files for COMPLEX tasks (full)
    COMPLEX_CONTEXT = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "USER.md": WORKSPACE / "USER.md",
        "MEMORY.md": WORKSPACE / "MEMORY.md",
        "TOOLS.md": WORKSPACE / "TOOLS.md",
        "HEARTBEAT.md": WORKSPACE / "HEARTBEAT.md",
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
        if context_level == "minimal":
            context_files = list(TaskRouter.SIMPLE_CONTEXT.keys())
        else:
            context_files = list(TaskRouter.COMPLEX_CONTEXT.keys())
            # Add today's memory if exists
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            today_file = TaskRouter.WORKSPACE / "memory" / f"{today}.md"
            if today_file.exists():
                context_files.append(f"memory/{today}.md")
        
        # Step 6: Calculate expected response time
        if complexity == TaskComplexity.SIMPLE:
            expected_time = "0.5-1s"
        else:
            expected_time = "1-2s"
        
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
        
        return result
    
    @staticmethod
    def should_use_subagent(user_input: str) -> bool:
        """Check if task should be delegated to subagent (coding tasks)."""
        coding_keywords = ['code', 'build', 'debug', 'implement', 'test', 'refactor']
        text = user_input.lower()
        return any(kw in text for kw in coding_keywords)

def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: task_router.py '<user input>' [--verbose]")
        sys.exit(1)
    
    user_input = ' '.join(sys.argv[1:]).replace('--verbose', '').strip()
    verbose = '--verbose' in sys.argv
    
    result = TaskRouter.route(user_input, verbose=verbose)
    
    if not verbose:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
