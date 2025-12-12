# StratGov AI Agent

**StratGov AI** is an advanced autonomous agent designed to act as a Senior Strategy & Governance Consultant. It leverages the LangGraph framework and Large Language Models (LLMs) like Llama 3 to provide deep, evidence-based strategic advice.

## Features

-   **Strategic Search**: Uses Tavily API to search only trusted domains (McKinsey, BCG, Bain, Gartner, etc.).
-   **Agentic Workflow**: Cyclic state graph (LangGraph) that helps the agent "think", search, and refine answers.
-   **Multi-Model Support**: Validated with Llama 3.3 70B (Groq) and other models.
-   **Professional Persona**: Engineered to deliver executive-level consulting outputs.

## Project Structure

-   `agent.py`: Main LangGraph definition (Nodes & Edges).
-   `chat.py`: Chat logic and system prompting.
-   `search.py`: Tavily search integration with domain filtering.
-   `download.py`: Async content fetcher for deep reading of search results.
-   `server.py`: FastAPI server to expose the agent.
-   `frontend/`: Next.js application for the user interface.

## Prerequisites

-   Python 3.10+
-   Node.js 18+
-   Groq API Key
-   Tavily API Key

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DaniloBlancoMotta/StratGov_AI_Agent.git
    cd StratGov_AI_Agent
    ```

2.  **Backend Setup:**
    ```bash
    # Create virtual environment (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Environment Configuration:**
    Create a `.env` file in the root directory (see `.env.example`):
    ```env
    GROQ_API_KEY=your_groq_key
    TAVILY_API_KEY=your_tavily_key
    ```

4.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

1.  **Start the Backend Server:**
    ```bash
    # In the root directory
    python server.py
    ```

2.  **Start the Frontend:**
    ```bash
    # In the frontend directory
    npm run dev
    ```

    Open [http://localhost:3000](http://localhost:3000) to interact with the agent.
