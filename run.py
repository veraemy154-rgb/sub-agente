#!/usr/bin/env python3
"""CLI para operar sin levantar la API.

Uso:
    python run.py scan owner/repo
    python run.py scan owner/repo --md > out/informe.md
    python run.py leads --lang python,javascript --top 12
    python run.py outreach owner/repo --remitente "Tu Nombre"
"""
from __future__ import annotations

import argparse
import json

from app.scanner import auditar
from app.report import a_markdown, estimar_precio
from app.leadgen import generar_leads, guardar, ICP_DEFAULT
from app.outreach import secuencia


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
    print(f"\nDiagnostico Express: US$ {p['diagnostico_express_usd']} · "
          f"Remediacion estimada: US$ {p['remediacion_estimada_usd']} · "
          f"Retainer sugerido: US$ {p['retainer_sugerido_usd_mes']}/mes")
    print(f"Informe completo: python run.py scan {a.repo} --md")
    return 0


def cmd_leads(a):
    icp = {**ICP_DEFAULT, "lenguajes": [l.strip() for l in a.lang.split(",") if l.strip()]}
    leads = generar_leads(icp=icp, por_lenguaje=a.por_lang, auditar_top=a.top,
                          con_osv=not a.no_osv, delay=a.delay)
    ruta = guardar(leads, a.out)
    print(f"\n{'PRIO':10} {'SCORE':>5}  {'REPO':42} {'TICKET':>7}  SENALES")
    for l in leads:
        print(f"{l['prioridad']:10} {l['score_riesgo']:5}  {l['repo'][:42]:42} "
              f"{l['ticket_potencial_usd']:7}  {'; '.join(l['senales'][:2])[:60]}")
    print(f"\nPipeline potencial: US$ {sum(l['ticket_potencial_usd'] for l in leads):,}")
    print(f"Guardado en {ruta}")
    return 0


def cmd_outreach(a):
    rep = auditar(a.repo, con_osv=not a.no_osv)
    if rep.get("error"):
        print(f"Error: {rep['error']}")
        return 1
    from app.leadgen import puntuar_lead
    lead = puntuar_lead(rep)
    seq = secuencia(lead, rep, a.remitente)
    print(f"# Secuencia para {lead['repo']} [{lead['prioridad']}]\n")
    for paso in seq:
        print(f"\n{'='*70}\nDIA {paso['dia']} · {paso['canal'].upper()}\n{'='*70}\n")
        print(paso["mensaje"])
    return 0


def main():
    p = argparse.ArgumentParser(prog="sub-agente")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="auditar un repo publico")
    s.add_argument("repo")
    s.add_argument("--md", action="store_true", help="imprimir el informe en Markdown")
    s.add_argument("--no-osv", action="store_true", help="no consultar CVEs")
    s.set_defaults(fn=cmd_scan)

    l = sub.add_parser("leads", help="generar prospectos priorizados")
    l.add_argument("--lang", default="python,javascript")
    l.add_argument("--por-lang", type=int, default=10)
    l.add_argument("--top", type=int, default=12, help="cuantos auditar")
    l.add_argument("--delay", type=float, default=1.0)
    l.add_argument("--out", default="out/leads.json")
    l.add_argument("--no-osv", action="store_true")
    l.set_defaults(fn=cmd_leads)

    o = sub.add_parser("outreach", help="generar la secuencia de contacto")
    o.add_argument("repo")
    o.add_argument("--remitente", default="Equipo de Seguridad")
    o.add_argument("--no-osv", action="store_true")
    o.set_defaults(fn=cmd_outreach)

    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == "__main__":
    main()
