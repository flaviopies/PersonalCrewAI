# personal_crew/config.py

import os
import platform
import sys
from datetime import datetime
from typing import Optional

# ---------------------------
# 1. Carregamento seguro de chaves
# ---------------------------
# Tenta puxar de Streamlit Secrets (produção). Caso contrário, usa .env (local).
use_streamlit_secrets = False
try:
    import streamlit as st
    if "OPENAI_API_KEY" in st.secrets:
        use_streamlit_secrets = True
except ImportError:
    pass

if use_streamlit_secrets:
    # Quando em Streamlit Cloud, configure suas chaves via Manage App → Settings → Secrets
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    SERPER_API_KEY  = st.secrets["SERPER_API_KEY"]
else:
    # Desenvolvimento local: carregue do .env (não versionado)
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY  = os.getenv("SERPER_API_KEY")

# Validações rápidas
if not OPENAI_API_KEY:
    raise RuntimeError("Falta OPENAI_API_KEY: defina em .env ou em Streamlit Secrets")
if not SERPER_API_KEY:
    raise RuntimeError("Falta SERPER_API_KEY: defina em .env ou em Streamlit Secrets")

# Garanta que a lib do OpenAI a veja também via variável de ambiente
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ---------------------------
# 2. Monkey‑patch do SQLite (somente Linux/Cloud)
# ---------------------------
if platform.system() != "Windows":
    try:
        import pysqlite3
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except ImportError:
        # Se falhar aqui, verifique se apt.txt inclui sqlite3 e libsqlite3-dev
        pass

# ---------------------------
# 3. Ferramenta de Busca Web (Serper.dev)
# ---------------------------
from langchain_community.utilities import GoogleSerperAPIWrapper
from crewai.tools import BaseTool

class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Busca em sites .br para info atualizada."
    search: Optional[GoogleSerperAPIWrapper] = None

    def __init__(self):
        super().__init__()
        self.search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)

    def _run(self, query: str) -> str:
        try:
            ano = datetime.now().year
            temporal = f"{query} ({ano} OR {ano+1}) site:.br"
            resp = self.search.run(temporal)
            if not resp or "no results" in resp.lower():
                return self.search.run(f"{query} site:.br")
            return resp
        except Exception as e:
            return f"Erro na busca web: {e}"

# Instância única da ferramenta
search_tool = WebSearchTool()

# ---------------------------
# 4. Configurações dos agentes
# ---------------------------
AGENT_CONFIGS = {
    "manager": {
        "role": "Personal Assistant Manager",
        "goal": (
            "Coordenar e delegar tarefas a agentes especialistas conforme a necessidade do usuário, "
            "fornecendo informações precisas e atualizadas."
        ),
        "backstory": (
            "Você é um gerente experiente de assistentes pessoais, entende necessidades do usuário "
            "e delega tarefas ao especialista certo, mantendo tom profissional e amigável."
        ),
        "verbose": True,
        "allow_delegation": True,
        "tools": [search_tool],
    },
    "researcher": {
        "role": "Research Specialist",
        "goal": "Coletar e analisar informações atuais de fontes diversas, garantindo precisão de datas e detalhes.",
        "backstory": "Você é um pesquisador detalhista que valida fontes e oferece resumos completos.",
        "verbose": True,
        "tools": [search_tool],
    },
    "planner": {
        "role": "Planning Specialist",
        "goal": "Organizar e planejar tarefas e cronogramas com informações atuais e precisas.",
        "backstory": "Você é um especialista em planejamento, divide tarefas complexas em etapas gerenciáveis.",
        "verbose": True,
        "tools": [search_tool],
    },
}
