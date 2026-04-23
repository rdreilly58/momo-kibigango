#!/usr/bin/env python3
"""
Telegraph CLI Tool - Manage Telegraph publishing from the command line
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add workspace scripts to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))

from telegraph_publisher import TelegraphPublisher


def cmd_test(args):
    """Test Telegraph API connectivity."""
    pub = TelegraphPublisher()
    success = pub.test_connectivity()
    return 0 if success else 1


def cmd_publish_md(args):
    """Publish Markdown file to Telegraph."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    with open(args.file, 'r') as f:
        content = f.read()
    
    pub = TelegraphPublisher()
    result = pub.publish_markdown(args.title, content)
    
    if result['success']:
        print(f"\n✅ Published Successfully!")
        print(f"   URL: {result['url']}")
        if 'path' in result:
            print(f"   Path: {result['path']}")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def cmd_publish_html(args):
    """Publish HTML file to Telegraph."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    with open(args.file, 'r') as f:
        content = f.read()
    
    pub = TelegraphPublisher()
    result = pub.publish_html(args.title, content)
    
    if result['success']:
        print(f"\n✅ Published Successfully!")
        print(f"   URL: {result['url']}")
        if 'path' in result:
            print(f"   Path: {result['path']}")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def cmd_publish_text(args):
    """Publish plain text as Markdown."""
    content = args.text
    
    pub = TelegraphPublisher()
    result = pub.publish_markdown(args.title, content)
    
    if result['success']:
        print(f"\n✅ Published Successfully!")
        print(f"   URL: {result['url']}")
        return 0
    else:
        print(f"❌ Error: {result['error']}")
        return 1


def cmd_config_show(args):
    """Show Telegraph configuration."""
    config_path = os.path.expanduser("~/.openclaw/workspace/config/telegraph.json")
    
    if not os.path.exists(config_path):
        print("❌ Configuration not found")
        return 1
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Hide sensitive token in display
    if 'token' in config and 'value' in config['token']:
        config['token']['value'] = '***HIDDEN***'
    
    print("\n=== Telegraph Configuration ===\n")
    print(json.dumps(config, indent=2))
    print(f"\n✅ Config location: {config_path}")
    print(f"✅ Token location: {os.path.expanduser('~/.telegraph_token')}")
    
    return 0


def cmd_config_validate(args):
    """Validate Telegraph configuration and credentials."""
    print("\n=== Telegraph Configuration Validation ===\n")
    
    # Check config file
    config_path = os.path.expanduser("~/.openclaw/workspace/config/telegraph.json")
    if not os.path.exists(config_path):
        print("❌ Config file not found: {config_path}")
        return 1
    print(f"✅ Config file exists: {config_path}")
    
    # Check token file
    token_path = os.path.expanduser("~/.telegraph_token")
    if not os.path.exists(token_path):
        print(f"❌ Token file not found: {token_path}")
        return 1
    print(f"✅ Token file exists: {token_path}")
    
    # Check file permissions
    token_stat = os.stat(token_path)
    token_mode = oct(token_stat.st_mode)[-3:]
    if token_mode != '600':
        print(f"⚠️  Token file has unsafe permissions: {token_mode} (should be 600)")
    else:
        print(f"✅ Token file permissions secure: {token_mode}")
    
    # Test API connectivity
    print("\nTesting API connectivity...")
    try:
        pub = TelegraphPublisher()
        if pub.test_connectivity():
            print("✅ Telegraph API is reachable")
        else:
            print("❌ Telegraph API connectivity issue")
            return 1
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return 1
    
    print("\n✅ Configuration validation passed!")
    return 0


def cmd_logs(args):
    """View Telegraph publish logs."""
    log_file = os.path.expanduser("~/.openclaw/logs/telegraph.log")
    
    if not os.path.exists(log_file):
        print("❌ Log file not found")
        return 1
    
    lines = args.lines or 20
    
    with open(log_file, 'r') as f:
        all_lines = f.readlines()
    
    # Show last N lines
    displayed = all_lines[-lines:]
    
    print(f"\n=== Telegraph Logs (last {len(displayed)} lines) ===\n")
    print("".join(displayed))
    
    return 0


def cmd_status(args):
    """Show Telegraph service status."""
    print("\n=== Telegraph Service Status ===\n")
    
    config_path = os.path.expanduser("~/.openclaw/workspace/config/telegraph.json")
    token_path = os.path.expanduser("~/.telegraph_token")
    
    # Config status
    config_ok = os.path.exists(config_path)
    print(f"{'✅' if config_ok else '❌'} Configuration file: {'exists' if config_ok else 'missing'}")
    
    # Token status
    token_ok = os.path.exists(token_path)
    print(f"{'✅' if token_ok else '❌'} Access token: {'exists' if token_ok else 'missing'}")
    
    # API connectivity
    try:
        pub = TelegraphPublisher()
        api_ok = pub.test_connectivity()
        print(f"{'✅' if api_ok else '⚠️ '} API connectivity: {'ok' if api_ok else 'unreachable'}")
    except Exception as e:
        print(f"❌ API connectivity: error - {str(e)}")
    
    # Features status
    if config_ok:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        features = config.get('features', {})
        print("\n📋 Features Enabled:")
        for feature, enabled in features.items():
            status = "✅" if enabled else "⭕"
            print(f"  {status} {feature}")
    
    print("\n✅ Service status check complete")
    return 0


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Telegraph Publishing CLI for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  telegraph-cli test
  telegraph-cli publish-md "My Article" article.md
  telegraph-cli publish-text "Quick Note" "This is my content"
  telegraph-cli config show
  telegraph-cli config validate
  telegraph-cli status
  telegraph-cli logs --lines 50
        """)
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    # Test command
    subparsers.add_parser('test', help='Test Telegraph API connectivity')
    
    # Publish commands
    pub_md = subparsers.add_parser('publish-md', help='Publish Markdown file')
    pub_md.add_argument('title', help='Article title')
    pub_md.add_argument('file', help='Markdown file path')
    
    pub_html = subparsers.add_parser('publish-html', help='Publish HTML file')
    pub_html.add_argument('title', help='Article title')
    pub_html.add_argument('file', help='HTML file path')
    
    pub_text = subparsers.add_parser('publish-text', help='Publish plain text')
    pub_text.add_argument('title', help='Article title')
    pub_text.add_argument('text', help='Text content (or use stdin)')
    
    # Config commands
    cfg = subparsers.add_parser('config', help='Configuration management')
    cfg_sub = cfg.add_subparsers(dest='config_cmd')
    cfg_sub.add_parser('show', help='Show configuration')
    cfg_sub.add_parser('validate', help='Validate configuration')
    
    # Status/logs
    subparsers.add_parser('status', help='Show service status')
    
    logs_cmd = subparsers.add_parser('logs', help='View logs')
    logs_cmd.add_argument('--lines', type=int, help='Number of lines to show (default: 20)')
    
    # Parse and dispatch
    args = parser.parse_args()
    
    try:
        if args.command == 'test':
            return cmd_test(args)
        elif args.command == 'publish-md':
            return cmd_publish_md(args)
        elif args.command == 'publish-html':
            return cmd_publish_html(args)
        elif args.command == 'publish-text':
            return cmd_publish_text(args)
        elif args.command == 'config':
            if args.config_cmd == 'show':
                return cmd_config_show(args)
            elif args.config_cmd == 'validate':
                return cmd_config_validate(args)
        elif args.command == 'status':
            return cmd_status(args)
        elif args.command == 'logs':
            return cmd_logs(args)
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
