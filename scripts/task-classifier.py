#!/usr/bin/env python3
"""
Task Classifier - Automatically categorizes tasks as SIMPLE or COMPLEX.
Used to determine model selection (Haiku vs Opus) and context loading.
"""

import sys
import re
from enum import Enum


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class TaskClassifier:
    """
    3-tier decision tree: SIMPLE (Haiku) → MEDIUM (Sonnet) → COMPLEX (Opus).
    Returns: TaskComplexity enum + reasoning
    """

    # Keywords that require Opus — deep reasoning, architecture, multi-step execution
    OPUS_KEYWORDS = {
        # Deep coding/architecture
        "refactor",
        "architecture",
        "algorithm",
        "implement",
        "unit test",
        "integration test",
        # Strategic / multi-step
        "strategy",
        "audit",
        "migrate",
        "automate",
        "troubleshoot",
        "workflow",
        "procedure",
        # Research + synthesis
        "research",
        "analyze",
        "evaluate",
        "assess",
        "optimize",
        # Project-specific context
        "momo",
        "kibidango",
        "ios",
        "leidos",
    }

    # Keywords that need Sonnet — conversational analysis, writing, medium coding
    SONNET_KEYWORDS = {
        # Writing / content
        "write",
        "document",
        "email",
        "article",
        "post",
        "summary",
        "report",
        "outline",
        "edit",
        "revise",
        "draft",
        "content",
        # Medium coding
        "code",
        "build",
        "create",
        "design",
        "function",
        "class",
        "fix",
        "error",
        "issue",
        "bug",
        # Analysis lite
        "explain",
        "interpret",
        "compare",
        "review",
        "plan",
        "think",
        # Context-aware
        "project",
        "memory",
        "context",
        "history",
        "continuity",
        "configure",
        "setup",
        "manage",
        "monitor",
    }

    # Keywords that indicate SIMPLE tasks (Haiku)
    SIMPLE_KEYWORDS = {
        "weather",
        "time",
        "date",
        "calendar",
        "check",
        "status",
        "list",
        "what",
        "when",
        "where",
        "who",
        "how many",
        "count",
        "find",
        "show",
        "view",
        "get",
        "fetch",
        "search",
        "lookup",
        "is",
        "delete",
        "remove",
        "rm",
        "kill",
        "stop",
        "start",
    }

    @staticmethod
    def classify(user_input: str) -> tuple[TaskComplexity, str]:
        """
        Classify a task as SIMPLE, MEDIUM, or COMPLEX.

        Returns:
            (TaskComplexity, reasoning_string)
        """
        text = user_input.lower().strip()
        token_count = len(text.split())

        # Rule 1: Code/command patterns → at least Sonnet
        if re.search(r"```|#!/|def |class |function |=>|const |let ", text):
            return (TaskComplexity.MEDIUM, "Code snippet detected")

        # Rule 2: Opus keywords (strong signal for deep reasoning)
        opus_matches = [kw for kw in TaskClassifier.OPUS_KEYWORDS if kw in text]
        if opus_matches:
            return (
                TaskComplexity.COMPLEX,
                f"Opus keyword(s): {', '.join(opus_matches[:5])}",
            )

        # Rule 3: Sonnet keywords
        sonnet_matches = [kw for kw in TaskClassifier.SONNET_KEYWORDS if kw in text]
        if sonnet_matches:
            return (
                TaskComplexity.MEDIUM,
                f"Sonnet keyword(s): {', '.join(sonnet_matches[:5])}",
            )

        # Rule 4: Multi-line or chained → at least Sonnet
        if "\n" in text or text.count("?") > 1 or text.count("&&") > 0:
            return (TaskComplexity.MEDIUM, "Multi-line or chained query")

        # Rule 5: Simple keyword match + short input → Haiku
        simple_matches = sum(1 for kw in TaskClassifier.SIMPLE_KEYWORDS if kw in text)
        if simple_matches >= 2 or (simple_matches >= 1 and token_count <= 10):
            return (
                TaskComplexity.SIMPLE,
                f"Simple keyword(s) detected, short input ({token_count} tokens)",
            )

        # Rule 6: Very short factual query → Haiku
        if token_count <= 3:
            return (TaskComplexity.SIMPLE, "Short factual query")

        # Default: Sonnet (safe middle ground — not Haiku, not Opus)
        return (
            TaskComplexity.MEDIUM,
            "Ambiguous — defaulting to Sonnet (safe middle ground)",
        )

    @staticmethod
    def get_model(complexity: TaskComplexity) -> str:
        """Return recommended model for complexity level."""
        return {
            TaskComplexity.SIMPLE: "anthropic/claude-haiku-4-5-20251001",
            TaskComplexity.MEDIUM: "anthropic/claude-sonnet-4-6",
            TaskComplexity.COMPLEX: "anthropic/claude-opus-4-6",
        }[complexity]

    @staticmethod
    def get_thinking(complexity: TaskComplexity) -> str:
        """Return recommended thinking level."""
        return {
            TaskComplexity.SIMPLE: "off",
            TaskComplexity.MEDIUM: "off",  # upgrade to medium for analysis tasks
            TaskComplexity.COMPLEX: "medium",
        }[complexity]

    @staticmethod
    def get_context_level(complexity: TaskComplexity) -> str:
        """Return recommended context loading level."""
        return {
            TaskComplexity.SIMPLE: "minimal",
            TaskComplexity.MEDIUM: "standard",
            TaskComplexity.COMPLEX: "full",
        }[complexity]


def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: task-classifier.py '<user input>'")
        print("Example: task-classifier.py 'what is the weather?'")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    complexity, reasoning = TaskClassifier.classify(user_input)
    model = TaskClassifier.get_model(complexity)
    thinking = TaskClassifier.get_thinking(complexity)
    context = TaskClassifier.get_context_level(complexity)

    print(f"Task: {user_input}")
    print(f"Complexity: {complexity.value.upper()}")
    print(f"Reasoning: {reasoning}")
    print(f"Model: {model}")
    print(f"Thinking: {thinking}")
    print(f"Context: {context}")


if __name__ == "__main__":
    main()
