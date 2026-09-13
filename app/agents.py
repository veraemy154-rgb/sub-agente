"""Sub-agentes por area de negocio."""

AGENTS = {
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
