from fastapi import FastAPI
from pydantic import BaseModel
from .router import clasificar
from .agents import AGENTS, ejecutar

app = FastAPI(title="Sub-Agente Core")

class Task(BaseModel):
    task: str

@app.get("/")
def root():
    return {"status": "online", "agent": "sub-agente", "areas": list(AGENTS.keys())}

@app.post("/task")
def task(payload: Task):
    area = clasificar(payload.task)
    return ejecutar(area, payload.task)
