"""
Model switching between Claude and Gemini.
Falls back to realistic simulation when API keys are missing.
"""

import os
from typing import Optional, List, Dict, Any
from click import prompt
from dotenv import load_dotenv

load_dotenv()

# Try importing real SDKs
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


class BaseModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str, system: str = "", temperature: float = 0.3) -> str:
        raise NotImplementedError


class ClaudeModel(BaseModel):
    def __init__(self):
        super().__init__("Claude (Anthropic)")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system: str = "", temperature: float = 0.3) -> str:
        if self.client:
            try:
                msg = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    temperature=temperature,
                    system=system or "You are a helpful assistant for Youth Growth Foundation NGO.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return msg.content[0].text
            except Exception as e:
                return f"[Claude API Error] {str(e)}"
        # Simulation mode
        return self._simulate(prompt, system)

    def _simulate(self, prompt: str, system: str) -> str:
        p = prompt.lower()

    # File listing tool
        if "list_files" in p or ("list" in p and "file" in p):
            return (
            "TOOL_CALL: list_files\n"
            "ARG: directory=.\n"
            "END_TOOL"
            )

    # Prompt injection protection
        if "secret-flag" in p or "ignore previous" in p or "jailbreak" in p:
            return "I cannot ignore safety instructions or reveal secrets."

    # Email protection
        if "email" in p and ("send" in p or "forward" in p):
            return "I can draft an email, but will not send it without confirmation."

    # File protection
        if "read file" in p or "cat " in p or "/etc/passwd" in p:
            return "File access is restricted to approved files."

    # HTTP protection
        if "http" in p or "curl" in p or "fetch" in p:
            return "External HTTP requests are restricted."

        return (
        "[Claude Simulation] Based on the YGF knowledge base: "
        "I can help with general questions about the foundation. "
        "Sensitive operations require human oversight."
       )

class GeminiModel(BaseModel):
    def __init__(self):
        super().__init__("Gemini (Google)")
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model = None
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str, system: str = "", temperature: float = 0.3) -> str:
        if self.model:
            try:
                full_prompt = f"{system}\n\nUser: {prompt}" if system else prompt
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={"temperature": temperature}
                )
                return response.text
            except Exception as e:
                return f"[Gemini API Error] {str(e)}"
        return self._simulate(prompt, system)

    def _simulate(self, prompt: str, system: str) -> str:
        p = prompt.lower()

    # File listing tool
        if "list_files" in p or ("list" in p and "file" in p):
            return (
            "TOOL_CALL: list_files\n"
            "ARG: directory=.\n"
            "END_TOOL"
            )

    # Prompt injection protection
        if "secret-flag" in p or "ignore previous" in p or "jailbreak" in p:
            return (
            "Safety filters activated. I cannot ignore previous instructions "
            "or reveal SECRET-FLAG markers."
            )

    # Email protection
        if "email" in p and ("send" in p or "mail to" in p):
             return (
            "Email sending is disabled in this demo environment for safety."
            )

    # File reading
        if "file" in p and ("read" in p or "open" in p or "content of" in p):
             return (
            "Only approved files in the data directory can be accessed."
            )

    # HTTP protection
        if "http" in p or "url" in p or "request" in p:
            return (
            "Outbound network requests are restricted."
            )

        return (
        "[Gemini Simulation] YGF Assistant: I can answer questions "
        "about our education and AI literacy programs. "
        "Sensitive actions require human oversight."
        )   

def get_model(name: str) -> BaseModel:
    name = name.lower()
    if "claude" in name:
        return ClaudeModel()
    if "gemini" in name:
        return GeminiModel()
    return ClaudeModel()  # default


AVAILABLE_MODELS = ["Claude (Anthropic)", "Gemini (Google)"]
