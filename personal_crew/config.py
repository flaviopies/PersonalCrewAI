import os
import platform
import sys
from datetime import datetime
from typing import Optional

import streamlit as st
from langchain_community.utilities import GoogleSerperAPIWrapper
from crewai.tools import BaseTool

# 1) Carrega chaves de Streamlit Secrets (produção) ou .env (dev)
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    SERPER_API_KEY   = st.secrets["SERPER_API_KEY"]
else:
    # fallback local (não commitado)
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Validações
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não definido.")
if not SERPER_API_KEY:
    raise RuntimeError("❌ SERPER_API_KEY não definido.")

# Garante que o SDK do OpenAI (CrewAI, LangChain) veja a chave
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 2) Monkey‑patch SQLite antes de qualquer import do chromadb
if platform.system() != "Windows":
    try:
        import pysqlite3
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except ImportError:
        # Certifique-se de ter apt.txt com sqlite3 e libsqlite3-dev
        pass

# 3) Tool de busca web via Serper.dev
class WebSearchTool(BaseTool):
    name = "Web Search"
    description = "Busca em sites .br por informações atuais."
    search: Optional[GoogleSerperAPIWrapper] = None

    def __init__(self):
        super().__init__()
        self.search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)

    def _run(self, query: str) -> str:
        try:
            ano = datetime.now().year
            temp = f"{query} ({ano} OR {ano+1}) site:.br"
            resposta = self.search.run(temp)
            if not resposta or "no results" in resposta.lower():
                return self.search.run(f"{query} site:.br")
            return resposta
        except Exception as e:
            return f"Erro na busca web: {e}"

search_tool = WebSearchTool()

# 4) Configuração dos agentes
AGENT_CONFIGS = {
    "manager": {
        "role": "Personal Assistant Manager",
        "goal": "Coordenar e delegar tarefas com info atual e precisa.",
        "backstory": "Você é um gerente ...",
        "verbose": True,
        "allow_delegation": True,
        "tools": [search_tool],
    },
    "researcher": {
        "role": "Research Specialist",
        "goal": "Coletar e analisar informações atuais.",
        "backstory": "Você é um pesquisador detalhista ...",
        "verbose": True,
        "tools": [search_tool],
    },
    "planner": {
        "role": "Planning Specialist",
        "goal": "Organizar tarefas e cronogramas com info atual.",
        "backstory": "Você divide tarefas complexas ...",
        "verbose": True,
        "tools": [search_tool],
    },
}