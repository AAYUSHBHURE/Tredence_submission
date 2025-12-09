import random
from typing import Dict, Any

# --- Option A: Code Review Mini-Agent Nodes ---

def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates extracting functions from code."""
    # In a real scenario, this would parse an AST.
    print("  [Node] Extracting functions...")
    code = state.get("code", "")
    # Mock behavior: Split by "def " just to have something
    count = code.count("def ")
    return {"function_count": count, "extracted": True}

def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates a fake complexity score."""
    print("  [Node] Checking complexity...")
    # Mock behavior: random score between 1 and 10 + function count magnitude
    base = random.randint(1, 5)
    score = base + state.get("function_count", 0)
    return {"complexity_score": score}

def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detects bad patterns."""
    code = state.get("code", "")
    improvements = state.get("improvements_made", 0)
    if improvements > 3:
        print("  [Node] Forced exit: improvements limit reached.")
        return {"issues": [], "issue_count": 0}
        
    issues = []
    if "import *" in code:
        issues.append("Avoid wildcard imports")
    if "print(" in code: # strict linter!
        issues.append("Use logging instead of print")
    
    print(f"  [Node] Detecting issues... Found {len(issues)}: {issues}", flush=True)
    return {"issues": issues, "issue_count": len(issues)}

def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """Suggests fixes and 'improves' the code to lower complexity."""
    print("  [Node] Suggesting improvements...")
    current_score = state.get("complexity_score", 100)
    
    # Simulate improvement by lowering the score
    new_score = max(0, current_score - 2)
    
    # Also clear some issues to simulate fixing
    issues = state.get("issues", [])
    code = state.get("code", "")
    
    if issues:
        fixed_issue = issues.pop()
        # Mock fix: remove the triggering pattern from code
        if "wildcard" in fixed_issue:
            code = code.replace("import *", "# import * (fixed)")
        elif "print" in fixed_issue:
            code = code.replace("print(", "log(")
            
                    
    return {
        "complexity_score": new_score, 
        "issues": issues,
        "issue_count": len(issues),
        "improvements_made": state.get("improvements_made", 0) + 1,
        "code": code
    }

# --- Registry Helper ---
def register_option_a_nodes(engine):
    engine.register_tool("extract_functions", extract_functions)
    engine.register_tool("check_complexity", check_complexity)
    engine.register_tool("detect_issues", detect_issues)
    engine.register_tool("suggest_improvements", suggest_improvements)
