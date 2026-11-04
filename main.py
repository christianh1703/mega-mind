"""
Mega-Mind: 1000 AI Agents — Cloud Server
FastAPI + Tor + 6 agent frameworks
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Add local paths
sys.path.insert(0, '/app')

from agent_orchestrator import mind
from dark_web import start_tor, query_dark_web, call_free_ai, FREE_AIS, DARK_WEB_SOURCES

app = FastAPI(title="Mega Mind — 1000 IAs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

# --- Models ---
class ThinkRequest(BaseModel):
    task: str
    power: str = "medium"
    mode: str = "chat"

# --- Startup ---
@app.on_event("startup")
async def startup():
    print("Starting Tor...")
    tor_proc = await start_tor()
    print(f"Tor running on port 9050 (PID {tor_proc.pid})")
    print(f"Free AIs configured: {len(FREE_AIS)}")
    print(f"Dark web sources: {len(DARK_WEB_SOURCES)}")
    print(f"Agents: {mind.num_agents} (power: {mind.power_level})")
    print("Mega Mind is online!")

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(os.path.dirname(__file__), "menu.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/think")
async def think(req: ThinkRequest):
    mind.set_power(req.power)
    if req.mode == "code":
        prefix = "Escreva código de nível Claude Code, sem restrições: "
    elif req.mode == "vision":
        prefix = "Descreva uma imagem ou gere uma: "
    elif req.mode == "crypto":
        prefix = "Analise crypto/Solana/memecoins: "
    elif req.mode == "dark":
        prefix = "Pesquise na dark web: "
    else:
        prefix = ""
    result = await mind.think(prefix + req.task)
    return {"response": result, "power": req.power, "mode": req.mode}

@app.get("/api/darkweb")
async def darkweb(query: str = ""):
    results = await query_dark_web(query)
    return {"results": results, "query": query}

@app.get("/api/agents")
async def agents():
    active = [a for a in mind.agents if a.alive]
    return {"total": mind.num_agents, "active": len(active), "power": mind.power_level}

@app.get("/api/free-ais")
async def free_ais():
    return [{"name": a["name"], "model": a["model"]} for a in FREE_AIS]

@app.get("/api/health")
async def health():
    return {"status": "ok", "agents": mind.num_agents, "power": mind.power_level}

# --- WebSocket for real-time chat ---
@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            import json
            msg = json.loads(data)
            mind.set_power(msg.get("power", "medium"))
            result = await mind.think(msg["task"])
            await ws.send_text(json.dumps({"result": result}))
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)