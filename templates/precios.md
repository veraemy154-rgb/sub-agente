# Escalera de precios

Todo en USD. Cobrar en USD. No cotizar en moneda local: el que paga en
moneda debil compra tiempo, no seguridad.

## Principios del director

1. **Nunca cobres por hora en la primera venta.** Cobra por entregable. La hora
   castiga tu velocidad y hace que el cliente negocie tu tiempo.
2. **El precio de entrada existe para comprar el caso de estudio, no el margen.**
   El Diagnostico Express es un loss leader con precio.
3. **Sube el precio cada 5 clientes.** Sin excepcion. Si no subes, trabajas gratis
   en la parte donde ya eres bueno.
4. **Nunca des el informe completo antes de cobrar.** El valor esta en la
   priorizacion, y esa se entrega con la propuesta, no antes.

## Etapa 1 — Diagnostico Express · US$ 490

| | |
|---|---|
| Duracion | 48–72 h |
| Alcance | Hasta 3 repositorios del mismo cliente |
| Entregable | Informe de exposicion, plan priorizado impacto/esfuerzo, mapeo a controles SOC 2, estimado de remediación |
| Para que sirve realmente | Es la cerradura de la puerta. Nadie te compra US$ 3.000 de entrada; todos te compran US$ 490. |

**Fase de lanzamiento (primeros 5 clientes): US$ 290 a cambio de testimonio publico
y referencia.** Despues, US$ 490. A partir del cliente 15, US$ 750.

## Etapa 2 — Remediacion · US$ 1.200 – 6.500 por proyecto

Se cotiza con el diagnostico en la mano. Formula interna (no se la muestres al cliente):

```
precio = 1200 + (hallazgos_altos x 220) + (hallazgos_medios x 90)
techo: 6500
```

| Perfil de cliente | Ticket tipico |
|---|---|
| Startup temprana, 1 repo, pocos hallazgos | US$ 1.200 – 1.800 |
| SaaS en crecimiento, 3–5 repos | US$ 2.500 – 4.000 |
| Con cliente enterprise esperando la evidencia | US$ 4.000 – 6.500 |

Cobro: **50 % al firmar, 50 % al mergear.** Sin excepciones. El PR mergeado es el
hito, no el PR abierto.

## Etapa 3 — Retainer "Gestion de Vulnerabilidades" · US$ 1.200 – 2.500/mes

Aqui esta el negocio: ingreso predecible.

| Plan | Precio/mes | Incluye |
|---|---|---|
| Base | US$ 1.200 | Escaneo en CI, triage de hallazgos, informe mensual de evidencia para el auditor |
| Pro | US$ 1.800 | Base + SLA de 72 h en criticos + 8 h/mes de remediación |
| Enterprise | US$ 2.500 | Pro + 20 h/mes + acompanamiento en la entrevista con el auditor |

**Objetivo: 6 retainers = US$ 9.000–15.000/mes de ingreso recurrente.** Con eso
dejas de vender y pasas a operar.

## Descuentos prohibidos

- No bajes el precio "porque es una startup". Cambia el alcance, no el precio.
- No hagas trabajo a cambio de equity en empresas que no conoces.
- No hagas el diagnostico gratis "para demostrar valor". Si lo regalas, vale cero.
  Hazlo a US$ 290 con testimonio, que es distinto: hay transaccion.

## Objeciones y respuestas

| Objecion | Respuesta |
|---|---|
| "Es caro" | "Mas caro es responder el cuestionario de seguridad de un cliente grande sin poder evidenciar gestion de vulnerabilidades. Eso cuesta el contrato." |
| "Lo hacemos nosotros" | "Perfecto. Les entrego el plan priorizado de US$ 490 y lo ejecutan. Si en dos sprints no esta, me llaman y lo hago yo." |
| "Ya tenemos Snyk/Sonar" | "Entonces tienen deteccion. Esto es evidencia y remediación: quien cierra el hallazgo y quien se lo muestra al auditor." |
| "Mandame mas info" | "Con gusto. Te mando el informe de 3 paginas y agendamos 15 minutos. El informe sale con la orden de compra." |
