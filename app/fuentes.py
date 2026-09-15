"""Fuentes de prospectos: donde encontrar empresas con presupuesto y deadline.

La herramienta escanea GitHub, pero GitHub NO es la mejor fuente: esta lleno de
proyectos que no son empresas. La mejor fuente es la gente que YA dijo en publico
que tiene el problema. No hay que convencerla: solo aparecer.

Este modulo generabusquedas listas para hacer clic. No hay API que consultar:
son enlaces pre-armados a LinkedIn, X, Reddit, HN, GitHub y bolsas de empleo.

Uso:
    python run.py fuentes                 # todas
    python run.py fuentes --nivel 1       # solo las de mayor conversion
    python run.py fuentes --md            # para guardar e ir tachando
"""
from __future__ import annotations

import urllib.parse

# (id, nivel, nombre, que buscas, url, nota)
FUENTES: list[tuple[str, int, str, str, str, str]] = [
    # ---------------- NIVEL 1: ya dijeron que tienen el problema ----------
    ("x-quejas", 1, "X/Twitter: quejas sobre SOC 2",
     "Fundadores que publicaron su dolor. Es la senal mas caliente que existe.",
     "https://x.com/search?q=" + urllib.parse.quote(
         '(SOC 2 OR "security questionnaire") (startup OR founder) -is:retweet&f=live'),
     "Ordena por 'Latest'. Responde en menos de 24 h: la ventana de dolor es corta."),

    ("reddit-soc2", 1, "Reddit: quien pregunta por SOC 2",
     "Gente resolviendo el problema ahora mismo, en publico",
     "https://www.reddit.com/search/?q=" + urllib.parse.quote("SOC 2 startup"),
     "r/SaaS, r/startups, r/devops, r/cybersecurity. Responde util y sin vender: el perfil vende solo."),

    ("li-contenido", 1, "LinkedIn: publicaciones sobre SOC 2",
     "Posts recientes de gente en proceso de auditoria",
     "https://www.linkedin.com/search/results/content/?keywords=" + urllib.parse.quote("SOC 2 startup")
     + "&sortBy=%22date_posted%22",
     "Filtra por 'Publicaciones' y fecha reciente. Comenta con sustancia antes de escribirles al DM."),

    ("hn-soc2", 1, "Hacker News: hilos de cumplimiento",
     "Fundadores tecnicos hablando de auditorias y seguridad",
     "https://hn.algolia.com/?query=" + urllib.parse.quote("SOC 2") + "&sort=byDate&type=story",
     "Los hilos viejos tambien sirven: saca los nombres y buscalos en LinkedIn."),

    ("auditores", 1, "Auditores y consultores SOC 2 (socios de referencia)",
     "Quien audita recibe clientes que necesitan arreglar el codigo y no lo implementa",
     "https://www.linkedin.com/search/results/people/?keywords=" + urllib.parse.quote(
         "SOC 2 auditor OR compliance consultant OR vCISO"),
     "EL CANAL MAS INFRAVALORADO. Trabaja por referencia. Mensaje en templates/mensaje-lanzamiento.md #5."),

    ("reddit-saas", 1, "Reddit r/SaaS: 'security questionnaire'",
     "Fundadores a los que un cliente enterprise ya les pidio el cuestionario",
     "https://www.reddit.com/r/SaaS/search/?q=security%20questionnaire&restrict_sr=1&sort=new",
     "Filtra por New. Responde en el hilo sin vender: el DM va despues."),

    ("reddit-soc2-new", 1, "Reddit: SOC 2 mas reciente",
     "La senal mas caliente, ordenada por fecha",
     "https://www.reddit.com/search/?q=SOC%202&sort=new",
     "sort=new es obligatorio: una queja de hace 3 meses ya contrato a alguien."),

    ("reddit-soc2-saas", 1, "Reddit r/SaaS: SOC 2",
     "El subreddit con mejor densidad de compradores",
     "https://www.reddit.com/r/SaaS/search/?q=SOC%202&restrict_sr=1&sort=new",
     "Lee el hilo antes de escribir: si el problema es de verdad, aporta la solucion ahi mismo."),

    ("reddit-startups", 1, "Reddit r/startups: cuestionario de seguridad",
     "Mas ruido que r/SaaS, pero mas volumen",
     "https://www.reddit.com/r/startups/search/?q=security%20questionnaire%20OR%20SOC%202&restrict_sr=1&sort=new",
     "Filtra por New y por comentarios recientes."),

    ("reddit-devops", 1, "Reddit r/devops: cumplimiento",
     "Quien lo implementa, no quien decide: sirve para llegar al CTO",
     "https://www.reddit.com/r/devops/search/?q=SOC%202%20OR%20compliance&restrict_sr=1&sort=new",
     "Aqui el que pregunta es tecnico. Aporta y pregunta quien decide."),

    ("reddit-engmanagers", 1, "Reddit r/ExperiencedDevs y r/engineeringmanagers",
     "Gente senior con presupuesto de herramientas",
     "https://www.reddit.com/r/ExperiencedDevs/search/?q=security%20OR%20compliance&restrict_sr=1&sort=new",
     "Menos volumen, mas decision. Buenos para el retainer, no para el diagnostico."),

    ("li-contenido-semana", 1, "LinkedIn: publicaciones de la ultima semana",
     "Gente que publico sobre su auditoria hace dias",
     "https://www.linkedin.com/search/results/content/?keywords=SOC%202&sortBy=%22date_posted%22",
     "Elige 'Publicaciones' y 'Ultima semana'. Comenta con sustancia antes del DM."),

    ("li-cuestionario", 1, "LinkedIn: 'security questionnaire'",
     "La frase exacta del que ya esta trabado",
     "https://www.linkedin.com/search/results/content/?keywords=security%20questionnaire",
     "Mucho mas caliente que buscar 'SOC 2': quien dice esto ya tiene el correo del cliente."),

    ("li-empleos-semana", 1, "LinkedIn: ofertas de empleo de la ultima semana",
     "Si contratan, hay presupuesto y dolor reconocido",
     "https://www.linkedin.com/jobs/search?keywords=SOC%202%20OR%20security%20compliance&f_TPR=r604800",
     "LA MEJOR SENAL DE PRESUPUESTO. El que busca su PRIMER ingeniero de seguridad no tiene a nadie."),

    ("li-personas", 1, "LinkedIn: personas con SOC 2 en el perfil",
     "CTOs y heads of engineering en proceso",
     "https://www.linkedin.com/search/results/people/?keywords=SOC%202%20CTO%20startup",
     "Filtra por tu region o por empresas de 11-50 empleados."),

    # ---------------- NIVEL 2: senal de presupuesto -----------------------
    ("empleos-sec", 2, "Ofertas de empleo de seguridad/compliance",
     "Si estan contratando, hay presupuesto aprobado y dolor reconocido",
     "https://www.linkedin.com/jobs/search?keywords=" + urllib.parse.quote(
         "SOC 2 compliance OR security engineer") + "&f_TPR=r604800",
     "La empresa que busca su PRIMER ingeniero de seguridad es tu cliente ideal: no tiene nadie y tiene prisa."),

    ("empleos-empresa", 2, "Empresas que crecen rapido",
     "Contratar mucho = acaba de levantar = hay caja",
     "https://www.linkedin.com/jobs/search?keywords=" + urllib.parse.quote(
         "senior backend engineer startup") + "&f_TPR=r604800",
     "Filtra por empresas de 11-50 empleados: el punto dulce."),

    ("funding", 2, "Rondas recientes (serie A/B)",
     "Acaban de levantar: tienen dinero y, pronto, clientes enterprise",
     "https://news.crunchbase.com/sections/venture-capital-investing/",
     "Una ronda anunciada hoy es un cuestionario de seguridad en 6 meses. Anotalos y espera el momento."),

    ("wellfound", 2, "Wellfound: startups que contratan",
     "Directorio de startups con tamano y stack visible",
     "https://wellfound.com/companies",
     "Filtra por tamano 11-50 y por tu stack. Es la fuente mas limpia de empresas reales."),

    ("producthunt", 2, "Product Hunt: lanzamientos recientes",
     "Producto nuevo con traccion publica: suele tener repo publico",
     "https://www.producthunt.com/",
     "Los que apuntan a B2B ('for teams') son tu perfil. Los de consumo, no."),

    # ---------------- NIVEL 3: volumen con nuestra herramienta ------------
    ("gh-compliance", 3, "GitHub: repos que mencionan cumplimiento",
     "README que menciona SOC 2 / HIPAA / GDPR: ESA EMPRESA YA ESTA EN MODO AUDITORIA",
     "https://github.com/search?q=" + urllib.parse.quote('"SOC 2" in:readme') + "&type=repositories",
     "La senal mas caliente que da GitHub. Pasa el resultado por python run.py leads."),

    ("gh-empresa", 3, "GitHub: organizaciones del tamano ideal",
     "Org con 3-30 contribuyentes y repos activos",
     "https://github.com/search?q=" + urllib.parse.quote(
         "language:python stars:50..800 pushed:>2026-06-01 fork:false") + "&type=repositories&s=updated&o=desc",
     "Automatizable: python run.py leads --lang python,javascript --top 20"),

    ("gh-seguridad", 3, "GitHub: repos con SECURITY.md",
     "Ya tienen politica de divulgacion: les falta la evidencia, no la intencion",
     "https://github.com/search?q=" + urllib.parse.quote("filename:SECURITY.md") + "&type=code",
     "Contra-intuitivo pero util: estosSI entienden el problema. Vendes el informe mensual, no el diagnostico."),

    # ---------------- NIVEL 4: comunidades --------------------------------
    ("indiehackers", 4, "Indie Hackers",
     "Fundadores de SaaS pequenos, muy accesibles por DM",
     "https://www.indiehackers.com/",
     "Publica tu analisis publico ahi. Deja que te encuentren."),

    ("slack-discord", 4, "Comunidades de founders y dev shops",
     "Donde se piden recomendaciones de proveedores",
     "https://www.google.com/search?q=" + urllib.parse.quote(
         'slack OR discord community "SaaS founders" "SOC 2"'),
     "No vendas en el canal. Responde preguntas de seguridad durante un mes y llegan solos."),

    ("agencias", 4, "Agencias de desarrollo y estudios",
     "Tienen clientes con el problema y no hacen seguridad",
     "https://www.linkedin.com/search/results/companies/?keywords=" + urllib.parse.quote(
         "software development agency SaaS"),
     "Ofreceles white-label: tu haces la seguridad, ellos facturan. Volumen sin prospeccion."),
]

NIVELES = {
    1: "NIVEL 1 - Ya dijeron que tienen el problema (mayor conversion, bajo volumen)",
    2: "NIVEL 2 - Senal de presupuesto (conversion media, volumen medio)",
    3: "NIVEL 3 - Volumen con la herramienta (conversion baja, alto volumen)",
    4: "NIVEL 4 - Comunidades y socios (largo plazo, efecto compuesto)",
}


def filtrar(nivel: int | None = None) -> list[tuple[str, int, str, str, str, str]]:
    if not nivel:
        return FUENTES
    return [f for f in FUENTES if f[1] == nivel]


def a_markdown(nivel: int | None = None) -> str:
    L = ["# Fuentes de prospectos", "",
         "De mayor a menor conversion. Los niveles 1 y 2 son los que producen",
         "clientes esta semana; el 3 es para llenar el embudo.", ""]
    for n in sorted(NIVELES):
        if nivel and n != nivel:
            continue
        fs = [f for f in FUENTES if f[1] == n]
        L.append(f"## {NIVELES[n]}")
        L.append("")
        for fid, _, nombre, que, url, nota in fs:
            L.append(f"### {nombre}")
            L.append("")
            L.append(f"**Que buscas:** {que}")
            L.append("")
            L.append(f"**Ir:** {url}")
            L.append("")
            L.append(f"**Como usarlo:** {nota}")
            L.append("")
            L.append("- [ ] revisado")
            L.append("")
    L.append("---")
    L.append("")
    L.append("Rutina semanal: 1 hora en nivel 1 + 1 hora en nivel 2 + el resto")
    L.append("automatizado con `python run.py leads`. Lo de nivel 1 y 2 no se")
    L.append("automatiza: se contesta a mano, y ahi esta la ventaja.")
    return "\n".join(L)
