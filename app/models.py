from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

class WorkflowState(BaseModel):
    """
    Represents the shared state of the workflow.
    Using a flexible dictionary to allow arbitrary data flow.
    """
    data: Dict[str, Any] = Field(default_factory=dict)
    
class NodeDefinition(BaseModel):
    id: str
    function_name: str # The name of the function in the tool registry

class EdgeDefinition(BaseModel):
    from_node: str
    to_node: str
    condition_key: Optional[str] = None # If present, check state[condition_key]
    condition_value: Optional[Any] = None # Jump to 'to_node' if state[key] == value (simple equality)
    # For more complex branching, we might register specific condition functions, 
    # but for this assignment, simple key-value matching or specific "next" logic is often enough.

class GraphDefinition(BaseModel):
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str

class ExecutionLog(BaseModel):
    step_id: int
    node_id: str
    state_snapshot: Dict[str, Any]

class ExecutionResult(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    logs: List[ExecutionLog]
