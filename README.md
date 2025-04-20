# Personal CrewAI Assistant 🤖

## Resumo
Este projeto implementa um assistente pessoal inteligente usando CrewAI, uma framework que permite a criação de equipes de agentes AI especializados. O sistema é projetado com uma estrutura hierárquica onde um agente gerente coordena outros agentes especializados para realizar tarefas complexas.

### Principais Características   
- 🎯 **Gerenciamento Inteligente**: Um agente gerente que coordena todas as atividades
- 🔍 **Pesquisa Especializada**: Agente dedicado para pesquisas e análise de informações
- 📋 **Planejamento Eficiente**: Agente especializado em organização e planejamento
- 🌐 **Pesquisa Web**: Integração com DuckDuckGo para pesquisas em tempo real
- 💬 **Interface Amigável**: Interface Streamlit intuitiva com histórico de conversas

## Estrutura do Projeto
```
personalcrewAI/
├── app.py                    # Interface Streamlit
├── requirements.txt          # Dependências
├── README.md                # Documentação
└── personal_crew/           # Módulo principal
    ├── __init__.py          # Inicialização do pacote
    ├── config.py            # Configurações e ferramentas
    ├── agents.py            # Definição dos agentes
    ├── tasks.py             # Definição das tarefas
    └── crew.py              # Gerenciamento da equipe
```

## Setup

1. Clone este repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o arquivo `.env` na raiz do projeto:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Executando a Aplicação

Para rodar a aplicação localmente:
```bash
streamlit run app.py
```

## Opções de Deployment

### Local
1. Siga as instruções de setup acima
2. Execute `streamlit run app.py`
3. Acesse em `http://localhost:8501`

### Streamlit Cloud
1. Crie uma conta no Streamlit Cloud
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. Deploy automático

### AWS
1. Crie uma instância EC2
2. Configure o ambiente Python
3. Use PM2 ou Supervisor para gerenciamento de processos
4. Configure Nginx como proxy reverso
5. Configure SSL com Let's Encrypt

### Heroku
1. Crie um `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT
   ```
2. Deploy via Heroku CLI:
   ```bash
   heroku create
   git push heroku main
   ```

## Variáveis de Ambiente

- `OPENAI_API_KEY`: Sua chave de API do OpenAI
- `STREAMLIT_SERVER_PORT`: Porta para o servidor Streamlit (padrão: 8501)

## Contribuindo

Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests
- Melhorar a documentação

## Licença

MIT License - veja o arquivo LICENSE para mais detalhes. 