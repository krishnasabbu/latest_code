from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List
import requests
from simpleeval import simple_eval
import uvicorn

# --------------------------
# FastAPI setup
# --------------------------

app = FastAPI(title="Dynamic JSON Service Node Executor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Mapping Engine
# --------------------------

def apply_mappings(state: dict, mappings: list):
    """
    Apply mappings to produce a node request or modify response
    """
    payload = {}
    for mapping in mappings:
        src_path = mapping["source"].split(".")
        value = state
        for key in src_path:
            value = value.get(key)
            if value is None:
                break
        if value is None:
            continue
        transform = mapping.get("transform")
        if transform == "upper":
            value = str(value).upper()
        elif transform == "lower":
            value = str(value).lower()
        elif transform == "strip":
            value = str(value).strip()
        payload[mapping["target"]] = value
    return payload

# --------------------------
# Node Execution
# --------------------------

def execute_node(node: dict, state: dict):
    """
    Execute a single service node.
    - Apply request mappings from previous node responses
    - Send JSON payload to the service
    - Store JSON response
    """
    # Start with base request
    payload = node.get("request", {}).copy()
    # Apply mappings
    mappings = node.get("mappings", [])
    mapped_payload = apply_mappings(state, mappings)
    payload.update(mapped_payload)

    # Execute HTTP request
    url = node["url"]
    method = node.get("method", "POST").upper()
    try:
        resp = requests.request(method, url, json=payload, timeout=10)
        data = resp.json() if resp.ok else {"error": resp.text}
    except Exception as e:
        data = {"error": str(e)}
    return data

# --------------------------
# Workflow Runner
# --------------------------

def run_workflow(graph_json: dict, initial_input: dict):
    state = {"input": initial_input}
    nodes_by_id = {n["id"]: n for n in graph_json["nodes"]}
    executed_nodes = set()
    current_node_id = graph_json["nodes"][0]["id"]

    while current_node_id:
        node = nodes_by_id[current_node_id]
        # Execute node
        response = execute_node(node, state)
        state[node["id"]] = response
        executed_nodes.add(current_node_id)

        # Determine next node based on edges and conditions
        edges = [e for e in graph_json["edges"] if e["source"] == current_node_id]
        next_node_id = None
        for e in edges:
            cond = e.get("condition")
            if cond:
                try:
                    if simple_eval(cond, names=state):
                        next_node_id = e["target"]
                        break
                except Exception as ex:
                    print("Condition eval error:", ex)
            else:
                next_node_id = e["target"]
                break
        current_node_id = next_node_id

    return state

# --------------------------
# FastAPI Models
# --------------------------

class ExecuteRequest(BaseModel):
    graph: Dict[str, Any]
    inputs: Dict[str, Any] = {}

class ExecuteResponse(BaseModel):
    status: str
    result: Dict[str, Any]

# --------------------------
# API Endpoints
# --------------------------

@app.post("/execute", response_model=ExecuteResponse)
def execute_workflow(req: ExecuteRequest):
    try:
        result = run_workflow(req.graph, req.inputs)
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", result={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Dynamic JSON Service Node Executor running"}

# --------------------------
# Run server
# --------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
