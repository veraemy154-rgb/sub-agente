"""Sub-agentes por area de negocio."""

AGENTS = {
    "seguridad": {
        "rol": "AppSec & Compliance Remediation Lead",
        "prompt": (
            "Auditamos exposicion a partir de informacion publica y convertimos cada hallazgo en "
            "evidencia de control para SOC 2 / ISO 27001 / cuestionarios enterprise. "
            "Prioriza por impacto sobre la auditoria y por esfuerzo de remediación. "
            "Nunca propongas explotar ni acceder sin autorizacion escrita. "
            "El entregable siempre es un plan que el cliente pueda ejecutar o comprarte."
        ),
        "keywords": [
            "seguridad", "vulnerabilidad", "vulnerabilidades", "cve", "cves", "pentest",
            "auditoria", "auditoría", "soc 2", "soc2", "iso 27001", "owasp", "parche",
            "remediacion", "remediación", "secretos", "secrets", "dependencias",
            "scan", "escaneo", "riesgo", "exposicion", "exposición", "brecha", "sast",
            "ci", "pipeline", "hardening", "appsec", "compliance", "cumplimiento",
        ],
    },
    "seo": {
        "rol": "Senior SEO Strategist",
        "prompt": "Analiza intencion de busqueda, clustering semantico y brechas de contenido. Devuelve acciones priorizadas por impacto/esfuerzo.",
        "keywords": ["seo", "keyword", "contenido", "blog", "posicionamiento", "serp", "trafico", "brief", "competencia"],
    },
    "ventas": {
        "rol": "Sales Development Rep",
        "prompt": "Redacta secuencias de outreach, manejo de objeciones y propuestas. Optimiza por reply rate y cierre.",
        "keywords": ["venta", "lead", "prospecto", "cold email", "crm", "propuesta", "cliente", "cierre", "objecion", "precio"],
    },
    "operaciones": {
        "rol": "Operations Controller",
        "prompt": "Resuelve back-office: extraccion de datos, SOPs, reportes y automatizacion de procesos.",
        "keywords": ["factura", "sop", "proceso", "erp", "inventario", "reporte", "dato", "automatiza", "planilla"],
    },
    "soporte": {
        "rol": "Customer Success Agent",
        "prompt": "Responde incidencias con precision y empatia. Escala solo cuando la politica lo exija.",
        "keywords": ["soporte", "ticket", "error", "incidencia", "ayuda", "no funciona", "bug", "caido"],
    },
}


def ejecutar(area: str, tarea: str) -> dict:
    agente = AGENTS[area]
    return {
        "area": area,
        "rol": agente["rol"],
        "system_prompt": agente["prompt"],
        "tarea": tarea,
        "estado": "enrutado",
    }
