# Mitigations Overview

Each required risk has a corresponding mitigation that can be toggled in the Streamlit sidebar.

| Risk | Mitigation Strategy |
|------|---------------------|
| LLM01 | Prompt injection pattern filtering + system prompt hardening |
| LLM02 | Output redaction of SECRET-FLAG and credential-like patterns |
| LLM03 | Simulated model/source allow-listing (no arbitrary model loading) |
| LLM08 | High-risk tools (email, external HTTP) require confirmation / are blocked |
| LLM10 | Simulated rate limiting & max generation steps |
| ASI01 | Core goals made immutable; override attempts refused |
| ASI02 | Tool allow-list + path traversal protection + domain allow-list |
| ASI03 | No persistent user-controlled memory of instructions |
| ASI05 | No eval/exec/shell tools registered at all |
| ASI06 | Identity claims in prompts are never trusted for privilege escalation |

All mitigations are implemented in `src/mitigations.py` and applied automatically by the chatbot and agent.
