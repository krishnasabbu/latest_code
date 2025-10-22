from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END
from simpleeval import simple_eval
import requests
import uvicorn
import re
import copy

# -------------------------------------------------------------------
# FastAPI setup
# -------------------------------------------------------------------

app = FastAPI(title="Dynamic JSON Workflow + Drools Executor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Utility: Recursive lookup and template substitution
# -------------------------------------------------------------------

def deep_get(data: Dict[str, Any], path: str):
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        elif isinstance(data, list):
            try:
                idx = int(key)
                data = data[idx]
            except Exception:
                return None
        else:
            return None
    return data


def render_template(obj: Any, context: Dict[str, Any]):
    if isinstance(obj, str):
        matches = re.findall(r"\{([^{}]+)\}", obj)
        for m in matches:
            val = deep_get(context, m.strip())
            if val is not None:
                obj = obj.replace("{" + m + "}", str(val))
        return obj
    elif isinstance(obj, dict):
        return {k: render_template(v, context) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_template(v, context) for v in obj]
    return obj

# -------------------------------------------------------------------
# Node: Service Node
# -------------------------------------------------------------------

def make_service_node(node_data: Dict[str, Any]):
    url = node_data["data"]["url"]
    method = node_data["data"].get("method", "POST").upper()
    request_template = node_data["data"].get("request", {})
    mappings = node_data["data"].get("mappings", [])

    def run_fn(state: Dict[str, Any]):
        payload = render_template(copy.deepcopy(request_template), state)

        # Apply explicit mappings
        for m in mappings:
            val = deep_get(state, m["source"])
            if val is not None:
                if transform := m.get("transform"):
                    if transform == "upper":
                        val = str(val).upper()
                    elif transform == "lower":
                        val = str(val).lower()
                    elif transform == "strip":
                        val = str(val).strip()
                payload[m["target"]] = val

        try:
            resp = requests.request(method, url, json=payload, timeout=10)
            data = resp.json() if resp.ok else {"error": resp.text}
        except Exception as e:
            data = {"error": str(e)}

        state[node_data["id"]] = data
        return state

    return run_fn

# -------------------------------------------------------------------
# Node: Drools / Decision Node
# -------------------------------------------------------------------

def make_decision_node(node_data: Dict[str, Any]):
    data = node_data.get("data", {})
    rules = data.get("rules", [])
    script = data.get("script")

    def run_fn(state: Dict[str, Any]):
        new_state = state.copy()

        # Rule-based evaluation
        if rules:
            for rule in rules:
                cond = rule.get("condition")
                try:
                    if simple_eval(cond, names={"state": new_state}):
                        action = rule.get("action", {})
                        if isinstance(action, dict):
                            new_state.update(action)
                except Exception as e:
                    print(f"[DecisionNode-Rules] Condition error: {e}")

        # Script mode (multi-line Python)
        if script:
            try:
                local_env = {"state": new_state}
                exec(script, {}, local_env)
                new_state = local_env.get("state", new_state)
            except Exception as e:
                print(f"[DecisionNode-Script] Script error: {e}")

        return new_state

    return run_fn

# -------------------------------------------------------------------
# Node Factory
# -------------------------------------------------------------------

NODE_FACTORY = {
    "service": make_service_node,
    "decision": make_decision_node,
}

# -------------------------------------------------------------------
# Graph Builder
# -------------------------------------------------------------------

def build_graph_from_json(graph_json: Dict[str, Any]):
    g = StateGraph(dict)

    for node in graph_json["nodes"]:
        ntype = node["type"]
        func = NODE_FACTORY[ntype](node)
        g.add_node(node["id"], func)

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
                            if simple_eval(cond, names={"state": state}):
                                return edge["target"]
                        except Exception as ex:
                            print("Condition eval error:", ex)
                for e in edges:
                    if "condition" not in e:
                        return e["target"]
                return None
            g.add_conditional_edges(source, conditional_fn)
        else:
            for e in edges:
                g.add_edge(e["source"], e["target"])

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
        state = {"input": req.inputs}
        graph = build_graph_from_json(req.graph)
        result = graph.invoke(state)
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", result={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Dynamic JSON + Drools Executor running"}

# -------------------------------------------------------------------
# Example Graph JSON
# -------------------------------------------------------------------

example_graph = {
    "nodes": [
        {
            "id": "n1",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {
                    "customerInfo": {
                        "customerId": "{input.company.name}",
                        "country": "{input.company.address.country}"
                    }
                },
                "mappings": []
            }
        },
        {
            "id": "n2",
            "type": "decision",
            "data": {
                "script": """
# Example: check country from previous node
if state['n1']['json']['customerInfo']['country'] == 'United States':
    state['region'] = 'US'
else:
    state['region'] = 'Other'
"""
            }
        },
        {
            "id": "n3",
            "type": "service",
            "data": {
                "url": "https://httpbin.org/post",
                "method": "POST",
                "request": {"finalRegion": "{state.region}"},
                "mappings": []
            }
        }
    ],
    "edges": [
        {"source": "n1", "target": "n2"},
        {"source": "n2", "target": "n3"}
    ]
}

# -------------------------------------------------------------------
# Run server
# -------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
