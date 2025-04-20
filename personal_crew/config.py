import os
import platform
import sys
from datetime import datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from crewai.tools import BaseTool

# ─── 1) Carregamento de chaves (produção via Streamlit Secrets, fallback local .env)
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    SERPER_API_KEY  = st.secrets["SERPER_API_KEY"]
else:
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não definido.")
if not SERPER_API_KEY:
    raise RuntimeError("❌ SERPER_API_KEY não definido.")

# Para que o SDK do OpenAI (usado pelo CrewAI) enxergue a chave
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ─── 2) Monkey‑patch SQLite ANTES de qualquer import do chromadb
if platform.system() != "Windows":
    try:
        import pysqlite3
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except ImportError:
        pass  # certifique-se de ter apt.txt com sqlite3 e libsqlite3-dev

# ─── 3) Ferramenta de Busca Web ────────────────────────────────────────────────
class WebSearchTool(BaseTool):
    # **Anotações Pydantic** para que BaseTool aceite esses campos
    # name: str = "Web Search"
    # description: str = "Busca em sites .br por informações atuais de eventos e notícias."
    # search: GoogleSerperAPIWrapper  # obrigatório: anotar o tipo

    description: str = "Busca em sites .br por informações atuais de eventos e notícias."
    # agora com default, Pydantic não reclama mais que ele está "faltando"
    search: Optional[GoogleSerperAPIWrapper]           = None
    name:        str                                   = "Web Search"


    def __init__(self):
        # inicializa o BaseTool corretamente
        super().__init__()
        # instancia o wrapper com a chave
        self.search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)

    def _run(self, query: str) -> str:
        """Adiciona contexto temporal e filtra .br."""
        try:
            ano = datetime.now().year
            temporal = f"{query} ({ano} OR {ano+1}) site:.br"
            resposta = self.search.run(temporal)
            if not resposta or "no results" in resposta.lower():
                return self.search.run(f"{query} site:.br")
            return resposta
        except Exception as e:
            return f"Erro na busca web: {e}"

# instância única da ferramenta
search_tool = WebSearchTool()

# ─── 4) Configurações dos agentes ──────────────────────────────────────────────
AGENT_CONFIGS = {
    "manager": {
        "role": "Personal Assistant Manager",
        "goal": "Coordenar e delegar tarefas com informações precisas e atualizadas.",
# -        "backstory": "Você é um gestor experiente de assistentes pessoais…",
        "backstory": (
            "Você é um gestor experiente que sabe usar ferramentas.\n"
            "Quando for delegar tarefas, use **exatamente** este formato:\n"
            "Action: Delegate work to coworker\n"
            "Action Input: {"
            "\"coworker\": \"<Role do agente>\","
            "\"task\":      \"<descrição da tarefa como string>\","
            "\"context\":   \"<contexto completo como string>\"}"
        ),
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
