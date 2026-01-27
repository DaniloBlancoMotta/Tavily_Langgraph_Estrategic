# 🧹 AI Project Cleaner Skill

> **Expert in cleaning and structuring AI Agent projects with production-grade engineering practices**

## 🎯 What This Skill Does

This skill provides automated analysis and actionable recommendations for cleaning up AI agent projects, transforming messy codebases into production-ready, maintainable systems.

## 🚀 Quick Start

### 1. Run Analysis

```bash
python .agent/skills/ai-project-cleaner/analyzer.py
```

This will generate `PROJECT_ANALYSIS.md` with:
- File classification (production, test, temp, unused)
- Code quality issues
- Structural recommendations
- Specific action items

### 2. Review Report

Open `PROJECT_ANALYSIS.md` and review:
- Which test files should move to `/tests`
- Which temporary files can be deleted
- Which files are potentially unused
- Code smells and quality issues

### 3. Take Action

Based on the report, organize your project following the recommended structure.

## 📁 Skill Contents

```
ai-project-cleaner/
├── SKILL.md          # Complete skill documentation and methodology
├── analyzer.py       # Automated analysis script
├── examples.md       # Usage examples and expected outputs
└── README.md         # This file
```

## 🎓 What You Get

### Automated Detection

✅ **Test Files**: Identifies all test files that should be in `/tests`
✅ **Temporary Files**: Finds logs, outputs, and other temp files
✅ **Unused Code**: Detects files that are never imported
✅ **Code Smells**: Large files, excessive imports, duplicates
✅ **Structure Issues**: Missing organization patterns

### Recommendations

💡 **Modular Structure**: Suggested `/src`, `/config`, `/tests` organization
💡 **Best Practices**: AI-specific patterns for RAG, agents, tools
💡 **Production Ready**: Environment configs, error handling, observability

## 📋 Example Output

```
📊 File Classification
- Production Files: 15
- Test Files: 8 → Move to /tests
- Temporary Files: 3 → Safe to delete
- Unused Files: 2 → Review for removal

💡 Recommendations
- Move 8 test files to /tests directory
- Remove 3 temporary/log files  
- Organize production code in /src
- Centralize configs in /config
```

## 🔍 What It Analyzes

### Code Quality
- File sizes and complexity
- Import dependencies
- Dead/unused code
- Duplicate logic

### Project Structure
- Directory organization
- File categorization
- Module separation
- Configuration management

### AI-Specific Patterns
- RAG system organization
- Agent workflow structure
- Tool integration
- State management

## 🛡️ Safety First

This skill follows a **non-destructive** approach:

✅ Generates reports for review
✅ **NEVER** deletes files automatically
✅ Provides recommendations, not automatic actions
✅ User reviews and approves all changes

## 📚 Documentation

- **SKILL.md**: Complete methodology and engineering principles
- **examples.md**: Real-world usage examples
- **This README**: Quick start guide

## 🎯 Best For

- Cleaning up proof-of-concept code
- Preparing projects for production
- Onboarding new team members
- Refactoring legacy AI projects
- Establishing code standards

## 🤝 Senior Engineer Approach

This skill follows senior-level engineering practices:

1. **Analyze before acting** (generate reports first)
2. **Non-destructive by default** (never auto-delete)
3. **Clear documentation** (explain all recommendations)
4. **Production mindset** (scalable, maintainable patterns)
5. **AI-specific expertise** (RAG, LangGraph, observability)

## 🔧 Requirements

- Python 3.8+
- No external dependencies (uses only stdlib)

## 📖 Usage

See `examples.md` for detailed usage examples and expected outputs.

See `SKILL.md` for complete documentation of methodology and principles.

## ✨ Result

A clean, organized, production-ready AI project that:
- New engineers can understand in minutes
- Follows industry best practices
- Scales with your requirements
- Maintains clear separation of concerns
- Ready for professional deployment

---

**Made with 💙 by Senior AI Engineers, for Senior AI Engineers**
