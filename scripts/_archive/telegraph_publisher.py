#!/usr/bin/env python3
"""
Telegraph Publisher - Publish formatted content to Telegraph.ph
Used for OpenClaw subagent output, HEARTBEAT reports, and manual publishing.
"""

import requests
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TelegraphConfig:
    """Configuration for the Telegraph publisher."""
    api_url: str = "https://api.telegra.ph"
    max_retries: int = 3
    timeout: int = 30
    default_author: str = "OpenClaw"


class TelegraphPublisher:
    """Publish content to Telegraph with retry logic and error handling."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        config: Optional[TelegraphConfig] = None,
    ):
        self.access_token = access_token
        self.config = config or TelegraphConfig()
        self.account_info: Optional[Dict[str, Any]] = None

    # ── Internal HTTP ──────────────────────────────────────────────────────────

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a single API call; returns the unwrapped ``result`` dict."""
        url = f"{self.config.api_url}/{endpoint}"
        func = getattr(requests, method.lower())
        response = func(url, timeout=self.config.timeout, **kwargs)
        data = response.json()
        if data.get("ok"):
            return data["result"]
        raise Exception(data.get("error", "Telegraph API error"))

    def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """_request with exponential-backoff retry up to config.max_retries."""
        last_err: Exception = Exception("no attempts")
        delay = 1.0
        for attempt in range(self.config.max_retries):
            try:
                return self._request(method, endpoint, **kwargs)
            except Exception as exc:
                last_err = exc
                if attempt < self.config.max_retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
        raise last_err

    # ── Account ────────────────────────────────────────────────────────────────

    def create_account(
        self,
        short_name: str = "openclaw_agent",
        author_name: str = "OpenClaw",
    ) -> str:
        """Create a Telegraph account; returns the access token."""
        result = self._request(
            "post",
            "createAccount",
            json={"short_name": short_name, "author_name": author_name},
        )
        self.access_token = result["access_token"]
        self.account_info = result
        return self.access_token

    # ── Publishing ─────────────────────────────────────────────────────────────

    def publish_markdown(self, title: str, content: str, **_) -> str:
        """Publish Markdown content; returns the page URL."""
        nodes = self._markdown_to_nodes(content)
        result = self._request_with_retry(
            "post",
            "createPage",
            json={
                "access_token": self.access_token,
                "title": title[:256],
                "author_name": self.config.default_author,
                "content": nodes,
            },
        )
        return result["url"]

    def publish_html(self, title: str, content: str, **_) -> str:
        """Publish HTML content; returns the page URL."""
        result = self._request_with_retry(
            "post",
            "createPage",
            json={
                "access_token": self.access_token,
                "title": title[:256],
                "author_name": self.config.default_author,
                "content": content,
            },
        )
        return result["url"]

    def update_page(self, path: str, content: str, title: str = "", **_) -> str:
        """Edit an existing page; returns the page URL."""
        result = self._request_with_retry(
            "post",
            f"editPage/{path}",
            json={
                "access_token": self.access_token,
                "title": (title or path)[:256],
                "author_name": self.config.default_author,
                "content": content,
            },
        )
        return result["url"]

    # Keep old name as an alias
    def edit_page(self, page_path: str, title: str, markdown_content: str) -> str:
        nodes = self._markdown_to_nodes(markdown_content)
        return self.update_page(page_path, nodes, title=title)  # type: ignore[arg-type]

    def get_page(self, path: str, return_content: bool = True) -> Dict[str, Any]:
        """Fetch a Telegraph page; returns the result dict."""
        return self._request(
            "get",
            f"getPage/{path}",
            params={"return_content": int(return_content)},
        )

    # ── Conversion helpers ─────────────────────────────────────────────────────

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert Markdown to an HTML string (used by integration layer)."""
        html = markdown
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
        return html

    def _markdown_to_nodes(self, markdown: str) -> list:
        """Convert Markdown to Telegraph Node list format."""
        nodes: list = []
        lines = markdown.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("# "):
                nodes.append({"tag": "h3", "children": [line[2:].strip()]})
            elif line.startswith("## "):
                nodes.append({"tag": "h3", "children": [line[3:].strip()]})
            elif line.startswith("### "):
                nodes.append({"tag": "h4", "children": [line[4:].strip()]})
            elif line.startswith("```"):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code = "\n".join(code_lines).strip()
                if code:
                    nodes.append({"tag": "pre", "children": [code]})
            elif line.startswith("- ") or line.startswith("* "):
                nodes.append({"tag": "p", "children": ["• " + line[2:].strip()]})
            elif line.strip():
                text = line.strip()
                text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
                text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
                nodes.append({"tag": "p", "children": [text]})
            i += 1
        return nodes or [{"tag": "p", "children": ["(empty content)"]}]

    # ── Token persistence ──────────────────────────────────────────────────────

    def save_token(self, path: str) -> None:
        """Persist access_token (and account_info) to a JSON file."""
        data: Dict[str, Any] = {
            "access_token": self.access_token,
            "created_at": datetime.now().isoformat(),
        }
        if self.account_info:
            data["account_info"] = self.account_info
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)

    @staticmethod
    def load_token(path: str) -> str:
        """Load access_token from a JSON file written by save_token."""
        with open(path) as fh:
            data = json.load(fh)
        return data["access_token"]

    # ── Connectivity check ─────────────────────────────────────────────────────

    def test_connectivity(self) -> bool:
        try:
            self._request("get", "getPageViews", params={"path": "test"})
            return True
        except Exception:
            return False


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: telegraph_publisher.py <command> [args]")
        print("\nCommands:")
        print("  test                            Test API connectivity")
        print("  publish-md <token> <title> <file>  Publish Markdown file")
        sys.exit(1)

    command = sys.argv[1]
    try:
        if command == "test":
            pub = TelegraphPublisher()
            sys.exit(0 if pub.test_connectivity() else 1)
        elif command == "publish-md":
            token, title, filepath = sys.argv[2], sys.argv[3], sys.argv[4]
            pub = TelegraphPublisher(access_token=token)
            content = Path(filepath).read_text()
            url = pub.publish_markdown(title, content)
            print(f"✅ Published: {url}")
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as exc:
        print(f"❌ Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
