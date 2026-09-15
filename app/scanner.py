"""Auditoria pasiva de repositorios publicos.

Regla de oro del director: SOLO datos publicos, SOLO lectura, SOLO observacion.
Nunca explotamos, nunca descargamos secretos, nunca tocamos un sistema sin
autorizacion escrita. El producto es el INFORME, no la intrusion.

Salida: hallazgos priorizados + score de riesgo + mapeo a controles SOC 2.
Ese mapeo es lo que convierte un "tecnico encontrando bugs" en un proveedor
que le resuelve una auditoria al cliente. Ahi esta el margen.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
OSV = "https://api.osv.dev/v1/querybatch"
UA = {"User-Agent": "sub-agente-auditor/1.0 (+contacto previa autorizacion)"}

# Sin token, GitHub permite 60 peticiones/hora y 10 de busqueda por minuto.
# En una IP movil (Termux, datos) eso se agota en minutos y el scan devuelve
# basura en lugar de datos. Con token: 5.000 por hora.
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None

# ---------------------------------------------------------------- red

_CACHE: dict[str, tuple] = {}


def _get(path: str, token: str | None = None, timeout: int = 20):
    url = path if path.startswith("http") else API + path
    token = token or TOKEN
    ck = f"GET {url}"
    if ck in _CACHE:
        return _CACHE[ck]
    headers = dict(UA)
    headers["Accept"] = "application/vnd.github+json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = (json.loads(r.read().decode("utf-8", "replace")), r.status)
    except urllib.error.HTTPError as e:
        # Leemos el cuerpo: GitHub explica ahi si es limite de tasa o falta de permiso.
        try:
            cuerpo = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            cuerpo = {}
        msg = cuerpo.get("message") or e.reason
        out = ({"_error": e.code, "_msg": msg,
                "_rate_limit": "rate limit" in str(msg).lower()}, e.code)
    except Exception as e:  # red caida, timeout, DNS
        out = ({"_error": 0, "_msg": str(e)}, 0)
    if out[1] == 200:
        _CACHE[ck] = out
    return out


# ------------------------------------------------------- parsing deps

_REQ_RE = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(==|>=|<=|~=|>|<|!=)\s*([0-9][^\s;,\[]*)", re.M)
_NPM_VERSION_RE = re.compile(r"[~^>=<v\s]*(.+)")


def parse_requirements(text: str) -> list[tuple[str, str]]:
    out = []
    for m in _REQ_RE.finditer(text):
        name = m.group(1).lower()
        if m.group(2) == "==":  # solo pins exactos: los rangos no son auditables
            out.append((name, m.group(3).strip()))
    return out


def parse_package_json(text: str) -> list[tuple[str, str]]:
    try:
        data = json.loads(text)
    except Exception:
        return []
    out = []
    for section in ("dependencies", "devDependencies"):
        for name, spec in (data.get(section) or {}).items():
            if not isinstance(spec, str):
                continue
            m = _NPM_VERSION_RE.match(spec)
            if m and re.match(r"^\d", m.group(1)):
                out.append((name.lower(), m.group(1).strip()))
    return out


def parse_go_mod(text: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"^\s*([\w./\-]+)\s+v(\d[\w.\-+]*)", text, re.M):
        out.append((m.group(1), m.group(2)))
    return out


MANIFESTS = {
    "requirements.txt": ("PyPI", parse_requirements),
    "requirements-dev.txt": ("PyPI", parse_requirements),
    "package.json": ("npm", parse_package_json),
    "go.mod": ("Go", parse_go_mod),
}


# --------------------------------------------------------- hallazgos

def finding(fid, sev, title, detail, fix, control, effort="m"):
    return {
        "id": fid,
        "severidad": sev,
        "titulo": title,
        "detalle": detail,
        "remediacion": fix,
        "control_soc2": control,
        "esfuerzo": effort,
    }


SEV_ORDER = {"critica": 0, "alta": 1, "media": 2, "baja": 3, "informativa": 4}

SECRET_FILE_PATTERNS = [
    r"^\.env$", r"^\.env\.", r"(^|/)secrets?\.", r"(^|/)credentials?\.",
    r"(^|/)\.npmrc$", r"(^|/)\.pypirc$", r"(^|/)\.dockercfg$",
    r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$", r"\.(pem|p12|pfx|key)$",
    r"(^|/)service[-_]?account.*\.json$", r"(^|/)firebase.*\.json$",
    r"(^|/)\.aws/credentials$",
]
CI_DEP_SCAN_PATTERNS = [
    "pip-audit", "osv-scanner", "npm audit", "snyk", "trivy", "grype",
    "bundler-audit", "govulncheck", "retire.js", "dependency-check",
]
CI_SAST_PATTERNS = [
    "bandit", "semgrep", "codeql", "gosec", "brakeman", "eslint-plugin-security",
    "sonar", "trufflehog", "gitleaks", "detect-secrets",
]


def _tree(repo_full: str, branch: str, token=None) -> list[str]:
    data, st = _get(f"/repos/{repo_full}/git/trees/{branch}?recursive=1", token)
    if st != 200 or "tree" not in data:
        return []
    return [i["path"] for i in data.get("tree", []) if i.get("type") == "blob"]


def _raw(repo_full: str, ref: str, path: str, token=None) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo_full}/{ref}/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def osv_lookup(deps: list[tuple[str, str, str]], token=None, timeout=25):
    """deps = [(ecosystem, name, version)]. Devuelve {nombre: [ids]} o {'_skip': motivo}."""
    if not deps:
        return {}
    queries = [{"package": {"name": n, "ecosystem": e}, "version": v} for e, n, v in deps[:200]]
    payload = json.dumps({"queries": queries}).encode()
    req = urllib.request.Request(
        OSV, data=payload,
        headers={"Content-Type": "application/json", **UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        return {"_skip": f"OSV no alcanzable ({type(e).__name__}); ejecutar desde VPS con salida a internet"}
    hits = {}
    for q, res in zip(queries, data.get("results", [])):
        vulns = res.get("vulns") or []
        if vulns:
            hits[q["package"]["name"]] = sorted({v.get("id", "?") for v in vulns})[:5]
    return hits


# ------------------------------------------------------------ motor

def auditar(repo_full: str, token: str | None = None, con_osv: bool = True) -> dict:
    """Audita un repo publico. repo_full = 'owner/name'."""
    meta, st = _get(f"/repos/{repo_full}", token)
    if st != 200:
        return {"repo": repo_full, "error": meta.get("_msg", f"HTTP {st}"), "http": st}

    branch = meta.get("default_branch", "main")
    paths = _tree(repo_full, branch, token)
    low = {p.lower(): p for p in paths}
    hallazgos: list[dict] = []

    # --- 1. Politica de divulgacion -------------------------------------
    if "security.md" not in low and ".github/security.md" not in low:
        hallazgos.append(finding(
            "SEC-001", "media",
            "Sin SECURITY.md (politica de divulgacion)",
            "No existe politica publica para reportar vulnerabilidades. Los cuestionarios "
            "enterprise y SOC 2 suelen pedirla explicitamente.",
            "Crear SECURITY.md con alcance, canal de reporte, SLA de triage y compromiso de no represalias.",
            "CC7.1 / CC2.3", "s"))

    # --- 2. Posibles secretos en el arbol (solo nombres de archivo) ------
    sospechosos = []
    for p in paths:
        for pat in SECRET_FILE_PATTERNS:
            if re.search(pat, p.lower()):
                sospechosos.append(p)
                break
    if sospechosos:
        hallazgos.append(finding(
            "SEC-002", "alta",
            f"{len(sospechosos)} archivo(s) con nombre de credencial en el arbol",
            "Se detectaron rutas tipicas de secretos versionados (no se abrieron sus contenidos): "
            + ", ".join(sospechosos[:6]) + ("..." if len(sospechosos) > 6 else ""),
            "Verificar si estan tracked: si lo estan, rotar credenciales YA, purgar historial "
            "(git filter-repo) y meter .env en .gitignore + pre-commit secret scanning.",
            "CC6.1 / CC6.8", "m"))

    # --- 3. CI presente y que escanea ------------------------------------
    workflows = [p for p in paths if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))]
    ci_text = ""
    for w in workflows[:6]:
        ci_text += (_raw(repo_full, branch, w, token) or "") + "\n"

    if not workflows:
        hallazgos.append(finding(
            "SEC-003", "alta",
            "Sin CI/CD visible",
            "No hay workflows de GitHub Actions. Sin pipeline no hay lugar donde colgar "
            "controles automaticos: todo depende de revision humana.",
            "Definir pipeline minimo: build + tests + escaneo de dependencias + escaneo de secretos en cada PR.",
            "CC8.1 / CC7.1", "l"))
    else:
        if not any(k in ci_text.lower() for k in CI_DEP_SCAN_PATTERNS):
            hallazgos.append(finding(
                "SEC-004", "alta",
                "CI sin escaneo de vulnerabilidades en dependencias",
                f"Hay {len(workflows)} workflow(s) pero ninguno ejecuta "
                f"{'/'.join(CI_DEP_SCAN_PATTERNS[:3])} o equivalente.",
                "Agregar job de auditoria de dependencias que falle el PR ante CVEs altos/criticos.",
                "CC7.1 / CC8.1", "m"))
        if not any(k in ci_text.lower() for k in CI_SAST_PATTERNS):
            hallazgos.append(finding(
                "SEC-005", "media",
                "CI sin analisis estatico ni deteccion de secretos",
                "No se observa SAST ni secret scanning en el pipeline.",
                "Agregar semgrep/bandit + gitleaks/trufflehog como job obligatorio en PRs.",
                "CC7.1 / CC8.1", "m"))

    # --- 4. Dependabot ----------------------------------------------------
    if ".github/dependabot.yml" not in low and ".github/dependabot.yaml" not in low:
        hallazgos.append(finding(
            "SEC-006", "baja",
            "Sin Dependabot/Renovate configurado",
            "Las dependencias no se actualizan automaticamente; la deuda de CVE crece en silencio.",
            "Habilitar Dependabot con PRs agrupados semanales y auto-merge en parches de seguridad.",
            "CC7.1 / CC8.1", "s"))

    # --- 5. Proteccion de rama -------------------------------------------
    bp, bst = _get(f"/repos/{repo_full}/branches/{branch}/protection", token)
    if bst == 404:
        hallazgos.append(finding(
            "SEC-007", "alta",
            f"Rama '{branch}' sin proteccion",
            "Cualquier colaborador puede pushear directo a la rama principal: sin revision "
            "obligatoria ni historial aprobado. Es de los controles que mas preguntan los auditores.",
            "Proteger la rama: PR obligatorio, 1+ aprobacion, deshabilitar force-push, exigir CI verde.",
            "CC8.1 / CC6.1", "s"))

    # --- 6. Higiene general ------------------------------------------------
    if "license" not in low and "license.md" not in low and not meta.get("license"):
        hallazgos.append(finding(
            "SEC-008", "baja",
            "Repositorio sin licencia",
            "Sin licencia declarada el uso del codigo es ambiguo; bloquea ventas enterprise y M&A.",
            "Agregar LICENSE (la que corresponda al modelo de negocio).",
            "CC2.2 / legal", "s"))

    if ".gitignore" not in low:
        hallazgos.append(finding(
            "SEC-009", "media",
            "Sin .gitignore",
            "Sin .gitignore es cuestion de tiempo que se versione un .env o un artefacto sensible.",
            "Agregar .gitignore del stack y revisar historial con gitleaks.",
            "CC6.1 / CC8.1", "s"))

    # --- 7. CVEs reales en dependencias -----------------------------------
    deps: list[tuple[str, str, str]] = []
    manifiestos_vistos = []
    for fname, (eco, parser) in MANIFESTS.items():
        if fname in low:
            manifiestos_vistos.append(fname)
            txt = _raw(repo_full, branch, low[fname], token)
            if txt:
                for n, v in parser(txt):
                    deps.append((eco, n, v))

    cve = {}
    if con_osv and deps:
        cve = osv_lookup(deps)
    if cve.get("_skip"):
        hallazgos.append(finding(
            "SEC-010", "informativa",
            "Escaneo de CVEs pendiente", cve["_skip"],
            "Reejecutar la auditoria desde el VPS con salida a api.osv.dev.",
            "CC7.1", "s"))
    elif cve:
        total = sum(len(v) for v in cve.values())
        hallazgos.append(finding(
            "SEC-011", "alta",
            f"{total} CVE(s) en dependencias con version fija",
            "Paquetes con vulnerabilidades conocidas (fuente: OSV): "
            + "; ".join(f"{k}: {', '.join(v)}" for k, v in list(cve.items())[:8]),
            "Actualizar a la version parcheada; si no existe parche, pinnear o mitigar y documentar "
            "la excepcion con su justificacion para el auditor.",
            "CC7.1", "m"))

    # --- 8. Frescura -------------------------------------------------------
    pushed = meta.get("pushed_at")
    dias = None
    if pushed:
        try:
            dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
            dias = (datetime.now(timezone.utc) - dt).days
        except Exception:
            pass
    if dias is not None and dias > 180:
        hallazgos.append(finding(
            "SEC-012", "media",
            f"Repositorio sin actividad desde hace {dias} dias",
            "Codigo sin mantenimiento acumula CVEs sin parchear; los auditores lo marcan como riesgo de ciclo de vida.",
            "Definir owner, o archivar el repo y sacarlo del alcance de la auditoria.",
            "CC7.1 / CC8.1", "s"))

    hallazgos.sort(key=lambda f: SEV_ORDER.get(f["severidad"], 9))
    pesos = {"critica": 30, "alta": 18, "media": 8, "baja": 3, "informativa": 0}
    score = min(100, sum(pesos.get(f["severidad"], 0) for f in hallazgos))

    if score >= 60:
        banda, urgencia = "ALTA", "Venta calida: hay trabajo de remediacion evidente y urgente."
    elif score >= 30:
        banda, urgencia = "MEDIA", "Venta posible: conviene el Diagnostico Express como entrada."
    else:
        banda, urgencia = "BAJA", "No priorizar: poca superficie de mejora visible."

    return {
        "repo": repo_full,
        "url": meta.get("html_url"),
        "descripcion": (meta.get("description") or "")[:200],
        "lenguaje": meta.get("language"),
        "estrellas": meta.get("stargazers_count", 0),
        "forks": meta.get("forks_count", 0),
        "rama_default": branch,
        "ultimo_push_dias": dias,
        "manifiestos": manifiestos_vistos,
        "dependencias_analizadas": len(deps),
        "cves": {k: v for k, v in cve.items() if k != "_skip"},
        "hallazgos": hallazgos,
        "n_hallazgos": len(hallazgos),
        "score_riesgo": score,
        "banda": banda,
        "lectura_comercial": urgencia,
        "auditado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
