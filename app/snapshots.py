"""Estado historico de hallazgos por cliente: la base del informe de evidencia.

Sin esto, el informe mensual se escribe a mano y el retainer no escala.
Con esto, el sistema sabe SOLO que se cerro y que aparecio este mes, y con
que antiguedad. Esa informacion (MTTR, tasa de cierre, antiguedad de la deuda)
es exactamente lo que el auditor quiere ver y lo que ningun escaneo aislado da.

Modelo: un JSON por cliente en out/estado/<slug>.json con los hallazgos
abiertos, su fecha de deteccion y el historico de cierres.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timezone

ESTADO_DIR = "out/estado"


def slug(texto: str) -> str:
    s = (texto or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "cliente"


def _ruta(cliente: str) -> str:
    os.makedirs(ESTADO_DIR, exist_ok=True)
    return os.path.join(ESTADO_DIR, f"{slug(cliente)}.json")


def cargar(cliente: str) -> dict:
    try:
        with open(_ruta(cliente), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"cliente": cliente, "repos": [], "abiertos": {},
                "historial_cerrados": [], "snapshots": []}


def guardar(cliente: str, estado: dict) -> str:
    os.makedirs(ESTADO_DIR, exist_ok=True)
    with open(_ruta(cliente), "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
    return _ruta(cliente)


def _clave(rep: str, h: dict) -> str:
    return f"{rep}::{h['id']}"


def actualizar(cliente: str, repos: list[str], escaneos: list[dict],
               periodo: str | None = None, hoy: date | None = None) -> dict:
    """Compara el escaneo de hoy contra el estado guardado.

    Devuelve {'abiertos': [...], 'nuevos': [...], 'cerrados': [...]} y
    persiste el nuevo estado.
    """
    hoy = hoy or datetime.now(timezone.utc).date()
    periodo = periodo or hoy.strftime("%Y-%m")
    est = cargar(cliente)
    prev = est.get("abiertos", {})

    actuales: dict[str, dict] = {}
    for rep in escaneos:
        if rep.get("error"):
            continue
        r = rep["repo"]
        for h in rep.get("hallazgos", []):
            if h["severidad"] == "informativa":
                continue
            actuales[_clave(r, h)] = {
                "id": h["id"], "severidad": h["severidad"], "titulo": h["titulo"],
                "repo": r, "control_soc2": h["control_soc2"], "esfuerzo": h.get("esfuerzo", "m"),
            }

    nuevos = []
    for k, v in actuales.items():
        if k in prev:
            v["detectado_en"] = prev[k].get("detectado_en", hoy.isoformat())
        else:
            v["detectado_en"] = hoy.isoformat()
            nuevos.append(v)

    cerrados = []
    for k, v in prev.items():
        if k in actuales:
            continue
        try:
            d0 = date.fromisoformat(v.get("detectado_en", hoy.isoformat()))
        except Exception:
            d0 = hoy
        v = dict(v)
        v["cerrado_en"] = hoy.isoformat()
        v["dias_abierto"] = max(0, (hoy - d0).days)
        cerrados.append(v)

    est["cliente"] = cliente
    est["repos"] = repos
    est["abiertos"] = actuales
    est.setdefault("historial_cerrados", []).extend(cerrados)
    est.setdefault("snapshots", [])
    if periodo not in est["snapshots"]:
        est["snapshots"].append(periodo)
    est["actualizado_en"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    guardar(cliente, est)

    return {"abiertos": list(actuales.values()), "nuevos": nuevos, "cerrados": cerrados,
            "periodo": periodo, "estado_archivo": _ruta(cliente)}


def primer_dia(periodo: str) -> date:
    y, m = (int(x) for x in periodo.split("-"))
    return date(y, m, 1)


def marcar_novedad(hallazgos: list[dict], periodo: str) -> list[dict]:
    inicio = primer_dia(periodo)
    out = []
    for h in hallazgos:
        h = dict(h)
        try:
            h["es_nuevo"] = date.fromisoformat(h.get("detectado_en", "")) >= inicio
        except Exception:
            h["es_nuevo"] = False
        out.append(h)
    return out


def cierres_del_periodo(cliente: str, periodo: str) -> list[dict]:
    est = cargar(cliente)
    return [c for c in est.get("historial_cerrados", [])
            if c.get("cerrado_en", "").startswith(periodo)]
