---
description: Clean and structure AI projects with production best practices
---

# AI Project Cleaner & Structure Optimizer

This skill analyzes and organizes AI agent projects following senior-level engineering standards.

## Workflow Steps

### Step 1: Analyze Current Project Structure
```bash
python .agent/workflows/scripts/ai_cleaner_analyzer.py --analyze
```

This will:
- Map all files and directories
- Identify test files
- Find unused imports and dead code
- Detect duplicate logic
- Check for proper modular structure

### Step 2: Generate Cleanup Report
```bash
python .agent/workflows/scripts/ai_cleaner_analyzer.py --report
```

This generates:
- `cleanup_report.md` - Detailed analysis
- `files_to_remove.txt` - Safe-to-delete files
- `refactoring_suggestions.md` - Structure improvements

### Step 3: Review and Approve
**MANUAL STEP**: Review the generated reports before proceeding

### Step 4: Execute Cleanup (Dry Run)
```bash
python .agent/workflows/scripts/ai_cleaner_analyzer.py --cleanup --dry-run
```

Preview what will be cleaned without making changes

### Step 5: Execute Cleanup (Real)
```bash
python .agent/workflows/scripts/ai_cleaner_analyzer.py --cleanup --execute
```

Actually remove unnecessary files and reorganize structure

### Step 6: Validate Project Health
```bash
python .agent/workflows/scripts/ai_cleaner_analyzer.py --validate
```

Ensure all imports work and no breaking changes occurred

## Production Best Practices Applied

1. **Modular Architecture**
   - Separate concerns (RAG, agents, tools, state)
   - Clear interfaces between modules
   - Dependency injection patterns

2. **Clean Code Principles**
   - Remove test files from production
   - Eliminate dead code
   - DRY principle enforcement

3. **AI Engineering Standards**
   - Proper prompt management
   - State persistence patterns
   - Observability hooks
   - Error handling strategies

4. **Project Structure**
   ```
   project/
   ├── src/
   │   ├── agents/
   │   ├── rag/
   │   ├── tools/
   │   └── utils/
   ├── config/
   ├── data/
   ├── tests/
   ├── scripts/
   └── docs/
   ```
