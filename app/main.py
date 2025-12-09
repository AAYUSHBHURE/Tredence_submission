from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import asyncio
import json

from .engine import WorkflowEngine, ExecutionLog
from .models import GraphDefinition, NodeDefinition, EdgeDefinition, ExecutionResult
from .workflows import register_option_a_nodes

app = FastAPI(title="Mini Agent Workflow Engine")

# Initialize Engine
engine = WorkflowEngine()

# Register Tools
register_option_a_nodes(engine)

# --- Pre-register Option A Graph ---
CODE_REVIEW_GRAPH_ID = "code_review_v1"
code_review_graph = GraphDefinition(
    start_node="extract",
    nodes=[
        NodeDefinition(id="extract", function_name="extract_functions"),
        NodeDefinition(id="complexity", function_name="check_complexity"),
        NodeDefinition(id="issues", function_name="detect_issues"),
        NodeDefinition(id="improve", function_name="suggest_improvements"),
    ],
    edges=[
        EdgeDefinition(from_node="extract", to_node="complexity"),
        EdgeDefinition(from_node="complexity", to_node="issues"),
        EdgeDefinition(from_node="issues", to_node="improve", condition_key="issue_count", condition_value=None), 
        EdgeDefinition(from_node="improve", to_node="complexity"),
    ]
)
engine.register_graph(CODE_REVIEW_GRAPH_ID, code_review_graph)


# --- API Models ---
class CreateGraphRequest(BaseModel):
    definition: GraphDefinition

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


# --- Endpoints ---

@app.post("/graph/create")
async def create_graph(request: CreateGraphRequest):
    """Register a new graph definition."""
    graph_id = str(uuid.uuid4())
    engine.register_graph(graph_id, request.definition)
    return {"graph_id": graph_id, "message": "Graph created successfully"}

@app.post("/graph/run")
async def run_graph_endpoint(request: RunGraphRequest):
    """Execute a workflow (Synchronous/Blocked)."""
    if request.graph_id not in engine.graphs:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    run_id = str(uuid.uuid4())
    try:
        result = await engine.run_workflow(run_id, request.graph_id, request.initial_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/graph/run")
async def websocket_run(websocket: WebSocket):
    """
    WebSocket endpoint to run a graph and stream logs.
    Send JSON: {"graph_id": "...", "initial_state": {...}}
    Receive: Stream of JSON logs, followed by final result.
    """
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        try:
            payload = json.loads(data)
            graph_id = payload.get("graph_id")
            initial_state = payload.get("initial_state", {})
        except json.JSONDecodeError:
             await websocket.send_json({"error": "Invalid JSON"})
             await websocket.close()
             return

        if not graph_id or graph_id not in engine.graphs:
            await websocket.send_json({"error": "Graph not found"})
            await websocket.close()
            return

        run_id = str(uuid.uuid4())
        await websocket.send_json({"type": "start", "run_id": run_id})

        async def ws_logger(log: ExecutionLog):
            # Send log to client
            # We serialize pydantic model to dict
            await websocket.send_json({
                "type": "log",
                "step_id": log.step_id,
                "node_id": log.node_id,
                "state_snapshot": log.state_snapshot
            })
            # Add a small artificial delay to make the streaming visible/aesthetic
            await asyncio.sleep(0.5) 

        # Run workflow with callback
        result = await engine.run_workflow(run_id, graph_id, initial_state, step_callback=ws_logger)
        
        await websocket.send_json({
            "type": "result",
            "final_state": result.final_state
        })
        await websocket.close()

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        # Try to send error if still connected
        try:
            await websocket.send_json({"error": str(e)})
            await websocket.close()
        except:
            pass

@app.get("/graph/state/{run_id}")
async def get_run_state(run_id: str):
    state = engine.get_run_state(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return {"run_id": run_id, "state": state}

@app.get("/")
async def root():
    return {
        "message": "Workflow Engine Ready",
        "preloaded_graphs": list(engine.graphs.keys())
    }
