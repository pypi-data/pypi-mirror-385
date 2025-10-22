import sys
from pathlib import Path

# Add parent directory to path so we can import thinagents
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
import importlib.util
from typing import Dict, List
from contextlib import asynccontextmanager
from types import ModuleType
from thinagents import Agent
from pydantic import BaseModel

ROOT_AGENT = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ROOT_AGENT
    user_main_path = "/Users/prabhukirankonda/Desktop/thinagents_web/examples/main.py"
    try:
        module = load_module_from_path(user_main_path)
        ROOT_AGENT = get_root_agent_from_module(module)
    except Exception as e:
        ROOT_AGENT = None
        print("Failed loading user module:", e)
    yield

app = FastAPI(lifespan=lifespan)

def load_module_from_path(path: str):
    spec = importlib.util.spec_from_file_location("main", Path(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_root_agent_from_module(module: ModuleType) -> Agent:
    if hasattr(module, "root_agent"):
        return getattr(module, "root_agent")
    raise AttributeError("No `root_agent` found in module")

def serialize_agent(agent: Agent) -> Dict:
    def serialize_tools(tools: List) -> List[str]:
        out = []
        for t in tools or []:
            name = getattr(t, "__name__", None) or getattr(t, "name", str(t))
            out.append(name)
        return out

    data = {
        "name": getattr(agent, "name", None),
        "model": getattr(agent, "model", None),
        "tools": serialize_tools(getattr(agent, "tools", [])),
    }

    sub_agents = getattr(agent, "sub_agents", None) or getattr(agent, "children", None)
    if sub_agents:
        data["sub_agents"] = [serialize_agent(a) for a in sub_agents]
    else:
        data["sub_agents"] = []

    return data

class AgentRunRequest(BaseModel):
    input: str

@app.get("/agent/info")
async def agent_info():
    if ROOT_AGENT is None:
        raise HTTPException(status_code=404, detail="root agent not loaded")
    return serialize_agent(ROOT_AGENT)


@app.post("/agent/run")
async def agent_run(request: AgentRunRequest):
    if ROOT_AGENT is None:
        raise HTTPException(status_code=404, detail="root agent not loaded")
    return ROOT_AGENT.run(request.input)