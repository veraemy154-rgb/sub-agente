# sub-agente

Núcleo multi-agente ejecutado fuera de GitHub (VPS + Docker).

**Linea de negocio activa:** deteccion pasiva de exposicion en repositorios
publicos y venta de la remediación como evidencia para SOC 2 / ISO 27001 /
cuestionarios de seguridad enterprise.

## Arranque rapido

```bash
pip install -r requirements.txt

python run.py scan owner/repo              # auditoria de un repo
python run.py scan owner/repo --md         # informe entregable al cliente
python run.py leads --lang python,go --top 12
python run.py outreach owner/repo --remitente "Tu Nombre"
```

Con Docker (VPS):

```bash
docker build -t sub-agente .
docker run -p 8000:8000 -e GITHUB_TOKEN=ghp_xxx sub-agente
```

Endpoints:

| Metodo | Ruta | Que hace |
|---|---|---|
| GET | `/` | estado y areas disponibles |
| POST | `/task` | router heurístico de tareas (0 tokens) |
| GET | `/scan?repo=owner/nombre` | auditoria + informe + precio sugerido |
| POST | `/leads` | descubre prospectos, los audita y prioriza P1/P2/P3 |
| POST | `/outreach` | secuencia de 5 toques lista para enviar |

## Estructura

```
app/
  agents.py    sub-agentes por area (seguridad, seo, ventas, operaciones, soporte)
  router.py    clasificacion por keywords, sin coste de tokens
  scanner.py   auditoria pasiva: GitHub API + OSV, solo lectura
  report.py    informe entregable y estimacion de precio
  leadgen.py   descubrimiento y priorizacion comercial de prospectos
  outreach.py  mensajes de primer contacto (5 toques)
  main.py      API FastAPI
templates/     SOW/autorizacion, precios, secuencia de prospeccion
docs/          plan-90-dias.md · legal-y-etica.md
run.py         CLI
```

## Lo que el scanner revisa

Sobre **informacion publica unicamente**, sin explotar nada:

| ID | Hallazgo | Control |
|---|---|---|
| SEC-001 | Sin politica de divulgacion (SECURITY.md) | CC7.1 |
| SEC-002 | Archivos con nombre de credencial en el arbol | CC6.1 |
| SEC-003 | Sin CI/CD | CC8.1 |
| SEC-004 | CI sin escaneo de vulnerabilidades en dependencias | CC7.1 |
| SEC-005 | CI sin SAST ni deteccion de secretos | CC7.1 |
| SEC-006 | Sin Dependabot/Renovate | CC7.1 |
| SEC-007 | Rama principal sin proteccion | CC8.1 |
| SEC-008 | Sin licencia | legal |
| SEC-009 | Sin .gitignore | CC6.1 |
| SEC-011 | CVEs conocidos en dependencias (OSV) | CC7.1 |
| SEC-012 | Repo sin actividad | CC7.1 |

## Linea roja

Solo lectura, solo datos publicos, nunca sin autorizacion escrita para cualquier
trabajo de remediación. Ver `docs/legal-y-etica.md` antes de escribirle a nadie.

## Documentos de operacion

- `docs/plan-90-dias.md` — el plan comercial completo, semana a semana.
- `docs/legal-y-etica.md` — limites legales y protocolo de contacto.
- `templates/precios.md` — escalera de precios y manejo de objeciones.
- `templates/sow-autorizacion.md` — firmar antes de tocar cualquier sistema.
- `templates/secuencia-outreach.md` — como prospectar.
