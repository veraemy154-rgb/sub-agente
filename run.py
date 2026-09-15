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
import io
import os
import subprocess
import sys

from app.scanner import auditar
from app.report import a_markdown, estimar_precio
from app.leadgen import generar_leads, guardar, ICP_DEFAULT
from app.outreach import secuencia
from app.icp import perfil
from app.leadgen import puntuar_lead
from app.evidence import generar, ejemplo, mes_actual
from app.fuentes import filtrar, a_markdown, NIVELES
from app.analisis import redactar, post_linkedin
from app import pipeline as pipe


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


CTA_DEFAULT = ("Hago este mismo analisis por encargo para equipos que se preparan "
               "para SOC 2 o les llega el cuestionario de seguridad de un cliente "
               "grande. Si es tu caso, escribeme y te mando el de tu repo.")


def cmd_analisis(a):
    rep = auditar(a.repo, con_osv=not a.no_osv)
    if rep.get("error"):
        print(f"Error: {rep['error']}")
        return 1
    cta = a.cta or ("" if a.sin_cta else CTA_DEFAULT)
    if a.linkedin:
        out = post_linkedin(rep, autor=a.autor, anonimo=a.anonimo, cta=cta)
    else:
        out = redactar(rep, autor=a.autor, anonimo=a.anonimo, cta=cta)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Escrito en {a.out}")
    else:
        print(out)
    if not a.anonimo:
        print("\n[recordatorio] Avisa al proyecto antes de publicar. "
              "Ver templates/analisis-publico.md", file=sys.stderr)
    return 0


def cmd_pipeline(a):
    if a.accion == "add":
        r = pipe.add(a.repo, contacto=a.contacto, canal=a.canal,
                     valor=a.valor, nota=a.nota, estado=a.estado, enlace=a.enlace)
        print(r.get("error") or f"Agregado: {r['repo']} [{r['estado']}] · "
                                f"proximo toque {r['proximo_en']}")
        return 0

    if a.accion == "mov":
        r = pipe.mover(a.repo, a.estado, nota=a.nota, dias=a.dias)
        if r.get("error"):
            print(r["error"])
            return 1
        print(f"{r['repo']}: {r['estado']} · proximo toque {r['proximo_en'] or '—'}")
        if r["estado"] == "retainer":
            print(f"  MRR +US$ {r.get('mrr_usd', 0):,}")
        return 0

    if a.accion == "rm":
        print("Eliminado" if pipe.eliminar(a.repo) else "No estaba en el pipeline")
        return 0

    if a.accion == "importar":
        r = pipe.importar(a.desde, solo=[p.upper() for p in a.solo.split(",") if p.strip()])
        print(r.get("error") or f"{r['importados']} importados · pipeline: {r['total']}")
        return 0

    if a.accion == "hoy":
        ps = pipe.pendientes_hoy()
        if not ps:
            print("Nada pendiente hoy. Entonces te falta prospectar: "
                  "python run.py leads --top 20")
            return 0
        print(f"SEGUIMIENTOS PENDIENTES: {len(ps)}\n")
        for r in ps:
            print(f"  {r['repo']:42} [{r['estado']}]  vence {r.get('proximo_en')}")
        return 0

    if a.accion == "stats":
        m = pipe.metricas()
        print(f"Registros: {m['total']}")
        for e, n in m["por_estado"].items():
            if n:
                print(f"  {e:12} {n:4}  (x {int(pipe.PROB[e]*100)}% cierre)")
        print(f"\nMRR actual:            US$ {m['mrr_usd']:,}   (anualizado {m['arr_usd']:,})")
        print(f"Pipeline bruto:        US$ {m['pipeline_bruto_usd']:,}")
        print(f"Pipeline ponderado:    US$ {m['pipeline_ponderado_usd']:,}  <- el numero honesto")
        print(f"Tasa de respuesta:     {m['tasa_respuesta_pct']}%  (sana: 8-15%)")
        print(f"Tasa de cierre:        {m['tasa_cierre_pct']}%")
        print(f"Seguimientos vencidos: {m['pendientes_hoy']}")
        return 0

    regs = pipe.cargar()
    if a.estado:
        regs = [r for r in regs if r["estado"] == a.estado]
    print(pipe.a_tabla(regs))
    return 0


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def cmd_doctor(a):
    """Diagnostico del entorno. Responde 'por que me salen resultados raros'."""
    ok = lambda b: "OK  " if b else "FALLA"
    problemas = 0

    print("=== ENTORNO ===")
    py = sys.version.split()[0]
    mayor, menor = (int(x) for x in py.split(".")[:2])
    print(f"  {ok((mayor, menor) >= (3, 9))} Python {py}  (minimo 3.9)")

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        from app.scanner import _get
        d, st = _get("/rate_limit")
        if d.get("_auth_error"):
            print(f"  FALLA GITHUB_TOKEN INVALIDO ({token[:11]}...): 401 Bad credentials")
            print("        Ese valor es un placeholder o esta mal copiado.")
            print("        Crea uno real en github.com/settings/tokens y:")
            print("          export GITHUB_TOKEN=ghp_tu_token_real")
            print("        (y quita la linea mala de ~/.bashrc: sed -i '/ghp_tu_token/d' ~/.bashrc)")
            problemas += 2
        else:
            core = (d.get("resources") or {}).get("core") or {}
            limite = core.get("limit", "?")
            quedan = core.get("remaining", "?")
            print(f"  {ok(limite == 5000)} GITHUB_TOKEN valido · limite {limite}/h · quedan {quedan}")
            if limite != 5000:
                print("        Un token valido da 5000/h. Si da 60, no te lo esta tomando.")
                problemas += 1
    else:
        print(f"  {ok(False)} GITHUB_TOKEN NO configurado -> 60 peticiones/hora")
        print("       export GITHUB_TOKEN=ghp_... (github.com/settings/tokens)")
        problemas += 1

    print("\n=== REPOSITORIO ===")
    ruta = _git("rev-parse", "--show-toplevel")
    if not ruta:
        print("  FALLA Este directorio NO es un repositorio git.")
        print("        No se puede sincronizar. Solucion:")
        print("        git clone https://github.com/veraemy154-rgb/sub-agente.git")
        print("        cd sub-agente && git checkout arena/01a0a513-sub-agente")
        problemas += 3
    else:
        print(f"  OK   Repositorio en {ruta}")

    rama = _git("rev-parse", "--abbrev-ref", "HEAD") or "(desconocida)"
    rama_ok = rama == "arena/01a0a513-sub-agente"
    print(f"  {ok(rama_ok)} Rama: {rama}")
    if not rama_ok:
        print("        git checkout arena/01a0a513-sub-agente")
        problemas += 1

    head = _git("log", "-1", "--oneline")
    print(f"  {'OK  ' if head else '?   '} Ultimo commit: {head or 'ninguno'}")

    sucios = [l for l in _git("status", "--porcelain").splitlines() if l.strip()] if ruta else []
    if sucios:
        print(f"  FALLA {len(sucios)} archivo(s) MODIFICADOS localmente:")
        for l in sucios[:8]:
            print(f"        {l}")
        print("        Si no los cambiaste TU, alguien los reescribio. Arreglo:")
        print("        git fetch origin && git reset --hard origin/arena/01a0a513-sub-agente")
        problemas += 2
    else:
        print("  OK   Sin modificaciones locales")

    remoto = _git("rev-parse", "--abbrev-ref", "@{upstream}")
    if remoto:
        atras = _git("rev-list", "--count", f"HEAD..{remoto}")
        n = int(atras or 0)
        print(f"  {ok(n == 0)} Actualizado con {remoto}"
              + ("" if n == 0 else f" -> {n} commit(s) ATRAS"))
        if n:
            print("        git pull --ff-only")
            problemas += 1

    print("\n=== INTEGRIDAD DEL CODIGO ===")
    # Senales que NO existen en esta rama: si aparecen, los filtros fueron
    # reescritos por otra version y los resultados no son confiables.
    fantasmas = ["issues abiertos", "sin triage", "Cuenta con politica de seguridad"]
    base = os.path.dirname(os.path.abspath(__file__))
    hallados = []
    for raiz, _, archivos in os.walk(os.path.join(base, "app")):
        for f in archivos:
            if not f.endswith(".py"):
                continue
            try:
                t = io.open(os.path.join(raiz, f), encoding="utf-8").read()
            except Exception:
                continue
            for fan in fantasmas:
                if fan in t:
                    hallados.append((f, fan))
    limpio = not hallados
    print(f"  {ok(limpio)} Filtros sin versiones ajenas mezcladas")
    if not limpio:
        for f, fan in hallados[:6]:
            print(f"        {f} contiene '{fan}' <- NO es de esta rama")
        problemas += 2

    esperados = ["scanner.py", "icp.py", "leadgen.py", "pipeline.py",
                 "analisis.py", "fuentes.py", "evidence.py", "facturacion.py"]
    faltan = [e for e in esperados
              if not os.path.exists(os.path.join(base, "app", e))]
    print(f"  {ok(not faltan)} Modulos completos"
          + ("" if not faltan else f" -> faltan: {', '.join(faltan)}"))
    if faltan:
        problemas += 1

    print("\n=== SALIDA ===")
    try:
        os.makedirs("out", exist_ok=True)
        with open(os.path.join("out", ".doctor"), "w") as f:
            f.write("ok")
        os.remove(os.path.join("out", ".doctor"))
        print("  OK   Se puede escribir en out/")
    except Exception as e:
        print(f"  FALLA No se puede escribir en out/: {e}")
        problemas += 1

    print()
    if problemas:
        print(f"RESULTADO: {problemas} problema(s) encontrado(s).")
        if not ruta:
            print("Esta copia no es un clon de git: no se puede actualizar.")
            print("Arranca de cero (es lo mas rapido y lo mas seguro):")
            print("  cd ~ && git clone https://github.com/veraemy154-rgb/sub-agente.git")
            print("  cd sub-agente && git checkout arena/01a0a513-sub-agente")
            print("  python run.py doctor")
        else:
            print("Arreglo:")
            print("  git fetch origin && git reset --hard origin/arena/01a0a513-sub-agente")
            print("  (si tienes cambios tuyos, guardalos antes con: git stash)")
        return 1
    print("RESULTADO: todo correcto. Ya puedes correr: python run.py leads --top 8")
    return 0


def cmd_fuentes(a):
    nivel = a.nivel or None
    if a.md:
        print(a_markdown(nivel))
        return 0
    for n in sorted(NIVELES):
        fs = [f for f in filtrar() if f[1] == n and (not nivel or n == nivel)]
        if not fs:
            continue
        print(f"\n{'='*72}\n{NIVELES[n]}\n{'='*72}")
        for fid, _, nombre, que, url, nota in fs:
            print(f"\n[{fid}] {nombre}")
            print(f"     que: {que}")
            print(f"     url: {url}")
            print(f"     uso: {nota}")
    print("\n" + "=" * 72)
    print("Guarda la lista para ir tachando: python run.py fuentes --md > out/fuentes.md")
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

    f = sub.add_parser("fuentes", help="donde encontrar prospectos (enlaces listos)")
    f.add_argument("--nivel", type=int, default=0, choices=[0, 1, 2, 3, 4])
    f.add_argument("--md", action="store_true")
    f.set_defaults(fn=cmd_fuentes)

    n = sub.add_parser("analisis", help="borrador de analisis publico para publicar")
    n.add_argument("repo")
    n.add_argument("--anonimo", action="store_true", help="no nombrar el proyecto")
    n.add_argument("--linkedin", action="store_true", help="post nativo en vez de articulo")
    n.add_argument("--autor", default="")
    n.add_argument("--cta", default="")
    n.add_argument("--sin-cta", action="store_true")
    n.add_argument("--no-osv", action="store_true")
    n.add_argument("--out", default="")
    n.set_defaults(fn=cmd_analisis)

    sub.add_parser("doctor", help="diagnostica el entorno y la copia del repo").set_defaults(fn=cmd_doctor)

    pl = sub.add_parser("pipeline", help="tablero comercial: prospecto -> retainer")
    pl.add_argument("--estado", default="", choices=pipe.ESTADOS)
    plsub = pl.add_subparsers(dest="accion")
    pl.set_defaults(fn=cmd_pipeline)

    pa = plsub.add_parser("add", help="agregar un prospecto")
    pa.add_argument("repo")
    pa.add_argument("--contacto", default="")
    pa.add_argument("--canal", default="email")
    pa.add_argument("--valor", type=float, default=0)
    pa.add_argument("--nota", default="")
    pa.add_argument("--enlace", default="")
    pa.add_argument("--estado", default="prospecto", choices=pipe.ESTADOS)

    pm = plsub.add_parser("mov", help="mover de estado")
    pm.add_argument("repo")
    pm.add_argument("estado", choices=pipe.ESTADOS)
    pm.add_argument("--nota", default="")
    pm.add_argument("--dias", type=int, default=None)

    pr = plsub.add_parser("rm", help="quitar del pipeline")
    pr.add_argument("repo")

    pi = plsub.add_parser("importar", help="cargar out/leads.json")
    pi.add_argument("--desde", default="out/leads.json")
    pi.add_argument("--solo", default="P1,P2")

    pls = plsub.add_parser("ls", help="ver el tablero")
    pls.add_argument("--estado", default="", choices=pipe.ESTADOS)

    plsub.add_parser("hoy", help="seguimientos vencidos")
    plsub.add_parser("stats", help="metricas del embudo")

    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == "__main__":
    main()
