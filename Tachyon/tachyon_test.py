from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END
from simpleeval import simple_eval
import requests
import uvicorn
import re
from copy import deepcopy

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
# Node Factory (Service Node)
# -------------------------------------------------------------------

def make_service_node(node_data: Dict[str, Any]):
    """
    Service Node executes an HTTP request dynamically.
    - Supports {input.key} and {prevnode.response.key} placeholders
    - Applies mappings from previous nodes
    - Returns both request and response
    """
    data = node_data.get("data", node_data)
    url = data.get("url")
    method = data.get("method", "POST").upper()
    request_template = data.get("request", {})
    mappings = data.get("mappings", [])

    if not url:
        raise ValueError(f"Node {node_data.get('id')} missing 'url'")

    # ---------------- Helper: placeholder substitution ----------------
    def substitute_placeholders(obj, context):
        if isinstance(obj, str):
            # Replace {a.b.c} patterns
            def replacer(match):
                expr = match.group(1)
                value = context
                for key in expr.split("."):
                    if isinstance(value, dict):
                        value = value.get(key)
                    else:
                        value = None
                        break
                return str(value) if value is not None else match.group(0)
            return re.sub(r"{([^{}]+)}", replacer, obj)
        elif isinstance(obj, dict):
            return {k: substitute_placeholders(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [substitute_placeholders(v, context) for v in obj]
        else:
            return obj

    # ---------------- Node Execution ----------------
    def run_fn(state: Dict[str, Any]):
        # Merge state into context
        context = deepcopy(state)
        if "input" not in context:
            context["input"] = {}

        payload = deepcopy(request_template)

        # Apply mappings first
        for m in mappings:
            src_path = m.get("source")
            tgt_path = m.get("target")
            transform = m.get("transform")
            if not src_path or not tgt_path:
                continue

            # Deep get
            value = context
            for k in src_path.split("."):
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = None
                    break

            if value is None:
                continue

            if transform == "upper":
                value = str(value).upper()
            elif transform == "lower":
                value = str(value).lower()
            elif transform == "strip":
                value = str(value).strip()

            payload[tgt_path] = value

        # Replace placeholders like {input.message}
        payload = substitute_placeholders(payload, context)

        # Execute HTTP request
        try:
            resp = requests.request(method, url, json=payload, timeout=10)
            resp_data = resp.json() if resp.ok else {"error": resp.text}
        except Exception as e:
            resp_data = {"error": str(e)}

        return {node_data["id"]: {"request": payload, "response": resp_data}}

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

    # Step 2: Add edges with multiple condition handling
    edges_by_source = {}
    for e in graph_json["edges"]:
        edges_by_source.setdefault(e["source"], []).append(e)

    for source, edges in edges_by_source.items():
        if any("condition" in e for e in edges):
            def conditional_fn(state, edges=edges):
                for edge in edges:
                    cond = edge.get("condition")
                    if cond:
                        try:
                            if simple_eval(cond, names=state):
                                return edge["target"]
                        except Exception as ex:
                            print(f"Condition error on {source} → {edge['target']}: {ex}")
                # fallback (no matching condition)
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
# Endpoint
# -------------------------------------------------------------------

@app.post("/execute", response_model=ExecuteResponse)
def execute_workflow(req: ExecuteRequest):
    try:
        graph = build_graph_from_json(req.graph)
        result = graph.invoke({"input": req.inputs})
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", result={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Dynamic JSON Service Node Executor running"}

# -------------------------------------------------------------------
# Example Flow
# -------------------------------------------------------------------

example_flow = {
    "nodes": [
        {
            "id": "n1",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {"msg": "{input.message}"}
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
                    {"source": "n1.response.json.msg", "target": "upper_msg", "transform": "upper"},
                    {"source": "n1.response.json.msg", "target": "lower_msg", "transform": "lower"}
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
                    {"source": "n1.response.json.msg", "target": "original_msg"}
                ]
            }
        }
    ],
    "edges": [
        {"source": "n1", "target": "n2", "condition": "input.message.startswith('H')"},
        {"source": "n1", "target": "n3", "condition": "input.message.startswith('B')"}
    ]
}

# -------------------------------------------------------------------
# Run Server
# -------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
