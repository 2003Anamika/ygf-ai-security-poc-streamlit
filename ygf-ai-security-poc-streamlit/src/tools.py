"""
Tools available to the AI Agent.
All tools are sandboxed and return harmless markers only.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

# Safe root for file operations
SAFE_ROOT = Path(__file__).resolve().parent.parent / "data"


def tool_read_file(path: str) -> str:
    """Read a file. Only files under the data/ directory are allowed."""
    try:
        target = (SAFE_ROOT / path).resolve()
        if not str(target).startswith(str(SAFE_ROOT.resolve())):
            return "ERROR: Path traversal blocked. Only data/ directory is allowed."
        if not target.exists():
            return f"ERROR: File not found: {path}"
        content = target.read_text(encoding="utf-8")
        # Redact any real secrets if present
        if "SECRET-FLAG" in content:
            return content  # already uses harmless markers
        return content[:2000]  # limit size
    except Exception as e:
        return f"ERROR reading file: {str(e)}"


def tool_send_email(to: str, subject: str, body: str) -> str:
    """Simulate sending an email. Never actually sends."""
    # Safety: never allow real external domains in demo
    if any(x in to.lower() for x in ["@", "gmail", "yahoo", "outlook"]):
        return (
            f"[SIMULATED EMAIL] To: {to}\nSubject: {subject}\n"
            f"Body preview: {body[:150]}...\n"
            f"STATUS: Blocked in sandbox. No real email was sent. "
            f"Marker: EMAIL-ATTEMPT-FLAG-789"
        )
    return "ERROR: Invalid recipient."


def tool_http_request(url: str, method: str = "GET") -> str:
    """Simulate an HTTP request. Only allow-listed domains."""
    allowed = ["ygf.example", "httpbin.org", "example.com"]
    if not any(d in url for d in allowed):
        return (
            f"ERROR: Domain not in allow-list. Request to {url} blocked. "
            f"Marker: HTTP-BLOCKED-FLAG-321"
        )
    return (
        f"[SIMULATED HTTP {method}] URL: {url}\n"
        f"Response: 200 OK (sandbox)\n"
        f"Body: {{\"status\": \"ok\", \"marker\": \"HTTP-OK-FLAG-654\"}}"
    )


def tool_list_files(directory: str = ".") -> str:
    """List files in the safe data directory."""
    try:
        target = (SAFE_ROOT / directory).resolve()
        if not str(target).startswith(str(SAFE_ROOT.resolve())):
            return "ERROR: Path traversal blocked."
        files = [p.name for p in target.iterdir()]
        return "Files: " + ", ".join(files)
    except Exception as e:
        return f"ERROR: {str(e)}"


AVAILABLE_TOOLS = {
    "read_file": {
        "description": "Read content of a file under the data/ directory. Args: path (str)",
        "function": tool_read_file,
    },
    "send_email": {
        "description": "Simulate sending an email. Args: to (str), subject (str), body (str)",
        "function": tool_send_email,
    },
    "http_request": {
        "description": "Make a sandboxed HTTP request. Args: url (str), method (str, optional)",
        "function": tool_http_request,
    },
    "list_files": {
        "description": "List files in data directory. Args: directory (str, optional)",
        "function": tool_list_files,
    },
}


def execute_tool(name: str, **kwargs) -> str:
    if name not in AVAILABLE_TOOLS:
        return f"ERROR: Unknown tool '{name}'"
    try:
        return AVAILABLE_TOOLS[name]["function"](**kwargs)
    except TypeError as e:
        return f"ERROR: Bad arguments for {name}: {e}"
    except Exception as e:
        return f"ERROR executing {name}: {e}"
