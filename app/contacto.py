"""Encontrar el correo de contacto sin pagar LinkedIn Premium.

Por que existe esto: el InMail de LinkedIn es caro y convierte peor que un
correo directo. Y para lo nuestro hay un atajo enorme: los repos con
SECURITY.md casi siempre publican  security@empresa.com , que es EXACTAMENTE
la bandeja a la que deberiamos escribir: la persona que recibe ahi es la que
tiene el problema que resolvemos.

Fuentes, de mayor a menor calidad:
  1. SECURITY.md / security.txt      -> security@  (oro: es el dueno del problema)
  2. Email publico de la organizacion
  3. Correo del autor de los commits  -> el fundador o el CTO
  4. README / CONTRIBUTING
  5. Patrones adivinados sobre el dominio

Solo informacion publica. No se verifican envios: solo se recogen direcciones
que la propia empresa publico.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .scanner import _get, _raw

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

BASURA = (
    "noreply", "no-reply", "donotreply", "example.com", "example.org", "example.net",
    "users.noreply.github.com", "@github.com", "dependabot", "sentry.io",
    "localhost", "test@", "your@", "you@", "email@", "@domain", "@company",
    "@email.com", "@sample", "foo@", "bar@", "@test", ".png", ".jpg", ".svg",
    "w3.org", "schema.org", "apache.org", "python.org", "mozilla.org",
    "sentry-cdn", "@users.noreply", "web-flow@", "renovate@", "github-actions",
)

RUTAS_SEGURIDAD = [
    "SECURITY.md", "security.md", ".github/SECURITY.md", "docs/SECURITY.md",
    "SECURITY.txt", ".well-known/security.txt", "security.txt",
]
RUTAS_GENERALES = ["README.md", "readme.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]

PESO = {
    "SECURITY.md": 100,
    "org": 60,
    "commit": 45,
    "README": 25,
    "patron": 15,
}


def limpiar(email: str) -> str | None:
    e = email.strip().strip(".,;:()<>[]\"'").lower()
    if not e or len(e) > 100:
        return None
    if any(b in e for b in BASURA):
        return None
    if not EMAIL_RE.fullmatch(e):
        return None
    return e


def extraer(texto: str) -> list[str]:
    if not texto:
        return []
    out = []
    for e in EMAIL_RE.findall(texto):
        limpio = limpiar(e)
        if limpio and limpio not in out:
            out.append(limpio)
    return out


SUBDOMINIOS = ("www.", "docs.", "doc.", "app.", "api.", "developer.", "developers.",
               "about.", "blog.", "help.", "support.", "go.", "portal.", "console.",
               "dashboard.", "status.", "kb.", "learn.")


def dominio_de(sitio: str) -> str:
    """Devuelve el dominio registrable, quitando subdominios tipicos.

    docs.mindroom.chat -> mindroom.chat (si no, generabas security@docs.empresa.com).
    """
    if not sitio:
        return ""
    if "://" not in sitio:
        sitio = "https://" + sitio
    host = urlparse(sitio).netloc.lower().split(":")[0]
    for sub in SUBDOMINIOS:
        if host.startswith(sub):
            host = host[len(sub):]
            break
    partes = host.split(".")
    # dominios compuestos tipo .co.uk / .com.br: conserva las 3 ultimas
    if len(partes) >= 3 and partes[-2] in ("co", "com", "org", "net", "gob", "edu") \
            and len(partes[-1]) == 2:
        return ".".join(partes[-3:])
    return ".".join(partes[-2:]) if len(partes) >= 2 else host


def adivinar(dominio: str) -> list[str]:
    """Patrones habituales. NO verificados: son candidatos a probar."""
    if not dominio or "." not in dominio:
        return []
    return [f"{p}@{dominio}" for p in
            ("security", "hello", "hola", "info", "contact", "contacto", "team")]


def buscar(repo_full: str, branch: str = "main", con_commits: bool = True,
           con_patrones: bool = True) -> dict:
    meta, st = _get(f"/repos/{repo_full}")
    if st != 200:
        return {"repo": repo_full, "error": meta.get("_msg", f"HTTP {st}")}
    branch = meta.get("default_branch") or branch
    owner = (meta.get("owner") or {}).get("login", "")

    hallados: list[dict] = []
    visto = set()

    def agregar(email: str, fuente: str, detalle: str = ""):
        if email in visto:
            return
        visto.add(email)
        hallados.append({"email": email, "fuente": fuente, "detalle": detalle,
                         "peso": PESO.get(fuente, 10)})

    # 1. SECURITY.md: la mejor fuente con diferencia
    for ruta in RUTAS_SEGURIDAD:
        txt = _raw(repo_full, branch, ruta)
        for e in extraer(txt or ""):
            agregar(e, "SECURITY.md", f"en {ruta}")

    # 2. Email publico de la organizacion
    if (meta.get("owner") or {}).get("type") == "Organization":
        org, _ = _get(f"/orgs/{owner}")
        for e in extraer(org.get("email") or ""):
            agregar(e, "org", "email publico de la organizacion")

    # 3. Autores de commits: suele ser el fundador o el CTO
    if con_commits:
        commits, _ = _get(f"/repos/{repo_full}/commits?per_page=100")
        if isinstance(commits, list):
            for c in commits:
                ca = (c.get("commit") or {}).get("author") or {}
                for e in extraer(ca.get("email") or ""):
                    agregar(e, "commit", f"autor: {ca.get('name','?')}")

    # 4. README y similares
    for ruta in RUTAS_GENERALES:
        for e in extraer(_raw(repo_full, branch, ruta) or ""):
            agregar(e, "README", f"en {ruta}")

    # 5. Patrones sobre el dominio (no verificados)
    sitio = ""
    if (meta.get("owner") or {}).get("type") == "Organization":
        org2, _ = _get(f"/orgs/{owner}")
        sitio = org2.get("blog") or ""
    sitio = sitio or meta.get("homepage") or ""
    dominio = dominio_de(sitio)
    candidatos = []
    if con_patrones and dominio:
        for p in adivinar(dominio):
            if p not in visto:
                candidatos.append(p)

    hallados.sort(key=lambda h: -h["peso"])
    return {
        "repo": repo_full,
        "owner": owner,
        "sitio": sitio or "",
        "dominio": dominio,
        "emails": hallados,
        "candidatos_sin_verificar": candidatos,
        "recomendado": (hallados[0]["email"] if hallados else
                        (candidatos[0] if candidatos else "")),
    }


def a_texto(res: dict) -> str:
    if res.get("error"):
        return f"{res['repo']}: {res['error']}"
    L = [f"Contactos de {res['repo']}" + (f"  ({res['sitio']})" if res.get("sitio") else ""), ""]
    if res["emails"]:
        L.append("ENCONTRADOS (publicados por ellos mismos):")
        for h in res["emails"]:
            L.append(f"  {h['email']:42} {h['fuente']:12} {h['detalle']}")
    else:
        L.append("No se encontro ningun correo publicado.")
    if res["candidatos_sin_verificar"]:
        L.append("")
        L.append("CANDIDATOS POR PATRON (NO verificados, pruebalos):")
        for c in res["candidatos_sin_verificar"]:
            L.append(f"  {c}")
    L.append("")
    L.append(f"Recomendado: {res['recomendado'] or 'ninguno'}")
    if res["recomendado"] and res["emails"]:
        top = res["emails"][0]
        if top["fuente"] == "SECURITY.md":
            L.append("  ^ Este sale de su politica de seguridad: es la persona")
            L.append("    que YA tiene el problema. Escribele primero.")
    return "\n".join(L)
