from typing import Callable, Dict, List, Optional, Any
import copy
import inspect
import asyncio
from .models import WorkflowState, GraphDefinition, ExecutionResult, ExecutionLog

# Type definition for a node function: takes dict, returns dict (updates)
NodeFunction = Callable[[Dict[str, Any]], Dict[str, Any]]

class WorkflowEngine:
    def __init__(self):
        self.tool_registry: Dict[str, NodeFunction] = {}
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, ExecutionResult] = {}

    def register_tool(self, name: str, func: NodeFunction):
        """Registers a Python function as a usable node."""
        self.tool_registry[name] = func

    def register_graph(self, graph_id: str, definition: GraphDefinition):
        """Stores a graph definition."""
        self.graphs[graph_id] = definition

    def get_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        if run_id in self.runs:
            return self.runs[run_id].final_state
        return None

    async def run_workflow(self, run_id: str, graph_id: str, initial_state: Dict[str, Any], step_callback: Optional[Callable[[ExecutionLog], Any]] = None) -> ExecutionResult:
        """
        Executes the workflow graph.
        This is a simplified synchronous execution wrapped in async for the API.
        """
        if graph_id not in self.graphs:
            raise ValueError(f"Graph {graph_id} not found")

        graph = self.graphs[graph_id]
        state = copy.deepcopy(initial_state)
        logs: List[ExecutionLog] = []
        
        # Build adjacency map for O(1) lookups
        # Structure: {node_id: [EdgeDefinition]}
        edges_map: Dict[str, List] = {node.id: [] for node in graph.nodes}
        for edge in graph.edges:
            if edge.from_node in edges_map:
                edges_map[edge.from_node].append(edge)

        current_node_id = graph.start_node
        step_count = 0
        max_steps = 100 # Safety limit for loops

        while current_node_id and step_count < max_steps:
            step_count += 1
            
            # 1. Find the node definition
            node_def = next((n for n in graph.nodes if n.id == current_node_id), None)
            if not node_def:
                break # Should not happen in a valid graph

            # 2. Execute the node's function
            func_name = node_def.function_name
            if func_name not in self.tool_registry:
                raise ValueError(f"Tool {func_name} not found in registry")
            
            tool_func = self.tool_registry[func_name]
            
            # Execute logic
            try:
                if inspect.iscoroutinefunction(tool_func):
                    updates = await tool_func(state)
                else:
                    updates = tool_func(state)
                
                state.update(updates) # Merge updates into shared state
            except Exception as e:
                # In a real engine, we'd handle errors gracefully
                print(f"Error executing node {current_node_id}: {e}")
                break

            # Log execution
            logs.append(ExecutionLog(
                step_id=step_count,
                node_id=current_node_id,
                state_snapshot=copy.deepcopy(state)
            ))
            
            if step_callback:
                # If callback is async, await it; otherwise just call it
                if inspect.iscoroutinefunction(step_callback):
                    await step_callback(logs[-1])
                else:
                    step_callback(logs[-1])

            # 3. Determine next node (Transition logic)
            # Simple priority: First matching condition wins. Default edge (no condition) is fallback.
            next_node_id = None
            possible_edges = edges_map.get(current_node_id, [])
            
            for edge in possible_edges:
                if edge.condition_key:
                    # Conditional branch
                    val = state.get(edge.condition_key)
                    # Python's flexible equality check (e.g. 5 > 3) is hard to encode purely in JSON for this simple assignment
                    # So we will rely on boolean flags or exact matches as per the assignment description:
                    # "if some value in the state is above a threshold" -> often implies the NODE set a flag like "is_quality_good": True
                    
                    # For a truly simple engine, let's support exact match or simple boolean truthiness if value is not specified
                    if edge.condition_value is not None:
                        if val == edge.condition_value:
                            next_node_id = edge.to_node
                            break
                    else:
                        # If no value specified, just check truthiness (useful for flags)
                        if val:
                            next_node_id = edge.to_node
                            break
                else:
                    # Unconditional edge (Default)
                    # We only take this if we haven't matched a specific condition yet? 
                    # Usually default edges are last. Let's assume the user orders them or we treat this as fallback.
                    # For simplicity, if we haven't found a match yet, take this.
                    if next_node_id is None:
                        next_node_id = edge.to_node
            
            # Loop continues with next_node_id
            current_node_id = next_node_id

        result = ExecutionResult(
            run_id=run_id,
            final_state=state,
            logs=logs
        )
        self.runs[run_id] = result
        return result
