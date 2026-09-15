"""Calificacion de ICP: separar empresas con tarjeta de credito de repos sueltos.

El error numero uno del tecnico que se hace consultor es perseguir el bug en
lugar de perseguir al comprador. Un repo con 4 estrellas y un proxy de V2Ray
puede tener diez vulnerabilidades: no tiene diez dolares.

Este modulo responde una sola pregunta: **esta empresa tiene presupuesto,
dolor y deadline?** Lo demas es ruido.

Metodo: solo informacion publica (GitHub API + README publico).
"""
from __future__ import annotations

import re

from .scanner import _get, _raw

# ------------------------------------------------------------------ pesos

W = {
    "es_organizacion": 15,
    "sitio_web": 10,
    "email_corporativo": 6,
    "equipo_3_plus": 10,
    "equipo_8_plus": 8,
    "portafolio_5_plus": 8,
    "senal_b2b": 20,
    "facturacion": 10,
    "multiempresa_auth": 8,
    "api_publica": 8,
    "docs": 5,
    "infra": 5,
    "presion_compliance": 18,
    "tamano_ideal": 14,
    "consumo_no_b2b": -14,
    "demasiado_grande": -35,
    "seguridad_ya_resuelta": -30,
}

# Tu comprador: demasiado pequeno para tener CISO, demasiado grande para
# ignorar el cuestionario de seguridad. Ni PostHog ni el repo de un chaval.
CONTRIB_MIN_IDEAL, CONTRIB_MAX_IDEAL = 3, 30
CONTRIB_MAX_VENDIBLE = 50
REPOS_MIN_IDEAL, REPOS_MAX_IDEAL = 5, 45
REPOS_MAX_VENDIBLE = 60

# Un proyecto de comunidad famoso no es un prospecto: no tiene dueno que
# compre, no tiene presupuesto y, si llega a tenerlo, contrata una firma
# grande. Que salga por REGLA, no por puntaje: si depende de restar puntos,
# un dia cuela uno y te hace perder la manana.
ESTRELLAS_MAX_VENDIBLE = 10000

B2B_KEYWORDS = [
    "dashboard", "workspace", "team", "teams", "collaborat", "seats", "seat-based",
    "billing", "subscription", "subscribe", "pricing", "plan", "plans", "invoice",
    "customer", "client", "tenant", "organization", "enterprise", "customers",
    "integration", "integrations", "webhook", "saas", "platform", "onboarding",
    "trial", "free trial", "account", "user management", "admin panel",
]
FACTURACION_KEYWORDS = ["stripe", "paddle", "chargebee", "braintree", "billing",
                        "payment", "checkout", "subscription", "recurly"]
AUTH_KEYWORDS = ["multi-tenant", "multitenant", "multi tenant", "sso", "saml",
                 "oauth", "oidc", "rbac", "tenant", "organization", "2fa", "mfa"]
COMPLIANCE_KEYWORDS = ["soc 2", "soc2", "iso 27001", "iso27001", "hipaa", "gdpr",
                       "pci dss", "pci-dss", "fedramp", "ccpa", "hipaa compliant",
                       "security questionnaire", "vendor assessment", "due diligence"]
INFRA_KEYWORDS = ["dockerfile", "docker-compose", "kubernetes", "helm", "terraform",
                  "helm chart", "k8s", ".tf", "ansible"]
API_KEYWORDS = ["openapi", "swagger", "api reference", "api docs", "rest api",
                "graphql", "endpoints", "postman"]

# Descarte duro: aqui no hay venta posible o hay riesgo reputacional.
RECHAZO_NOMBRE = [
    r"awesome[-_]", r"^ctf", r"ctf[-_]", r"malware", r"exploit", r"payload",
    r"crack", r"keygen", r"^vpn", r"vpn[-_]", r"v2ray", r"proxy[-_]", r"^proxy",
    r"shadowsocks", r"trojan", r"rat[-_]", r"bot[-_]", r"^telegram", r"^discord",
    r"scraper", r"spider", r"crawler", r"^free[-_]", r"unlimited", r"cracked",
    r"^tutorial", r"^curso", r"^course", r"^book", r"^notes", r"^apuntes",
    r"^lista", r"^roadmap", r"^interview", r"^leetcode", r"^cheatsheet",
    r"browser[-_]extension", r"extension[-_]", r"^wallpaper", r"^theme", r"^icon",
    # Proyectos de comunidad y educativos: muchisimas estrellas, cero comprador.
    r"algorithm", r"^public[-_]apis", r"curated", r"^learn", r"^learn[-_]",
    r"build[-_]your[-_]own", r"^resources$", r"^tools$", r"handbook",
    r"^ossu", r"^study", r"^edu", r"^bootcamp", r"^projects$", r"^project[-_]based", r"[-_]community$", r"^community[-_]",
]
# Multinacionales y plataformas: aunque el repo satelite sea pequeno (pocos
# contribuyentes, pocos repos), detras hay un equipo de seguridad corporativo.
# nvidia-isaac/leapp parecia un prospecto perfecto y es NVIDIA.
GRANDES = [
    "nvidia", "google", "microsoft", "amazon", "aws", "meta", "facebook", "apple",
    "ibm", "oracle", "intel", "amd", "cisco", "sap", "siemens", "redhat",
    "canonical", "apache", "kubernetes", "tensorflow", "pytorch", "huggingface",
    "openai", "anthropic", "deepmind", "adobe", "salesforce", "shopify", "spotify",
    "netflix", "uber", "lyft", "airbnb", "stripe", "databricks", "snowflake",
    "mongodb", "elastic", "hashicorp", "docker", "gitlab", "github", "atlassian",
    "vmware", "broadcom", "qualcomm", "samsung", "huawei", "alibaba", "tencent",
    "baidu", "bytedance", "lenovo", "dell", "datadog", "splunk", "cloudflare",
    "twilio", "crowdstrike", "paloalto", "okta", "vercel", "supabase", "posthog",
    # Grandes corporaciones no tecnologicas: presencia minima en GitHub pero
    # departamentos de seguridad enormes. petrobras/ross colo entero.
    "petrobras", "pemex", "ecopetrol", "vale", "repsol", "eni", "shell", "bp",
    "chevron", "exxon", "totalenergies", "equinor", "sinopec", "gazprom",
    "telefonica", "movistar", "vodafone", "orange", "telcel", "claro", "entel",
    "santander", "bbva", "itau", "bradesco", "caixa", "bancolombia", "mercantil",
    "bancoestado", "hsbc", "citibank", "jpmorgan", "goldman", "wellsfargo",
    "boeing", "airbus", "embraer", "siemens", "bosch", "philips", "unilever",
    "nestle", "pepsico", "cocacola", "walmart", "carrefour", "mercadolibre",
    "sony", "panasonic", "toyota", "volkswagen", "ford", "general motors",
    "pfizer", "novartis", "roche", "bayer", "basf", "dupont", "arcelormittal",
    "gerdau", "cemex", "eletrobras", "copel", "isa", "ecopetrol",
]

# Academia: mucho codigo publico, cero presupuesto de seguridad.
# AnubisLMS puntuo 93 y es un LMS de la NYU.
ACADEMICO_TEXTO = [
    "course", "courses", "coursework", "students", "autograder", "classroom",
    "lecture", "syllabus", "assignment", "homework", "grader", "bootcamp",
    "lms", "universidad", "university", "computing science", "cs course",
]
ACADEMICO_DOMINIO = [".edu", ".edu.", ".ac.", ".ac.", ".gouv", ".gov"]

# Dominios de consumo/juego: no son B2B, no hay cuestionario de seguridad.
CONSUMO_TLD = [".games", ".store", ".shop", ".fun", ".xyz", ".club",
               ".blog", ".online", ".site", ".top", ".space"]
CONSUMO_SITIO = ["steamcommunity", "steampowered", "itch.io", "moddb",
                 "nexusmods", "curseforge", "reddit.com", "discord.gg"]
UNIVERSIDADES = [r"\bnyu\b", r"\bmit\b", r"\bstanford\b", r"\bberkeley\b",
                 r"\bcmu\b", r"\bcaltech\b", r"\bharvard\b", r"\btandon\b",
                 r"\bpolytechnic\b", r"\bpolitecnico\b", r"\buniversidad\b",
                 r"\buniversity\b", r"\binstitute of technology\b"]


def es_institucion(login: str, sitio: str, *textos: str) -> str | None:
    """Devuelve el motivo si es multinacional o academico, o None si pasa."""
    bajo = (login or "").lower()
    for g in GRANDES:
        if g in bajo or g in (sitio or "").lower():
            return f"es una multinacional/plataforma grande ('{g}'): ya tiene equipo de seguridad"
    dom = (sitio or "").lower()
    for d in ACADEMICO_DOMINIO:
        if d in dom:
            return f"dominio academico/gubernamental ({sitio}): no compra"
    junto = " ".join([dom] + [t.lower() for t in textos if t])
    for k in ACADEMICO_TEXTO:
        if k in junto:
            return f"proyecto academico/educativo ('{k}'): no hay presupuesto"
    for u in UNIVERSIDADES:
        if re.search(u, junto):
            return f"proyecto universitario ({u}): no hay presupuesto"
    return None


RECHAZO_TEXTO = [
    "ctf", "capture the flag", "malware", "exploit", "payload", "reverse shell",
    "vpn", "v2ray", "shadowsocks", "clash", "free proxies", "sock5", "sock 5",
    "crack", "keygen", "activation key", "nulled", "cheat", "hack tool",
    "brute force", "ddos", "stresser", "booter", "telegram bot", "discord bot",
    "wallpaper", "icon pack", "leetcode solutions", "my dotfiles", "study notes",
]


def _kw(texto: str, lista: list[str]) -> list[str]:
    t = texto.lower()
    return [k for k in lista if k in t]


def es_descartable(nombre: str, descripcion: str) -> str | None:
    """Devuelve el motivo de rechazo, o None si pasa el filtro."""
    n = nombre.lower()
    for pat in RECHAZO_NOMBRE:
        if re.search(pat, n):
            return f"patron de exclusion en el nombre: {pat}"
    texto = (descripcion or "").lower()
    for k in RECHAZO_TEXTO:
        if k in texto:
            return f"tematica excluida en la descripcion: '{k}'"
    return None


# ------------------------------------------------------------------ perfil

def perfil(repo_full: str, branch: str = "main", senales_seguridad: dict | None = None) -> dict:
    """Construye el perfil comercial de un repo. Todo publico."""
    nombre = repo_full.split("/")[-1]
    meta, st = _get(f"/repos/{repo_full}")
    if st != 200:
        return {"repo": repo_full, "veredicto": "ERROR", "motivo": meta.get("_msg", f"HTTP {st}")}

    descripcion = meta.get("description") or ""
    rechazo = es_descartable(nombre, descripcion)
    if rechazo:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "motivo": rechazo,
                "score_icp": 0, "senales": []}

    # El patron de exclusion tambien aplica al DUENO: openbase-community
    # se colaba porque el repo se llama "openbase", no "openbase-community".
    login0 = (meta.get("owner") or {}).get("login", "")
    rechazo_dueno = es_descartable(login0, "")
    if rechazo_dueno:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "owner": login0,
                "motivo": f"dueno excluido ({rechazo_dueno})"}

    estrellas = meta.get("stargazers_count", 0) or 0
    if estrellas > ESTRELLAS_MAX_VENDIBLE:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas,
                "motivo": f"proyecto de comunidad famoso ({estrellas:,} estrellas): "
                          f"no hay empresa que compre"}

    owner = meta.get("owner") or {}
    es_org = owner.get("type") == "Organization"
    login = owner.get("login", "")

    org_meta = {}
    if es_org:
        org_meta, _ = _get(f"/orgs/{login}")

    # Rechazo duro por portafolio: 60+ repos publicos es una empresa que ya
    # tiene estructura de seguridad, o un proyecto de comunidad. Fuera.
    n_repos = org_meta.get("public_repos", owner.get("public_repos", 0)) or 0
    if n_repos > REPOS_MAX_VENDIBLE:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas, "owner": login,
                "repos_publicos": n_repos,
                "motivo": f"demasiado grande ({n_repos} repos publicos): "
                          f"probable equipo de seguridad propio"}

    sitio = org_meta.get("blog") or meta.get("homepage") or ""
    inst = es_institucion(login, sitio, descripcion,
                          org_meta.get("description") or "")
    if inst:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas, "owner": login,
                "sitio": sitio, "repos_publicos": n_repos,
                "motivo": inst}

    contrib, _ = _get(f"/repos/{repo_full}/contributors?per_page=100&anon=false")
    n_contrib = len(contrib) if isinstance(contrib, list) else 0

    # Suelo duro: 1 sola persona no es una empresa. No hay quien compre.
    if n_contrib < 2:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas, "owner": login,
                "sitio": sitio, "contribuyentes": n_contrib,
                "repos_publicos": n_repos,
                "motivo": f"un solo contribuyente: es una persona, no una empresa"}

    # Rechazo duro por tamano de equipo. Igual que arriba: por regla.
    if n_contrib > CONTRIB_MAX_VENDIBLE:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas, "owner": login,
                "contribuyentes": n_contrib, "repos_publicos": n_repos,
                "motivo": f"demasiado grande ({n_contrib}+ contribuyentes): "
                          f"probable equipo de seguridad propio"}

    readme = ""
    for cand in ("README.md", "readme.md", "README.rst", "README", "readme"):
        readme = _raw(repo_full, branch, cand) or ""
        if readme:
            break
    readme = readme[:20000]

    inst2 = es_institucion(login, sitio, readme[:4000])
    if inst2:
        return {"repo": repo_full, "veredicto": "DESCARTAR", "score_icp": 0,
                "senales": [], "estrellas": estrellas, "owner": login,
                "sitio": sitio, "contribuyentes": n_contrib,
                "repos_publicos": n_repos,
                "motivo": inst2 + " (detectado en el README)"}

    senales, score = [], 0

    def add(clave, etiqueta):
        nonlocal score
        score += W[clave]
        senales.append(etiqueta)

    if es_org:
        add("es_organizacion", "es una organizacion (hay estructura)")
    if (any(t in (sitio or "").lower() for t in CONSUMO_TLD)
            or any(t in (sitio or "").lower() for t in CONSUMO_SITIO)):
        add("consumo_no_b2b", "dominio de consumo/juego: no vende a empresas")
    if sitio:
        add("sitio_web", f"tiene sitio propio ({sitio[:40]})")
    email = org_meta.get("email") or ""
    if email and "@" in email:
        add("email_corporativo", "email corporativo publico")

    if n_contrib >= 3:
        add("equipo_3_plus", f"{n_contrib}+ contribuyentes (equipo real)")
    if n_contrib >= 8:
        add("equipo_8_plus", "equipo grande")

    if n_repos >= 5:
        add("portafolio_5_plus", f"{n_repos} repos publicos (portafolio)")

    # Punto dulce: la empresa mediana. La grande ya tiene CISO (y ya salio por
    # regla mas arriba), la de una persona no tiene tarjeta.
    if CONTRIB_MIN_IDEAL <= n_contrib <= CONTRIB_MAX_IDEAL and REPOS_MIN_IDEAL <= n_repos <= REPOS_MAX_IDEAL:
        add("tamano_ideal",
            f"tamano ideal ({n_contrib} contribuyentes, {n_repos} repos): sin CISO, con clientes")

    b2b = _kw(readme + " " + descripcion, B2B_KEYWORDS)
    if len(b2b) >= 2:
        add("senal_b2b", "lenguaje de producto B2B: " + ", ".join(b2b[:4]))

    if _kw(readme, FACTURACION_KEYWORDS):
        add("facturacion", "cobra (senal de facturacion/Stripe)")
    if _kw(readme, AUTH_KEYWORDS):
        add("multiempresa_auth", "modelo multiusuario/autenticacion")

    tree, _ = _get(f"/repos/{repo_full}/git/trees/{branch}?recursive=1")
    paths = [i["path"].lower() for i in (tree or {}).get("tree", []) if i.get("type") == "blob"]
    joined = " ".join(paths[:600])

    if any(k in joined for k in ("openapi", "swagger")) or _kw(readme, API_KEYWORDS):
        add("api_publica", "API publica documentada")
    if any(p.startswith("docs/") for p in paths) or "docs" in joined[:4000]:
        add("docs", "documentacion estructurada")
    if any(k in joined for k in ("dockerfile", "docker-compose", "terraform", "chart", "k8s")):
        add("infra", "infraestructura como codigo")

    compliance = _kw(readme + " " + descripcion, COMPLIANCE_KEYWORDS)
    if compliance:
        add("presion_compliance",
            "MENCIONA CUMPLIMIENTO: " + ", ".join(compliance[:3]) + " <- vender Ya")

    if senales_seguridad and senales_seguridad.get("resuelto"):
        add("seguridad_ya_resuelta", "ya tiene seguridad resuelta (probable proveedor actual)")

    if score >= 60:
        veredicto = "IDEAL"
    elif score >= 35:
        veredicto = "POSIBLE"
    else:
        veredicto = "DESCARTAR"

    return {
        "repo": repo_full,
        "owner": login,
        "es_organizacion": es_org,
        "sitio": sitio,
        "email": email,
        "contribuyentes": n_contrib,
        "repos_publicos": n_repos,
        "estrellas": estrellas,
        "descripcion": descripcion[:200],
        "senales": senales,
        "score_icp": max(0, min(100, score)),
        "veredicto": veredicto,
        "presion_compliance": bool(compliance),
        "motivo": "",
    }


def resuelto_o_no(rep: dict) -> bool:
    """True si el repo ya tiene la seguridad basica cubierta -> no es prospecto."""
    ids = {f["id"] for f in rep.get("hallazgos", [])}
    return not ({"SEC-001", "SEC-004", "SEC-007"} & ids)


def prioridad_final(score_riesgo: int, score_icp: int, compliance: bool) -> tuple[str, str]:
    """Combina dolor tecnico y capacidad de pago."""
    s = score_riesgo * 0.45 + score_icp * 0.55 + (15 if compliance else 0)
    # Umbrales altos a proposito: si todo es P1, la prioridad no sirve.
    # P1 tiene que significar "este va hoy", no "este paso el filtro".
    if s >= 72:
        return "P1", f"Contactar HOY (indice {s:.0f}). Dolor alto + capacidad de pago."
    if s >= 58:
        return "P2", f"Secuencia esta semana (indice {s:.0f})."
    if s >= 44:
        return "P3", f"Nurturing, reauditar en 60 dias (indice {s:.0f})."
    return "DESCARTAR", f"Sin encaje comercial (indice {s:.0f})."
