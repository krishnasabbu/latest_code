from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import requests
import uvicorn
from simpleeval import simple_eval

# -------------------------------------------------------------------
#  FastAPI setup
# -------------------------------------------------------------------

app = FastAPI(title="LangGraph Dynamic Executor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for React Flow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
#  Node Factory Implementations
# -------------------------------------------------------------------

def make_llm_node(node_data: Dict[str, Any]):
    """Node that connects to LLM (OpenAI / local)"""
    model = node_data["data"].get("model", "gpt-4o-mini")
    prompt = node_data["data"]["prompt"]
    llm = ChatOpenAI(model=model)

    def run_fn(state: Dict[str, Any]):
        text = prompt.format(**state)
        res = llm.invoke(text)
        sentiment = None
        if "good" in res.content.lower():
            sentiment = "positive"
        elif "bad" in res.content.lower():
            sentiment = "negative"
        return {"llm_output": res.content, "sentiment": sentiment}

    return run_fn


def make_api_node(node_data: Dict[str, Any]):
    """Node that calls a REST API"""
    url = node_data["data"]["url"]
    method = node_data["data"].get("method", "GET").upper()

    def run_fn(state: Dict[str, Any]):
        try:
            resp = requests.request(method, url, json=state, timeout=10)
            data = resp.json() if resp.ok else {"error": resp.text}
        except Exception as e:
            data = {"error": str(e)}
        return {"api_response": data}

    return run_fn


def make_manual_node(node_data: Dict[str, Any]):
    """Node that pauses for manual approval"""
    message = node_data["data"].get("message", "Awaiting approval...")
    def run_fn(state: Dict[str, Any]):
        print(f"Manual node reached: {message}")
        # you can set a DB flag or send webhook here
        return {"status": "WAITING_MANUAL", "message": message}
    return run_fn


NODE_FACTORY = {
    "llm": make_llm_node,
    "api": make_api_node,
    "manual": make_manual_node
}

# -------------------------------------------------------------------
#  Graph Builder
# -------------------------------------------------------------------

def build_graph_from_json(graph_json: Dict[str, Any]):
    g = StateGraph(dict)
    node_funcs = {}

    # Step 1: Add nodes
    for node in graph_json["nodes"]:
        ntype = node["type"]
        if ntype not in NODE_FACTORY:
            raise ValueError(f"Unknown node type: {ntype}")
        func = NODE_FACTORY[ntype](node)
        node_funcs[node["id"]] = func
        g.add_node(node["id"], func)

    # Step 2: Add edges (with optional conditions)
    edges_by_source = {}
    for e in graph_json["edges"]:
        edges_by_source.setdefault(e["source"], []).append(e)

    for source, edges in edges_by_source.items():
        if any("condition" in e for e in edges):
            # conditional edge handler
            def condition_fn(state, edges=edges):
                for edge in edges:
                    cond = edge.get("condition")
                    if not cond:
                        continue
                    try:
                        # safe evaluation with simpleeval
                        if simple_eval(cond, names=state):
                            return edge["target"]
                    except Exception as ex:
                        print("Condition error:", ex)
                # fallback if no condition matches
                for e in edges:
                    if "condition" not in e:
                        return e["target"]
                return None
            g.add_conditional_edges(source, condition_fn)
        else:
            for e in edges:
                g.add_edge(e["source"], e["target"])

    # Step 3: Define start/end
    entry = graph_json["nodes"][0]["id"]
    g.set_entry_point(entry)
    g.add_edge(graph_json["nodes"][-1]["id"], END)

    return g.compile()

# -------------------------------------------------------------------
#  Request/Response Models
# -------------------------------------------------------------------

class ExecuteRequest(BaseModel):
    graph: Dict[str, Any]
    inputs: Dict[str, Any] = {}

class ExecuteResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    logs: Optional[List[str]] = None

# -------------------------------------------------------------------
#  API Endpoint
# -------------------------------------------------------------------

@app.post("/execute", response_model=ExecuteResponse)
def execute_workflow(req: ExecuteRequest):
    try:
        graph = build_graph_from_json(req.graph)
        result = graph.invoke(req.inputs)
        return ExecuteResponse(status="success", result=result)
    except Exception as e:
        return ExecuteResponse(status="error", result={"error": str(e)})

# -------------------------------------------------------------------
#  Example JSON for Testing
# -------------------------------------------------------------------

example_flow = {
    "nodes": [
        {"id": "n1", "type": "llm", "data": {"prompt": "Analyze sentiment: {text}"}},
        {"id": "n2", "type": "api", "data": {"url": "https://api.positive.com"}},
        {"id": "n3", "type": "api", "data": {"url": "https://api.negative.com"}},
        {"id": "n4", "type": "manual", "data": {"message": "Need approval to proceed"}}
    ],
    "edges": [
        {"source": "n1", "target": "n2", "condition": "sentiment == 'positive'"},
        {"source": "n1", "target": "n3", "condition": "sentiment == 'negative'"},
        {"source": "n2", "target": "n4"},
        {"source": "n3", "target": "n4"}
    ]
}

@app.get("/")
def root():
    return {"message": "LangGraph Executor is running", "example_graph": example_flow}

# -------------------------------------------------------------------
#  Run server
# -------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
