"""Tablero comercial minimalista: donde esta parado cada prospecto.

Sin esto, la rutina semanal se cae en tres dias: pierdes el hilo de a quien
escribiste, cuando tocaba el seguimiento y cuanto dinero hay realmente en juego.
No necesitas un CRM de pago. Necesitas un archivo y cuatro comandos.

Estados del embudo:
    prospecto -> contactado -> respondio -> diagnostico -> remediacion -> retainer
                                                                      \-> perdido

Uso:
    python run.py pipeline add owner/repo --contacto cto@acme.com
    python run.py pipeline mov owner/repo respondio --nota "pide precio"
    python run.py pipeline ls
    python run.py pipeline stats
    python run.py pipeline hoy          # a quien le toca seguimiento HOY
    python run.py pipeline importar     # carga out/leads.json
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

ARCHIVO = "out/pipeline.json"

ESTADOS = ["prospecto", "contactado", "respondio", "diagnostico",
           "remediacion", "retainer", "perdido"]

# Probabilidad de cierre por etapa. No es ciencia: es para saber cuanto vale
# de verdad el embudo y no autoenganarse con la suma de todos los numeros.
PROB = {"prospecto": 0.03, "contactado": 0.06, "respondio": 0.18,
        "diagnostico": 0.45, "remediacion": 0.75, "retainer": 1.0, "perdido": 0.0}

# Ticket tipico por etapa (USD). Se puede sobreescribir por registro.
TICKET = {"prospecto": 490, "contactado": 490, "respondio": 490,
          "diagnostico": 2500, "remediacion": 2500, "retainer": 1800, "perdido": 0}

# Cuantos dias hasta el proximo toque, por etapa.
SIGUIENTE = {"prospecto": 0, "contactado": 3, "respondio": 1, "diagnostico": 2,
             "remediacion": 5, "retainer": 30, "perdido": 0}

MRR_POR_RETAINER = 1800


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


def cargar() -> list[dict]:
    try:
        with open(ARCHIVO, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar(registros: list[dict]) -> str:
    os.makedirs(os.path.dirname(ARCHIVO) or ".", exist_ok=True)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    return ARCHIVO


def _slug(repo: str) -> str:
    return repo.strip().lower().rstrip("/")


def buscar(registros: list[dict], repo: str) -> dict | None:
    s = _slug(repo)
    for r in registros:
        if _slug(r["repo"]) == s:
            return r
    return None


def add(repo: str, contacto: str = "", canal: str = "email", valor: float = 0,
        nota: str = "", estado: str = "prospecto", enlace: str = "") -> dict:
    regs = cargar()
    if buscar(regs, repo):
        return {"error": f"{repo} ya esta en el pipeline"}
    hoy = _hoy()
    reg = {
        "repo": repo,
        "estado": estado,
        "contacto": contacto,
        "canal": canal,
        "enlace": enlace,
        "valor_usd": valor or TICKET.get(estado, 490),
        "mrr_usd": MRR_POR_RETAINER if estado == "retainer" else 0,
        "creado_en": hoy.isoformat(),
        "actualizado_en": hoy.isoformat(),
        "proximo_en": (hoy + timedelta(days=SIGUIENTE.get(estado, 3))).isoformat(),
        "nota": nota,
        "historial": [{"fecha": hoy.isoformat(), "estado": estado, "nota": nota or "alta"}],
    }
    regs.append(reg)
    guardar(regs)
    return reg


def mover(repo: str, estado: str, nota: str = "", dias: int | None = None) -> dict:
    if estado not in ESTADOS:
        return {"error": f"Estado invalido. Usa: {', '.join(ESTADOS)}"}
    regs = cargar()
    reg = buscar(regs, repo)
    if not reg:
        return {"error": f"{repo} no esta en el pipeline. Agregalo con: run.py pipeline add {repo}"}
    hoy = _hoy()
    anterior = reg["estado"]
    reg["estado"] = estado
    reg["actualizado_en"] = hoy.isoformat()
    d = dias if dias is not None else SIGUIENTE.get(estado, 3)
    reg["proximo_en"] = (hoy + timedelta(days=d)).isoformat() if d else ""
    if estado == "retainer":
        reg["mrr_usd"] = reg.get("mrr_usd") or MRR_POR_RETAINER
    if estado == "perdido":
        reg["mrr_usd"] = 0
    if nota:
        reg["nota"] = nota
    reg.setdefault("historial", []).append(
        {"fecha": hoy.isoformat(), "estado": estado, "nota": nota or f"{anterior} -> {estado}"})
    guardar(regs)
    return reg


def eliminar(repo: str) -> bool:
    regs = cargar()
    reg = buscar(regs, repo)
    if not reg:
        return False
    regs.remove(reg)
    guardar(regs)
    return True


def pendientes_hoy(registros: list[dict] | None = None) -> list[dict]:
    hoy = _hoy()
    out = []
    for r in (registros if registros is not None else cargar()):
        if r["estado"] in ("perdido", "retainer"):
            continue
        p = r.get("proximo_en") or ""
        if not p:
            continue
        try:
            if date.fromisoformat(p) <= hoy:
                out.append(r)
        except Exception:
            continue
    out.sort(key=lambda r: r.get("proximo_en", ""))
    return out


def metricas(registros: list[dict] | None = None) -> dict:
    regs = registros if registros is not None else cargar()
    por_estado = {e: 0 for e in ESTADOS}
    for r in regs:
        por_estado[r["estado"]] = por_estado.get(r["estado"], 0) + 1

    mrr = sum(r.get("mrr_usd", 0) for r in regs if r["estado"] == "retainer")
    ponderado = sum(r.get("valor_usd", 0) * PROB.get(r["estado"], 0) for r in regs)
    bruto = sum(r.get("valor_usd", 0) for r in regs if r["estado"] != "perdido")

    contactados = por_estado["contactado"] + por_estado["respondio"] + \
        por_estado["diagnostico"] + por_estado["remediacion"] + por_estado["retainer"]
    cerrados = por_estado["remediacion"] + por_estado["retainer"]
    hablados = por_estado["respondio"] + por_estado["diagnostico"] + \
        por_estado["remediacion"] + por_estado["retainer"]

    return {
        "total": len(regs),
        "por_estado": por_estado,
        "mrr_usd": mrr,
        "arr_usd": mrr * 12,
        "pipeline_bruto_usd": bruto,
        "pipeline_ponderado_usd": round(ponderado),
        "tasa_respuesta_pct": round(100 * hablados / contactados, 1) if contactados else 0.0,
        "tasa_cierre_pct": round(100 * cerrados / hablados, 1) if hablados else 0.0,
        "pendientes_hoy": len(pendientes_hoy(regs)),
    }


def importar(ruta: str = "out/leads.json", solo: list[str] | None = None) -> dict:
    """Carga prospectos de out/leads.json al pipeline."""
    try:
        with open(ruta, encoding="utf-8") as f:
            leads = json.load(f)
    except Exception as e:
        return {"error": f"No se pudo leer {ruta}: {e}"}
    regs = cargar()
    nuevos = 0
    for l in leads:
        if solo and l["prioridad"] not in solo:
            continue
        if buscar(regs, l["repo"]):
            continue
        regs.append({
            "repo": l["repo"],
            "estado": "prospecto",
            "contacto": l.get("email", ""),
            "canal": "email",
            "enlace": l.get("url", ""),
            "valor_usd": l.get("ticket_potencial_usd", 490),
            "mrr_usd": 0,
            "creado_en": _hoy().isoformat(),
            "actualizado_en": _hoy().isoformat(),
            "proximo_en": _hoy().isoformat(),
            "nota": f"{l['prioridad']} · riesgo {l.get('score_riesgo')} · icp {l.get('score_icp')}",
            "historial": [{"fecha": _hoy().isoformat(), "estado": "prospecto",
                           "nota": f"importado ({l.get('prioridad')})"}],
        })
        nuevos += 1
    guardar(regs)
    return {"importados": nuevos, "total": len(regs)}


def a_tabla(registros: list[dict] | None = None) -> str:
    regs = registros if registros is not None else cargar()
    if not regs:
        return "Pipeline vacio. Agrega: python run.py pipeline add owner/repo"
    hoy = _hoy()
    L = []
    L.append(f"{'REPO':38} {'ESTADO':12} {'PROX':11} {'VALOR':>7} {'MRR':>6}  NOTA")
    L.append("-" * 100)
    orden = {e: i for i, e in enumerate(ESTADOS)}
    for r in sorted(regs, key=lambda x: (orden.get(x["estado"], 9), x.get("proximo_en", ""))):
        prox = r.get("proximo_en", "")
        marca = "!" if prox and prox <= hoy.isoformat() and r["estado"] not in ("retainer", "perdido") else " "
        L.append(f"{r['repo'][:38]:38} {r['estado']:12} {prox + marca:11} "
                 f"{r.get('valor_usd', 0):7.0f} {r.get('mrr_usd', 0):6.0f}  {r.get('nota', '')[:34]}")
    return "\n".join(L)
