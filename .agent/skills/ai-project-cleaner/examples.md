# AI Project Cleaner - Examples

## Example 1: Basic Analysis

```bash
# Navigate to your project
cd c:\Users\UNIVERSO\OneDrive\Desktop\Strategic

# Run analysis
python .agent\skills\ai-project-cleaner\analyzer.py --project . --output PROJECT_ANALYSIS.md
```

**Output**: Generates `PROJECT_ANALYSIS.md` with complete analysis

---

## Example 2: Analyze Specific Directory

```bash
# Analyze only the source code
python .agent\skills\ai-project-cleaner\analyzer.py --project ./src --output SRC_ANALYSIS.md
```

---

## Example Report Structure

```markdown
# 🧹 AI Project Cleanup Report

**Total Files Analyzed**: 45

## 📊 File Classification

- **Production Files**: 15
- **Test Files**: 8
- **Temporary Files**: 3
- **Unused Files**: 2

### 🧪 Test Files (should be in /tests)

- `cli_test.py`
- `test_fallback.py`
- `test_import.py`
- `test_search.py`

### 🗑️ Temporary Files (safe to delete)

- `search_output.txt`
- `search_results_log.txt`

### ⚠️ Potentially Unused Files

- `ssl_fix.py`
- `review_agent_architecture.md` (should be in /docs)

## 👃 Code Smells Detected

### Large Files
- `index_knowledge.py (823 lines)`

### Many Imports
- `chat.py (25 imports)`

### Duplicate Names
- `search` in `search.py, agent.py`

## 💡 Recommendations

🧪 Move 8 test files to dedicated /tests directory

🗑️  Remove 3 temporary/log files

⚠️  Review 2 potentially unused files

📁 Consider organizing code in /src directory

⚙️  Move configuration files to /config directory
```

---

## Example 3: Integration with Workflow

Use the `/ai-project-cleaner` workflow:

```bash
# Step 1: Read the skill
cat .agent\skills\ai-project-cleaner\SKILL.md

# Step 2: Run analyzer
python .agent\skills\ai-project-cleaner\analyzer.py

# Step 3: Review generated report
cat PROJECT_ANALYSIS.md

# Step 4: Make decisions based on report
# (manual review and approval)
```

---

## Expected Workflow

1. **Analyze**: Run the analyzer script
2. **Review**: Examine the generated markdown report
3. **Plan**: Decide which files to remove/move
4. **Execute**: Manually move files or create migration script
5. **Validate**: Ensure everything still works

---

## Production-Ready Structure (Target)

```
Strategic/
├── src/                          # All source code
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── state.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── index_knowledge.py
│   │   └── rag_store.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   └── download.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   └── ui/
│       ├── __init__.py
│       ├── chat.py
│       └── streamlit_app.py
├── config/
│   ├── .env.example
│   └── settings.py
├── tests/
│   ├── test_search.py
│   ├── test_fallback.py
│   ├── test_import.py
│   └── cli_test.py
├── scripts/
│   └── utilities/
├── docs/
│   └── review_agent_architecture.md
├── frontend/
│   └── (Next.js app)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Key Benefits

✅ **Clear separation of concerns**
✅ **Easy to navigate and understand**
✅ **Production-ready structure**
✅ **Scalable architecture**
✅ **Professional code organization**

---

## Safety Notes

⚠️ The analyzer **NEVER** deletes files automatically
⚠️ Always review the report before taking action
⚠️ Create a git branch before major reorganization
⚠️ Test thoroughly after restructuring

---

*Remember: The goal is maintainable, production-grade AI systems!*
