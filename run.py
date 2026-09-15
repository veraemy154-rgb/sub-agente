#!/usr/bin/env python3
"""CLI para operar sin levantar la API.

Uso:
    python run.py scan owner/repo
    python run.py scan owner/repo --md > out/informe.md
    python run.py leads --lang python,javascript --top 12
    python run.py outreach owner/repo --remitente "Tu Nombre"
    python run.py evidencia --cliente "Acme" --repos acme/api,acme/web
    python run.py evidencia --demo
"""
from __future__ import annotations

import argparse

from app.scanner import auditar
from app.report import a_markdown, estimar_precio
from app.leadgen import generar_leads, guardar, ICP_DEFAULT
from app.outreach import secuencia
from app.icp import perfil
from app.leadgen import puntuar_lead
from app.evidence import generar, ejemplo, mes_actual


def cmd_scan(a):
    rep = auditar(a.repo, con_osv=not a.no_osv)
    if rep.get("error"):
        print(f"Error auditando {a.repo}: {rep['error']}")
        return 1
    if a.md:
        print(a_markdown(rep))
        return 0
    print(f"{rep['repo']}  score={rep['score_riesgo']}/100 ({rep['banda']})  "
          f"hallazgos={rep['n_hallazgos']}")
    for f in rep["hallazgos"]:
        print(f"  [{f['severidad'].upper():11}] {f['id']}  {f['titulo']}  ({f['control_soc2']})")
    p = estimar_precio(rep)
    print(f"\nDiagnostico: US$ {p['diagnostico_express_usd']} · "
          f"Remediacion: US$ {p['remediacion_estimada_usd']} · "
          f"Retainer: US$ {p['retainer_sugerido_usd_mes']}/mes")
    print(f"Informe completo: python run.py scan {a.repo} --md")
    return 0


def cmd_leads(a):
    icp = {**ICP_DEFAULT, "lenguajes": [l.strip() for l in a.lang.split(",") if l.strip()]}
    leads = generar_leads(icp=icp, por_lenguaje=a.por_lang, auditar_top=a.top,
                          con_osv=not a.no_osv, delay=a.delay,
                          solo_organizaciones=not a.incluir_usuarios)
    ruta = guardar(leads, a.out)
    print(f"\n{'PRIO':10} {'R':>3} {'ICP':>4} {'CON':>4}  {'REPO':40} {'TICKET':>7}")
    print("-" * 88)
    for l in leads:
        print(f"{l['prioridad']:10} {l['score_riesgo']:3} {l['score_icp']:4} "
              f"{l['contribuyentes']:4}  {l['repo'][:40]:40} {l['ticket_potencial_usd']:7}")
        for s in l["senales_comerciales"][:2]:
            print(f"{'':26}-> {s}")
    print("-" * 88)
    print(f"Pipeline potencial: US$ {sum(l['ticket_potencial_usd'] for l in leads):,}")
    print(f"Guardado en {ruta}")
    return 0


def cmd_outreach(a):
    rep = auditar(a.repo, con_osv=not a.no_osv)
    if rep.get("error"):
        print(f"Error: {rep['error']}")
        return 1
    lead = puntuar_lead(rep, perfil(a.repo))
    print(f"# Secuencia para {lead['repo']} [{lead['prioridad']}] "
          f"ICP={lead['score_icp']} riesgo={lead['score_riesgo']}\n")
    for paso in secuencia(lead, rep, a.remitente):
        print(f"\n{'='*70}\nDIA {paso['dia']} · {paso['canal'].upper()}\n{'='*70}\n")
        print(paso["mensaje"])
    return 0


def cmd_evidencia(a):
    if a.demo:
        md = ejemplo()
    else:
        if not a.cliente or not a.repos:
            print("Falta --cliente y --repos (o usa --demo)")
            return 1
        repos = [r.strip() for r in a.repos.split(",") if r.strip()]
        md = generar(a.cliente, a.periodo or mes_actual(), repos,
                     responsable=a.responsable, notas=a.notas)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Escrito en {a.out}")
    else:
        print(md)
    return 0


def main():
    p = argparse.ArgumentParser(prog="sub-agente")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="auditar un repo publico")
    s.add_argument("repo")
    s.add_argument("--md", action="store_true", help="imprimir el informe en Markdown")
    s.add_argument("--no-osv", action="store_true")
    s.set_defaults(fn=cmd_scan)

    l = sub.add_parser("leads", help="generar prospectos calificados")
    l.add_argument("--lang", default="python,javascript")
    l.add_argument("--por-lang", type=int, default=10)
    l.add_argument("--top", type=int, default=12)
    l.add_argument("--delay", type=float, default=1.0)
    l.add_argument("--out", default="out/leads.json")
    l.add_argument("--no-osv", action="store_true")
    l.add_argument("--incluir-usuarios", action="store_true",
                   help="incluir repos de usuarios (por defecto solo organizaciones)")
    l.set_defaults(fn=cmd_leads)

    o = sub.add_parser("outreach", help="generar secuencia de contacto")
    o.add_argument("repo")
    o.add_argument("--remitente", default="Equipo de Seguridad")
    o.add_argument("--no-osv", action="store_true")
    o.set_defaults(fn=cmd_outreach)

    e = sub.add_parser("evidencia", help="informe mensual de evidencia (retainer)")
    e.add_argument("--cliente", default="")
    e.add_argument("--repos", default="")
    e.add_argument("--periodo", default="")
    e.add_argument("--responsable", default="________________")
    e.add_argument("--notas", default="")
    e.add_argument("--demo", action="store_true")
    e.add_argument("--out", default="")
    e.set_defaults(fn=cmd_evidencia)

    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == "__main__":
    main()
