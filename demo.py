import asyncio
from app.engine import WorkflowEngine
from app.models import GraphDefinition, NodeDefinition, EdgeDefinition
from app.workflows import register_option_a_nodes
import json

async def main():
    print("Initializing Engine...")
    engine = WorkflowEngine()
    register_option_a_nodes(engine)
    
    # 1. Define Graph
    print("Defining Code Review Graph...")
    graph_id = "test_graph"
    graph = GraphDefinition(
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
            # Loop if issues exist
            EdgeDefinition(from_node="issues", to_node="improve", condition_key="issue_count"), 
            # Loop back
            EdgeDefinition(from_node="improve", to_node="complexity"),
        ],
    )
    engine.register_graph(graph_id, graph)
    
    # 2. Run Workflow
    print("\nRunning Workflow...")
    initial_state = {
        "code": "def foo():\n    import *\n    print('hello')\n    print('world')\n"
    }
    
    result = await engine.run_workflow("run_1", graph_id, initial_state)
    
    print("\n--- Execution Finished ---")
    print(f"Final Complexity: {result.final_state.get('complexity_score')}")
    print(f"Remaining Issues: {result.final_state.get('issue_count')}")
    print(f"Total Steps: {len(result.logs)}")
    
    print("\nStep-by-Step Log:")
    for log in result.logs:
        node = log.node_id
        score = log.state_snapshot.get('complexity_score', 'N/A')
        issues_count = log.state_snapshot.get('issue_count', 'N/A')
        issues = log.state_snapshot.get('issues', [])
        print(f"[{log.step_id}] Node: {node} | Complexity: {score} | Count: {issues_count} | Issues: {issues}")

if __name__ == "__main__":
    asyncio.run(main())
