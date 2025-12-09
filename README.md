# Minimal Agent Workflow Engine

This is a lightweight Python backend for defining and executing agentic workflows.

## Features
- **Graph Engine**: Supports DAGs, Branching, and Looping.
- **State Management**: Shared dictionary state flowing between nodes.
- **Tool Registry**: Simple function registration system.
- **FastAPI**: Endpoints to create and run workflows.
- **Sample Agent**: "Code Review" workflow (Option A) fully implemented.

## Project Structure
```
ai_assignment/
├── app/
│   ├── main.py          # FastAPI Entry Point
│   ├── engine.py        # Core Workflow Engine
│   ├── models.py        # Pydantic Models
│   └── workflows.py     # Sample "Code Review" Nodes
├── demo.py              # CLI Demo Script
└── requirements.txt     # Dependencies
```

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

2. **Run the CLI Demo**:
   Execute the sample Code Review workflow in your terminal:
   ```bash
   python demo.py
   ```

3. **Run the API Server**:
   Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

   - **Interact via Swagger UI**: Go to `http://127.0.0.1:8000/docs`
   - **Endpoints**:
     - `POST /graph/run`: Run the pre-loaded `code_review_v1` graph.
     - `GET /graph/state/{run_id}`: Check status.
     - `WS /ws/graph/run`: WebSocket endpoint for streaming logs.

   - **Test WebSocket Streaming**:
     Make sure the server is running, then run the test client:
     ```bash
     python ws_test.py
     ```

## Workflow Supported
**Code Review Mini-Agent**:
1. `extract`: Extracts functions (mock).
2. `complexity`: Calculates complexity score.
3. `issues`: Detects style issues ("import *", "print").
4. `improve`: Fixes issues and loops back to check complexity.
5. EXITS when issues are resolved (or safety limit reached).

## Improvements 
- **Persistent Storage**: Use SQLite/Postgres for run history.
- **Async Nodes**: Fully async node execution for long LLM calls.
- **Dynamic Registry**: API to register new Python functions dynamically (via code upload or plugin system).
- **Better Conditions**: A rich expression language for edge conditions (e.g. `state.score > 5`).
