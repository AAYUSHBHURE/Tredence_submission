import asyncio
import websockets
import json

async def test_websocket_run():
    uri = "ws://127.0.0.1:8000/ws/graph/run"
    request = {
        "graph_id": "code_review_v1",
        "initial_state": {
            "code": "def test():\n    import *\n    print('debugging')\n"
        }
    }

    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send Request
            await websocket.send(json.dumps(request))
            print("Request sent. Waiting for logs...")

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    msg_type = data.get("type")
                    if msg_type == "start":
                        print(f"--- Workflow Started (Run ID: {data['run_id']}) ---")
                    elif msg_type == "log":
                        print(f"[Step {data['step_id']}] Node: {data['node_id']} | State keys: {list(data['state_snapshot'].keys())}")
                        if "issues" in data["state_snapshot"]:
                             print(f"      Issues: {data['state_snapshot']['issues']}")
                    elif msg_type == "result":
                        print("\n--- Execution Finished ---")
                        print("Final State:", json.dumps(data['final_state'], indent=2))
                        break
                    elif "error" in data:
                        print("Error:", data["error"])
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed.")
                    break
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure the uvicorn server is running: 'uvicorn app.main:app --reload'")

if __name__ == "__main__":
    asyncio.run(test_websocket_run())
