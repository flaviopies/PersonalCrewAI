import os
import platform
import sys
from datetime import datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from crewai.tools import BaseTool

# ─── 1) Carregamento de chaves ────────────────────────────────────────────────
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    SERPER_API_KEY   = st.secrets["SERPER_API_KEY"]
else:
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não definido.")
if not SERPER_API_KEY:
    raise RuntimeError("❌ SERPER_API_KEY não definido.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ─── 2) Monkey-patch SQLite antes de chromadb ────────────────────────────────
if platform.system() != "Windows":
    try:
        import pysqlite3
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except ImportError:
        pass  # lembre-se de ter apt.txt com sqlite3 e libsqlite3-dev

# ─── 3) Ferramenta de Busca Web ──────────────────────────────────────────────
class WebSearchTool(BaseTool):
    # NÃO sobrescreva `name` ou `description` aqui sem anotação Pydantic.
    search: Optional[GoogleSerperAPIWrapper]

    def __init__(self):
        super().__init__()
        self.name = "Web Search"
        self.description = (
            "Busca em sites .br por informações atuais de eventos e notícias."
        )
        self.search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)

    def _run(self, query: str) -> str:
        try:
            ano = datetime.now().year
            temporal = f"{query} ({ano} OR {ano+1}) site:.br"
            resposta = self.search.run(temporal)
            if not resposta or "no results" in resposta.lower():
                return self.search.run(f"{query} site:.br")
            return resposta
        except Exception as e:
            return f"Erro na busca web: {e}"

search_tool = WebSearchTool()

# ─── 4) Configurações dos Agentes ───────────────────────────────────────────
AGENT_CONFIGS = {
    "manager": {
        "role": "Personal Assistant Manager",
        "goal": "Coordenar e delegar tarefas com informações precisas e atualizadas.",
        "backstory": "Você é um gerente experiente de assistentes pessoais...",
        "verbose": True,
        "allow_delegation": True,
        "tools": [search_tool],
    },
    "researcher": {
        "role": "Research Specialist",
        "goal": "Coletar e analisar informações atuais de fontes diversas.",
        "backstory": "Você é um pesquisador detalhista que valida fontes...",
        "verbose": True,
        "tools": [search_tool],
    },
    "planner": {
        "role": "Planning Specialist",
        "goal": "Organizar tarefas e cronogramas com dados precisos.",
        "backstory": "Você divide tarefas complexas em etapas gerenciáveis...",
        "verbose": True,
        "tools": [search_tool],
    },
}
