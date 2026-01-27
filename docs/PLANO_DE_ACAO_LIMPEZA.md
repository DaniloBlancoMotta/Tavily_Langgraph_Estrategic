# 🎯 Plano de Ação: Limpeza e Estruturação do Projeto Strategic

> **Análise de Engenharia de IA Sênior**
> Data: 2026-01-27
> Projeto: Strategic (StratGov AI Agent)

---

## 📊 Status Atual (Diagnóstico)

### Métricas do Projeto
- **Total de Arquivos**: 54
- **Arquivos de Produção**: 30
- **Arquivos de Teste**: 4 (❌ na raiz do projeto)
- **Arquivos Temporários**: 3 (❌ precisam ser removidos)
- **Arquivos Não Utilizados**: 0 (✅ bom!)

### ✅ Pontos Positivos
1. Nenhum arquivo completamente não utilizado
2. Projeto relativamente organizado
3. Documentação presente (README.md)

### ❌ Problemas Identificados

#### 1. Arquivos de Teste Misturados com Produção
```
cli_test.py          → Deveria estar em /tests/
test_fallback.py     → Deveria estar em /tests/
test_import.py       → Deveria estar em /tests/
test_search.py       → Deveria estar em /tests/
```

#### 2. Arquivos Temporários no Repositório
```
search_output.txt        → Deletar (logs temporários)
search_results_log.txt   → Deletar (logs temporários)
requirements.txt         → Mover para /config/ ou raiz organizada
```

#### 3. Falta de Estrutura Modular
```
❌ Estrutura Atual (Flat):
Strategic/
├── agent.py
├── chat.py
├── download.py
├── index_knowledge.py
├── model.py
├── rag_store.py
├── search.py
├── server.py
├── state.py
├── streamlit_app.py
├── cli_test.py
├── test_*.py
└── ...

✅ Estrutura Ideal (Modular):
Strategic/
├── src/
│   ├── agents/
│   ├── rag/
│   ├── tools/
│   ├── api/
│   └── ui/
├── config/
├── tests/
├── scripts/
└── docs/
```

---

## 🎯 Plano de Ação (Fases)

### **Fase 0: Preparação** 🔒
**Status**: Pré-requisito obrigatório

```bash
# 1. Criar backup
git add .
git commit -m "backup: before cleanup and restructure"
git branch backup/pre-cleanup

# 2. Criar branch de trabalho
git checkout -b refactor/project-cleanup
```

**⚠️ NÃO prossiga sem backup!**

---

### **Fase 1: Limpeza Básica** 🗑️
**Objetivo**: Remover arquivos desnecessários

#### Ações:
1. **Deletar arquivos temporários**
   ```bash
   # Revisar conteúdo antes de deletar
   cat search_output.txt
   cat search_results_log.txt
   
   # Deletar se confirmado como temporário
   rm search_output.txt search_results_log.txt
   ```

2. **Adicionar ao .gitignore**
   ```gitignore
   # Logs e outputs temporários
   *_output.txt
   *_log.txt
   *.log
   search_results*.txt
   ```

**Resultado Esperado**: 
- ✅ 3 arquivos temporários removidos
- ✅ .gitignore atualizado

---

### **Fase 2: Organizar Testes** 🧪
**Objetivo**: Separar código de teste do código de produção

#### Ações:
1. **Criar estrutura de testes**
   ```bash
   mkdir tests
   mkdir tests\unit
   mkdir tests\integration
   ```

2. **Mover arquivos de teste**
   ```bash
   # Mover testes para diretório dedicado
   mv test_search.py tests/unit/
   mv test_import.py tests/unit/
   mv test_fallback.py tests/integration/
   mv cli_test.py tests/integration/
   ```

3. **Criar __init__.py nos testes**
   ```bash
   echo "" > tests\__init__.py
   echo "" > tests\unit\__init__.py
   echo "" > tests\integration\__init__.py
   ```

4. **Atualizar imports nos testes** (se necessário)
   - Adicionar `sys.path` ou usar imports relativos
   - Garantir que testes ainda funcionam

**Resultado Esperado**: 
- ✅ 4 arquivos de teste movidos
- ✅ Estrutura `/tests` criada
- ✅ Testes ainda executam corretamente

---

### **Fase 3: Estrutura Modular** 📁
**Objetivo**: Organizar código em módulos lógicos

#### Ações:
1. **Criar estrutura de diretórios**
   ```bash
   mkdir src
   mkdir src\agents
   mkdir src\rag
   mkdir src\tools
   mkdir src\api
   mkdir src\ui
   mkdir config
   mkdir scripts
   mkdir docs
   ```

2. **Mover arquivos de agentes**
   ```bash
   mv agent.py src\agents\
   mv state.py src\agents\
   echo "" > src\agents\__init__.py
   ```

3. **Mover arquivos RAG**
   ```bash
   mv rag_store.py src\rag\
   mv index_knowledge.py src\rag\
   echo "" > src\rag\__init__.py
   ```

4. **Mover ferramentas**
   ```bash
   mv search.py src\tools\
   mv download.py src\tools\
   mv model.py src\tools\
   echo "" > src\tools\__init__.py
   ```

5. **Mover API/Server**
   ```bash
   mv server.py src\api\
   echo "" > src\api\__init__.py
   ```

6. **Mover UI**
   ```bash
   mv chat.py src\ui\
   mv streamlit_app.py src\ui\
   echo "" > src\ui\__init__.py
   ```

7. **Mover configurações**
   ```bash
   mv requirements.txt config\
   # .env.example já está correto na raiz
   ```

8. **Mover documentação**
   ```bash
   mv review_agent_architecture.md docs\
   ```

9. **Mover utilitários**
   ```bash
   mv ssl_fix.py scripts\
   ```

**Resultado Esperado**: 
```
Strategic/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── state.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_store.py
│   │   └── index_knowledge.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── download.py
│   │   └── model.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   └── ui/
│       ├── __init__.py
│       ├── chat.py
│       └── streamlit_app.py
├── config/
│   └── requirements.txt
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
│   └── ssl_fix.py
├── docs/
│   └── review_agent_architecture.md
├── frontend/
├── .env.example
├── .gitignore
└── README.md
```

---

### **Fase 4: Atualizar Imports** 🔧
**Objetivo**: Corrigir todos os imports após reorganização

#### Ações:
1. **Criar src/__init__.py principal**
   ```python
   # src/__init__.py
   """Strategic AI Agent - Production Package"""
   __version__ = "1.0.0"
   ```

2. **Atualizar imports em todos os arquivos**
   
   **Antes**:
   ```python
   from agent import Agent
   from state import State
   from search import search_web
   ```
   
   **Depois**:
   ```python
   from src.agents.agent import Agent
   from src.agents.state import State
   from src.tools.search import search_web
   ```

3. **Criar arquivo de instalação local**
   ```bash
   # criar setup.py ou pyproject.toml
   # para instalar package em modo desenvolvimento
   pip install -e .
   ```

**Resultado Esperado**: 
- ✅ Todos os imports funcionando
- ✅ Código executável
- ✅ Testes passando

---

### **Fase 5: Validação** ✅
**Objetivo**: Garantir que nada quebrou

#### Checklist:
```bash
# 1. Verificar imports
python -c "from src.agents import agent; print('✅ Agents OK')"
python -c "from src.rag import rag_store; print('✅ RAG OK')"
python -c "from src.tools import search; print('✅ Tools OK')"

# 2. Executar testes
cd tests
python -m pytest unit/
python -m pytest integration/

# 3. Testar funcionalidade principal
python src/ui/chat.py
# ou
streamlit run src/ui/streamlit_app.py

# 4. Verificar servidor
python src/api/server.py
```

**Resultado Esperado**: 
- ✅ Todos os imports funcionando
- ✅ Testes passando
- ✅ Aplicação rodando normalmente
- ✅ Servidor respondendo

---

### **Fase 6: Documentação** 📚
**Objetivo**: Atualizar documentação para nova estrutura

#### Ações:
1. **Atualizar README.md**
   - Adicionar seção "Estrutura do Projeto"
   - Atualizar instruções de instalação
   - Atualizar comandos de execução

2. **Criar ARCHITECTURE.md**
   ```markdown
   # Arquitetura do Projeto
   
   ## Estrutura de Diretórios
   [Explicar cada diretório]
   
   ## Fluxo de Dados
   [Diagrama de como os componentes interagem]
   
   ## Padrões Utilizados
   [RAG, LangGraph, etc]
   ```

3. **Atualizar docs/**
   - Migrar review_agent_architecture.md
   - Adicionar documentação de módulos

**Resultado Esperado**: 
- ✅ README atualizado
- ✅ Documentação de arquitetura criada
- ✅ Guias de desenvolvimento atualizados

---

## 📋 Checklist Final

### Qualidade de Código
- [ ] Nenhum arquivo de teste em produção
- [ ] Nenhum arquivo temporário no repositório
- [ ] Estrutura modular implementada
- [ ] Imports organizados e funcionais
- [ ] Configurações centralizadas
- [ ] Documentação atualizada

### Funcionalidade
- [ ] Aplicação executa sem erros
- [ ] Testes passam
- [ ] Servidor responde
- [ ] Frontend funciona
- [ ] RAG indexa e busca documentos

### DevOps
- [ ] .gitignore atualizado
- [ ] requirements.txt completo
- [ ] .env.example documentado
- [ ] README com instruções claras

---

## 🎓 Princípios de Engenharia Aplicados

### 1. **Separation of Concerns**
- Código de produção separado de testes
- Módulos com responsabilidades únicas
- Configuração separada de lógica

### 2. **DRY (Don't Repeat Yourself)**
- Código centralizado em módulos
- Imports consistentes
- Evitar duplicação de lógica

### 3. **Clean Code**
- Nomes descritivos de diretórios
- Estrutura previsível
- Fácil navegação

### 4. **Production Ready**
- Sem arquivos temporários
- Configuração por ambiente
- Logs estruturados
- Error handling robusto

### 5. **AI Engineering Best Practices**
- RAG modular (embeddings, retrieval, ranking)
- Agents desacoplados
- State management claro
- Observabilidade (LangSmith ready)

---

## 🚨 Avisos Importantes

### ⚠️ Backup Obrigatório
**NUNCA** execute limpeza sem:
1. Commit do estado atual
2. Branch de backup criado
3. Confirmação de que tudo está versionado

### ⚠️ Revisão Manual
**SEMPRE** revise antes de deletar:
1. Conteúdo de arquivos temporários
2. Funcionalidade de arquivos "não utilizados"
3. Imports quebrados após movimentação

### ⚠️ Validação Incremental
**TESTE** após cada fase:
1. Execute a aplicação
2. Rode os testes
3. Verifique imports
4. Confirme funcionalidade

---

## 📞 Suporte

Se encontrar problemas durante a execução:

1. **Rollback seguro**:
   ```bash
   git checkout backup/pre-cleanup
   ```

2. **Debug de imports**:
   ```bash
   python -v -c "import src.agents.agent"
   ```

3. **Consultar skill**:
   ```bash
   cat .agent/skills/ai-project-cleaner/SKILL.md
   ```

---

## ✨ Resultado Final Esperado

Um projeto:
- ✅ **Limpo**: Sem testes ou temporários em produção
- ✅ **Modular**: Código organizado por responsabilidade
- ✅ **Profissional**: Estrutura de nível sênior
- ✅ **Escalável**: Fácil adicionar novos componentes
- ✅ **Manutenível**: Qualquer dev entende em minutos

---

**Este plano foi gerado pela skill `ai-project-cleaner`**
**Baseado em análise automática do projeto Strategic**
**Seguindo padrões de Engenharia de IA de nível sênior**

🚀 **Bom trabalho!**
