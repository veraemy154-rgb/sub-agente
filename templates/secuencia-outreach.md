# Secuencia de prospeccion — 5 toques en 14 dias

El mensaje lo genera `app/outreach.py` para cada prospecto auditado
(`POST /outreach`). Este documento es la doctrina detras de esos mensajes.

## Los numeros que importan

| Metrica | Referencia sana |
|---|---|
| Emails por semana | 40–60 |
| Tasa de apertura | > 40 % |
| Tasa de respuesta | 8–15 % |
| Tasa de cierre sobre respuestas | 10–20 % |
| Cada 50 mensajes valen | ~US$ 600–900 |

Si tu tasa de respuesta esta debajo del 5 %, **no cambies la oferta: cambia el
asunto**. El asunto es el 80 % del resultado.

---

## Dia 0 — Email 1 · El gancho

**Objetivo:** que respondan. No que compren.

**Estructura:**
1. Un hecho publico y concreto sobre SU repositorio (no un elogio, no una presentacion tuya).
2. La consecuencia en terminos que le importen a un fundador: el cuestionario de seguridad, la auditoria, el contrato que no cierra.
3. Una oferta pequeña y cerrada: US$ 490, 48 horas.
4. Un cierre facil de responder.

**Asunto que funciona:** `{repo}: 2 punto(s) que frenan un cuestionario de seguridad`
Especifico, con numero, y apunta a un problema de negocio y no a "urgente!!".

**Regla:** se menciona la AUSENCIA DE UN CONTROL, nunca un hallazgo explotable.
Ver `docs/legal-y-etica.md`.

---

## Dia 3 — LinkedIn · El refuerzo

Mas corto que el email. Mismo gancho. Una pregunta al final.

Sirve porque el fundador revisa LinkedIn y no revisa el correo de la empresa.
No repitas el email textualmente: que parezca la misma persona en otro canal.

---

## Dia 7 — Email 2 · La repeticion

La mayoria de la gente no responde al primer mail porque no lo vio, no porque
no le interese. El toque 2 y 3 son donde esta el dinero.

Reenmarca: "el punto critico es X". Sin disculparte por escribir de nuevo.

---

## Dia 11 — Email 3 · La prueba social

Cuenta un caso concreto con numeros. Si todavia no tienes cliente, cuenta el
patron generico de lo que ves en equipos de su tamaño — no inventes un cliente.

Ejemplo real del scanner: "equipo similar: CI sin escaneo de dependencias,
17 CVEs acumulados en produccion; se resolvio en dos sprints".

---

## Dia 14 — Email 4 · El cierre

Cierra con dignidad y deja la puerta abierta. El "cierro el tema" es el segundo
mensaje que mas respuestas genera en toda la secuencia: activa la perdida.

Si no responden: **reauditar en 60 dias y volver a entrar.** Muchos de los que
ignoran el primer contacto compran cuando les llega el cuestionario del cliente
grande, seis meses despues.

---

## A quien SI y a quien NO

### SI

- SaaS con 50–1.500 estrellas y push en los ultimos 60 dias → hay empresa y hay movimiento.
- Repos de organizacion (no de usuario personal) → hay estructura.
- Stack con dependencias auditables (Python, JS/TS, Go, Ruby).
- Senales de venta B2B: docs de API, pagina de precios, terminos empresariales.

### NO

- Repos con menos de 15 estrellas → no hay tarjeta de credito.
- Herramientas y repos académicos → no son compradores.
- Repos que YA tienen SECURITY.md + CI con escaneo + rama protegida → esa empresa ya tiene proveedor.
- Proyectos cripto/DeFi → es otro juego (Immunefi), otra especializacion.
- Forks y archivados.

El filtro esta implementado en `app/leadgen.py` (`puntuar_lead` y el ICP).

---

## Registro obligatorio

Un CSV o una planilla. Sin registro no hay mejora posible.

```
repo | contacto | canal | dia_tocado | estado | proximo_paso | monto
```

Estados: `contactado` · `respondio` · `diagnostico_enviado` · `cerrado` · `perdido` · `nurturing`

Cada viernes: mirar cuantos mensajes salieron, cuantos respondieron. Si no
sabes el numero, no estas operando, estas esperando.

---

## Manejo de objeciones

| Objecion | Respuesta |
|---|---|
| "No somos objetivo de ataques" | "No se trata de ser objetivo: se trata de que su cliente enterprise les va a pedir evidencia. Sin ella, el contrato no se firma." |
| "Manda info" | "Te mando el informe de 3 paginas ahora y agendamos 15 min. El informe sale con la orden de compra." |
| "No hay presupuesto" | "Entonces empecemos por el diagnostico de US$ 490. Si no hay nada que corregir, te lo digo y no te vendo nada mas." |
| "Ya lo cubre Snyk" | "Snyk te dice que esta roto. Yo te lo arreglo y te lo documento para el auditor. Son dos trabajos distintos." |
| "Hablamos el trimestre que viene" | "Perfecto. Te guardo el analisis 90 dias. Si antes les llega un cuestionario, escribime." |

---

## Regla final del director

**Ningun dia pasa sin mensajes enviados.** Los dias que no prospectas son los dias
en que el mes que viene no cobras. La prospeccion no es lo que haces cuando no
tienes trabajo: es el trabajo.
