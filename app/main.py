import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .router import clasificar
from .agents import AGENTS, ejecutar
from .scanner import auditar
from .report import a_markdown, estimar_precio
from .leadgen import generar_leads, guardar
from .outreach import secuencia
from .evidence import generar, ejemplo as evidencia_ejemplo

app = FastAPI(title="Sub-Agente Core", version="0.3.0")

SITE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "site")
if os.path.isdir(SITE):
    app.mount("/site", StaticFiles(directory=SITE, html=True), name="site")


class Task(BaseModel):
    task: str


class OutreachIn(BaseModel):
    repo: str
    remitente: str = "Equipo de Seguridad"


class Contacto(BaseModel):
    repo: str
    email: str
    mensaje: str = ""


class EvidenceIn(BaseModel):
    cliente: str
    repos: list[str]
    periodo: str = ""
    responsable: str = "________________"
    notas: str = ""
    abiertos: list[dict] = []
    cerrados: list[dict] = []
    excepciones: list[dict] = []


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
          auditar_top: int = 12, osv: bool = True,
          solo_organizaciones: bool = True):
    """Descubre prospectos, califica ICP, audita y prioriza P1/P2/P3."""
    from .leadgen import ICP_DEFAULT
    lenguajes = [l.strip() for l in lang.split(",") if l.strip()]
    icp = {**ICP_DEFAULT, "lenguajes": lenguajes}
    res = generar_leads(icp=icp, por_lenguaje=por_lenguaje, auditar_top=auditar_top,
                        con_osv=osv, solo_organizaciones=solo_organizaciones)
    ruta = guardar(res)
    return {"n": len(res), "archivo": ruta,
            "pipeline_usd": sum(l["ticket_potencial_usd"] for l in res), "leads": res}


@app.post("/outreach")
def outreach(payload: OutreachIn):
    """Genera la secuencia de 5 toques para un prospecto auditado."""
    from .icp import perfil
    from .leadgen import puntuar_lead
    rep = auditar(payload.repo)
    if rep.get("error"):
        return rep
    lead = puntuar_lead(rep, perfil(payload.repo))
    return {"lead": lead, "secuencia": secuencia(lead, rep, payload.remitente),
            "informe_md": a_markdown(rep)}


@app.post("/evidence")
def evidence(payload: EvidenceIn):
    """Informe mensual de evidencia (el producto del retainer)."""
    periodo = payload.periodo or datetime.now(timezone.utc).strftime("%Y-%m")
    md = generar(payload.cliente, periodo, payload.repos,
                 payload.abiertos, payload.cerrados, payload.excepciones,
                 payload.responsable, payload.notas)
    os.makedirs("out", exist_ok=True)
    nombre = f"out/evidencia-{periodo}-{payload.cliente.lower().replace(' ', '-')}.md"
    with open(nombre, "w", encoding="utf-8") as f:
        f.write(md)
    return {"cliente": payload.cliente, "periodo": periodo, "archivo": nombre, "markdown": md}


@app.get("/evidence/demo")
def evidence_demo():
    """Informe de muestra, para ensenarle el formato a un prospecto."""
    return {"markdown": evidencia_ejemplo()}


@app.post("/contacto")
def contacto(payload: Contacto):
    """Recibe los leads de la landing (site/index.html)."""
    os.makedirs("out", exist_ok=True)
    registro = {**payload.dict(),
                "recibido_en": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    ruta = "out/inbound.json"
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(registro)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"ok": True, "recibido": registro["recibido_en"]}
