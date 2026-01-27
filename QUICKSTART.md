# 🚀 Strategic AI Agent - Quick Start Guide

## Como Executar o Projeto

### 📋 Pré-requisitos

1. Python 3.10+ instalado
2. Node.js 18+ (para frontend)
3. API Keys configuradas no `.env`:
   ```env
   GROQ_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ```

---

## ⚡ Comandos Rápidos

### 1. Instalar Dependências

```bash
# Backend
pip install -r config/requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Executar Backend (FastAPI)

```bash
python run_server.py
```

**Acesse**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 3. Executar Streamlit (Interface Alternativa)

```bash
python run_streamlit.py
```

**Acesse**: http://localhost:8501

### 4. Executar Frontend (Next.js)

```bash
cd frontend
npm run dev
```

**Acesse**: http://localhost:3000

### 5. Executar Testes

```bash
# Todos os testes de integração
python tests/test_integration_all.py

# Testes específicos
pytest tests/unit/
pytest tests/integration/
```

---

## 🎯 Endpoints da API

### POST /api/chat
Enviar mensagem para o agente:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is digital transformation?",
    "model": "groq",
    "temperature": 0.2,
    "max_tokens": 4096
  }'
```

### GET /health
Verificar status do servidor:

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "active",
  "service": "StratGov_Agent",
  "version": "2.1.0"
}
```

---

## 📁 Estrutura do Projeto

```
Strategic/
├── src/                    # Código fonte
│   ├── agents/            # LangGraph agents
│   ├── rag/               # Sistema RAG
│   ├── tools/             # Ferramentas
│   ├── api/               # FastAPI server
│   └── ui/                # Interfaces
├── tests/                  # Testes
├── config/                 # Configurações
├── docs/                   # Documentação
├── scripts/                # Utilitários
├── frontend/               # Next.js app
├── run_server.py          # 🚀 Launcher backend
├── run_streamlit.py       # 🚀 Launcher Streamlit
└── README.md
```

---

## 🔍 Troubleshooting

### Erro de Import
Se encontrar `ModuleNotFoundError: No module named 'src'`:

**Solução**: Use os launchers:
```bash
python run_server.py        # Ao invés de: python src/api/server.py
python run_streamlit.py     # Ao invés de: streamlit run src/ui/streamlit_app.py
```

### Erro de API Key
Se ver `TAVILY_API_KEY not configured`:

**Solução**: Copie `.env.example` para `.env` e adicione suas keys:
```bash
cp .env.example .env
# Edite .env com suas chaves
```

### Servidor Não Inicia
Verifique se a porta 8000 está livre:

```bash
# Windows
netstat -ano | findstr :8000

# Se ocupada, mude a porta em run_server.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📚 Documentação Completa

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura técnica
- **[INTEGRATION_TEST_REPORT.md](docs/INTEGRATION_TEST_REPORT.md)** - Relatório de testes
- **[CLEANUP_SUMMARY.md](docs/CLEANUP_SUMMARY.md)** - Histórico de reorganização
- **[README.md](README.md)** - Documentação principal

---

## ✅ Validação Rápida

Execute para testar tudo:

```bash
# 1. Teste de integração
python tests/test_integration_all.py

# 2. Inicie o backend
python run_server.py

# 3. Em outro terminal, teste o health
curl http://localhost:8000/health
```

Se todos passarem: ✅ **Sistema funcionando!**

---

## 🎉 Está Funcionando!

Agora você pode:

1. **Chat via API**: POST para `/api/chat`
2. **Interface Streamlit**: `python run_streamlit.py`
3. **Frontend Next.js**: `cd frontend && npm run dev`

**Documentação completa**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Última atualização**: 2026-01-27  
**Versão**: 1.0.0 (após reorganização modular)
