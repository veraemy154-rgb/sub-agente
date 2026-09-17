"""Encontrar el correo de contacto sin pagar LinkedIn Premium.

Por que existe esto: el InMail de LinkedIn es caro y convierte peor que un
correo directo. Y para lo nuestro hay un atajo enorme: los repos con
SECURITY.md casi siempre publican  security@empresa.com , que es EXACTAMENTE
la bandeja a la que deberiamos escribir: quien recibe ahi es quien ya tiene
el problema que resolvemos.

Orden de calidad de una direccion (peso):
  security@ / SECURITY.md ....... 100   dueno del problema
  founder@ / ceo@ ...............  80   quien firma el cheque
  persona real (autor commit) ...  70   fundador o CTO
  hello@ / hola@ / contact@ .....  45   bandeja que si leen
  info@ / support@ / team@ ......  25   casi nadie las mira
  community@ / admin@ ...........  20   las peores

Se descartan cuentas de bots (agent, bot, ci), direcciones falsas (.local,
.test) y dominios de ejemplo.

Ademas cruza con el ICP: si el repo ya esta descartado (Petrobras, academia,
mega-corp), avisa de que NO hay que escribirle. Antes se buscaba el correo de
cualquiera y se perdia el tiempo con quien no va a comprar nunca.

Solo informacion publica: direcciones que la propia empresa publico.
"""
from __future__ import annotations

import io
import re
from urllib.parse import urlparse

from .scanner import _get, _raw

try:
    from .scanner import _b64 as _b64_scanner
except Exception:
    _b64_scanner = None

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

BASURA = (
    "noreply", "no-reply", "donotreply", "example.com", "example.org", "example.net",
    "users.noreply.github.com", "@github.com", "dependabot", "sentry.io",
    "localhost", "test@", "your@", "you@", "email@", "@domain", "@company",
    "@email.com", "@sample", "foo@", "bar@", "@test", ".png", ".jpg", ".svg",
    "w3.org", "schema.org", "apache.org", "python.org", "mozilla.org",
    "sentry-cdn", "@users.noreply", "web-flow@", "renovate@", "github-actions",
    # direcciones que no existen fuera de la maquina del desarrollador
    ".local", ".test", ".invalid", ".example", "@localhost",
)

BOT = ("bot", "agent", "-ci", "ci-", "actions", "automation", "dependabot",
       "renovate", "copilot", "sweeper", "cron")

ROLES = {
    "security": 100, "sec": 100, "vulnerability": 100, "vuln": 100, "abuse": 45,
    "founder": 80, "founders": 80, "ceo": 80, "cto": 75, "owner": 70,
    "hello": 45, "hi": 45, "hola": 45, "contact": 45, "contacto": 45, "hey": 45,
    "sales": 35, "partners": 35, "business": 35,
    "info": 25, "support": 25, "help": 25, "team": 25, "admin": 20,
    "community": 20, "office": 20, "mail": 15, "press": 20,
}

RUTAS_SEGURIDAD = [
    "SECURITY.md", "security.md", ".github/SECURITY.md", "docs/SECURITY.md",
    "SECURITY.txt", ".well-known/security.txt", "security.txt",
]
RUTAS_GENERALES = ["README.md", "readme.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]

SUBDOMINIOS = ("www.", "docs.", "doc.", "app.", "api.", "developer.", "developers.",
               "about.", "blog.", "help.", "support.", "go.", "portal.", "console.",
               "dashboard.", "status.", "kb.", "learn.")


def _texto(repo_full: str, ref: str, path: str) -> str:
    """Lee un archivo del repo con respaldo.

    _raw() tira de raw.githubusercontent.com sin token: en redes capadas
    (sandbox, datos moviles) devuelve None EN SILENCIO y el SECURITY.md
    simplemente no aparece. Si falla, cae a la API de contenidos, que va por
    api.github.com (autenticada y con mas cuota).
    """
    t = _raw(repo_full, ref, path)
    if t:
        return t
    import base64
    datos, st = _get(f"/repos/{repo_full}/contents/{path}?ref={ref}")
    if st == 200 and isinstance(datos, dict) and datos.get("encoding") == "base64":
        try:
            return base64.b64decode(datos.get("content") or "").decode("utf-8", "replace")
        except Exception:
            return ""
    return ""



# Un dominio corporativo dice "hay empresa detras"; un gmail puede ser cualquiera.
FREEMAIL = ("gmail.com", "googlemail.com", "hotmail.com", "outlook.com", "live.com",
            "yahoo.com", "proton.me", "protonmail.com", "icloud.com", "me.com",
            "aol.com", "mail.com", "gmx.com", "yandex.com", "qq.com", "163.com",
            "zoho.com", "pm.me", "tutanota.com", "fastmail.com", "msn.com")

def limpiar(email: str, autor: str = "") -> str | None:
    e = email.strip().strip(".,;:()<>[]\"'").lower()
    if not e or len(e) > 100:
        return None
    if any(b in e for b in BASURA):
        return None
    if not EMAIL_RE.fullmatch(e):
        return None
    local = e.split("@")[0]
    # cokev.bot@ se colaba porque solo miraba guiones: separar por cualquier
    # caracter que no sea letra, y comparar el token completo.
    if any(t in BOT for t in re.split(r"[^a-z]+", local)):
        return None
    if (autor or "").lower().count("bot") or (autor or "").lower().endswith("agent"):
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


def dominio_de(sitio: str) -> str:
    """Devuelve el dominio registrable, quitando subdominios tipicos."""
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
    if len(partes) >= 3 and partes[-2] in ("co", "com", "org", "net", "gob", "edu") \
            and len(partes[-1]) == 2:
        return ".".join(partes[-3:])
    return ".".join(partes[-2:]) if len(partes) >= 2 else host




# --- Verificacion de entrega -------------------------------------------------
# Un SECURITY.md puede llevar anios copiado de una plantilla: pone security@
# pero el buzon nunca se creo (ggui.ai reboto 550 5.1.1 teniendo MX de Google).
# No podemos saber si un buzon existe, pero SI si el dominio recibe correo:
# esposter.com tiene MX "ms28275001.msv1.invalid" = no recibe nada.
# Se consulta por DNS sobre HTTPS: sin instalar dnspython, funciona en Termux.
DOH = ("https://dns.google/resolve", "https://cloudflare-dns.com/dns-query")


def mx_de(dominio: str) -> tuple[str, list[str]]:
    """(estado, exchanges). estado: 'ok' | 'sin_correo' | 'error'."""
    import json, time, urllib.parse
    if not dominio or "." not in dominio:
        return "error", []
    for base in DOH:
        for _ in range(2):
            try:
                u = base + "?name=" + urllib.parse.quote(dominio) + "&type=MX"
                req = urllib.request.Request(
                    u, headers={"User-Agent": "sub-agente",
                                "Accept": "application/dns-json"})
                d = json.loads(urllib.request.urlopen(req, timeout=12).read())
                ex = [(a.get("data") or "").strip() for a in d.get("Answer", [])]
                # El registro llega como "0 ms28275001.msv1.invalid." con punto
                # final: sin quitarlo, endswith(".invalid") era False y el
                # dominio sin correo colaba como valido.
                hosts = []
                for e in ex:
                    partes = e.split()
                    h = (partes[-1] if partes else e).rstrip(".").lower()
                    if h:
                        hosts.append(h)
                if hosts:
                    if all(h.endswith(".invalid") for h in hosts):
                        return "sin_correo", hosts
                    return "ok", hosts
                if d.get("Status") == 0:      # NOERROR sin MX: no recibe correo
                    return "sin_correo", []
            except Exception:
                time.sleep(0.3)
    return "error", []


def _ruta_rebotados() -> str:
    import os
    os.makedirs("out", exist_ok=True)
    return os.path.join("out", "rebotados.json")


def cargar_rebotados() -> set:
    import json
    try:
        with io.open(_ruta_rebotados(), encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def registrar_rebote(email: str) -> int:
    import json
    r = cargar_rebotados()
    r.add(email.strip().lower())
    with io.open(_ruta_rebotados(), "w", encoding="utf-8") as f:
        json.dump(sorted(r), f, indent=1)
    return len(r)


def peso(email: str, fuente: str) -> int:
    """Cuanto vale esta direccion. Manda el rol sobre la fuente."""
    local = email.split("@")[0].split("+")[0]
    dom = email.split("@")[-1]
    bonus = 0 if dom in FREEMAIL else 15
    if local in ROLES:
        return min(100, ROLES[local] + bonus)
    if fuente == "SECURITY.md":
        return 90 + bonus
    if fuente == "commit":
        return min(100, 70 + bonus)   # una persona real: fundador o CTO
    if fuente == "org":
        return 50
    base = 30           # README y demas
    # jimmyc@resonatesolutions.com.au vale mas que jimmychen12138@gmail.com:
    # el dominio corporativo demuestra que existe una empresa que paga.
    dom = email.split("@")[-1]
    if dom not in FREEMAIL:
        base += 15
    return min(100, base)


def adivinar(dominio: str) -> list[str]:
    """Patrones habituales. NO verificados: son candidatos a probar."""
    if not dominio or "." not in dominio:
        return []
    return [f"{p}@{dominio}" for p in
            ("security", "hello", "hola", "info", "contact", "contacto", "team")]


def buscar(repo_full: str, branch: str = "main", con_commits: bool = True,
           con_patrones: bool = True, con_icp: bool = True) -> dict:
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
                         "peso": peso(email, fuente)})

    # 1. SECURITY.md: la mejor fuente con diferencia
    for ruta in RUTAS_SEGURIDAD:
        for e in extraer(_texto(repo_full, branch, ruta)):
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
                nom = ca.get("name") or ""
                lim = limpiar(ca.get("email") or "", nom)
                if lim:
                    agregar(lim, "commit", f"autor: {nom or '?'}")

    # 4. README y similares
    for ruta in RUTAS_GENERALES:
        for e in extraer(_texto(repo_full, branch, ruta)):
            agregar(e, "README", f"en {ruta}")

    # 5. Patrones sobre el dominio (no verificados)
    sitio = ""
    if (meta.get("owner") or {}).get("type") == "Organization":
        org2, _ = _get(f"/orgs/{owner}")
        sitio = org2.get("blog") or ""
    sitio = sitio or meta.get("homepage") or ""
    dominio = dominio_de(sitio)
    rebotados = cargar_rebotados()
    candidatos = [p for p in adivinar(dominio)
                  if con_patrones and p not in visto and p not in rebotados]

    hallados.sort(key=lambda h: -h["peso"])

    mx_estado, mx_hosts = mx_de(dominio) if dominio else ("error", [])
    if mx_estado == "sin_correo":
        # ninguna direccion de ese dominio va a llegar: las de persona mandan
        hallados = [h for h in hallados
                    if h["email"].split("@")[-1] != dominio]
        hallados.sort(key=lambda h: -h["peso"])

    # 6. Cruce con el ICP: no pierdas el tiempo con quien no va a comprar
    icp = None
    if con_icp:
        try:
            from .icp import perfil
            icp = perfil(repo_full)
        except Exception as e:
            icp = {"veredicto": "?", "motivo": str(e)}

    vivos = [h for h in hallados if h["email"] not in rebotados
             and not (mx_estado == "sin_correo"
                      and h["email"].split("@")[-1] == dominio)]

    descartado = bool(icp and icp.get("veredicto") == "DESCARTAR")

    return {
        "repo": repo_full,
        "owner": owner,
        "sitio": sitio or "",
        "dominio": dominio,
        "emails": hallados,
        "candidatos_sin_verificar": candidatos,
        "mx": mx_estado,
        "mx_hosts": mx_hosts,
        "rebotados": rebotados,
        "icp": icp,
        "descartado": descartado,
        # Una direccion que rebotó no se vuelve a recomendar: ggui.ai rebotó
        # security@ y la herramienta seguia mandandote ahi.
        "recomendado": ((vivos[0]["email"] if vivos else "")
                        or (candidatos[0] if candidatos else "")),
    }


def a_texto(res: dict) -> str:
    if res.get("error"):
        return f"{res['repo']}: {res['error']}"

    L = [f"Contactos de {res['repo']}" + (f"  ({res['sitio']})" if res.get("sitio") else "")]

    icp = res.get("icp")
    if icp:
        ver = icp.get("veredicto", "?")
        sc = icp.get("score_icp", "?")
        if res.get("descartado"):
            L.append(f"ICP: DESCARTADO (icp={sc}) -- {icp.get('motivo','')}")
            L.append(">>> NO LE ESCRIBAS. El filtro ya lo rechazo. Siguiente.")
        else:
            L.append(f"ICP: {ver} (icp={sc})")
    mx = res.get("mx")
    if mx == "sin_correo":
        L.append("AVISO: " + (res.get("dominio") or "?") +
                 " NO recibe correo (MX nulo). Ninguna direccion de ese dominio")
        L.append("       te va a llegar: usa la de una persona, no la de la empresa.")
    elif mx == "ok":
        L.append("MX: " + (res.get("dominio") or "?") + " recibe correo ("
                 + (res["mx_hosts"][0] if res.get("mx_hosts") else "?") + ")")
    L.append("")

    if res["emails"]:
        L.append("ENCONTRADOS (publicados por ellos mismos):")
        for h in res["emails"]:
            marca = "  <-- REBOTO" if h["email"] in (res.get("rebotados") or set()) else ""
            L.append(f"  {h['email']:40} peso {h['peso']:3}  {h['fuente']:11} "
                     f"{h['detalle']}{marca}")
        if any(h["email"] in (res.get("rebotados") or set()) for h in res["emails"]):
            L.append("  (los marcados rebotaron antes: no los vuelvas a usar)")
    else:
        L.append("No se encontro ningun correo publicado.")

    if res["candidatos_sin_verificar"] and not res.get("descartado"):
        L.append("")
        L.append("CANDIDATOS POR PATRON (NO verificados, pruebalos):")
        for c in res["candidatos_sin_verificar"]:
            L.append(f"  {c}")

    L.append("")
    if res.get("descartado"):
        L.append("Recomendado: NINGUNO (descartado por ICP)")
    elif not res["recomendado"]:
        L.append("Recomendado: NINGUNO (todo lo demas rebotó o no recibe correo)")
    else:
        L.append(f"Recomendado: {res['recomendado']}")
        if res["emails"]:
            # el aviso debe ir con el recomendado, no con el que rebotó
            top = next((h for h in res["emails"]
                        if h["email"] == res["recomendado"]), res["emails"][0])
            if top["fuente"] == "SECURITY.md" or top["email"].startswith("security@"):
                L.append("  ^ Sale de su politica de seguridad: es la persona que")
                L.append("    YA tiene el problema. Escribele primero.")
                L.append("  OJO: los SECURITY.md suelen ser plantilla copiada y el")
                L.append("  buzon a veces no existe (ggui.ai reboto 550). Si rebota,")
                L.append("  pasa al correo de una persona y anotalo: --rebotado X")
    if res.get("recomendado"):
        L.append("")
        L.append("  COPIA ESTA LINEA TAL CUAL (sin traducir y sin reescribir):")
        L.append("      " + res["recomendado"])
    return "\n".join(L)
