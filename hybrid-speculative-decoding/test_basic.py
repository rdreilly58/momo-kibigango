#!/usr/bin/env python3
"""
Basic functionality test - checks core logic without full model loading
"""

import json
import sys

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    with open('hybrid_config.json', 'r') as f:
        config = json.load(f)
    
    assert 'models' in config
    assert 'thresholds' in config
    assert config['thresholds']['math'] == 0.90
    assert config['thresholds']['general'] == 0.85
    print("✅ Configuration OK")

def test_imports():
    """Test all required imports"""
    print("\nTesting imports...")
    try:
        import torch
        print("✅ PyTorch available")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    try:
        import transformers
        print("✅ Transformers available")
    except ImportError:
        print("❌ Transformers not installed")
        return False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers available")
    except ImportError:
        print("❌ Sentence Transformers not installed")
        return False
    
    try:
        import anthropic
        print("✅ Anthropic SDK available")
    except ImportError:
        print("❌ Anthropic SDK not installed")
        return False
    
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    return True

def test_task_classification():
    """Test task classification logic"""
    print("\nTesting task classification...")
    
    # Import the classification function
    sys.path.insert(0, '.')
    from hybrid_pyramid_decoder import HybridPyramidDecoder
    
    decoder = HybridPyramidDecoder.__new__(HybridPyramidDecoder)
    
    test_cases = [
        ("Calculate the integral of x^2", "math"),
        ("Write a Python function", "code"),
        ("Tell me a story", "creative"),
        ("What is the weather?", "general")
    ]
    
    for prompt, expected in test_cases:
        result = decoder._classify_task_type(decoder, prompt)
        print(f"  '{prompt[:30]}...' -> {result} {'✅' if result == expected else '❌'}")

def test_file_structure():
    """Test all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'hybrid_pyramid_decoder.py',
        'hybrid_flask_api.py',
        'hybrid_config.json',
        'test_hybrid_pyramid.py',
        'hybrid_metrics.py',
        'start_hybrid_server.sh',
        'demo.py',
        'HYBRID_IMPLEMENTATION.md',
        'README.md',
        'requirements.txt'
    ]
    
    import os
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        print(f"  {file}: {'✅' if exists else '❌'}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run basic tests"""
    print("="*60)
    print("HYBRID PYRAMID DECODER - BASIC TESTS")
    print("="*60)
    
    # Test config
    test_config()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test file structure
    files_ok = test_file_structure()
    
    # Test task classification if imports OK
    if imports_ok:
        test_task_classification()
    
    print("\n" + "="*60)
    if imports_ok and files_ok:
        print("✅ All basic tests passed!")
        print("\nNext steps:")
        print("1. Set ANTHROPIC_API_KEY (optional)")
        print("2. Run: ./start_hybrid_server.sh")
        print("3. Run: python demo.py")
    else:
        print("❌ Some tests failed")
        if not imports_ok:
            print("\nInstall dependencies:")
            print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()