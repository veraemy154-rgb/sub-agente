"""Render del informe que se le entrega al prospecto.

El informe NO es un volcado de tecnico: es una pieza de venta.
Estructura: que nos preocupa -> que significa para tu auditoria/venta -> que hacemos -> cuanto.
"""
from __future__ import annotations

SEV_LABEL = {
    "critica": "CRITICA", "alta": "ALTA", "media": "MEDIA",
    "baja": "BAJA", "informativa": "INFO",
}
PRECIO_BASE = 490
PRECIO_POR_HALLAZGO = 120


def estimar_precio(rep: dict) -> dict:
    """Precio del Diagnostico Express y estimado de la remediacion.

    Ancla en el diagnostico barato; el ticket real se cotiza despues
    con el numero de hallazgos altos/criticos a la vista.
    """
    h = rep.get("hallazgos", [])
    altos = sum(1 for f in h if f["severidad"] in ("critica", "alta"))
    medios = sum(1 for f in h if f["severidad"] == "media")
    rem = PRECIO_BASE + altos * 220 + medios * 90
    rem = max(1200, min(6500, rem))
    return {
        "diagnostico_express_usd": PRECIO_BASE,
        "remediacion_estimada_usd": rem,
        "retainer_sugerido_usd_mes": 1200 if altos + medios < 6 else 1800,
        "justificacion": f"{altos} hallazgo(s) alto/critico y {medios} medio(s).",
    }


def a_markdown(rep: dict, idioma: str = "es") -> str:
    if rep.get("error"):
        return f"# Auditoria: {rep['repo']}\n\nNo se pudo auditar: `{rep['error']}`.\n"
    h = rep["hallazgos"]
    p = estimar_precio(rep)
    L = []
    L.append(f"# Evaluacion de exposicion - `{rep['repo']}`")
    L.append("")
    L.append(f"Generado: {rep['auditado_en']} · Fuente: **informacion publica** (GitHub) · Metodo: observacion pasiva, sin explotacion.")
    L.append("")
    L.append(f"**Indice de exposicion: {rep['score_riesgo']}/100 ({rep['banda']})** · {rep['n_hallazgos']} hallazgo(s)")
    L.append("")
    L.append(f"_{rep['lectura_comercial']}_")
    if rep.get("descripcion"):
        L.append(f"\n> {rep['descripcion']}")
    L.append("")
    L.append("## Resumen para direccion")
    L.append("")
    L.append(
        "Este no es un reporte de intrusión ni una prueba de explotación. Es una lectura "
        "de la superficie pública del repositorio contra los controles que suelen exigir "
        "SOC 2, ISO 27001 y los cuestionarios de seguridad de clientes enterprise. "
        "Cada hallazgo es un control que hoy no se puede evidenciar.")
    L.append("")
    L.append("## Hallazgos")
    L.append("")
    L.append("| # | Severidad | Hallazgo | Control | Esfuerzo |")
    L.append("|---|-----------|----------|---------|----------|")
    for f in h:
        L.append(f"| {f['id']} | {SEV_LABEL[f['severidad']]} | {f['titulo']} | {f['control_soc2']} | {f['esfuerzo'].upper()} |")
    L.append("")
    for f in h:
        L.append(f"### {f['id']} · [{SEV_LABEL[f['severidad']]}] {f['titulo']}")
        L.append("")
        L.append(f"**Que observamos:** {f['detalle']}")
        L.append("")
        L.append(f"**Por que importa para la auditoria:** control {f['control_soc2']} — hoy no hay evidencia automatica de este control.")
        L.append("")
        L.append(f"**Como se remedia:** {f['remediacion']}")
        L.append("")
    if rep.get("cves"):
        L.append("## Vulnerabilidades conocidas en dependencias")
        L.append("")
        for k, v in rep["cves"].items():
            L.append(f"- `{k}`: {', '.join(v)}")
        L.append("")
    L.append("## Propuesta")
    L.append("")
    L.append("| Etapa | Alcance | Inversion |")
    L.append("|-------|---------|-----------|")
    L.append(f"| Diagnostico Express | Inventario completo + plan priorizado + evidencia para el auditor | US$ {p['diagnostico_express_usd']} |")
    L.append(f"| Remediacion | Implementacion de los {p['justificacion']} | US$ {p['remediacion_estimada_usd']} (estimado) |")
    L.append(f"| Gestion continua | Escaneo en CI + informe mensual de evidencia + SLA de respuesta | US$ {p['retainer_sugerido_usd_mes']}/mes |")
    L.append("")
    L.append("---")
    L.append("")
    L.append("_Documento generado a partir de informacion publica. No se accedio, exploto ni "
             "se extrajo dato alguno de sistemas privados. La remediation requiere autorizacion "
             "escrita previa._")
    return "\n".join(L)
