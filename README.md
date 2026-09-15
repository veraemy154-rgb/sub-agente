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
python run.py evidencia --demo             # informe mensual de evidencia (retainer)
python run.py fuentes                       # donde encontrar prospectos (enlaces listos)
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
| POST | `/leads` | busca, califica ICP, audita y prioriza P1/P2/P3 |
| POST | `/outreach` | secuencia de 5 toques lista para enviar |
| POST | `/evidence` | informe mensual de evidencia (retainer) |
| GET | `/evidence/demo` | informe de muestra para mostrar a un prospecto |
| POST | `/contacto` | recibe los leads de la landing |
| GET | `/site/` | landing page (`site/index.html`) |

## Estructura

```
app/
  agents.py    sub-agentes por area (seguridad, seo, ventas, operaciones, soporte)
  router.py    clasificacion por keywords, sin coste de tokens
  scanner.py   auditoria pasiva: GitHub API + OSV, solo lectura
  report.py    informe entregable y estimacion de precio
  icp.py       calificacion comercial: separa empresas con presupuesto de repos sueltos
  leadgen.py   descubrimiento y priorizacion comercial de prospectos
  outreach.py  mensajes de primer contacto (5 toques)
  evidence.py  informe mensual de evidencia para el retainer
  snapshots.py estado historico de hallazgos: detecta que se cerro y que aparecio
  facturacion.py facturas y estado de cuenta del retainer
  main.py      API FastAPI
templates/     SOW/autorizacion, precios, secuencia, informe mensual de evidencia
docs/          plan-90-dias.md · legal-y-etica.md
site/          landing page de la oferta (index.html, sin dependencias)
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
- `templates/testimonios.md` — como conseguir testimonios reales sin regalar el trabajo.
- `templates/mensaje-lanzamiento.md` — mensajes de la oferta de lanzamiento a contactos templados.
- `docs/fuentes-de-prospectos.md` — los 4 niveles de fuentes y la rutina semanal.

## Automatizacion mensual (lo que hace que el retainer no dependa de ti)

El dia 1 de cada mes, `.github/workflows/evidencia-mensual.yml` ejecuta:

```bash
python scripts/evidencia_mensual.py        # escanea, compara y emite
```

Para cada cliente de `clientes.json`:

1. Escanea sus repos.
2. Compara contra el estado guardado en `out/estado/` -> sabe que se cerro,
   que aparecio y con que antiguedad (MTTR real, no inventado).
3. Escribe el informe de evidencia en `out/evidencia/`.
4. Escribe la factura en `out/facturas/`.
5. Imprime el MRR del mes.

Tu trabajo queda en revisar, firmar y enviar. Cuatro horas al mes por cliente.

```bash
cp clientes.ejemplo.json clientes.json   # clientes.json va en .gitignore
python scripts/evidencia_mensual.py --periodo 2026-09
```

El pipeline de seguridad que se le instala al cliente (el control CC7.1
automatizado) esta en `templates/cliente-seguridad.yml`.
