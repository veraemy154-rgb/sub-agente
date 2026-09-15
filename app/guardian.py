"""Vigilancia de la rama: quien ha tocado el codigo y con que autorizacion.

Contexto: el 15-09-2026 dos sesiones de agente escribieron a la vez sobre
app/icp.py. El criterio de filtrado quedo con dos versiones incompatibles y
el generador de prospectos devolvio proyectos de codigo abierto famosos en
lugar de empresas durante dos rondas. El sintoma tardo horas en rastrearse.

Esto no bloquea a nadie (no hay permisos para bloquear la rama), pero hace que
sea imposible que una sesion ajena pase desapercibida.

Uso:
    python run.py guardian            # ultimos 20 commits
    python run.py guardian --n 50
"""
from __future__ import annotations

import re
import subprocess

MARCA = "Sesion: 01a0a513"
RAMA_ESPERADA = "arena/01a0a513-sub-agente"
SEP = "\x1f"
FIN = "\x1e"


def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _archivos(h: str) -> list[str]:
    return [l for l in _git("show", "--name-only", "--format=", h).splitlines() if l.strip()]


def commits(n: int = 20) -> list[dict]:
    """Ultimos n commits, con si tocan codigo y si estan autorizados."""
    formato = SEP.join(["%h", "%an", "%ae", "%ad", "%s", "%b"]) + FIN
    salida = _git("log", f"-{n}", f"--format={formato}", "--date=short")
    if not salida:
        return []

    out = []
    for bloque in salida.split(FIN + "\n"):
        bloque = bloque.strip("\n")
        if not bloque.strip():
            continue
        partes = bloque.split(SEP)
        while len(partes) < 6:
            partes.append("")
        h, an, ae, ad, asunto, cuerpo = partes[:6]
        archivos = _archivos(h)
        toca_app = any(a.startswith("app/") for a in archivos)
        autorizado = True
        if toca_app:
            autorizado = MARCA in cuerpo
        out.append({
            "hash": h.strip(),
            "autor": an.strip(),
            "email": ae.strip(),
            "fecha": ad.strip(),
            "asunto": asunto.strip(),
            "toca_app": toca_app,
            "autorizado": autorizado,
            "coautores": [c.strip() for c in re.findall(r"Co-authored-by:\s*(.+)", cuerpo, re.I)],
            "archivos": archivos,
        })
    return out


def informe(n: int = 20) -> str:
    cs = commits(n)
    if not cs:
        return "No hay commits (o esto no es un repositorio git)."

    rama = _git("rev-parse", "--abbrev-ref", "HEAD")
    L = []
    L.append("=== GUARDIAN DE RAMA ===")
    L.append(f"Rama: {rama}" + ("" if rama == RAMA_ESPERADA else "  <- NO es la rama esperada"))
    L.append(f"Marca exigida en cambios de codigo: '{MARCA}'")
    L.append("")

    L.append(f"{'HASH':9} {'FECHA':11} {'AUTOR':16} {'CODIGO':7} ESTADO")
    L.append("-" * 78)
    for c in cs:
        estado = "—" if not c["toca_app"] else ("autorizado" if c["autorizado"] else "NO AUTORIZADO")
        L.append(f"{c['hash']:9} {c['fecha']:11} {c['autor'][:16]:16} "
                 f"{'si' if c['toca_app'] else 'no':7} {estado}")
        L.append(f"{'':9} {c['asunto'][:70]}")
        for co in c["coautores"]:
            L.append(f"{'':9} co-autor: {co}")
    L.append("")

    # La convencion arranca en el primer commit que lleva la marca: lo anterior
    # es historico legitimo, no una intrusion. Asi el guardian se autoconfigura.
    base = (_git("log", "--format=%H", "--grep=" + MARCA, "--reverse").split() or [""])[0]
    if base:
        nuevos = set(_git("rev-list", f"{base}..HEAD").split())
        sospechosos = [c for c in cs
                       if c["toca_app"] and not c["autorizado"] and c["hash"] in nuevos]
    else:
        sospechosos = []
    coautores = sorted({co for c in cs for co in c["coautores"]})
    autores = sorted({f"{c['autor']} <{c['email']}>" for c in cs})

    L.append("=== AUTORES ===")
    for a in autores:
        L.append(f"  {a}")
    if coautores:
        L.append("")
        L.append("=== CO-AUTORES (identifican a la sesion de agente) ===")
        for co in coautores:
            L.append(f"  {co}")
    L.append("")

    L.append(f"Convencion en vigor desde: {base[:7] if base else '(aun no: este commit la activa)'}")
    L.append("")

    if sospechosos:
        L.append(f"!!! {len(sospechosos)} COMMIT(S) DE CODIGO SIN MARCA DE SESION !!!")
        L.append("Posible segunda sesion de agente escribiendo en esta rama.")
        for c in sospechosos:
            L.append(f"  {c['hash']} {c['autor']}: {c['asunto']}")
            L.append(f"      archivos: {', '.join(c['archivos'][:6])}")
        L.append("")
        L.append("NO los reviertas a ciegas: puede ser trabajo legitimo que hay que revisar.")
        L.append("Avisa al usuario y cierra la otra sesion desde la interfaz de Arena.")
        L.append("Lee .github/SESION-AUTORIZADA.md")
    else:
        L.append("OK: ningun cambio de codigo posterior a la convencion esta sin marcar.")
        L.append("(El historico anterior no cuenta: la marca no existia todavia.)")

    return "\n".join(L)
