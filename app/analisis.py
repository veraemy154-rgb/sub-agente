"""Redacta un analisis publico listo para publicar.

Cuidado con lo que es esto: NO es una denuncia publica, es una DEMOSTRACION DE
CRITERIO. El objetivo no es que el lector piense "que listo es", es que piense
"este sabe exactamente que me falta y como arreglarlo".

Reglas que el generador respeta por construccion:
  1. Solo se publican AUSENCIAS DE CONTROL, nunca hallazgos explotables.
  2. Nunca se listan rutas concretas de posibles credenciales: se dice cuantas
     hay y de que tipo, sin decir donde estan.
  3. Cada observacion lleva su arreglo, con el codigo o comando para hacerlo.
  4. Tono de colega que ayuda, no de fiscal que acusa.
  5. Se puede anonimizar por completo.

Salida: borrador en Markdown. Lo editas y lo publicas.
"""
from __future__ import annotations

from datetime import datetime, timezone

# Arreglos concretos por hallazgo. Esto es lo que hace que el analisis sea util
# y no una lista de quejas: el lector se lleva algo ejecutable.
ARREGLOS = {
    "SEC-001": (
        "Politica de divulgacion",
        "Crea `SECURITY.md` en la raiz. Es lo primero que busca quien quiere "
        "reportarte algo con buena intencion, y lo primero que pregunta un "
        "cuestionario de seguridad.",
        """```markdown
# Politica de seguridad

## Versiones soportadas
Solo la ultima version menor recibe parches de seguridad.

## Como reportar
Escribe a security@tu-dominio.com. No abras un issue publico.

## Que esperar
- Confirmacion en 48 h habiles
- Evaluacion inicial en 5 dias habiles
- Actualizacion de estado cada 10 dias hasta el cierre

## Compromiso
No tomaremos acciones legales contra quien reporte de buena fe.
```""",
    ),
    "SEC-002": (
        "Credenciales en el repositorio",
        "Sin entrar en que archivos son: hay rutas con nombre de credencial "
        "versionadas. Es el hallazgo que mas incidentes reales causa y el mas "
        "rapido de arreglar.",
        """```bash
# 1. Rota YA lo que haya estado expuesto (rotar primero, limpiar despues)
# 2. Deja de versionarlo
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
git rm --cached .env

# 3. Purgar el historial (reescribe: coordinar con el equipo)
pip install git-filter-repo
git filter-repo --path .env --invert-paths

# 4. Que no vuelva a pasar: escaneo en pre-commit
pip install pre-commit
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
EOF
pre-commit install
```""",
    ),
    "SEC-003": (
        "Sin pipeline de CI/CD",
        "Sin pipeline no hay donde colgar controles automaticos: todo depende "
        "de que a alguien se le acuerde revisar. Es el prerrequisito de todo lo demas.",
        """```yaml
# .github/workflows/seguridad.yml
name: Seguridad
on: [push, pull_request]
jobs:
  dependencias:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pip-audit -q
      - run: pip-audit
```""",
    ),
    "SEC-004": (
        "CI sin escaneo de vulnerabilidades en dependencias",
        "El pipeline existe pero no revisa dependencias. Es el control que mas "
        "CVEs evita por hora invertida: se configura en diez minutos.",
        """```yaml
# Python
      - run: pip install pip-audit -q && pip-audit
# Node
      - run: npm audit --audit-level=high
# Cualquier stack
      - uses: google/osv-scanner-action@v1
```""",
    ),
    "SEC-005": (
        "Sin analisis estatico ni deteccion de secretos",
        "Falta la red que atrapa lo que el escaneo de dependencias no ve: "
        "secretos y patrones de codigo peligroso.",
        """```yaml
      - run: pip install semgrep -q && semgrep --config p/default --error
      - uses: gitleaks/gitleaks-action@v2
```""",
    ),
    "SEC-006": (
        "Sin actualizacion automatica de dependencias",
        "Sin esto, la deuda de CVE crece en silencio y se descubre el dia de la auditoria.",
        """```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
  - package-ecosystem: npm
    directory: "/"
    schedule:
      interval: weekly
```""",
    ),
    "SEC-007": (
        "Rama principal sin proteccion",
        "Cualquier persona con acceso puede pushear directo a la rama que va a "
        "produccion, sin revision y sin que pase nada automatico. Es de los "
        "controles que mas preguntan los auditores y de los mas rapidos de activar.",
        """```bash
gh api -X PUT repos/OWNER/REPO/branches/main/protection \\
  -F required_status_checks.strict=true \\
  -F 'required_status_checks.contexts[]=Seguridad' \\
  -F enforce_admins=false \\
  -F required_pull_request_reviews.required_approving_review_count=1 \\
  -F restrictions=null
```""",
    ),
    "SEC-008": (
        "Sin licencia",
        "Sin licencia declarada el codigo no es usable por terceros: frena ventas "
        "enterprise, integraciones y cualquier proceso de M&A.",
        "Agrega `LICENSE` con la licencia que corresponda a tu modelo de negocio.",
    ),
    "SEC-009": (
        "Sin .gitignore",
        "Sin .gitignore es cuestion de tiempo que se versione un artefacto sensible.",
        """```bash
# Python
curl -sL https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore
# Node
curl -sL https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore > .gitignore
```""",
    ),
    "SEC-011": (
        "Dependencias con CVEs conocidos",
        "Hay paquetes con vulnerabilidades publicadas y version parcheada "
        "disponible. Es el trabajo mas ingrato y el que mas valor tiene documentado.",
        """```bash
pip-audit                 # Python
npm audit fix             # Node
osv-scanner --lockfile=poetry.lock
```""",
    ),
    "SEC-012": (
        "Repositorio sin actividad",
        "El codigo sin responsable asignado acumula CVEs sin parchear. Los "
        "auditores lo marcan como riesgo de ciclo de vida.",
        "Asigna un responsable o archiva el repo y sacalo del alcance de la auditoria.",
    ),
}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_es(dt=None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return f"{dt.day} de {MESES[dt.month - 1]} de {dt.year}"


PUBLICABLES = ["SEC-001", "SEC-003", "SEC-004", "SEC-005", "SEC-006",
               "SEC-007", "SEC-008", "SEC-009", "SEC-011", "SEC-012"]


def redactar(rep: dict, autor: str = "", anonimo: bool = False,
             cta: str = "", solo_publicables: bool = True) -> str:
    """Genera el borrador del analisis publico a partir de una auditoria."""
    if rep.get("error"):
        return f"No se pudo generar el analisis: {rep['error']}"

    nombre = "Proyecto analizado" if anonimo else f"`{rep['repo']}`"
    hallazgos = [h for h in rep.get("hallazgos", [])
                 if h["id"] in PUBLICABLES or not solo_publicables]
    if not hallazgos:
        return f"{nombre}: sin hallazgos publicables. Mejor ejemplo para analizar: otro repo."

    L = []
    L.append(f"# Que falta en {nombre} (y en la mayoria de los repos que reviso)")
    L.append("")
    L.append(f"*{autor + ' · ' if autor else ''}"
             f"{fecha_es()}*")
    L.append("")
    L.append("---")
    L.append("")
    L.append(
        "Revise la informacion publica de este repositorio buscando una cosa concreta: "
        "**donde no se puede evidenciar gestion de vulnerabilidades**. No es una prueba "
        "de intrusion ni un listado de fallos explotables: es una lectura de la "
        "superficie publica contra los controles que piden SOC 2, ISO 27001 y los "
        "cuestionarios de seguridad de clientes enterprise.")
    L.append("")
    L.append("No encontre nada grave. Encontre algo mas comun y mas caro: **huecos de "
             "evidencia**.")
    L.append("")
    L.append("## Lo que encontre")
    L.append("")
    for i, h in enumerate(hallazgos, 1):
        L.append(f"{i}. **{h['titulo']}** (control {h['control_soc2']})")
    L.append("")
    L.append("## Como se ve uno por uno")
    L.append("")
    for h in hallazgos:
        info = ARREGLOS.get(h["id"])
        if not info:
            continue
        titulo, explicacion, arreglo = info
        L.append(f"### {titulo}")
        L.append("")
        L.append(explicacion)
        L.append("")
        L.append(arreglo)
        L.append("")
    L.append("## El patron")
    L.append("")
    L.append(
        "Ninguno de estos puntos es una vulnerabilidad dramatica. Ninguno sale en las "
        "noticias. Y sin embargo son los que frenan una auditoria, porque de cada uno "
        "el auditor pregunta **\"como lo hacen\"**, y la respuesta no esta escrita en "
        "ningun lado.")
    L.append("")
    L.append("La seguridad no se cae por el agujero espectacular: se cae por las diez "
             "cosas razonables que nadie documento.")
    L.append("")
    L.append("## Si solo tienes una tarde")
    L.append("")
    L.append("1. Protege la rama principal (10 minutos, evita el mayor riesgo de todos).")
    L.append("2. Mete un job de escaneo de dependencias en el CI (15 minutos).")
    L.append("3. Activa Dependabot (5 minutos).")
    L.append("4. Escribe el `SECURITY.md` (20 minutos).")
    L.append("")
    L.append("Con eso pasas de \"no tenemos nada documentado\" a \"tenemos los cuatro "
             "controles basicos con evidencia automatica\". El resto ya es mejora "
             "continua, no supervivencia.")
    L.append("")
    if cta:
        L.append("---")
        L.append("")
        L.append(cta)
        L.append("")
    L.append("---")
    L.append("")
    L.append("_Analisis sobre informacion publica, con fines educativos. No se accedio, "
             "exploto ni extrajo dato alguno. Los repositorios se revisan de forma "
             "constructiva: si algo aqui no te cuadra, escribeme y lo corrijo._")
    return "\n".join(L)


def post_linkedin(rep: dict, autor: str = "", anonimo: bool = False,
                  cta: str = "") -> str:
    """El post nativo. En LinkedIn los enlaces externos pierden alcance: el
    analisis va en el propio post."""
    nombre = "un repo publico" if anonimo else f"{rep['repo']}"
    altos = [h for h in rep.get("hallazgos", []) if h["severidad"] in ("critica", "alta")]
    L = []
    L.append(f"Revise {nombre} buscando una sola cosa: donde no se puede evidenciar "
             f"gestion de vulnerabilidades.")
    L.append("")
    L.append(f"Encontre {rep.get('n_hallazgos', 0)} puntos. "
             f"{len(altos)} de severidad alta. Ninguno es una vulnerabilidad "
             f"espectacular.")
    L.append("")
    L.append("Y ahi esta el problema, y el de casi todos los equipos con los que hablo:")
    L.append("")
    for h in rep.get("hallazgos", [])[:4]:
        if h["id"] in PUBLICABLES:
            t = h["titulo"][0].upper() + h["titulo"][1:]
            L.append(f"→ {t}")
    L.append("")
    L.append("El auditor no te pregunta si eres seguro. Te pregunta como lo haces. "
             "Y \"Snyk nos avisa\" no es una respuesta: es una herramienta.")
    L.append("")
    L.append("Lo que frena una auditoria no suele ser el agujero grave. Son las diez "
             "cosas razonables que nadie documento.")
    L.append("")
    L.append("En el primer comentario dejo como arreglar los cuatro mas importantes "
             "en una tarde.")
    L.append("")
    if cta:
        L.append(cta)
    return "\n".join(L)
