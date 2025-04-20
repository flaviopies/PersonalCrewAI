import platform
import sys

# Monkey-patch SQLite antes de qualquer import de chromadb
if platform.system() != "Windows":
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import streamlit as st
from personal_crew.config import AGENT_CONFIGS
from personal_crew.crew import create_crew
from datetime import datetime
import re

# ─── Streamlit UI ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Personal CrewAI Assistant", page_icon="🤖", layout="wide")

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Personal CrewAI Assistant")
st.write("Bem‑vindo ao seu assistente pessoal!")

user_input = st.text_area("O que você gostaria de saber?", height=100)

def format_event_response(text: str) -> str:
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    parts = [p.strip() for p in re.split(r'\d+\.\s+', clean) if p.strip()]
    out = ""
    for p in parts:
        lines = p.split("\n")
        name = lines[0].strip()
        details = "\n".join(lines[1:]).strip()
        out += f"🎉 {name}\n   {details}\n\n"
    return out or text

formatted_response = None
result = None

if st.button("Submit Request") and user_input:
    try:
        with st.spinner("Buscando informações..."):
            crew = create_crew(user_input)
            result = crew.kickoff()
            if isinstance(result, dict) and result.get("tasks_output"):
                raw = getattr(result["tasks_output"][0], "raw", str(result))
                formatted_response = format_event_response(str(raw))
            else:
                formatted_response = str(result)
            st.session_state.messages += [
                {"role":"user", "content":user_input, "timestamp":datetime.now().isoformat()},
                {"role":"assistant", "content":formatted_response, "timestamp":datetime.now().isoformat()}
            ]
    except Exception as e:
        st.error(f"Erro: {e}")

st.header("💬 Chat History")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        ts = datetime.fromisoformat(msg["timestamp"])
        st.caption(ts.strftime("%Y-%m-%d %H:%M:%S"))

if formatted_response:
    st.header("📝 Current Response")
    st.write(formatted_response)
