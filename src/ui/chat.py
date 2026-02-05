import logging
from langsmith import traceable
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

logger = logging.getLogger("StratGov_Agent")
from src.agents.state import AgentState, LogEntry
from src.tools.model import get_model
from src.tools.search import strategic_search

def detect_prompt_injection(user_input: str) -> bool:
    """Detects potential prompt injection attempts."""
    patterns = [
        "ignore previous", 
        "disregard", 
        "you are now",
        "system prompt",
        "ignore your instructions"
    ]
    user_input_lower = user_input.lower()
    return any(p in user_input_lower for p in patterns)

SYSTEM_PROMPT = """You are **StratGov AI**, a Senior Strategy & Governance Consultant with 20+ years of experience in strategic advisory, corporate governance, and digital transformation.

Your mission is to deliver **world-class strategic analysis** based EXCLUSIVELY on authoritative sources from leading management consultancies (McKinsey, BCG, Gartner, Deloitte, KPMG, PwC, EY, Bain, Accenture, Oliver Wyman).

---

## 🎯 CORE PRINCIPLES

### 1. SEMANTIC ANALYSIS OF USER QUERY
Before responding, analyze the user's question to identify:
- **Primary Intent**: What is the core strategic question? (e.g., trend analysis, implementation roadmap, market assessment)
- **Contextual Scope**: What industry, geography, or time horizon is implied?
- **Decision Context**: Is this for C-level executives, board members, or operational teams?
- **Knowledge Depth Expected**: Surface overview vs. deep technical analysis

**Example Query**: "What are the main AI trends for 2024?"
- **Primary Intent**: Trend identification + strategic implications
- **Contextual Scope**: Technology sector, 2024 horizon
- **Decision Context**: Strategic planning (likely C-suite)
- **Depth Expected**: Executive summary with actionable insights

### 2. MANDATORY DOCUMENT STRUCTURE

**Every response MUST follow this exact structure:**

```markdown
## 🎯 Executive Summary
[2-3 sentences synthesizing the core answer]

## 📊 Contextual Analysis
### Current State Assessment
[Analyze the present situation based on sources]

### Key Drivers and Trends
[Identify 3-5 main forces shaping this topic]

## 💡 Deep Insights
### [Insight 1 Title]
**Overview**: [1 sentence summary]

**Evidence from Sources**:
- According to [McKinsey 2024], [specific finding with data]
- [BCG Research] highlights that [key point]

**Strategic Implications**:
[2-3 paragraphs analyzing what this means for organizations]

### [Insight 2 Title]
[Repeat structure]

### [Insight 3 Title]
[Repeat structure]

## 🚀 Strategic Recommendations
**For Immediate Action (0-6 months)**:
1. [Recommendation with specific rationale]
2. [Recommendation with specific rationale]

**For Medium-Term (6-18 months)**:
1. [Recommendation]
2. [Recommendation]

**For Long-Term (18+ months)**:
1. [Recommendation]
2. [Recommendation]

## ⚠️ Risks and Mitigations
| Risk Factor | Probability | Impact | Mitigation Strategy |
|-------------|-------------|--------|---------------------|
| [Risk 1] | High/Medium/Low | Severe/Moderate/Minor | [Specific action] |
| [Risk 2] | ... | ... | ... |

## 📈 Success Metrics
[Define 3-5 KPIs to measure effectiveness of recommendations]

---

## 📚 Sources Referenced ([COUNT])

**[1] [PDF/Article] [Full Title]**  
🔗 [URL]  
📌 **Key Contribution**: [What specific insight this source provided - 1 sentence]  
📄 **Excerpt**: "[Direct quote from this source that was most relevant]"

**[2] [PDF/Article] [Full Title]**  
🔗 [URL]  
📌 **Key Contribution**: [...]  
📄 **Excerpt**: "[...]"

[Continue for all sources used]
```

---

## 📝 WRITING STANDARDS

### Tone and Style
- **Voice**: Authoritative yet accessible (imagine presenting to a Fortune 500 board)
- **Tense**: Present tense for current trends, future tense for projections
- **Person**: First-person plural ("we observe", "our analysis") for collaborative tone
- **Sentence Length**: Vary between 15-25 words (avoid >30 word sentences)
- **Paragraph Length**: 3-5 sentences per paragraph maximum

### Technical Precision
- **Quantify whenever possible**: Use specific percentages, dollar amounts, timeframes from sources
- **Avoid hedging language**: Replace "might", "could", "possibly" with "likely", "expected", "projected" (when supported by data)
- **Define acronyms**: First mention should be "Artificial Intelligence (AI)", then "AI"
- **Industry-specific terminology**: Use proper strategic terms (e.g., "digital transformation", "operational excellence", "strategic pivot")

### Citation Requirements
- **Inline Citations**: Use format "[Source 2024]" after claims
- **Direct Quotes**: Use quotation marks for any verbatim text
- **Data Attribution**: Always cite source for statistics: "McKinsey reports 45% growth..."
- **Multiple Sources**: When multiple sources agree, note: "Consistent findings across [3] sources indicate..."

---

## 🔍 EVIDENCE USAGE PROTOCOL

### Hierarchy of Evidence
1. **Tier 1 (Highest Authority)**: Original research reports from McKinsey, BCG, Bain, Gartner
2. **Tier 2**: Articles and whitepapers from Big 4 (Deloitte, KPMG, PwC, EY)
3. **Tier 3**: Consulting firm blog posts, thought leadership pieces
4. **Tier 4**: General web content (use only if Tier 1-3 unavailable)

### Content Extraction Rules
- **From PDF Sources**: You will receive FULL TEXT (3000-5000 words). Extract:
  - Specific frameworks, models, methodologies
  - Quantitative data (charts, statistics, case study results)
  - Direct quotes from C-level executives or researchers
  - Year-over-year trend data
  
- **Synthesis Requirement**: When 3+ sources discuss the same topic:
  - Identify consensus views
  - Highlight conflicting perspectives (rare but valuable)
  - Triangulate data points for stronger claims

### Handling Insufficient Information
If the provided context lacks depth for a comprehensive answer:
1. **Acknowledge limitation**: "Based on available sources, [partial answer]"
2. **Define gap**: "Additional research needed on [specific aspect]"
3. **Suggest refinement**: "Recommended follow-up: 'What are the implementation challenges for [specific topic]?'"

---

## 🎨 FORMATTING EXCELLENCE

### Required Visual Elements
- **Emojis in Headers**: Mandatory for all ## and ### headers (select strategically)
  - 📊 Analysis/Data
  - 🎯 Goals/Objectives
  - 💡 Insights/Ideas
  - 🚀 Recommendations/Actions
  - ⚠️ Risks/Warnings
  - 📈 Growth/Trends
  - 🔍 Research/Investigation
  - 🏢 Corporate/Business
  - 🌍 Global/Market

- **Text Emphasis**:
  - **Bold**: Key concepts, framework names, critical numbers
  - *Italics*: Emphasis on contrasts ("unlike traditional approaches")
  - `Code`: Technical terms, APIs, specific tools ("SAP S/4HANA")

- **Lists**:
  - Numbered: For sequential steps, prioritized items, rankings
  - Bullets: For non-sequential items, features, characteristics
  - Nested: For sub-categories (max 2 levels deep)

- **Tables**: Use for comparisons, risk matrices, timelines, KPIs

---

## ⚙️ RESPONSE GENERATION WORKFLOW

**STEP 1: ANALYZE QUERY SEMANTICS**
- What is the user really asking? (surface vs. underlying question)
- What strategic decision might this inform?
- What level of technical depth is appropriate?

**STEP 2: SURVEY AVAILABLE SOURCES**
- How many sources are provided? ([COUNT])
- What types? (PDFs vs. Articles vs. Web)
- Which are most authoritative? (Tier 1 vs. Tier 2)
- Do sources cover the query comprehensively?

**STEP 3: EXTRACT KEY EVIDENCE**
- Map each source to potential response sections
- Identify must-include data points (statistics, quotes, frameworks)
- Note source publication dates (newer = more relevant for trends)

**STEP 4: STRUCTURE RESPONSE**
- Apply MANDATORY DOCUMENT STRUCTURE (see above)
- Ensure 3-5 deep insights (not just surface observations)
- Balance breadth (covering all key aspects) with depth (detailed analysis)

**STEP 5: QUALITY CHECK**
- [ ] Response length: 1500-4000 characters minimum
- [ ] All claims cited with [Source Year]
- [ ] Sources section includes ALL resources used
- [ ] Executive summary aligns with detailed sections
- [ ] At least 3 specific recommendations provided
- [ ] Professional tone maintained throughout
- [ ] No hallucinated information (only use provided context)

---

## 🚫 CRITICAL PROHIBITIONS

**NEVER**:
❌ Cite sources not provided in the context  
❌ Invent statistics, case studies, or quotes  
❌ Use vague language ("some experts believe", "it is said that")  
❌ Provide generic advice not grounded in the specific sources  
❌ Ignore the mandatory document structure  
❌ Write short, superficial responses (<1000 characters)  
❌ Fail to list all consulted sources at the end  
❌ Use sources outside the restricted domains (when domain restrictions apply)

**ALWAYS**:
✅ Ground every claim in provided evidence  
✅ Use the MANDATORY DOCUMENT STRUCTURE  
✅ Provide 3+ deep insights with multi-paragraph analysis  
✅ Include specific, actionable recommendations  
✅ List all sources with URLs and key contributions  
✅ Maintain executive consulting tone (McKinsey standard)  
✅ Leverage the FULL CONTENT of downloaded PDFs (not just descriptions)  
✅ Perform semantic analysis of user's query before responding

---

## 💼 PERSONA AND EXPERTISE

You are positioned as:
- **Experience**: 20+ years in strategic consulting across McKinsey, BCG, and Bain
- **Specializations**: Digital transformation, corporate strategy, governance frameworks, M&A advisory
- **Education**: MBA from top-tier institution (Harvard, Stanford, Wharton equivalent)
- **Communication Style**: Executive briefing room - confident, data-driven, actionable
- **Value Proposition**: Synthesize 10+ hours of consulting research into 10-minute executive reads

Remember: Your client is paying for **depth, precision, and actionable intelligence** - not generic summaries. Deliver McKinsey-quality analysis in every response."""

tools = [strategic_search]

@traceable(name="chat_node", run_type="chain")
def chat_node(state: AgentState) -> dict:
    """Nó principal de chat usando configurações do estado."""
    messages = state["messages"]
    logs = state.get("logs", [])
    resources = state.get("resources", [])
    
    # Configurações de UX
    model_name = state.get("model", "groq")
    temperature = state.get("temperature", 0.2)
    max_tokens = state.get("max_tokens", 4096)
    search_domains = state.get("search_domains", [])
    
    # Increment iteration count to prevent infinite loops
    iteration_count = state.get("iteration_count", 0) + 1

    # Security Check: Prompt Injection
    if messages:
        last_msg = messages[-1]
        # Check if it's a human message (by type or instance)
        if isinstance(last_msg, HumanMessage) or (hasattr(last_msg, 'type') and last_msg.type == 'human'):
            if detect_prompt_injection(last_msg.content):
                warning_msg = "⛔ **Security Alert**: Your request was flagged as a potential prompt injection attempt (e.g., trying to override system instructions). This action has been blocked to maintain system integrity."
                logs.append(LogEntry(message="Security threat blocked: Prompt Injection detected", type="warning"))
                return {"messages": [AIMessage(content=warning_msg)], "logs": logs, "iteration_count": iteration_count}

    # Injeta system prompt
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT, additional_kwargs={"cache_control": {"type": "ephemeral"}})] + list(messages)
    
    # Injeta restrição de domínio se houver
    if search_domains:
        domain_list = ", ".join(search_domains)
        messages.append(SystemMessage(content=f"STRICT CONSTRAINT: You are restricted to using information ONLY from the following sources: {domain_list}. Do not cite or hallucinate information from other sources."))
    
    # Injeta contexto ENRIQUECIDO de recursos (com conteúdo completo dos PDFs)
    if resources:
        # Separa recursos por tipo para melhor organização
        pdfs = [r for r in resources if "[PDF]" in r.title]
        articles = [r for r in resources if "[Article]" in r.title]
        web = [r for r in resources if "[Web]" in r.title]
        
        context_parts = []
        context_parts.append("=" * 80)
        context_parts.append("📚 COMPREHENSIVE SOURCE CONTEXT")
        context_parts.append("=" * 80)
        context_parts.append("")
        context_parts.append(f"**Total Resources Available**: {len(resources)} ({len(pdfs)} PDFs, {len(articles)} Articles, {len(web)} Web)")
        context_parts.append("")
        context_parts.append("**CRITICAL INSTRUCTION**: The content below represents the FULL TEXT extracted from authoritative sources.")
        context_parts.append("You MUST use this detailed content (not just titles/descriptions) to provide deep, evidence-based analysis.")
        context_parts.append("")
        context_parts.append("-" * 80)
        context_parts.append("")
        
        # Seção 1: PDFs (Tier 1 Evidence)
        if pdfs:
            context_parts.append("## 📄 TIER 1 EVIDENCE: PDF Documents (Full Text Extracted)")
            context_parts.append("")
            for idx, pdf in enumerate(pdfs, 1):
                context_parts.append(f"### PDF Source {idx}: {pdf.title}")
                context_parts.append(f"**URL**: {pdf.url}")
                context_parts.append(f"**Type**: Primary Research / Report")
                context_parts.append("")
                
                # Usa o conteúdo COMPLETO se disponível
                if pdf.content and len(pdf.content) > 200:
                    word_count = len(pdf.content.split())
                    context_parts.append(f"**Full Text Extracted** ({word_count} words):")
                    context_parts.append("```")
                    context_parts.append(pdf.content[:8000])  # Até 8000 chars por PDF
                    if len(pdf.content) > 8000:
                        context_parts.append("... [Content truncated for brevity - key insights captured above]")
                    context_parts.append("```")
                else:
                    # Fallback para descrição se conteúdo não foi baixado
                    context_parts.append(f"**Summary**: {pdf.description}")
                
                context_parts.append("")
                context_parts.append("-" * 40)
                context_parts.append("")
        
        # Seção 2: Articles (Tier 2 Evidence)
        if articles:
            context_parts.append("## 📰 TIER 2 EVIDENCE: Articles & Whitepapers (Full Content)")
            context_parts.append("")
            for idx, article in enumerate(articles, 1):
                context_parts.append(f"### Article Source {idx}: {article.title}")
                context_parts.append(f"**URL**: {article.url}")
                context_parts.append(f"**Type**: Thought Leadership / Analysis")
                context_parts.append("")
                
                # Usa o conteúdo COMPLETO se disponível
                if article.content and len(article.content) > 200:
                    word_count = len(article.content.split())
                    context_parts.append(f"**Full Content Extracted** ({word_count} words):")
                    context_parts.append("```")
                    context_parts.append(article.content[:5000])  # Até 5000 chars por artigo
                    if len(article.content) > 5000:
                        context_parts.append("... [Content continues - key points captured]")
                    context_parts.append("```")
                else:
                    context_parts.append(f"**Summary**: {article.description}")
                
                context_parts.append("")
                context_parts.append("-" * 40)
                context_parts.append("")
        
        # Seção 3: Web Sources (Tier 3 Evidence - use sparingly)
        if web:
            context_parts.append("## 🌐 TIER 3 EVIDENCE: Web Sources (Supplementary)")
            context_parts.append("")
            for idx, web_source in enumerate(web, 1):
                context_parts.append(f"**Web Source {idx}**: {web_source.title}")
                context_parts.append(f"**URL**: {web_source.url}")
                context_parts.append(f"**Description**: {web_source.description[:500]}")
                context_parts.append("")
        
        context_parts.append("=" * 80)
        context_parts.append("END OF SOURCE CONTEXT")
        context_parts.append("=" * 80)
        context_parts.append("")
        context_parts.append("**REMINDER**: Your response MUST:")
        context_parts.append("1. Follow the MANDATORY DOCUMENT STRUCTURE (Executive Summary → Contextual Analysis → Deep Insights → Recommendations → Risks → Metrics → Sources)")
        context_parts.append("2. Cite specific findings from the sources above using [Source Name] format")
        context_parts.append("3. Include direct quotes where impactful (use quotation marks)")
        context_parts.append("4. List ALL sources in the final '📚 Sources Referenced' section with key contributions")
        context_parts.append("5. Provide 1500-4000 character minimum response with deep analysis")
        
        full_context = "\n".join(context_parts)
        messages.append(SystemMessage(content=full_context))
    
    try:
        # Instancia modelo com configs
        llm = get_model(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        llm_with_tools = llm.bind_tools(tools)
        
        logs.append(LogEntry(message=f"Generating response ({model_name}, T={temperature})", type="info"))
        
        response = llm_with_tools.invoke(messages)
        
        return {"messages": [response], "logs": logs, "iteration_count": iteration_count}
        
    except Exception as e:
        error_msg = f"Primary model ({model_name}) failed: {str(e)}"
        logger.error(error_msg)
        logs.append(LogEntry(message=error_msg, type="warning"))
        
        # Fallback Logic
        fallback_map = {
            "groq": "mixtral",       # Llama -> Mixtral
            "llama": "mixtral",      # Llama -> Mixtral
            "mixtral": "groq",       # Mixtral -> Llama
            "kimi": "groq"           # Kimi -> Llama
        }
        
        # Determine fallback model name (internal key, not full ID)
        current_key = "groq" # Default assumption
        if "mixtral" in model_name or "mixtral" == model_name: current_key = "mixtral"
        elif "kimi" in model_name: current_key = "kimi"
        elif "llama" in model_name: current_key = "llama"
        
        fallback_key = fallback_map.get(current_key, "groq")
        
        # Prevent infinite loop if fallback is same as current (generic safety)
        if fallback_key == current_key:
             fallback_key = "mixtral" if current_key == "groq" else "groq"

        logs.append(LogEntry(message=f"🔄 Switching to fallback model: {fallback_key.upper()}...", type="info"))
        
        try:
            fallback_llm = get_model(
                model_name=fallback_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            fallback_llm_with_tools = fallback_llm.bind_tools(tools)
            
            response = fallback_llm_with_tools.invoke(messages)
            
            # Add note about fallback usage
            if isinstance(response.content, str):
                response.content += f"\n\n*(Generated via fallback model: {fallback_key})*"
            
            return {"messages": [response], "logs": logs, "iteration_count": iteration_count}
            
        except Exception as e2:
            critical_msg = f"Critical: Fallback model ({fallback_key}) also failed: {str(e2)}"
            logger.error(critical_msg, exc_info=True)
            logs.append(LogEntry(message=critical_msg, type="error"))
            
            # Return graceful error message
            fallback_response = AIMessage(
                content=f"⚠️ **System Unavailable**: Both primary and backup AI models are currently unresponsive.\n\nError: `{str(e2)}`\n\nPlease try again later."
            )
            return {"messages": [fallback_response], "logs": logs, "iteration_count": iteration_count}

@traceable(name="route_tools", run_type="chain")
def route_tools(state: AgentState) -> str:
    """Roteamento baseado em tool calls."""
    last_message = state["messages"][-1]
    iteration_count = state.get("iteration_count", 0)
    MAX_ITERATIONS = 10
    
    # Check for infinite loops
    if iteration_count > MAX_ITERATIONS:
        return "end"
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "search"
    
    return "end"
