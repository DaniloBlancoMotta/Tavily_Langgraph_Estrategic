# 🏗️ Arquitetura do Projeto Strategic

> **StratGov AI Agent - Documentação Técnica de Arquitetura**

## 📋 Visão Geral

StratGov AI é um agente autônomo avançado que atua como Consultor Sênior de Estratégia & Governança, utilizando LangGraph e LLMs para fornecer consultoria estratégica baseada em evidências.

---

## 🗂️ Estrutura de Diretórios

### Organização Modular (Production-Ready)

```
Strategic/
├── src/                    # Código de produção
│   ├── agents/            # Agentes LangGraph
│   ├── rag/               # Sistema RAG
│   ├── tools/             # Ferramentas do agente
│   ├── api/               # API e servidor
│   └── ui/                # Interfaces de usuário
├── tests/                  # Testes
│   ├── unit/              # Testes unitários
│   └── integration/       # Testes de integração
├── config/                 # Configurações
├── docs/                   # Documentação
├── scripts/                # Scripts utilitários
├── frontend/               # Aplicação Next.js
└── .agent/                 # Skills e workflows
```

---

## 🧩 Componentes Principais

### 1. **Agents** (`src/agents/`)

#### `agent.py` - Definição do Agente
```python
# Define o grafo de estado (StateGraph) com nós e arestas
# Implementa o fluxo agentic: Think → Search → Refine
```

**Responsabilidades**:
- Definir nós do grafo (Think, Search, Answer)
- Configurar transições de estado
- Orquestrar workflow do agente

#### `state.py` - Gerenciamento de Estado
```python
# Define schemas de estado para LangGraph
# Mantém histórico de conversação e contexto
```

**Responsabilidades**:
- Schemas de estado TypedDict
- Gerenciamento de memória
- Persistência de contexto

---

### 2. **RAG System** (`src/rag/`)

#### `rag_store.py` - Armazenamento RAG
```python
# Implementa vector store para recuperação de conhecimento
```

**Responsabilidades**:
- Gerenciar vector store (FAISS/Chroma)
- Persistência de embeddings
- Busca por similaridade

#### `index_knowledge.py` - Indexação
```python
# Processa e indexa documentos para RAG
```

**Responsabilidades**:
- Processar PDFs e documentos
- Gerar embeddings
- Construir índice de conhecimento

---

### 3. **Tools** (`src/tools/`)

#### `search.py` - Busca Estratégica
```python
# Integração com Tavily API
# Filtragem de domínios confiáveis (McKinsey, BCG, Bain, etc.)
```

**Responsabilidades**:
- Busca web estratégica
- Filtrar fontes premium
- Retornar resultados ranqueados

#### `download.py` - Fetcher de Conteúdo
```python
# Busca assíncrona de conteúdo de URLs
```

**Responsabilidades**:
- Download assíncrono de páginas
- Extração de conteúdo relevante
- Preprocessamento de texto

#### `model.py` - Configurações de Modelo
```python
# Configurações de LLM (Groq, Ollama, etc.)
```

**Responsabilidades**:
- Inicialização de modelos
- Gestão de parâmetros
- Fallback entre modelos

---

### 4. **API** (`src/api/`)

#### `server.py` - Servidor FastAPI
```python
# Expõe endpoints REST para o agente
```

**Responsabilidades**:
- Endpoints HTTP/WebSocket
- Serialização de respostas
- CORS e middleware
- Rate limiting

**Endpoints**:
- `POST /chat` - Enviar mensagem ao agente
- `GET /stream` - Stream de respostas
- `GET /health` - Health check

---

### 5. **UI** (`src/ui/`)

#### `chat.py` - Interface de Chat
```python
# Lógica de chat e system prompting
```

**Responsabilidades**:
- Gerenciar conversação
- Formatação de prompts
- Histórico de mensagens

#### `streamlit_app.py` - App Streamlit
```python
# Interface web alternativa com Streamlit
```

**Responsabilidades**:
- UI interativa
- Visualização de respostas
- Debug/testing interface

---

## 🔄 Fluxo de Dados

### Fluxo de Conversação

```
User Input
    ↓
[UI Layer] chat.py / streamlit_app.py
    ↓
[API Layer] server.py (FastAPI)
    ↓
[Agent Layer] agent.py (LangGraph)
    ↓
[Decision Node]
    ├──→ [Search Tool] search.py → Tavily API
    ├──→ [RAG Tool] rag_store.py → Vector DB
    └──→ [Model] model.py → LLM (Groq/Ollama)
    ↓
[Response Synthesis]
    ↓
Return to User
```

### Fluxo RAG

```
Document Upload
    ↓
index_knowledge.py
    ├─→ Text Extraction
    ├─→ Chunking
    ├─→ Embedding Generation
    └─→ Vector Store (rag_store.py)
    
Query
    ↓
rag_store.py
    ├─→ Query Embedding
    ├─→ Similarity Search
    ├─→ Retrieve Top-K
    └─→ Return Context
    ↓
Agent (context-aware response)
```

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **LangGraph**: Framework de agentes com state graphs
- **LangChain**: Componentes LLM e tools
- **FastAPI**: Servidor REST assíncrono
- **Groq API**: Inferência LLM de alta velocidade (Llama 3.3 70B)
- **Tavily API**: Busca web estratégica

### RAG
- **FAISS / Chroma**: Vector stores
- **HuggingFace Embeddings**: Geração de embeddings
- **PyPDF2 / Unstructured**: Processamento de documentos

### Frontend
- **Next.js 15**: Framework React
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Streamlit**: Interface alternativa

---

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── unit/                   # Testes de unidade
│   ├── test_search.py     # Testa search.py
│   └── test_import.py     # Testa imports
└── integration/            # Testes de integração
    ├── test_fallback.py   # Testa fallback de modelos
    └── cli_test.py        # Testa CLI
```

### Executar Testes

```bash
# Todos os testes
pytest tests/

# Apenas unit
pytest tests/unit/

# Apenas integration
pytest tests/integration/
```

---

## 📦 Configuração

### Variáveis de Ambiente

```env
# .env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
LANGCHAIN_API_KEY=optional_langsmith_key
LANGCHAIN_TRACING_V2=true
```

### Dependencies

```bash
# Instalar dependências
pip install -r config/requirements.txt

# Principais packages:
# - langgraph
# - langchain
# - langchain-groq
# - fastapi
# - streamlit
# - tavily-python
# - faiss-cpu (ou faiss-gpu)
```

---

## 🚀 Deploy

### Local Development

```bash
# Backend
python src/api/server.py

# Frontend
cd frontend && npm run dev

# Streamlit (alternativa)
streamlit run src/ui/streamlit_app.py
```

### Production Considerations

1. **Environment Management**:
   - Usar `.env.production` para configs de prod
   - Secrets management (AWS Secrets Manager, etc.)

2. **Scaling**:
   - Load balancer para FastAPI
   - Redis para cache de embeddings
   - PostgreSQL para state persistence

3. **Monitoring**:
   - LangSmith para observabilidade de LLM
   - Prometheus/Grafana para métricas
   - Sentry para error tracking

4. **Containerization**:
   ```dockerfile
   # Future: Dockerfile para backend
   FROM python:3.11-slim
   WORKDIR /app
   COPY config/requirements.txt .
   RUN pip install -r requirements.txt
   COPY src/ ./src/
   CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0"]
   ```

---

## 🎯 Padrões de Engenharia

### Design Patterns Utilizados

1. **State Pattern** (LangGraph):
   - Gerenciamento de estado do agente
   - Transições baseadas em condições

2. **Strategy Pattern** (Tools):
   - Diferentes estratégias de busca
   - Fallback entre modelos

3. **Repository Pattern** (RAG):
   - Abstração de vector stores
   - Interface consistente para retrieval

4. **Factory Pattern** (Model):
   - Criação de instâncias de LLM
   - Configuração centralizada

### Clean Code Principles

- ✅ **Single Responsibility**: Cada módulo tem uma responsabilidade clara
- ✅ **DRY**: Código reutilizável em módulos
- ✅ **Separation of Concerns**: UI, API, Logic separados
- ✅ **Dependency Injection**: Configurações injetadas via .env

---

## 📊 Performance

### Otimizações Implementadas

1. **Caching**:
   - Cache de embeddings
   - Cache de resultados de busca

2. **Async Operations**:
   - Download assíncrono (`download.py`)
   - Batch processing de documentos

3. **Lazy Loading**:
   - Modelos carregados on-demand
   - Vector store carregado quando necessário

---

## 🔐 Segurança

### Medidas Implementadas

- ✅ Environment variables para secrets
- ✅ .gitignore para arquivos sensíveis
- ✅ CORS configurado no FastAPI
- ✅ Input validation nos endpoints

### TODO (Produção)

- [ ] Rate limiting por usuário
- [ ] Authentication/Authorization (JWT)
- [ ] Input sanitization
- [ ] Audit logging

---

## 📚 Documentação Adicional

- **[PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md)**: Análise técnica do projeto
- **[PLANO_DE_ACAO_LIMPEZA.md](PLANO_DE_ACAO_LIMPEZA.md)**: Plano de refatoração
- **[RESUMO_SKILL.md](RESUMO_SKILL.md)**: Skill de limpeza aplicada
- **[review_agent_architecture.md](review_agent_architecture.md)**: Review de arquitetura

---

## 🤝 Contribuindo

### Workflow de Desenvolvimento

1. Fork do repositório
2. Criar branch (`git checkout -b feature/nova-feature`)
3. Commit changes (`git commit -m 'feat: adiciona nova feature'`)
4. Push to branch (`git push origin feature/nova-feature`)
5. Abrir Pull Request

### Padrões de Commit

```
feat: nova funcionalidade
fix: correção de bug
docs: atualização de documentação
refactor: refatoração de código
test: adição de testes
chore: tarefas de manutenção
```

---

**Última atualização**: 2026-01-27
**Versão**: 1.0.0 (após cleanup e modularização)
