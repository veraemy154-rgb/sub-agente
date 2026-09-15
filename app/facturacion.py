"""Facturacion y cobranza del retainer.

Cobrar a tiempo es mas importante que vender mas. Un retainer de US$ 1.800
que no se cobra en tres meses es peor que no tenerlo: trabajaste gratis y
encima quedaste mal.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

FACT_DIR = "out/facturas"

PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL", "ev227166@gmail.com")
PAYPAL_ME = os.environ.get("PAYPAL_ME", "")          # ej: "tuempresa" -> paypal.me/tuempresa/490USD
COMISION_PAYPAL_PCT = 5.5   # transaccion internacional: ~4.99% + fijo. Redondea hacia arriba.

# Rieles de cobro. Ordenados por preferencia: rapido, sin retenciones raras y en dolares.
RIELES_DEFAULT = [
    ("PayPal", f"{PAYPAL_EMAIL}", "inmediato · comision a cargo del cliente"),
    ("Zelle", "________________", "mismo dia, sin comision"),
    ("USDT (TRC20)", "________________", "mismo dia, red barata"),
    ("Wise", "________________", "1-2 dias"),
    ("Payoneer", "________________", "1-2 dias"),
    ("Transferencia bancaria USD", "datos a solicitud", "2-5 dias"),
]


def link_paypal(monto_usd: float, concepto: str = "",
                aplicar_recargo: bool = True) -> str:
    """Enlace de pago directo. Con PayPal.Me si esta configurado, si no el
    enlace clasico de PayPal al correo.

    Por defecto suma el recargo de la comision: si no lo haces, la comision
    internacional de PayPal (~5%) sale de tu margen en cada cobro.
    """
    monto = con_recargo(monto_usd) if aplicar_recargo else monto_usd
    m = f"{monto:.2f}"
    if PAYPAL_ME:
        return f"https://paypal.me/{PAYPAL_ME}/{m}USD"
    import urllib.parse
    q = urllib.parse.urlencode({
        "cmd": "_xclick", "business": PAYPAL_EMAIL,
        "item_name": concepto or "Servicio de seguridad",
        "amount": m, "currency_code": "USD", "no_shipping": "1",
    })
    return f"https://www.paypal.com/cgi-bin/webscr?{q}"


def con_recargo(monto: float, pct: float = COMISION_PAYPAL_PCT) -> float:
    """Monto a cobrar por PayPal para que te llegue `monto` limpio.

    PayPal cobra ~4.99% + fijo en transacciones internacionales y se lo descuenta
    al que cobra. Si no lo sumas al precio, tu margen se lo come la comision.
    """
    return round(monto * (1 + pct / 100.0), 2)

PLANES = {
    "base": {"fee": 1200, "horas": 0, "sla": "sin SLA", "alcance": "Escaneo en CI + informe mensual de evidencia + triage"},
    "pro": {"fee": 1800, "horas": 8, "sla": "72 h en criticos", "alcance": "Base + SLA 72 h + 8 h/mes de remediación"},
    "enterprise": {"fee": 2500, "horas": 20, "sla": "24 h en criticos", "alcance": "Pro + 20 h/mes + acompanamiento con el auditor"},
}

DIAS_VENCIMIENTO = 8


def numero(cliente: str, periodo: str) -> str:
    slug = "".join(c for c in cliente.upper() if c.isalnum())[:6]
    return f"F-{periodo}-{slug}"


def vencimiento(periodo: str, dias: int = DIAS_VENCIMIENTO) -> str:
    y, m = (int(x) for x in periodo.split("-"))
    if m == 12:
        sig = date(y + 1, 1, 1)
    else:
        sig = date(y, m + 1, 1)
    return (sig + timedelta(days=dias - 1)).isoformat()


def factura(cliente: dict, periodo: str, rieles: list[tuple[str, str, str]] | None = None,
            emisor: dict | None = None, extra: list[dict] | None = None) -> str:
    """Genera la factura mensual en Markdown.

    cliente = {"nombre","contacto","repos","plan","fee_usd","horas_extra"}
    """
    rieles = rieles or RIELES_DEFAULT
    emisor = emisor or {
        "nombre": "________________",
        "id_fiscal": "________________",
        "direccion": "________________",
        "email": "________________",
    }
    plan = (cliente.get("plan") or "").lower()
    fee = cliente.get("fee_usd") or PLANES.get(plan, {}).get("fee", 0)
    alcance = cliente.get("alcance") or PLANES.get(plan, {}).get("alcance", "Servicio de gestion de vulnerabilidades")
    horas_extra = cliente.get("horas_extra", 0)
    tarifa_extra = cliente.get("tarifa_extra_usd", 95)

    items = [{
        "concepto": f"Gestion de vulnerabilidades · plan {plan or 'personalizado'} · {periodo}",
        "detalle": alcance,
        "cantidad": 1, "precio": fee,
    }]
    if horas_extra:
        items.append({
            "concepto": "Horas adicionales de remediación",
            "detalle": f"{horas_extra} h a US$ {tarifa_extra}/h",
            "cantidad": horas_extra, "precio": tarifa_extra,
        })
    for e in (extra or []):
        items.append(e)

    subtotal = sum(i["cantidad"] * i["precio"] for i in items)
    desc = cliente.get("descuento_usd", 0)
    total = max(0, subtotal - desc)

    hoy = datetime.now(timezone.utc).date().isoformat()
    L = []
    L.append(f"# Factura {numero(cliente['nombre'], periodo)}")
    L.append("")
    L.append(f"**Emisor:** {emisor['nombre']}  ")
    L.append(f"**ID fiscal / RIF:** {emisor['id_fiscal']}  ")
    L.append(f"**Direccion:** {emisor['direccion']}  ")
    L.append(f"**Contacto:** {emisor['email']}")
    L.append("")
    L.append(f"**Cliente:** {cliente['nombre']}  ")
    if cliente.get("contacto"):
        L.append(f"**Atencion:** {cliente['contacto']}  ")
    L.append(f"**Fecha de emision:** {hoy}  ")
    L.append(f"**Periodo de servicio:** {periodo}  ")
    L.append(f"**Vencimiento:** {vencimiento(periodo)}")
    L.append("")
    L.append("## Detalle")
    L.append("")
    L.append("| Concepto | Detalle | Cant. | Precio unit. (USD) | Importe (USD) |")
    L.append("|---|---|---:|---:|---:|")
    for i in items:
        L.append(f"| {i['concepto']} | {i['detalle']} | {i['cantidad']} | "
                 f"{i['precio']:,} | {i['cantidad'] * i['precio']:,} |")
    L.append("")
    L.append(f"| | | | **Subtotal** | **US$ {subtotal:,}** |")
    if desc:
        L.append(f"| | | | Descuento | -US$ {desc:,} |")
    L.append(f"| | | | **TOTAL** | **US$ {total:,}** |")
    L.append("")
    L.append("## Alcance del periodo")
    L.append("")
    for r in cliente.get("repos", []):
        L.append(f"- `{r}`")
    L.append(f"- SLA: {PLANES.get(plan, {}).get('sla', cliente.get('sla', 'segun contrato'))}")
    if PLANES.get(plan, {}).get("horas"):
        L.append(f"- Horas de remediación incluidas: {PLANES[plan]['horas']} h/mes")
    L.append("")
    L.append("## Formas de pago")
    L.append("")
    L.append("| Medio | Dato | Acreditacion |")
    L.append("|---|---|---|")
    for nombre, dato, nota in rieles:
        L.append(f"| {nombre} | {dato} | {nota} |")
    L.append("")
    L.append("**Moneda: dolares estadounidenses (USD).** El monto se abona integro; "
             "las comisiones del intermediario corren por cuenta del pagador.")
    L.append("")
    L.append("## Condiciones")
    L.append("")
    L.append(f"1. Pago a {DIAS_VENCIMIENTO} dias desde la emision.")
    L.append("2. El servicio del mes siguiente se presta contra factura del mes corriente al dia.")
    L.append("3. Tras 15 dias de atraso, el servicio entra en suspension sin perdida del acceso a lo ya entregado.")
    L.append("4. Tras 30 dias, se cancela el alcance acordado y se renegocia.")
    L.append("5. Los precios son en USD y no estan sujetos a conversion a moneda local.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("_Factura generada automaticamente por scripts/evidencia_mensual.py._")
    return "\n".join(L)


def mrr(clientes: list[dict]) -> dict:
    tot = sum(c.get("fee_usd", 0) for c in clientes)
    return {"clientes": len(clientes), "mrr_usd": tot, "arr_usd": tot * 12,
            "ticket_promedio": round(tot / len(clientes)) if clientes else 0}


def guardar_factura(contenido: str, cliente: str, periodo: str) -> str:
    os.makedirs(FACT_DIR, exist_ok=True)
    ruta = os.path.join(FACT_DIR, f"{periodo}-{cliente.lower().replace(' ', '-')}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def estado_cuenta(pendientes: list[dict], hoy: date | None = None) -> dict:
    """pendientes = [{cliente, periodo, monto, emitida_en}]"""
    hoy = hoy or datetime.now(timezone.utc).date()
    al_dia, por_vencer, vencido, critico = [], [], [], []
    for p in pendientes:
        try:
            dias = (hoy - date.fromisoformat(p["emitida_en"])).days
        except Exception:
            dias = 0
        restante = DIAS_VENCIMIENTO - dias
        item = {**p, "dias": dias, "restante": restante}
        if restante < 0 <= -restante and -restante <= 14:
            vencido.append(item)
        elif restante <= -15:
            critico.append(item)
        elif restante <= 3:
            por_vencer.append(item)
        else:
            al_dia.append(item)
    return {"al_dia": al_dia, "por_vencer": por_vencer, "vencido": vencido,
            "critico": critico,
            "total_pendiente": sum(p["monto"] for p in pendientes),
            "total_vencido": sum(p["monto"] for p in vencido + critico)}
