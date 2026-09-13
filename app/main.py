from fastapi import FastAPI

app = FastAPI(title="Sub-Agente Core")

@app.get("/")
def root():
    return {"status": "online", "agent": "sub-agente"}

@app.post("/task")
def task(payload: dict):
    # Aquí entrará el router que delega a sub-agentes por área
    return {"received": payload, "router": "pendiente"}
