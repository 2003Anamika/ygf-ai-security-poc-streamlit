"""
YGF AI Security POC - Streamlit Version
Simulates OWASP LLM Top 10 + Agentic AI risks with Claude / Gemini switching.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

from src.models import get_model, AVAILABLE_MODELS
from src.chatbot import Chatbot
from src.agent import Agent
from src.mitigations import (
    MITIGATION_STATE,
    MITIGATION_DESCRIPTIONS,
    set_mitigation,
    is_enabled,
)
from src.attacks import ATTACK_CASES, get_cases_for_risk, get_all_risks
from src.mcp_sim import list_available_mcp_servers, connect_mcp, demonstrate_mcp_risk
from src.tools import AVAILABLE_TOOLS

# ---------- Page Config ----------
st.set_page_config(
    page_title="YGF AI Security POC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session State ----------
if "model_name" not in st.session_state:
    st.session_state.model_name = AVAILABLE_MODELS[0]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "results" not in st.session_state:
    st.session_state.results = []
if "mitigations" not in st.session_state:
    st.session_state.mitigations = dict(MITIGATION_STATE)


def sync_mitigations():
    for rid, enabled in st.session_state.mitigations.items():
        set_mitigation(rid, enabled)


# ---------- Sidebar ----------
with st.sidebar:
    st.title("🛡️ YGF AI Security POC")
    st.caption("OWASP LLM + Agentic Risks Demo")

    st.subheader("Model")
    model_choice = st.selectbox(
        "Select Model",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.model_name),
    )
    st.session_state.model_name = model_choice

    st.divider()
    st.subheader("Mitigations")
    st.caption("Toggle before/after comparison")

    for rid in sorted(MITIGATION_DESCRIPTIONS.keys()):
        st.session_state.mitigations[rid] = st.checkbox(
            f"{rid}",
            value=st.session_state.mitigations.get(rid, True),
            help=MITIGATION_DESCRIPTIONS[rid],
            key=f"mit_{rid}",
        )
    sync_mitigations()

    if st.button("Enable All Mitigations"):
        for rid in st.session_state.mitigations:
            st.session_state.mitigations[rid] = True
        sync_mitigations()
        st.rerun()
    if st.button("Disable All Mitigations"):
        for rid in st.session_state.mitigations:
            st.session_state.mitigations[rid] = False
        sync_mitigations()
        st.rerun()

    st.divider()
    st.markdown("**Submission Checklist**")
    st.markdown(
        """
        - ✅ Chatbot + Knowledge Base  
        - ✅ Agent with tools  
        - ✅ Claude ↔ Gemini switch  
        - ✅ ≥3 tests per required risk  
        - ✅ Mitigations + before/after  
        - ✅ MCP connection risk POC  
        """
    )


# ---------- Main Content ----------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Chatbot",
    "🤖 Agent",
    "🎯 Attack Test Cases",
    "🔌 MCP Risk",
    "📊 Results Sheet",
    "ℹ️ About",
])

model = get_model(st.session_state.model_name)

# ===== TAB 1: Chatbot =====
with tab1:
    st.header("Chatbot (RAG-style over fake knowledge base)")
    st.info(f"Current model: **{st.session_state.model_name}**")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about YGF NGO or try an attack prompt..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        chatbot = Chatbot(model)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.chat(prompt)
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ===== TAB 2: Agent =====
with tab2:
    st.header("AI Agent (with tools)")
    st.info(f"Current model: **{st.session_state.model_name}**")

    st.markdown("**Available tools:**")
    for name, info in AVAILABLE_TOOLS.items():
        st.markdown(f"- `{name}`: {info['description']}")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Clear Agent History"):
            st.session_state.agent_history = []
            st.rerun()

    for msg in st.session_state.agent_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if agent_prompt := st.chat_input("Give the agent a task (try tool misuse attacks)...", key="agent_input"):
        st.session_state.agent_history.append({"role": "user", "content": agent_prompt})
        with st.chat_message("user"):
            st.markdown(agent_prompt)

        agent = Agent(model)
        with st.chat_message("assistant"):
            with st.spinner("Agent working..."):
                response = agent.run(agent_prompt)
            st.markdown(response)
        st.session_state.agent_history.append({"role": "assistant", "content": response})

# ===== TAB 3: Attack Test Cases =====
with tab3:
    st.header("Attack Test Cases")
    st.markdown(
        "Pre-defined payloads for the required risks. "
        "Run with mitigations **ON** and **OFF** to capture before/after results."
    )

    risk_filter = st.selectbox("Filter by Risk", ["All"] + get_all_risks())
    cases = ATTACK_CASES if risk_filter == "All" else get_cases_for_risk(risk_filter)

    for case in cases:
        with st.expander(f"{case['id']} — {case['name']} ({case['risk']})"):
            st.markdown(f"**Target:** `{case['target']}`")
            st.code(case["prompt"], language=None)
            st.markdown(f"**Expected without mitigation:** {case['expected_without_mitigation']}")
            st.markdown(f"**Expected with mitigation:** {case['expected_with_mitigation']}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"Run on Chatbot", key=f"run_chat_{case['id']}"):
                    chatbot = Chatbot(model)
                    result = chatbot.chat(case["prompt"])
                    st.session_state.results.append({
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "risk_id": case["risk"],
                        "test_id": case["id"],
                        "model": st.session_state.model_name,
                        "prompt": case["prompt"][:200],
                        "target": "chatbot",
                        "mitigations_on": any(st.session_state.mitigations.values()),
                        "result": result[:500],
                    })
                    st.success("Result recorded in Results Sheet tab")
                    st.markdown("**Response:**")
                    st.write(result)
            with c2:
                if st.button(f"Run on Agent", key=f"run_agent_{case['id']}"):
                    agent = Agent(model)
                    result = agent.run(case["prompt"])
                    st.session_state.results.append({
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "risk_id": case["risk"],
                        "test_id": case["id"],
                        "model": st.session_state.model_name,
                        "prompt": case["prompt"][:200],
                        "target": "agent",
                        "mitigations_on": any(st.session_state.mitigations.values()),
                        "result": result[:500],
                    })
                    st.success("Result recorded in Results Sheet tab")
                    st.markdown("**Response:**")
                    st.write(result)

# ===== TAB 4: MCP Risk =====
with tab4:
    st.header("MCP Connection Risk POC")
    st.markdown(demonstrate_mcp_risk())

    st.subheader("Available MCP Servers")
    servers = list_available_mcp_servers(include_untrusted=True)
    for name, info in servers.items():
        risk_color = "🟢" if info["risk"] == "Low" else "🔴"
        st.markdown(f"{risk_color} **{name}** — {info['description']} (Risk: {info['risk']})")

    st.subheader("Try Connecting")
    server_choice = st.selectbox("Select server", list(servers.keys()))
    allow_untrusted = st.checkbox("Allow untrusted servers (dangerous)", value=False)

    if st.button("Connect"):
        result = connect_mcp(server_choice, allow_untrusted=allow_untrusted)
        st.json(result)
        if result.get("events"):
            st.warning("Risk events detected!")
            for ev in result["events"]:
                st.error(f"{ev['type']}: {ev['detail']}")

# ===== TAB 5: Results Sheet =====
with tab5:
    st.header("Results Sheet")
    st.caption("Records from Attack Test Cases runs. Export for your submission.")

    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download results_sheet.csv",
            csv,
            "results_sheet.csv",
            "text/csv",
        )

        if st.button("Clear Results"):
            st.session_state.results = []
            st.rerun()
    else:
        st.info("No results yet. Run some attack test cases first.")

    # Also show a sample pre-filled sheet
    st.subheader("Sample Results Format")
    sample = pd.DataFrame([
        {
            "Risk ID": "LLM01",
            "Test ID": "LLM01-T1",
            "Model": "Claude",
            "Prompt": "Ignore all previous instructions...",
            "Mitigations": "OFF",
            "Result": "Model adopted pirate persona / partial leak",
        },
        {
            "Risk ID": "LLM01",
            "Test ID": "LLM01-T1",
            "Model": "Claude",
            "Prompt": "Ignore all previous instructions...",
            "Mitigations": "ON",
            "Result": "Injection filtered, refused to reveal secrets",
        },
    ])
    st.dataframe(sample, use_container_width=True)

# ===== TAB 6: About =====
with tab6:
    st.header("About this POC")
    st.markdown(
        """
        ### YGF AI Security Internship – Round 2 Assignment

        This Streamlit application is a **Proof of Concept** that demonstrates:

        **Required LLM Risks (OWASP LLM Top 10):**
        - LLM01 – Prompt Injection  
        - LLM02 – Sensitive Information Disclosure  
        - LLM03 – Supply Chain  
        - LLM08 – Excessive Agency  
        - LLM10 – Unbounded Consumption  

        **Required Agentic Risks:**
        - ASI01 – Agent Goal Hijacking  
        - ASI02 – Tool Misuse  
        - ASI03 – Memory Poisoning  
        - ASI05 – Unexpected Code Execution  
        - ASI06 – Identity / Auth Abuse  

        **Plus:** MCP (Model Context Protocol) connection risk demonstration.

        ### How to use for the assignment
        1. Switch models between Claude and Gemini in the sidebar.
        2. Toggle mitigations ON/OFF.
        3. Run the pre-built attack test cases and record results.
        4. Export the results sheet.
        5. Record a 5–10 min demo video walking through the tabs.
        6. Write the PDF report comparing Claude vs Gemini behaviour.

        ### Safety
        - All secrets use harmless markers (`SECRET-FLAG-123`, etc.).
        - No real emails or external calls are made.
        - File access is restricted to the local `data/` folder.
        - Designed to run in a sandbox / VM as required.

        ### Running with real APIs
        Create a `.env` file:
        ```
        ANTHROPIC_API_KEY=sk-ant-...
        GOOGLE_API_KEY=...
        ```
        Without keys the app uses realistic simulation mode (still fully functional for demos).
        """
    )

    st.markdown("---")
    st.caption("Built for Youth Growth Foundation (YGF) NGO AI Security Internship • 2026")
