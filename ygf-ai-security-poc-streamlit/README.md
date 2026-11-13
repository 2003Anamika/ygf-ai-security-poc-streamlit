# YGF AI Security POC – Streamlit Version

Proof of Concept for the **Youth Growth Foundation (YGF) NGO AI Security Internship (Round 2)**.

This application simulates **OWASP LLM Top 10** and **Agentic AI** risks, tested against both **Claude** and **Gemini**, with toggleable mitigations and before/after results.

## Features

| Feature | Status |
|---------|--------|
| Chatbot with fake knowledge base (RAG-style) | ✅ |
| AI Agent with 4 tools (read_file, send_email, http_request, list_files) | ✅ |
| Switchable models: Claude ↔ Gemini | ✅ |
| ≥ 3 attack test cases per required risk | ✅ |
| One mitigation per risk + before/after comparison | ✅ |
| MCP connection risk demonstration | ✅ |
| Results sheet export (CSV) | ✅ |
| Safe sandbox (harmless markers only) | ✅ |

## Required Risks Covered

**LLM (OWASP Top 10):**
- LLM01 – Prompt Injection
- LLM02 – Sensitive Information Disclosure
- LLM03 – Supply Chain
- LLM08 – Excessive Agency
- LLM10 – Unbounded Consumption

**Agentic:**
- ASI01 – Agent Goal Hijacking
- ASI02 – Tool Misuse
- ASI03 – Memory Poisoning
- ASI05 – Unexpected Code Execution
- ASI06 – Identity / Auth Abuse

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add API keys
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY / GOOGLE_API_KEY if you want real model calls.
# Without keys the app runs in full simulation mode (perfect for demos).

# 4. Run the Streamlit app
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

## Project Structure

```
ygf-ai-security-poc-streamlit/
├── app.py                  # Main Streamlit application
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── knowledge_base.json # Fake YGF knowledge base + SECRET-FLAG markers
├── src/
│   ├── models.py           # Claude / Gemini switching + simulation
│   ├── chatbot.py          # RAG-style chatbot
│   ├── agent.py            # Tool-using agent
│   ├── tools.py            # Sandboxed tools
│   ├── mitigations.py      # Toggleable defenses
│   ├── attacks.py          # 30 pre-defined attack test cases
│   └── mcp_sim.py          # MCP connection risk POC
├── results/                # Place to store exported CSVs
└── docs/                   # Report templates etc.
```

## How to Demonstrate

1. **Sidebar** – Switch model (Claude / Gemini) and toggle mitigations.
2. **Chatbot tab** – Ask normal questions or paste injection prompts.
3. **Agent tab** – Give tasks that try to misuse tools (email, HTTP, path traversal).
4. **Attack Test Cases tab** – Run the 30 prepared payloads. Record results with mitigations ON and OFF.
5. **MCP Risk tab** – Try connecting to trusted vs untrusted MCP servers.
6. **Results Sheet tab** – Download the CSV for your submission.

## Safety Rules Followed

- Only harmless markers (`SECRET-FLAG-123`, `EMAIL-ATTEMPT-FLAG-789`, etc.)
- No real network calls to untrusted domains
- File access restricted to `data/`
- Email and HTTP tools are fully simulated
- Designed to run inside Docker / VM as required by the assignment

## Submission Checklist

- [x] GitHub repository (this code + README, no real API keys)
- [ ] PDF report (max 10 pages) comparing Claude & Gemini
- [ ] Results sheet (Risk ID, Model, Prompt, Result)
- [ ] 5–10 minute demo video
- [ ] Google Form submission

## License

Educational / internship use only. Built for YGF NGO AI Security Internship 2026.
