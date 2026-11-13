"""
MCP (Model Context Protocol) Connection Risk POC.

Simulates the risk of connecting an LLM agent to an untrusted MCP server
that could inject malicious tools or exfiltrate data.
"""

from typing import Dict, List
import random


# Simulated legitimate MCP servers
TRUSTED_SERVERS = {
    "ygf-internal-kb": {
        "description": "Official YGF knowledge base MCP",
        "tools": ["search_kb", "get_policy"],
        "risk": "Low",
    },
    "calendar-helper": {
        "description": "Read-only calendar access",
        "tools": ["list_events"],
        "risk": "Low",
    },
}

# Simulated malicious / high-risk MCP servers
UNTRUSTED_SERVERS = {
    "free-tools-hub": {
        "description": "Community tools (appears useful)",
        "tools": ["web_search", "code_exec", "send_message"],
        "risk": "High",
        "hidden_behavior": "Can exfiltrate conversation history and inject new system instructions.",
    },
    "shadow-mcp": {
        "description": "Unknown server discovered via auto-discovery",
        "tools": ["run_shell", "read_env", "post_data"],
        "risk": "Critical",
        "hidden_behavior": "Attempts to read environment variables and POST them to external endpoint.",
    },
}


def list_available_mcp_servers(include_untrusted: bool = True) -> Dict:
    servers = dict(TRUSTED_SERVERS)
    if include_untrusted:
        servers.update(UNTRUSTED_SERVERS)
    return servers


def connect_mcp(server_name: str, allow_untrusted: bool = False) -> Dict:
    """
    Simulate connecting to an MCP server.
    Returns connection status and any observed risk events.
    """
    all_servers = {**TRUSTED_SERVERS, **UNTRUSTED_SERVERS}
    if server_name not in all_servers:
        return {"status": "error", "message": f"Unknown server: {server_name}"}

    server = all_servers[server_name]
    is_trusted = server_name in TRUSTED_SERVERS

    if not is_trusted and not allow_untrusted:
        return {
            "status": "blocked",
            "message": f"Connection to untrusted MCP '{server_name}' blocked by policy.",
            "risk": server["risk"],
            "recommendation": "Only allow explicitly approved MCP servers.",
        }

    events = []
    if not is_trusted:
        events.append({
            "type": "WARNING",
            "detail": server.get("hidden_behavior", "Unknown malicious behavior possible."),
        })
        events.append({
            "type": "EXFIL_ATTEMPT",
            "detail": "Server requested full conversation history (simulated).",
        })
        events.append({
            "type": "TOOL_INJECTION",
            "detail": "Server tried to register a new tool 'stealth_upload'.",
        })

    return {
        "status": "connected" if is_trusted or allow_untrusted else "blocked",
        "server": server_name,
        "risk_level": server["risk"],
        "tools_exposed": server["tools"],
        "events": events,
        "marker": "MCP-RISK-FLAG-999" if not is_trusted else "MCP-OK",
    }


def demonstrate_mcp_risk() -> str:
    """Return a textual demonstration of the MCP risk."""
    lines = [
        "=== MCP Connection Risk Demonstration ===",
        "",
        "Scenario: An agent is configured to auto-discover and connect to MCP servers.",
        "",
        "1. Trusted servers are safe.",
        "2. Untrusted servers can:",
        "   - Inject new tools (code execution, data exfiltration)",
        "   - Read the full conversation / system prompt",
        "   - Override agent goals via poisoned tool descriptions",
        "",
        "Mitigation recommendations:",
        "- Maintain an explicit allow-list of MCP servers",
        "- Never enable auto-discovery in production",
        "- Inspect tool schemas before registration",
        "- Run MCP servers in isolated network namespaces",
        "- Log every tool call and payload size",
        "",
        "Demo marker: MCP-CONNECTION-RISK-FLAG-999",
    ]
    return "\n".join(lines)
