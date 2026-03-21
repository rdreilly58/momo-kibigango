#!/usr/bin/env python3
"""
Roblox Lua syntax validator - checks Lua 5.1 + Roblox extensions
"""

import os
import sys
import re
from pathlib import Path

# Roblox API keywords that are valid but not standard Lua
ROBLOX_KEYWORDS = {
    'game', 'workspace', 'script', 'Instance', 'Vector3', 'CFrame',
    'BrickColor', 'Color3', 'UDim2', 'UDim', 'Enum', 'Ray', 'Region3',
    'TweenInfo', 'NumberRange', 'NumberSequence', 'ColorSequence',
    'task', 'warn', 'wait', 'spawn', 'pcall', 'xpcall',
    'setmetatable', 'getmetatable', 'table', 'debug', 'string', 'math',
}

# Standard Lua 5.1 keywords
LUA_KEYWORDS = {
    'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
    'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat',
    'return', 'then', 'true', 'until', 'while',
}

ALL_KEYWORDS = LUA_KEYWORDS | ROBLOX_KEYWORDS

def check_file(filepath):
    """Check a single Lua file for obvious syntax errors"""
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        return [str(e)], []
    
    # Basic checks
    paren_count = 0
    bracket_count = 0
    brace_count = 0
    in_comment = False
    in_string = False
    string_char = None
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        if '--[[' in line:
            in_comment = True
        if ']]' in line:
            in_comment = False
            continue
        if in_comment:
            continue
        
        # Remove single-line comments
        if '--' in line:
            code_part = line[:line.index('--')]
        else:
            code_part = line
        
        # Check parentheses, brackets, braces
        for char in code_part:
            if char in ('"', "'"):
                if in_string and char == string_char:
                    in_string = False
                elif not in_string:
                    in_string = True
                    string_char = char
            elif not in_string:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count < 0:
                        errors.append(f"Line {i}: Mismatched parenthesis ')'")
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count < 0:
                        errors.append(f"Line {i}: Mismatched bracket ']'")
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count < 0:
                        errors.append(f"Line {i}: Mismatched brace '}}'")
        
        # Check for common issues
        stripped = code_part.strip()
        
        # Missing 'end' warning
        if stripped.startswith('if ') or stripped.startswith('for ') or \
           stripped.startswith('while ') or stripped.startswith('function '):
            # These should have matching 'end'
            pass
        
        # Empty if/for/while
        if re.match(r'^\s*(if|while|for|function)\s*\(\s*\)\s*then?', line):
            warnings.append(f"Line {i}: Empty condition")
    
    # Final balance checks
    if paren_count > 0:
        errors.append(f"Unmatched opening parenthesis (count: {paren_count})")
    elif paren_count < 0:
        errors.append(f"Unmatched closing parenthesis (count: {paren_count})")
    
    if bracket_count > 0:
        errors.append(f"Unmatched opening bracket (count: {bracket_count})")
    elif bracket_count < 0:
        errors.append(f"Unmatched closing bracket (count: {bracket_count})")
    
    if brace_count > 0:
        errors.append(f"Unmatched opening brace (count: {brace_count})")
    elif brace_count < 0:
        errors.append(f"Unmatched closing brace (count: {brace_count})")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: validate-lua-roblox.py <file_or_directory>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = list(path.glob("*.lua")) + list(path.glob("**/*.lua"))
    else:
        print(f"Error: {path} not found")
        sys.exit(1)
    
    total_errors = 0
    total_warnings = 0
    
    for filepath in sorted(files):
        errors, warnings = check_file(filepath)
        
        if errors or warnings:
            print(f"\n📄 {filepath}")
            
            if errors:
                print(f"  ✗ ERRORS ({len(errors)}):")
                for err in errors:
                    print(f"    - {err}")
                total_errors += len(errors)
            
            if warnings:
                print(f"  ⚠️  WARNINGS ({len(warnings)}):")
                for warn in warnings:
                    print(f"    - {warn}")
                total_warnings += len(warnings)
        else:
            print(f"✓ {filepath}")
    
    print(f"\n{'='*50}")
    print(f"Total: {len(files)} files, {total_errors} errors, {total_warnings} warnings")
    
    sys.exit(1 if total_errors > 0 else 0)

if __name__ == '__main__':
    main()
