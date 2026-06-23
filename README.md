# Omni-Agent: Enterprise Knowledge & Operations Engine

## Overview
Omni-Agent is a production-ready, enterprise-grade AI architecture using a FastAPI asynchronous gateway. It features a custom ReAct loop, Vector RAG (ChromaDB), and GraphRAG (NetworkX) with a secondary Guardrail Proxy.

## Architectural Paradigm
The system is built on a non-blocking asynchronous event loop to handle concurrent agentic requests without I/O bottlenecks.

## The Architecture (The 5 Phases of Enterprise AI)

This project integrates five advanced AI Engineering patterns into a single FastAPI backend:

1. **Agentic Workflows (The Brain):** Implements a custom ReAct (Reason + Act) loop. The agent autonomously decides which tools to call, processes the results, and course-corrects. It features a Universal Output Parser to handle model drift and rogue XML/JSON tool-call formatting.
2. **Vector RAG (The Knowledge):** Utilizes **ChromaDB** to securely store and semantically search company documents, eliminating LLM hallucinations regarding internal policies and coding standards.
3. **GraphRAG (The Logic):** Utilizes **NetworkX** to build a Directed Knowledge Graph of the company's organizational chart. It performs N-hop sub-graph extractions to answer complex relational queries (e.g., "Who knows Rust in the Backend department?").
4. **Structured Outputs (The Integrator):** Uses **Pydantic** to force the LLM to synthesize its final findings into a strict JSON schema, ensuring downstream APIs and UIs do not crash due to unstructured text.
5. **Guardrail Proxy (The Shield):** Implements an "LLM-as-a-Judge" safety layer. A secondary, isolated model evaluates the agent's draft response against strict corporate policies (no legal/financial advice, no harmful content) before the user ever sees it.

## Tech Stack
* **Framework:** FastAPI / Python 3.10+
* **LLM Orchestration:** Ollama Cloud (qwen3-next:80b-cloud, gemma4:31b-cloud)
* **Vector Database:** ChromaDB + Sentence-Transformers
* **Graph Database:** NetworkX
* **Data Validation:** Pydantic

## Repository Structure
```
omni-agent/
│
├── database/
│   ├── __init__.py
│   ├── vector_db.py          # ChromaDB initialization & mock data
│   └── graph_db.py           # NetworkX graph initialization & metadata
│
├── core/
│   ├── __init__.py
│   ├── schemas.py            # Pydantic models for API responses
│   ├── tools.py              # Vector/Graph execution functions
│   ├── agent.py              # The ReAct Loop & Schema Synthesizer
│   └── guardrail.py          # Dual-model safety evaluation
│
├── main.py                   # FastAPI application router
├── requirements.txt          
└── .env                      # API Keys & Environment Variables
```

## Setup Instructions

1. **Clone the repository:**
   git clone <your-repo-url>

2. **Create and activate a virtual environment:**
   - Windows: python -m venv .venv and .venv\Scripts\activate
   - Mac/Linux: python3 -m venv .venv and source .venv/bin/activate

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Configure Environment:**
   Create a .env file in the root directory and add your Ollama Cloud API Key:
   OLLAMA_API_KEY=your_api_key_here

## Usage

1. **Start the FastAPI Server:**
   uvicorn main:app --reload

2. **Access the Interactive UI:**
   Open your browser and navigate to http://127.0.0.1:8000/docs to access the interactive Swagger UI.

3. **Test the Endpoint:**
   Expand the POST /api/chat route and test the agent with a complex query:
   *Prompt: "I want to build a new feature using Rust. What are the rules, and who in the Backend department can I ask for help?"*

## Watch the Terminal
As the request processes, monitor your terminal to see the Enterprise Pipeline in action:
1. Agent begins ReAct loop.
2. Agent triggers Document Tool (Vector RAG).
3. Agent triggers Org Chart Tool (GraphRAG).
4. Agent synthesizes JSON payload.
5. Guardrail evaluates and approves/blocks payload.
6. 200 OK Response returned to UI.