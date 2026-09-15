from fastapi import FastAPI, Query
from pydantic import BaseModel

from .router import clasificar
from .agents import AGENTS, ejecutar
from .scanner import auditar
from .report import a_markdown, estimar_precio
from .leadgen import generar_leads, guardar
from .outreach import secuencia

app = FastAPI(title="Sub-Agente Core", version="0.2.0")


class Task(BaseModel):
    task: str


class OutreachIn(BaseModel):
    repo: str
    remitente: str = "Equipo de Seguridad"


@app.get("/")
def root():
    return {"status": "online", "agent": "sub-agente", "areas": list(AGENTS.keys())}


@app.post("/task")
def task(payload: Task):
    area = clasificar(payload.task)
    return ejecutar(area, payload.task)


@app.get("/scan")
def scan(repo: str = Query(..., description="owner/nombre"),
         osv: bool = Query(True, description="consultar CVEs en OSV")):
    """Auditoria pasiva de un repo publico + informe + precio sugerido."""
    rep = auditar(repo, con_osv=osv)
    if rep.get("error"):
        return rep
    return {**rep, "precio": estimar_precio(rep), "informe_md": a_markdown(rep)}


@app.post("/leads")
def leads(lang: str = "python,javascript", por_lenguaje: int = 10,
          auditar_top: int = 12, osv: bool = True):
    """Descubre prospectos, los audita y los prioriza P1/P2/P3."""
    lenguajes = [l.strip() for l in lang.split(",") if l.strip()]
    from .leadgen import ICP_DEFAULT
    icp = {**ICP_DEFAULT, "lenguajes": lenguajes}
    res = generar_leads(icp=icp, por_lenguaje=por_lenguaje,
                        auditar_top=auditar_top, con_osv=osv)
    ruta = guardar(res)
    return {"n": len(res), "archivo": ruta,
            "pipeline_usd": sum(l["ticket_potencial_usd"] for l in res), "leads": res}


@app.post("/outreach")
def outreach(payload: OutreachIn):
    """Genera la secuencia de 5 toques para un prospecto auditado."""
    rep = auditar(payload.repo)
    if rep.get("error"):
        return rep
    from .leadgen import puntuar_lead
    lead = puntuar_lead(rep)
    return {"lead": lead, "secuencia": secuencia(lead, rep, payload.remitente),
            "informe_md": a_markdown(rep)}
