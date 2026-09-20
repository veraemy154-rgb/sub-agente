"""Mensajes de primer contacto.

Regla del director, y no es negociable: en el primer mensaje NUNCA se
revela un hallazgo explotable. Se menciona la AUSENCIA DE UN CONTROL
("no veo escaneo de dependencias en su CI"), que es publico, verificable
y no pone en riesgo a nadie. El detalle se entrega bajo autorizacion
escrita. Eso nos mantiene del lado correcto de la ley y de la etica,
y ademas convierte mejor: genera curiosidad sin generar panico.
"""
from __future__ import annotations

from .report import estimar_precio

TONOS = ("directo", "consultivo", "breve")


def _gancho(lead: dict, rep: dict) -> str:
    """Un hecho publico, concreto y no sensible sobre el que colgar el mensaje."""
    ids = {f["id"] for f in rep.get("hallazgos", [])}
    if "SEC-007" in ids:
        return "la rama principal acepta pushes directos (sin revision obligatoria ni CI bloqueante)"
    if "SEC-004" in ids:
        return "el pipeline de CI no incluye escaneo de vulnerabilidades en dependencias"
    if "SEC-002" in ids:
        return "hay archivos con nombre de credencial versionados en el repositorio"
    if "SEC-011" in ids:
        return "hay dependencias con CVEs publicados y version parcheada disponible"
    if "SEC-001" in ids:
        return "no hay una politica publica de divulgacion de vulnerabilidades"
    return "no hay controles de seguridad visibles en el ciclo de desarrollo"


def email(lead: dict, rep: dict, remitente: str, tono: str = "directo") -> str:
    gancho = _gancho(lead, rep)
    p = estimar_precio(rep)
    nombre = lead["repo"].split("/")[0]

    if tono == "breve":
        cuerpo = (
            f"Hola {nombre},\n\n"
            f"Revisando informacion publica de {lead['repo']} note que {gancho}. "
            f"Es el tipico punto que frena un cuestionario de seguridad enterprise o una auditoria SOC 2.\n\n"
            f"Hago un Diagnostico Express de {p['diagnostico_express_usd']} USD: inventario de exposicion, "
            f"plan de remediación priorizado y la evidencia que pide el auditor. 48 horas, sin compromiso.\n\n"
            f"Te mando el detalle de lo que vi si me confirms que tengo autorizacion para revisarlo.\n\n"
            f"{remitente}")
    elif tono == "consultivo":
        cuerpo = (
            f"Hola {nombre},\n\n"
            f"Trabajo con equipos de producto que estan pasando por SOC 2 o por la due diligence "
            f"de seguridad de un cliente grande. Viendo el repo publico de {lead['repo']}: {gancho}.\n\n"
            f"No es una emergencia, es un hueco de evidencia. Hoy no hay forma automatica de demostrar "
            f"gestion de vulnerabilidades, y eso es exactamente lo que preguntan.\n\n"
            f"Puedo entregarte en 48 h un Diagnostico Express ({p['diagnostico_express_usd']} USD) con priorizacion "
            f"por impacto y el estimado de la remediación. Si prefieres, lo vemos 15 minutos antes.\n\n"
            f"{remitente}")
    else:
        cuerpo = (
            f"Hola {nombre},\n\n"
            f"Vi {lead['repo']} y encontre {lead['n_hallazgos']} puntos donde hoy no se puede evidenciar "
            f"gestion de vulnerabilidades. El mas relevante: {gancho}.\n\n"
            f"Por que te lo digo: si venden a empresas, antes o despues les llega el cuestionario de "
            f"seguridad. Cada uno de esos puntos se convierte en una respuesta que no tienen.\n\n"
            f"Diagnostico Express: {p['diagnostico_express_usd']} USD. Entrego inventario priorizado, "
            f"esfuerzo estimado por hallazgo y el plan de remediación. Yo mismo puedo implementarlo "
            f"despues (estimado para su caso: {p['remediacion_estimada_usd']} USD) o se lo paso a su equipo.\n\n"
            f"Respondeme y te envio el detalle de los {lead['n_hallazgos']} puntos con la autorizacion formal.\n\n"
            f"{remitente}")

    asunto = (f"{lead['repo']}: {lead['hallazgos_altos']} punto(s) que frenan "
              f"un cuestionario de seguridad")
    return f"Asunto: {asunto}\n\n{cuerpo}"


def linkedin(lead: dict, rep: dict, remitente: str) -> str:
    gancho = _gancho(lead, rep)
    return (
        f"{lead['repo'].split('/')[0]}, viendo su repo publico: {gancho}. "
        f"Es el clasico freno cuando un cliente enterprise manda el cuestionario de seguridad. "
        f"Armo un diagnostico de exposicion en 48 h y se los priorizo por impacto/esfuerzo. "
        f"Les paso el detalle? — {remitente}")


def secuencia(lead: dict, rep: dict, remitente: str) -> list[dict]:
    """5 toques en 14 dias. La mayoria del dinero esta en el seguimiento,
    no en el primer mensaje."""
    gancho = _gancho(lead, rep)
    p = estimar_precio(rep)
    return [
        {"dia": 0, "canal": "email", "mensaje": email(lead, rep, remitente, "directo")},
        {"dia": 3, "canal": "linkedin", "mensaje": linkedin(lead, rep, remitente)},
        {"dia": 7, "canal": "email",
         "mensaje": (f"Seguimiento rapido: en {lead['repo']} el punto critico es que {gancho}. "
                     f"Si estan preparando SOC 2 o respondiendo un cuestionario, esto aparece. "
                     f"Diagnostico Express {p['diagnostico_express_usd']} USD, 48 h.\n\n{remitente}")},
        {"dia": 11, "canal": "email",
         "mensaje": (f"Caso concreto de un equipo de tamano similar: sin escaneo de dependencias en CI, "
                     f"17 CVEs acumulados en produccion. Se resolvio en dos sprints y paso la auditoria. "
                     f"Si les sirve, reviso {lead['repo']} bajo el mismo formato.\n\n{remitente}")},
        {"dia": 14, "canal": "email",
         "mensaje": (f"Cierro el tema: si no es prioridad ahora, sin problema. "
                     f"Guardo el analisis de {lead['repo']} por 90 dias; si entra un cliente grande "
                     f"y les pide evidencia, escribanme y lo retomamos.\n\n{remitente}")},
    ]
