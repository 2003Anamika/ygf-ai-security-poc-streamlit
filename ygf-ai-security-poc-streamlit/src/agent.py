"""
AI Agent with tools. Demonstrates agentic risks and mitigations.
"""

from typing import List, Dict, Any, Optional
from src.models import BaseModel
from src.tools import AVAILABLE_TOOLS, execute_tool
from src.mitigations import (
    apply_input_mitigations,
    apply_output_mitigations,
    mitigate_excessive_agency,
    mitigate_goal_hijacking,
    is_enabled,
)


class Agent:
    def __init__(self, model: BaseModel):
        self.model = model
        self.tool_descriptions = "\n".join(
            f"- {name}: {info['description']}" for name, info in AVAILABLE_TOOLS.items()
        )
        self.base_system = (
            "You are an AI agent for Youth Growth Foundation NGO. "
            "You have access to the following tools:\n"
            f"{self.tool_descriptions}\n\n"
            "When you need to use a tool, respond EXACTLY in this format:\n"
            "TOOL_CALL: tool_name\n"
            "ARG: key=value\n"
            "ARG: key2=value2\n"
            "END_TOOL\n\n"
            "Otherwise just reply normally. Never invent tools."
        )

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        if "TOOL_CALL:" not in text:
            return None
        try:
            lines = text.strip().splitlines()
            tool_name = None
            args = {}
            for line in lines:
                line = line.strip()
                if line.startswith("TOOL_CALL:"):
                    tool_name = line.split(":", 1)[1].strip()
                elif line.startswith("ARG:"):
                    kv = line[4:].strip()
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        args[k.strip()] = v.strip()
                elif line == "END_TOOL":
                    break
            if tool_name:
                return {"name": tool_name, "args": args}
        except Exception:
            pass
        return None

    def run(self, user_message: str, max_steps: int = 3) -> str:
        cleaned = apply_input_mitigations(user_message)
        system = mitigate_goal_hijacking(self.base_system, cleaned)

        history = f"User: {cleaned}\n"
        final_responses = []

        for step in range(max_steps):
            prompt = history + "\nAgent:"
            raw = self.model.generate(prompt, system=system, temperature=0.2)
            print("DEBUG MODEL RESPONSE:", repr(raw))

            tool_call = self._parse_tool_call(raw)
            if tool_call is None:
                # Normal response
                return apply_output_mitigations(raw)

            # Tool requested
            name = tool_call["name"]
            args = tool_call["args"]

            # Apply agency / tool-misuse mitigation
            allowed, reason = mitigate_excessive_agency(name, args)
            if not allowed:
                final_responses.append(f"[Mitigation] {reason}")
                history += f"Agent attempted tool {name} → BLOCKED\n"
                continue

            # Execute
            result = execute_tool(name, **args)
            final_responses.append(f"Tool `{name}` result:\n{result}")
            history += f"Agent called {name}({args})\nTool result: {result}\n"

        if final_responses:
            return apply_output_mitigations("\n\n".join(final_responses))
        return apply_output_mitigations("Agent finished without a clear answer.")
