"""Generacion de prospectos (leadgen).

El director no manda a nadie a "buscar bugs al azar". Se busca un perfil
de empresa: SaaS en crecimiento, codigo activo, sin senales de que ya
tengan seguridad resuelta. Y se prioriza por DOLOR + CAPACIDAD DE PAGO,
no por tamano.

Orden de ejecucion (importante para no gastar llamadas de API en basura):
  1. buscar  -> candidatos crudos por lenguaje/estrellas/actividad
  2. calificar ICP -> filtra repos sueltos, herramientas de hacking, VPNs...
  3. auditar -> solo los que pasaron el filtro comercial
  4. priorizar -> P1/P2/P3 combinando riesgo tecnico e indice comercial
"""
from __future__ import annotations

import json
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from .scanner import _get, auditar
from .icp import perfil, resuelto_o_no, prioridad_final
from .report import estimar_precio

ICP_DEFAULT = {
    "lenguajes": ["python", "javascript", "typescript", "go"],
    "estrellas_min": 15,
    "estrellas_max": 1500,
    "actividad_dias": 120,
}


def construir_query(lang: str, icp: dict) -> str:
    desde = (datetime.now(timezone.utc) - timedelta(days=icp["actividad_dias"])).date()
    return " ".join([
        f"language:{lang}",
        f"stars:{icp['estrellas_min']}..{icp['estrellas_max']}",
        f"pushed:>{desde}",
        "fork:false", "archived:false", "is:public",
    ])


def buscar_repos(lang: str, icp: dict, token: str | None = None, por_pagina: int = 30) -> list[dict]:
    q = construir_query(lang, icp)
    url = (f"/search/repositories?q={urllib.parse.quote(q)}"
           f"&sort=updated&order=desc&per_page={por_pagina}")
    data, st = _get(url, token)
    if st != 200:
        if data.get("_auth_error"):
            print("  ! TOKEN INVALIDO (401 Bad credentials).")
            print("    El GITHUB_TOKEN no sirve: es un placeholder, esta mal copiado o expiro.")
            print("    Crea uno en github.com/settings/tokens y luego:")
            print("      export GITHUB_TOKEN=ghp_tu_token_real")
            print("    O trabajar sin token (60 peticiones/hora, pocos prospectos):")
            print("      unset GITHUB_TOKEN")
            return []
        if data.get("_rate_limit"):
            print("  ! LIMITE DE TASA de GitHub alcanzado (sin token: 60 peticiones/hora).")
            print("    Crea uno en github.com/settings/tokens (sin permisos, solo public_repo)")
            print("    y ejecuta:  export GITHUB_TOKEN=ghp_tu_token")
            print("    Para que quede fijo:  echo 'export GITHUB_TOKEN=ghp_...' >> ~/.bashrc")
        else:
            print(f"  ! busqueda '{lang}' fallo (HTTP {st}): {data.get('_msg','')}")
        return []
    return [{
        "repo": r["full_name"],
        "url": r["html_url"],
        "estrellas": r.get("stargazers_count", 0),
        "lenguaje": r.get("language"),
        "descripcion": (r.get("description") or "")[:180],
        "rama": r.get("default_branch", "main"),
        "pushed_at": r.get("pushed_at"),
    } for r in data.get("items", [])]


def puntuar_lead(rep: dict, icp_data: dict) -> dict:
    """Combina la auditoria tecnica con la calificacion comercial."""
    h = rep.get("hallazgos", [])
    altos = sum(1 for f in h if f["severidad"] in ("critica", "alta"))
    ids = {f["id"] for f in h}

    tecnicas = []
    if "SEC-002" in ids:
        tecnicas.append("posibles credenciales versionadas")
    if "SEC-004" in ids:
        tecnicas.append("CI sin escaneo de dependencias")
    if "SEC-007" in ids:
        tecnicas.append("rama principal sin proteccion")
    if "SEC-011" in ids:
        tecnicas.append("CVEs conocidos en dependencias")
    if "SEC-001" in ids:
        tecnicas.append("sin politica de divulgacion")
    if "SEC-012" in ids:
        tecnicas.append("repo sin actividad")

    comerciales = icp_data.get("senales", [])
    prioridad, accion = prioridad_final(
        rep["score_riesgo"], icp_data.get("score_icp", 0), icp_data.get("presion_compliance", False))

    p = estimar_precio(rep)
    sitio = icp_data.get("sitio") or ""
    email = icp_data.get("email") or ""

    # Un repo que no se toca hace tiempo tiene detras gente que ya se fue:
    # sus correos rebotan 550 5.2.1. La antiguedad del push es la senal mas
    # barata de si el prospecto esta vivo AHORA.
    push = rep.get("pushed_at") or ""
    dias_push = None
    if push:
        try:
            from datetime import datetime, timezone
            f = datetime.fromisoformat(str(push).replace("Z", "+00:00"))
            dias_push = (datetime.now(timezone.utc) - f).days
        except Exception:
            dias_push = None

    return {
        "repo": rep["repo"],
        "url": rep.get("url"),
        "dias_desde_push": dias_push,
        "owner": icp_data.get("owner"),
        "sitio": sitio,
        "email": email,
        "descripcion": rep.get("descripcion"),
        "lenguaje": rep.get("lenguaje"),
        "estrellas": rep.get("estrellas", 0),
        "contribuyentes": icp_data.get("contribuyentes", 0),
        "score_riesgo": rep["score_riesgo"],
        "score_icp": icp_data.get("score_icp", 0),
        "banda": rep["banda"],
        "n_hallazgos": rep.get("n_hallazgos", 0),
        "hallazgos_altos": altos,
        "senales_tecnicas": tecnicas,
        "senales_comerciales": comerciales,
        "presion_compliance": icp_data.get("presion_compliance", False),
        "prioridad": prioridad,
        "accion": accion,
        "precio_objetivo_usd": p["diagnostico_express_usd"],
        "ticket_potencial_usd": p["remediacion_estimada_usd"],
    }


def generar_leads(token: str | None = None, icp: dict | None = None,
                  por_lenguaje: int = 10, auditar_top: int = 12,
                  con_osv: bool = True, delay: float = 1.0,
                  solo_organizaciones: bool = True) -> list[dict]:
    icp = icp or ICP_DEFAULT

    # 1. buscar ---------------------------------------------------------
    crudos: list[dict] = []
    for lang in icp["lenguajes"]:
        print(f"[1/4] buscando {lang}...")
        crudos += buscar_repos(lang, icp, token, por_pagina=por_lenguaje)
        time.sleep(delay)

    vistos, unicos = set(), []
    for c in crudos:
        if c["repo"] in vistos:
            continue
        vistos.add(c["repo"])
        unicos.append(c)
    unicos.sort(key=lambda c: c["estrellas"], reverse=True)
    print(f"[1/4] {len(unicos)} candidatos crudos")

    # 2. calificar ICP --------------------------------------------------
    calificados = []
    for i, c in enumerate(unicos, 1):
        p = perfil(c["repo"], branch=c.get("rama", "main"))
        if p.get("veredicto") == "DESCARTAR":
            continue
        if solo_organizaciones and not p.get("es_organizacion"):
            continue
        calificados.append((c, p))
        time.sleep(delay * 0.5)
    calificados.sort(key=lambda cp: cp[1]["score_icp"], reverse=True)
    print(f"[2/4] {len(calificados)} pasan el filtro comercial")

    # 3. auditar --------------------------------------------------------
    leads = []
    for i, (c, p) in enumerate(calificados[:auditar_top], 1):
        print(f"[3/4] auditando {i}/{min(len(calificados), auditar_top)} {c['repo']}...")
        rep = auditar(c["repo"], token=token, con_osv=con_osv)
        if rep.get("error"):
            continue
        if resuelto_o_no(rep):
            print(f"       - descartado: ya tiene la seguridad basica resuelta")
            continue
        # el informe de auditoria no trae la fecha de push, y sin ella no
        # podemos saber si el prospecto esta vivo hoy
        rep["pushed_at"] = c.get("pushed_at")
        leads.append(puntuar_lead(rep, p))
        time.sleep(delay)

    # 4. priorizar ------------------------------------------------------
    leads.sort(key=lambda l: (
        {"P1": 0, "P2": 1, "P3": 2, "DESCARTAR": 3}[l["prioridad"]],
        -(l["score_riesgo"] + l["score_icp"])))
    print(f"[4/4] {len(leads)} prospectos priorizados")
    return leads


def guardar(leads: list[dict], ruta: str = "out/leads.json") -> str:
    import os
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return ruta
