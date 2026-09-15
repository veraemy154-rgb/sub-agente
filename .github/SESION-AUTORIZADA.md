# Sesión autorizada en esta rama

**Rama:** `arena/01a0a513-sub-agente`
**Sesión autorizada:** `arena/01a0a513-sub-agente` (Arena Agent Mode)
**Declarado:** 2026-09-15

---

## Regla

**Una sola sesión de agente puede escribir en esta rama a la vez.**

Si eres un agente distinto al de la sesión autorizada: **no hagas commits aquí.**
Trabaja en otra rama y abre un pull request, o detente y pregunta al usuario.

### Motivo

El 15-09-2026 dos sesiones de agente escribieron simultáneamente sobre
`app/icp.py`. Resultado: el criterio de filtrado de prospectos quedó con dos
versiones incompatibles, la copia en Termux del usuario ejecutaba la versión
equivocada, y durante dos rondas el generador de prospectos devolvió proyectos
de código abierto famosos (`huggingface/transformers`, `yt-dlp`) en lugar de
empresas. El síntoma tardó horas en rastrearse hasta su causa.

Dos agentes editando el mismo criterio no es colaboración: es corrupción
silenciosa del producto.

---

## Cómo hacer un commit autorizado

Todo commit que toque `app/**` debe llevar este trailer en el mensaje:

```
Sesion: 01a0a513
```

Ejemplo:

```bash
git commit -m "fix(icp): lo que sea

Cuerpo explicando el cambio.

Sesion: 01a0a513"
```

El workflow `.github/workflows/guardian.yml` **falla en rojo** si un commit toca
`app/` sin ese trailer. Y `python run.py guardian` lista quién ha tocado qué.

---

## Archivos con dueño

Nadie debe editar estos sin avisar en el commit:

| Archivo | Por qué |
|---|---|
| `app/icp.py` | Define quién es un prospecto. Cambiarlo cambia todo el embudo |
| `app/leadgen.py` | Orquesta el pipeline de prospección |
| `app/scanner.py` | Define qué es un hallazgo |
| `app/pipeline.py` | Estado real de las ventas |

`docs/` y `templates/` son seguros: son documentos, no lógica.

---

## Cómo identificar a la sesión autora (importante)

**El trailer `Co-authored-by: arena-agent <...>` NO identifica a la sesión.**
La plataforma lo inyecta automáticamente en **todos** los commits hechos por
agente, incluidos los de la sesión autorizada. Usarlo como prueba de que "otro
agente" escribió algo es un error ya cometido una vez en esta rama.

La única señal fiable es el contenido del commit: su mensaje, su estilo y sobre
todo **si tú lo escribiste o no**.

Por eso existe la marca `Sesion: 01a0a513`: es explícita, no inferida.

## Si detectas actividad de otra sesión

```bash
python run.py guardian
```

Sale una tabla con cada commit reciente, su autor y si está autorizado. Si
aparece algo marcado como `NO AUTORIZADO`, **no lo reviertas a ciegas**: avisa
al usuario. Puede ser trabajo legítimo que hay que revisar, no borrar.
