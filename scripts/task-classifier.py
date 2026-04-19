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
    COMPLEX = "complex"

class TaskClassifier:
    """
    Decision tree for task classification.
    Returns: TaskComplexity enum + reasoning
    """
    
    # Keywords that indicate COMPLEX tasks
    COMPLEX_KEYWORDS = {
        # Code/Build
        'code', 'build', 'debug', 'refactor', 'compile', 'deploy', 'implement',
        'write', 'create', 'design', 'architecture', 'algorithm', 'function',
        'class', 'test', 'unit test', 'fix', 'error', 'issue', 'bug',
        
        # Analysis/Reasoning
        'analyze', 'analyze', 'research', 'think', 'strategy', 'plan',
        'decide', 'compare', 'evaluate', 'assess', 'review', 'audit',
        'optimize', 'improve', 'problem-solve', 'explain', 'interpret',
        
        # Multi-step/Workflow
        'workflow', 'process', 'procedure', 'automate', 'integrate', 'connect',
        'setup', 'configure', 'manage', 'monitor', 'troubleshoot',
        
        # Writing/Content
        'write', 'document', 'email', 'article', 'post', 'summary', 'report',
        'outline', 'edit', 'revise', 'polish', 'content', 'copy',
        
        # Projects/Context-aware
        'project', 'momo', 'kibidango', 'ios', 'portfolio', 'leidos',
        'memory', 'context', 'history', 'continuity',
    }
    
    # Keywords that indicate SIMPLE tasks
    SIMPLE_KEYWORDS = {
        'weather', 'time', 'date', 'calendar', 'check', 'status', 'list',
        'what', 'when', 'where', 'who', 'how many', 'count', 'find',
        'show', 'view', 'get', 'fetch', 'search', 'lookup', 'is',
        'delete', 'remove', 'rm', 'kill', 'stop', 'start',
    }
    
    @staticmethod
    def classify(user_input: str) -> tuple[TaskComplexity, str]:
        """
        Classify a task as SIMPLE or COMPLEX.
        
        Returns:
            (TaskComplexity, reasoning_string)
        """
        
        # Normalize input
        text = user_input.lower().strip()
        token_count = len(text.split())
        
        # Rule 1: Token count (heuristic)
        if token_count <= 10 and text.count(',') == 0 and text.count(';') == 0:
            # Short, single-thought input → likely simple
            score_simple = 1
        else:
            score_simple = 0
        
        # Rule 2: Complex keyword presence (strong signal)
        complex_matches = sum(1 for kw in TaskClassifier.COMPLEX_KEYWORDS 
                             if kw in text)
        if complex_matches >= 1:
            return (TaskComplexity.COMPLEX, 
                   f"Contains {complex_matches} complex keyword(s): {', '.join(kw for kw in TaskClassifier.COMPLEX_KEYWORDS if kw in text)[:50]}...")
        
        # Rule 3: Simple keyword presence
        simple_matches = sum(1 for kw in TaskClassifier.SIMPLE_KEYWORDS 
                            if kw in text)
        if simple_matches >= 2:
            return (TaskComplexity.SIMPLE,
                   f"Multiple simple keywords detected ({simple_matches})")
        
        # Rule 4: Multi-line or complex structure
        if '\n' in text or text.count('?') > 1 or text.count('&&') > 0:
            return (TaskComplexity.COMPLEX,
                   "Multi-line or chained query structure")
        
        # Rule 5: Code/command patterns
        if re.search(r'```|#!/|def |class |function |=>|const |let ', text):
            return (TaskComplexity.COMPLEX, "Code snippet detected")
        
        # Rule 6: Single word factual queries
        if token_count <= 3 and not any(kw in text for kw in 
                                        ['write', 'code', 'build', 'analyze']):
            return (TaskComplexity.SIMPLE, "Short factual query")
        
        # Default: When in doubt, go COMPLEX (safer)
        return (TaskComplexity.COMPLEX,
               "Ambiguous — defaulting to COMPLEX (safe default)")
    
    @staticmethod
    def get_model(complexity: TaskComplexity) -> str:
        """Return recommended model for complexity level."""
        return "anthropic/claude-haiku-4-5" if complexity == TaskComplexity.SIMPLE else "anthropic/claude-opus-4-0"
    
    @staticmethod
    def get_thinking(complexity: TaskComplexity) -> str:
        """Return recommended thinking level."""
        return "off" if complexity == TaskComplexity.SIMPLE else "medium"
    
    @staticmethod
    def get_context_level(complexity: TaskComplexity) -> str:
        """Return recommended context loading level."""
        return "minimal" if complexity == TaskComplexity.SIMPLE else "full"

def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: task-classifier.py '<user input>'")
        print("Example: task-classifier.py 'what is the weather?'")
        sys.exit(1)
    
    user_input = ' '.join(sys.argv[1:])
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
