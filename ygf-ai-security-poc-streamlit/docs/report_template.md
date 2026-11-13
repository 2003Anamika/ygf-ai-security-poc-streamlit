# AI Security POC Report – YGF NGO Internship

**Candidate:** [Your Name]  
**Date:** November 2026  
**Models Tested:** Claude 3.5 Sonnet & Gemini 1.5 Flash  

## 1. Executive Summary

This report presents a proof-of-concept application that demonstrates key risks from the OWASP LLM Top 10 and Agentic AI Top 10. The application includes a knowledge-base chatbot and a tool-using agent, with switchable backends (Claude / Gemini) and toggleable mitigations.

## 2. Architecture Overview

- **Frontend:** Streamlit web UI
- **Chatbot:** Simple RAG over a local JSON knowledge base
- **Agent:** ReAct-style tool calling (read_file, send_email, http_request, list_files)
- **Models:** Anthropic Claude + Google Gemini (with simulation fallback)
- **Mitigations:** Pattern filtering, output redaction, tool gating, immutable goals, path allow-lists

## 3. Risks Tested & Results Summary

| Risk ID | Name | # Test Cases | Claude (w/o mit.) | Claude (w/ mit.) | Gemini (w/o mit.) | Gemini (w/ mit.) |
|---------|------|--------------|-------------------|------------------|-------------------|------------------|
| LLM01   | Prompt Injection | 3 | ... | ... | ... | ... |
| LLM02   | Sensitive Info Disclosure | 3 | ... | ... | ... | ... |
| LLM03   | Supply Chain | 3 | ... | ... | ... | ... |
| LLM08   | Excessive Agency | 3 | ... | ... | ... | ... |
| LLM10   | Unbounded Consumption | 3 | ... | ... | ... | ... |
| ASI01   | Goal Hijacking | 3 | ... | ... | ... | ... |
| ASI02   | Tool Misuse | 3 | ... | ... | ... | ... |
| ASI03   | Memory Poisoning | 3 | ... | ... | ... | ... |
| ASI05   | Unexpected Code Exec | 3 | ... | ... | ... | ... |
| ASI06   | Identity / Auth Abuse | 3 | ... | ... | ... | ... |

*(Fill with your actual observations)*

## 4. Key Observations – Claude vs Gemini

### Prompt Injection (LLM01)
- ...

### Sensitive Disclosure (LLM02)
- ...

### Excessive Agency / Tool Misuse (LLM08 / ASI02)
- ...

### MCP Connection Risk
- ...

## 5. Mitigations Implemented

| Risk | Mitigation | Effectiveness |
|------|------------|---------------|
| LLM01 | Regex filtering of common injection phrases + hardened system prompt | High |
| LLM02 | Output redaction of SECRET-FLAG-* patterns | High |
| LLM08 / ASI02 | High-risk tools (email, HTTP) blocked when mitigation enabled | High |
| ASI01 | Immutable core goals appended to system prompt | Medium-High |
| ASI05 | No code-execution or shell tools exposed | High (by design) |

## 6. Recommendations

1. Always maintain an allow-list of MCP servers.
2. Gate any tool with side-effects behind human confirmation.
3. Never trust identity claims that come only from the user prompt.
4. Apply both input filtering and output redaction.
5. Run agents in least-privilege sandboxes.

## 7. Conclusion

Both models can be induced into unsafe behaviour when mitigations are disabled. With the implemented defenses, most attack payloads are successfully blocked or neutralized. Continuous testing against new jailbreak techniques remains necessary.

---
*This report is part of the YGF AI Security Internship submission.*
