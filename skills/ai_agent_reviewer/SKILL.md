---
name: AI Agent Reviewer & Optimizer
description: Comprehensive framework for evaluating, auditing, and improving AI agents. Use this skill when analyzing agent architectures, prompts, workflows, tool integrations, or when optimizing agent performance, reliability, and safety.
---

# AI Agent Reviewer & Optimizer

## Overview
Comprehensive framework for evaluating, auditing, and improving AI agents. Use this skill when analyzing agent architectures, prompts, workflows, tool integrations, or when optimizing agent performance, reliability, and safety.

## Core Competencies
This skill enables systematic evaluation across:
- **Agent architecture and design patterns**
- **Prompt engineering quality**
- **Tool usage and integration**
- **Error handling and resilience**
- **Performance and latency optimization**
- **Safety, alignment, and guardrails**
- **Context management and memory**
- **Multi-agent coordination**
- **Production readiness**

---

## 1. AGENT ARCHITECTURE REVIEW

### 1.1 Design Pattern Analysis

**Evaluate the agent's structural approach:**

#### ReAct Pattern (Reasoning + Acting)
*Strengths:*
- Transparent reasoning traces
- Good for complex, multi-step tasks
- Easy to debug

*Weaknesses:*
- Can be verbose
- May loop unnecessarily
- Higher token consumption

*Check for:*
- [ ] Clear thought → action → observation cycles
- [ ] Appropriate stopping conditions
- [ ] Prevention of infinite loops

#### Tool-Calling Pattern
*Strengths:*
- Structured tool invocation
- Better error handling
- Lower latency

*Weaknesses:*
- Less transparent reasoning
- Requires robust tool schemas

*Check for:*
- [ ] Well-defined tool schemas (JSON Schema/OpenAPI)
- [ ] Clear tool descriptions and parameters
- [ ] Proper parameter validation

#### Chain-of-Thought (CoT)
*Strengths:*
- Improved reasoning quality
- Better for mathematical/logical tasks
- Interpretable outputs

*Check for:*
- [ ] Appropriate use cases (not overkill)
- [ ] Clear step-by-step breakdown
- [ ] Correct final answer extraction

#### Agentic Workflows (Plan-Execute, Reflection)

**Plan-Execute:**
- [ ] Clear planning phase before execution
- [ ] Dynamic replanning when needed
- [ ] Progress tracking mechanisms

**Reflection:**
- [ ] Self-evaluation checkpoints
- [ ] Error correction loops
- [ ] Quality validation steps

### 1.2 Architecture Red Flags
- **No clear termination conditions** → Risk of infinite loops
- **Overly complex chains** → Fragile, hard to debug
- **Missing error boundaries** → Cascade failures
- **No state management** → Lost context between steps
- **Synchronous blocking calls** → Poor performance
- **Hardcoded logic** → Inflexible, hard to maintain

---

## 2. PROMPT ENGINEERING AUDIT

### 2.1 System Prompt Evaluation

**Essential Components Checklist**
- [ ] **Role Definition**: "You are [specific role] with expertise in [domain]"
- [ ] **Task Description**: Clear, unambiguous description of what the agent does
- [ ] **Behavioral Guidelines**: Tone, style, clarification, uncertainty handling
- [ ] **Output Format**: Structured format specifications (JSON, XML, markdown)
- [ ] **Constraints**: What NOT to do, safety boundaries, limits
- [ ] **Examples (Few-Shot)**: 2-5 high-quality input/output examples
- [ ] **Error Handling Instructions**: How to respond when tools fail or data is missing

### Prompt Quality Metrics

**Clarity Score (1-10)**
- Ambiguous words: "maybe", "try", "sometimes" → -2 each
- Vague pronouns without clear referents → -1 each
- Clear imperatives: "always", "never", "must" → +1 each

**Specificity Score (1-10)**
- Generic instructions → -2
- Domain-specific terminology → +1
- Concrete examples → +2
- Measurable success criteria → +2

**Completeness Score (1-10)**
- Missing edge case handling → -2
- No output format specification → -3
- No error handling → -3
- Comprehensive coverage → +3
