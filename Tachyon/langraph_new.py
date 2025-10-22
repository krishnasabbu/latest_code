from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END
import requests
import uvicorn
from simpleeval import simple_eval

# -------------------------------------------------------------------
# FastAPI setup
# -------------------------------------------------------------------

app = FastAPI(title="Dynamic JSON Service Node Executor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Node Execution Factory
# -------------------------------------------------------------------

def make_service_node(node_data: Dict[str, Any]):
    """
    Service Node executes an HTTP request.
    Supports multiple mappings from previous node responses.
    """
    url = node_data["data"]["url"]
    method = node_data["data"].get("method", "POST").upper()
    request_template = node_data["data"].get("request", {})
    mappings = node_data["data"].get("mappings", [])

    def run_fn(state: Dict[str, Any]):
        # Apply all mappings
        payload = request_template.copy()
        for m in mappings:
            src_path = m["source"].split(".")
            value = state
            for k in src_path:
                value = value.get(k)
                if value is None:
                    break
            if value is None:
                continue
            transform = m.get("transform")
            if transform == "upper":
                value = str(value).upper()
            elif transform == "lower":
                value = str(value).lower()
            elif transform == "strip":
                value = str(value).strip()
            payload[m["target"]] = value

        # Execute HTTP request
        try:
            resp = requests.request(method, url, json=payload, timeout=10)
            data = resp.json() if resp.ok else {"error": resp.text}
        except Exception as e:
            data = {"error": str(e)}
        return data

    return run_fn

NODE_FACTORY = {
    "service": make_service_node
}

# -------------------------------------------------------------------
# Graph Builder
# -------------------------------------------------------------------

def build_graph_from_json(graph_json: Dict[str, Any]):
    g = StateGraph(dict)

    # Step 1: Add nodes
    for node in graph_json["nodes"]:
        ntype = node["type"]
        if ntype not in NODE_FACTORY:
            raise ValueError(f"Unknown node type: {ntype}")
        func = NODE_FACTORY[ntype](node)
        g.add_node(node["id"], func)

    # Step 2: Add edges (support multiple conditional edges per node)
    edges_by_source = {}
    for e in graph_json["edges"]:
        edges_by_source.setdefault(e["source"], []).append(e)

    for source, edges in edges_by_source.items():
        # If there is any condition on the edges
        if any("condition" in e for e in edges):
            def conditional_fn(state, edges=edges):
                for edge in edges:
                    cond = edge.get("condition")
                    if cond:
                        try:
                            if simple_eval(cond, names=state):
                                return edge["target"]
                        except Exception as ex:
                            print("Condition eval error:", ex)
                # fallback: if an edge without condition exists
                for e in edges:
                    if "condition" not in e:
                        return e["target"]
                return None
            g.add_conditional_edges(source, conditional_fn)
        else:
            for e in edges:
                g.add_edge(e["source"], e["target"])

    # Step 3: Entry/Exit
    entry = graph_json["nodes"][0]["id"]
    g.set_entry_point(entry)
    g.add_edge(graph_json["nodes"][-1]["id"], END)

    return g.compile()

# -------------------------------------------------------------------
# FastAPI Models
# -------------------------------------------------------------------

class ExecuteRequest(BaseModel):
    graph: Dict[str, Any]
    inputs: Dict[str, Any] = {}

class ExecuteResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    logs: Optional[List[str]] = None

# -------------------------------------------------------------------
# API Endpoint
# -------------------------------------------------------------------

@app.post("/execute", response_model=ExecuteResponse)
def execute_workflow(req: ExecuteRequest):
    try:
        graph = build_graph_from_json(req.graph)
        result = graph.invoke(req.inputs)
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", result={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Dynamic JSON Service Node Executor running"}

# -------------------------------------------------------------------
# Example JSON Workflow
# -------------------------------------------------------------------

example_flow = {
    "nodes": [
        {
            "id": "n1",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {"msg": "{input.message}"},
                "mappings": []
            }
        },
        {
            "id": "n2",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {},
                "mappings": [
                    {"source": "n1.json.msg", "target": "upper_msg", "transform": "upper"},
                    {"source": "n1.json.msg", "target": "lower_msg", "transform": "lower"}
                ]
            }
        },
        {
            "id": "n3",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {},
                "mappings": [
                    {"source": "n1.json.msg", "target": "original_msg"}
                ]
            }
        }
    ],
    "edges": [
        {"source": "n1", "target": "n2", "condition": "input.message.startswith('H')"},
        {"source": "n1", "target": "n3", "condition": "input.message.startswith('B')"}
    ]
}
