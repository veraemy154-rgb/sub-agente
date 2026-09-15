"""Generacion de prospectos (leadgen).

El director no manda a nadie a "buscar bugs al azar". Se busca un perfil
de empresa: SaaS en crecimiento, codigo activo, sin senales de que ya
tengan seguridad resuelta. Y se prioriza por DOLOR, no por tamano.

Criterio de oro: si el repo ya tiene SECURITY.md + CI con escaneo + rama
protegida, NO es prospecto: esa empresa ya tiene alguien. El dinero esta
en las que estan creciendo y no llegaron a eso todavia.
"""
from __future__ import annotations

import json
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from .scanner import _get, auditar

ICP_DEFAULT = {
    "lenguajes": ["python", "javascript", "typescript", "go"],
    "estrellas_min": 15,
    "estrellas_max": 1500,
    "actividad_dias": 120,
}


def construir_query(lang: str, icp: dict) -> str:
    desde = (datetime.now(timezone.utc) - timedelta(days=icp["actividad_dias"])).date()
    q = [
        f"language:{lang}",
        f"stars:{icp['estrellas_min']}..{icp['estrellas_max']}",
        f"pushed:>{desde}",
        "fork:false",
        "archived:false",
        "is:public",
    ]
    return " ".join(q)


def buscar_repos(lang: str, icp: dict, token: str | None = None, por_pagina: int = 30) -> list[dict]:
    q = construir_query(lang, icp)
    url = (f"/search/repositories?q={urllib.parse.quote(q)}"
           f"&sort=updated&order=desc&per_page={por_pagina}")
    data, st = _get(url, token)
    if st != 200:
        print(f"  ! busqueda '{lang}' fallo (HTTP {st}): {data.get('_msg','')}")
        return []
    return [{
        "repo": r["full_name"],
        "url": r["html_url"],
        "estrellas": r.get("stargazers_count", 0),
        "lenguaje": r.get("language"),
        "descripcion": (r.get("description") or "")[:180],
        "ultimo_push": r.get("pushed_at"),
    } for r in data.get("items", [])]


def puntuar_lead(rep: dict) -> dict:
    """Convierte una auditoria en un lead con prioridad comercial."""
    h = rep.get("hallazgos", [])
    altos = sum(1 for f in h if f["severidad"] in ("critica", "alta"))
    ids = {f["id"] for f in h}

    # Senales de que el prospecto tiene presupuesto y dolor.
    senales = []
    if "SEC-002" in ids:
        senales.append("posibles credenciales versionadas")
    if "SEC-004" in ids:
        senales.append("CI sin escaneo de dependencias")
    if "SEC-007" in ids:
        senales.append("rama principal sin proteccion")
    if "SEC-011" in ids:
        senales.append("CVEs conocidos en dependencias")
    if "SEC-001" in ids:
        senales.append("sin politica de divulgacion")

    # Madurez: si tiene muchas estrellas y actividad reciente, hay empresa real.
    estrellas = rep.get("estrellas", 0)
    if estrellas >= 200:
        senales.append("traccion publica significativa")
    elif estrellas >= 50:
        senales.append("traccion media")

    score = rep["score_riesgo"] + altos * 6 + (8 if estrellas >= 200 else 0)

    if score >= 70:
        prioridad, accion = "P1", "Contactar esta semana. Mensaje personalizado con 2 hallazgos."
    elif score >= 45:
        prioridad, accion = "P2", "Contactar en batch. Secuencia automatizada."
    elif score >= 25:
        prioridad, accion = "P3", "Nurturing: agregar a lista y reauditar en 60 dias."
    else:
        prioridad, accion = "DESCARTAR", "Sin superficie vendible."

    from .report import estimar_precio
    return {
        "repo": rep["repo"],
        "url": rep.get("url"),
        "descripcion": rep.get("descripcion"),
        "lenguaje": rep.get("lenguaje"),
        "estrellas": estrellas,
        "score_riesgo": rep["score_riesgo"],
        "banda": rep["banda"],
        "n_hallazgos": rep.get("n_hallazgos", 0),
        "hallazgos_altos": altos,
        "senales": senales,
        "prioridad": prioridad,
        "accion": accion,
        "precio_objetivo_usd": estimar_precio(rep)["diagnostico_express_usd"],
        "ticket_potencial_usd": estimar_precio(rep)["remediacion_estimada_usd"],
    }


def generar_leads(token: str | None = None, icp: dict | None = None,
                  por_lenguaje: int = 10, auditar_top: int = 12,
                  con_osv: bool = True, delay: float = 1.0) -> list[dict]:
    icp = icp or ICP_DEFAULT
    crudos: list[dict] = []
    for lang in icp["lenguajes"]:
        print(f"[leadgen] buscando {lang}...")
        crudos += buscar_repos(lang, icp, token, por_pagina=por_lenguaje)
        time.sleep(delay)

    vistos, unicos = set(), []
    for c in crudos:
        if c["repo"] in vistos:
            continue
        vistos.add(c["repo"])
        unicos.append(c)

    # Pre-filtro barato: prioriza por traccion antes de gastar llamadas de API.
    unicos.sort(key=lambda c: c["estrellas"], reverse=True)
    objetivos = unicos[:auditar_top]

    leads = []
    for i, c in enumerate(objetivos, 1):
        print(f"[leadgen] auditando {i}/{len(objetivos)} {c['repo']}...")
        rep = auditar(c["repo"], token=token, con_osv=con_osv)
        if rep.get("error"):
            continue
        leads.append(puntuar_lead(rep))
        time.sleep(delay)

    leads.sort(key=lambda l: (
        {"P1": 0, "P2": 1, "P3": 2, "DESCARTAR": 3}[l["prioridad"]], -l["score_riesgo"]))
    return leads


def guardar(leads: list[dict], ruta: str = "out/leads.json") -> str:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return ruta
