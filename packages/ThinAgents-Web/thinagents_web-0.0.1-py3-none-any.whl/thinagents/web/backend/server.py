from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, List, Any


class AgentRunRequest(BaseModel):
    input: str


def serialize_agent(agent) -> Dict[str, Any]:
    def serialize_tools(tools: List) -> List[str]:
        out = []
        for t in tools or []:
            name = getattr(t, "__name__", None) or getattr(t, "name", str(t))
            out.append(name)
        return out

    data = {
        "name": getattr(agent, "name", "Unnamed Agent"),
        "model": getattr(agent, "model", None),
        "tools": serialize_tools(getattr(agent, "tools", [])),
    }

    sub_agents = getattr(agent, "sub_agents", None) or getattr(agent, "children", None)
    if sub_agents:
        data["sub_agents"] = [serialize_agent(a) for a in sub_agents]
    else:
        data["sub_agents"] = []

    return data


def create_app(agent):
    app = FastAPI(
        title="ThinAgents Web UI",
        description="Web interface for ThinAgents",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/agent/info")
    async def agent_info():
        return serialize_agent(agent)

    @app.post("/api/agent/run")
    async def agent_run(request: AgentRunRequest):
        try:
            # Check if agent.run is async or sync
            if hasattr(agent, 'arun'):
                result = await agent.arun(request.input)
            else:
                result = agent.run(request.input)
            
            if isinstance(result, dict):
                return result
            elif isinstance(result, str):
                return {"content": result}
            elif hasattr(result, 'content'):
                return {"content": result.content}
            else:
                return {"content": str(result)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    ui_build_path = Path(__file__).parent.parent / "ui" / "build"

    if ui_build_path.exists():
        app.mount("/_app", StaticFiles(directory=ui_build_path / "_app"), name="app")
        
        @app.get("/")
        async def serve_root():
            return FileResponse(ui_build_path / "index.html")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path.startswith("api/"):
                return
                
            file_path = ui_build_path / full_path
            
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            
            return FileResponse(ui_build_path / "index.html")
    else:
        @app.get("/")
        async def root():
            return {
                "message": "ThinAgents Backend API (UI not built)",
                "agent": getattr(agent, "name", "Unnamed Agent"),
                "endpoints": {
                    "info": "/api/agent/info",
                    "run": "/api/agent/run"
                }
            }

    return app

