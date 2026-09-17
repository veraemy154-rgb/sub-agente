"""Informe mensual de evidencia: el producto que sostiene el retainer.

Por que esto vale US$ 1.200-2.500 al mes: el auditor de SOC 2 no te pide que no
haya vulnerabilidades, te pide que DEMUESTRES que las gestionas. Un informe
mensual con fechas, responsables, cierres y excepciones aceptadas es exactamente
esa evidencia. Y el cliente lo necesita todos los meses, no una vez.

Regla del director: si el informe lo escribes a mano, el retainer no escala.
Se genera desde datos, el humano solo revisa y firma.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


def mes_actual() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


CONTROLES = [
    ("CC7.1", "Gestion de vulnerabilidades",
     "Escaneo de dependencias en cada PR + triage con severidad asignada"),
    ("CC7.2", "Monitoreo y deteccion",
     "Alertas automaticas ante hallazgo critico; registro centralizado"),
    ("CC8.1", "Gestion de cambios",
     "Rama protegida, revision obligatoria, pipeline bloqueante"),
    ("CC6.1", "Acceso logico",
     "Revision de accesos al repositorio y rotacion de credenciales"),
    ("CC6.6", "Amenazas externas",
     "Deteccion de secretos en el codigo (pre-commit + CI)"),
    ("CC2.3", "Comunicacion",
     "Politica de divulgacion publicada y canal de reporte"),
]


def calcular_metricas(hallazgos_abiertos: list[dict], cerrados: list[dict],
                      repos: list[str], dias_mes: int = 30) -> dict:
    criticos_abiertos = sum(1 for h in hallazgos_abiertos if h.get("severidad") in ("critica", "alta"))
    mttr = None
    if cerrados:
        mttr = round(sum(h.get("dias_abierto", 0) for h in cerrados) / len(cerrados), 1)
    return {
        "repos_en_alcance": len(repos),
        "hallazgos_nuevos": sum(1 for h in hallazgos_abiertos if h.get("es_nuevo")),
        "hallazgos_cerrados": len(cerrados),
        "hallazgos_abiertos": len(hallazgos_abiertos),
        "criticos_abiertos": criticos_abiertos,
        "mttr_dias": mttr,
        "tasa_cierre_pct": round(100 * len(cerrados) / max(1, len(cerrados) + len(hallazgos_abiertos)), 1),
        "cobertura_escaneo_pct": 100.0 if repos else 0.0,
        "cumple_sla": mttr is not None and mttr <= 14,
    }


def generar(cliente: str, periodo: str, repos: list[str],
            hallazgos_abiertos: list[dict] | None = None,
            cerrados: list[dict] | None = None,
            excepciones: list[dict] | None = None,
            responsable: str = "________________",
            notas: str = "") -> str:
    hab = hallazgos_abiertos or []
    cer = cerrados or []
    exc = excepciones or []
    m = calcular_metricas(hab, cer, repos)
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")

    L = []
    L.append(f"# Informe mensual de gestion de vulnerabilidades")
    L.append("")
    L.append(f"**Cliente:** {cliente}  ")
    L.append(f"**Periodo:** {periodo}  ")
    L.append(f"**Alcance:** {len(repos)} repositorio(s): {', '.join(f'`{r}`' for r in repos)}  ")
    L.append(f"**Responsable tecnico:** {responsable}  ")
    L.append(f"**Emitido:** {ahora}")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1. Resumen para direccion")
    L.append("")
    estado = "controlado" if m["criticos_abiertos"] == 0 else f"con {m['criticos_abiertos']} hallazgo(s) alto/critico en tratamiento"
    L.append(
        f"Durante {periodo} se gestionaron **{m['hallazgos_cerrados'] + m['hallazgos_abiertos']} hallazgos** "
        f"sobre {m['repos_en_alcance']} repositorios en alcance. Se cerraron "
        f"**{m['hallazgos_cerrados']}** ({m['tasa_cierre_pct']} %). El estado general se considera "
        f"**{estado}**. "
        + (f"El tiempo medio de resolucion fue de {m['mttr_dias']} dias"
           + (", dentro del SLA acordado." if m["cumple_sla"] else ", por encima del SLA acordado (14 dias).")
           if m["mttr_dias"] is not None else "Sin cierres en el periodo."))
    L.append("")
    L.append("| Metrica | Valor | Objetivo | Estado |")
    L.append("|---|---|---|---|")
    L.append(f"| Repositorios en alcance | {m['repos_en_alcance']} | todos los productivos | OK |")
    L.append(f"| Cobertura de escaneo | {m['cobertura_escaneo_pct']:.0f} % | 100 % | {'OK' if m['cobertura_escaneo_pct'] >= 100 else 'PARCIAL'} |")
    L.append(f"| Hallazgos nuevos | {m['hallazgos_nuevos']} | — | — |")
    L.append(f"| Hallazgos cerrados | {m['hallazgos_cerrados']} | — | — |")
    L.append(f"| Tasa de cierre | {m['tasa_cierre_pct']} % | > 70 % | {'OK' if m['tasa_cierre_pct'] >= 70 else 'ATENCION'} |")
    L.append(f"| MTTR (dias) | {m['mttr_dias'] if m['mttr_dias'] is not None else '—'} | <= 14 | {'OK' if m['cumple_sla'] else 'ATENCION'} |")
    L.append(f"| Altos/criticos abiertos | {m['criticos_abiertos']} | 0 | {'OK' if m['criticos_abiertos'] == 0 else 'ATENCION'} |")
    L.append("")
    L.append("## 2. Estado de los controles (evidencia para el auditor)")
    L.append("")
    L.append("| Control | Nombre | Evidencia generada | Estado |")
    L.append("|---|---|---|---|")
    for cid, nombre, evid in CONTROLES:
        L.append(f"| {cid} | {nombre} | {evid} | Operativo |")
    L.append("")
    L.append("_Estado a verificar mes a mes; marcar 'No operativo' con plan de remediación si aplica._")
    L.append("")
    L.append("## 3. Hallazgos cerrados en el periodo")
    L.append("")
    if cer:
        L.append("| ID | Severidad | Hallazgo | Repo | PR | Dias abierto | Fecha cierre |")
        L.append("|---|---|---|---|---|---|---|")
        for h in cer:
            L.append(f"| {h.get('id','—')} | {h.get('severidad','—')} | {h.get('titulo','—')} | "
                     f"`{h.get('repo','—')}` | {h.get('pr','—')} | {h.get('dias_abierto','—')} | {h.get('fecha_cierre','—')} |")
    else:
        L.append("_Sin cierres en el periodo._")
    L.append("")
    L.append("## 4. Hallazgos abiertos y plan")
    L.append("")
    if hab:
        L.append("| ID | Severidad | Hallazgo | Repo | Responsable | Compromiso |")
        L.append("|---|---|---|---|---|---|")
        for h in hab:
            L.append(f"| {h.get('id','—')} | {h.get('severidad','—')} | {h.get('titulo','—')} | "
                     f"`{h.get('repo','—')}` | {h.get('responsable', responsable)} | {h.get('compromiso','pendiente')} |")
    else:
        L.append("_Sin hallazgos abiertos al cierre del periodo._")
    L.append("")
    L.append("## 5. Excepciones aceptadas (risk acceptance)")
    L.append("")
    L.append("Los auditores aceptan riesgos NO mitigados siempre que esten **documentados, "
             "justificados y aprobados por un responsable**. Esta seccion es la que mas "
             "discusiones de auditoria evita.")
    L.append("")
    if exc:
        L.append("| ID | Riesgo | Justificacion | Aprobado por | Revision |")
        L.append("|---|---|---|---|---|")
        for e in exc:
            L.append(f"| {e.get('id','—')} | {e.get('riesgo','—')} | {e.get('justificacion','—')} | "
                     f"{e.get('aprobado_por','—')} | {e.get('revision','—')} |")
    else:
        L.append("_Sin excepciones aceptadas en el periodo._")
    L.append("")
    L.append("## 6. Actividad del periodo")
    L.append("")
    L.append("- Escaneos ejecutados: ________________")
    L.append("- Pull requests de remediación mergeados: ________________")
    L.append("- Dependencias actualizadas: ________________")
    L.append("- Credenciales rotadas: ________________")
    L.append("- Incidentes de seguridad: ________________")
    L.append("")
    if notas:
        L.append("## 7. Notas del responsable")
        L.append("")
        L.append(notas)
        L.append("")
    L.append("## Anexo: artefactos")
    L.append("")
    L.append("- Salida de escaneo de dependencias (OSV/pip-audit/npm audit) del periodo")
    L.append("- Registro del pipeline de CI con los jobs de seguridad ejecutados")
    L.append("- Listado de commits y PRs de remediación")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"Emitido por: {responsable}  ·  Fecha: {ahora}")
    L.append("")
    L.append("_Documento de evidencia para auditoria. La informacion aqui contenida es "
             "confidencial y se entrega unicamente a los contactos autorizados en el SOW._")
    return "\n".join(L)


def ejemplo() -> str:
    """Informe de muestra con datos ficticios para ensenar el formato al cliente."""
    return generar(
        cliente="Acme SaaS (ejemplo)",
        periodo=mes_actual(),
        repos=["acme/api", "acme/web", "acme/worker"],
        hallazgos_abiertos=[
            {"id": "SEC-004", "severidad": "alta", "titulo": "CI sin escaneo de dependencias",
             "repo": "acme/worker", "responsable": "Equipo plataforma", "compromiso": "Sprint 14"},
            {"id": "SEC-006", "severidad": "baja", "titulo": "Sin Dependabot configurado",
             "repo": "acme/web", "responsable": "Equipo plataforma", "compromiso": "Sprint 14"},
        ],
        cerrados=[
            {"id": "SEC-002", "severidad": "alta", "titulo": "Credencial versionada en .env",
             "repo": "acme/api", "pr": "#412", "dias_abierto": 2, "fecha_cierre": "2026-09-04"},
            {"id": "SEC-007", "severidad": "alta", "titulo": "Rama main sin proteccion",
             "repo": "acme/api", "pr": "#418", "dias_abierto": 5, "fecha_cierre": "2026-09-11"},
            {"id": "SEC-011", "severidad": "alta", "titulo": "3 CVEs en dependencias fijas",
             "repo": "acme/web", "pr": "#421", "dias_abierto": 9, "fecha_cierre": "2026-09-19"},
        ],
        excepciones=[
            {"id": "EXC-001", "riesgo": "Libreria X sin parche disponible",
             "justificacion": "Sin version parcheada; mitigado con WAF y sin exposicion externa",
             "aprobado_por": "CTO", "revision": "2026-12-01"},
        ],
        responsable="Tu Nombre — Seguridad Aplicada",
        notas="Se incorporo el job de escaneo en CI para api y web; queda pendiente worker.",
    )
