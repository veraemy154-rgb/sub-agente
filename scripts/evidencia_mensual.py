#!/usr/bin/env python3
"""Genera informes de evidencia y facturas del mes para todos los clientes.

Este es el script que convierte el retainer en una maquina: corre el 1 de mes,
escanea todo, compara contra el estado guardado, y escupe informe + factura
por cliente. Tu trabajo queda en revisar y firmar.

Uso:
    python scripts/evidencia_mensual.py                 # todos los clientes
    python scripts/evidencia_mensual.py --cliente acme  # uno solo
    python scripts/evidencia_mensual.py --no-facturar   # solo informes
    python scripts/evidencia_mensual.py --periodo 2026-09

Configuracion: clientes.json en la raiz (ver clientes.ejemplo.json)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.scanner import auditar          # noqa: E402
from app.snapshots import actualizar, marcar_novedad, cierres_del_periodo  # noqa: E402
from app.evidence import generar         # noqa: E402
from app.facturacion import factura      # noqa: E402

OUT_EVID = "out/evidencia"
OUT_FACT = "out/facturas"


def cargar_clientes(ruta: str = "clientes.json") -> list[dict]:
    if not os.path.exists(ruta):
        print(f"No existe {ruta}. Copia clientes.ejemplo.json y rellenalo.")
        return []
    with open(ruta, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("clientes", data if isinstance(data, list) else [])


def procesar(cliente: dict, periodo: str, facturar: bool = True,
             con_osv: bool = True, delay: float = 1.0) -> dict:
    import time
    nombre = cliente["nombre"]
    repos = cliente["repos"]
    print(f"\n=== {nombre} ===")

    escaneos = []
    for r in repos:
        print(f"  escaneando {r}...")
        rep = auditar(r, con_osv=con_osv)
        if rep.get("error"):
            print(f"    ! {rep['error']}")
        escaneos.append(rep)
        time.sleep(delay)

    diff = actualizar(nombre, repos, escaneos, periodo=periodo)
    abiertos = marcar_novedad(diff["abiertos"], periodo)
    cerrados = cierres_del_periodo(nombre, periodo)

    md = generar(
        cliente=nombre,
        periodo=periodo,
        repos=repos,
        hallazgos_abiertos=abiertos,
        cerrados=cerrados,
        excepciones=cliente.get("excepciones", []),
        responsable=cliente.get("responsable", "________________"),
        notas=cliente.get("notas", ""),
    )
    os.makedirs(OUT_EVID, exist_ok=True)
    slug = nombre.lower().replace(" ", "-")
    rut = os.path.join(OUT_EVID, f"{periodo}-{slug}.md")
    with open(rut, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  informe -> {rut}  ({len(abiertos)} abiertos, {len(cerrados)} cerrados)")

    rut_fact = None
    if facturar and cliente.get("fee_usd"):
        os.makedirs(OUT_FACT, exist_ok=True)
        fm = factura(cliente, periodo)
        rut_fact = os.path.join(OUT_FACT, f"{periodo}-{slug}.md")
        with open(rut_fact, "w", encoding="utf-8") as f:
            f.write(fm)
        print(f"  factura -> {rut_fact}  (US$ {cliente['fee_usd']})")

    return {"cliente": nombre, "abiertos": len(abiertos), "cerrados": len(cerrados),
            "nuevos": len(diff["nuevos"]), "informe": rut, "factura": rut_fact,
            "fee_usd": cliente.get("fee_usd", 0)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cliente", default="")
    p.add_argument("--periodo", default="")
    p.add_argument("--no-facturar", action="store_true")
    p.add_argument("--no-osv", action="store_true")
    p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--config", default="clientes.json")
    a = p.parse_args()

    periodo = a.periodo or datetime.now(timezone.utc).strftime("%Y-%m")
    clientes = cargar_clientes(a.config)
    if a.cliente:
        clientes = [c for c in clientes if c["nombre"].lower() == a.cliente.lower()]
    if not clientes:
        return 1

    print(f"Periodo: {periodo} · {len(clientes)} cliente(s)")
    res = []
    for c in clientes:
        try:
            res.append(procesar(c, periodo, facturar=not a.no_facturar,
                                con_osv=not a.no_osv, delay=a.delay))
        except Exception as e:
            print(f"  ! fallo con {c['nombre']}: {type(e).__name__}: {e}")

    print("\n" + "=" * 62)
    print(f"{'CLIENTE':26} {'ABIERT':>7} {'CERR':>5} {'NUEV':>5} {'FEE':>7}")
    print("-" * 62)
    tot = 0
    for r in res:
        tot += r["fee_usd"]
        print(f"{r['cliente'][:26]:26} {r['abiertos']:7} {r['cerrados']:5} {r['nuevos']:5} {r['fee_usd']:7}")
    print("-" * 62)
    print(f"{'TOTAL A FACTURAR':26} {'':20} US$ {tot:,}/mes")
    print(f"MRR anualizado: US$ {tot * 12:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
