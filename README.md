# StratGov AI Agent - Strategic Research Platform

## Overview

StratGov AI is a high-precision strategic research agent designed to perform autonomous market intelligence gathering. Unlike general-purpose chatbots, this system operates within a strictly controlled search surface, consulting only verified authority domains (Big Four, MBB, Gartner) to generate executive-level reports.

The agent mirrors the workflow of a senior strategy analyst:
1.  **Orchestration**: Analyzes the query to determine necessary information steps.
2.  **Optimized Retrieval**: Checks semantic cache before executing external API calls.
3.  **Deep Ingestion**: Downloads full strategic assets (whitepapers, PDFs).
4.  **Distillation**: Uses specialized smaller models to compress heavily tokened documents into dense insights.
5.  **Synthesis**: Generates verifiable, citation-backed strategic answers.

## Architecture

The system is built on a cyclic graph architecture using **LangGraph**, enabling state persistence and iterative reasoning.

### Core Components

*   **Orchestrator (State Management)**: Manages the conversation state, routing tools, and ensuring memory persistence across the session.
*   **Strategic Search Node**: Utilizes the Tavily API with strict domain filtering (e.g., `site:deloitte.com`, `filetype:pdf`) to retrieve high-value assets.
*   **Optimization Layer**:
    *   **Semantic Cache**: A local file-based cache (`.agent_cache/`) that stores search results and distilled document contents to minimize latency and API costs.
    *   **Document Distiller**: An asynchronous sub-process that uses cost-efficient models (e.g., GPT-4o-mini) to summarize raw PDF text into structured insights before context injection.
*   **Synthesis Engine**: The final generation step where the primary LLM integrates distilled contexts to produce the final output.

## Technical Requirements

*   **Python**: 3.10+
*   **LLM Provider**: OpenAI (GPT-4o) or Groq (Llama-3/Mixtral)
*   **Search Provider**: Tavily API
*   **Observability**: AgentOps / LangSmith (Optional)

## Directory Structure

```text
/Strategic
├── src/
│   ├── agents/         # LangGraph state management and core logic
│   ├── tools/          # External capability integrations (Search, PDF Processing)
│   ├── optimization/   # Performance modules (Distiller, Caching)
│   ├── ui/             # Frontend interfaces (Streamlit)
│   └── api/            # Server endpoints (FastAPI)
├── config/             # Configuration templates
├── main.py             # Application entry point
└── requirements.txt    # Dependency definitions
```

## Setup and Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/DaniloBlancoMotta/Tavily_Langgraph_Estrategic.git
    cd Tavily_Langgraph_Estrategic
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```ini
    # Core Keys
    OPENAI_API_KEY=sk-...
    TAVILY_API_KEY=tvly-...
    GROQ_API_KEY=gsk-...

    # Observability (Optional)
    AGENTOPS_API_KEY=...
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=...
    ```

## Usage

### Streamlit Interface (Default)
Launches the interactive web interface for research sessions.

```bash
python main.py streamlit
```

### API Server
Starts the FastAPI server for headless integrations.

```bash
python main.py server
```

## Optimization Strategy

To ensure production viability, the agent implements a "Minimal Runtime Footprint" strategy:

1.  **Token Reduction**: The *Document Distiller* reduces context size by approximately 85% for large PDFs, extracting only statistical data and strategic findings.
2.  **Latency Management**: The *Semantic Cache* creates a zero-latency path for recurrent queries.
3.  **Model Routing**: The system dynamically selects lighter models for classification/summarization tasks and reserves stronger models for final synthesis.

## Security

*   **Runtime Isolation**: Execution environment is stripped of development artifacts.
*   **Secret Management**: All credentials managed via environment variables; no hardcoded keys.
*   **Domain Whitelisting**: Search operations are contractually bound to specific high-authority domains, preventing hallucination from untrusted sources.
