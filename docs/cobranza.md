# Cobranza y flujo de caja

Vender es la mitad. Cobrar es la otra mitad, y es la que nadie sistematiza.
Este negocio no muere por falta de clientes: **muere por trabajar tres meses
gratis para un cliente que nunca pagó.**

---

## El calendario del dinero

| Día del mes | Qué pasa |
|---|---|
| 1 | Corre `scripts/evidencia_mensual.py`. Genera informe + factura de todos los clientes |
| 1–2 | Revisas cada informe, ajustas notas, firmas |
| 2 | Envías informe + factura juntos. **Nunca separados**: el informe es lo que justifica la factura |
| 8 | Vencimiento |
| 9 | Si no pagó: mensaje de seguimiento (día +3 del vencimiento real) |
| 15 | Segundo aviso |
| 23 | Suspensión |

**Envía el informe y la factura en el mismo correo.** Si los separas, el cliente
archiva el informe y "se le olvida" la factura. Juntos, el valor está a la vista
en el mismo momento en que se pide el dinero.

---

## Anticipo en proyectos de remediación

Para remediación (no retainer), siempre:

- **50 % al firmar el SOW, 50 % al mergear los PRs.**
- Nunca empieces sin el 50 % recibido. Ni por el mejor cliente del mundo.
- El hito es el **PR mergeado**, no el PR abierto. Si el cliente no mergea, no
  es tu problema de entrega: es su problema de priorización, y ya está facturado.

Para el diagnóstico (US$ 290–490): **100 % por adelantado.** Es un entregable de
48 horas; no hay motivo para financiarlo.

---

## Riesgo cambiario y operativo

Si operas desde un país con moneda inestable, esto no es un detalle contable:
es la diferencia entre cobrar y no cobrar.

1. **Todo en USD.** El precio, la factura, el contrato.
2. **No aceptes "te pago en moneda local al cambio oficial".** El cambio oficial
   casi nunca es el que consigues.
3. **Convierte lo antes posible** si tu costo de vida es en moneda local, y guarda
   un colchón de 2–3 meses de gastos en USD antes de tocar el resto.
4. **Separa cuentas:** una para la empresa, una personal. Mezclarlas es el error
   número uno del freelance que empieza a facturar bien.
5. **Guarda el comprobante de cada transferencia.** Cuando el cliente corporativo
   cambie de departamento de compras, ese PDF es tu prueba.

---

## Secuencia de cobranza (textos listos)

### Día −3 · Recordatorio

> Hola [nombre]: te paso la factura de [periodo] que vence el [fecha].
> Va junto al informe de evidencia del mes, que incluye [N] hallazgos cerrados.
> Cualquier duda me dices.

### Día +3 · Primer seguimiento

> Hola [nombre]: la factura [número] por US$ [monto] venció el [fecha].
> ¿Quedó en revisión o hay algo que necesites de mi parte para procesarla?

### Día +7 · Aviso formal

> Hola [nombre]: la factura [número] lleva 7 días vencida. Según las condiciones
> del servicio, a los 15 días de atraso se suspende la generación del informe de
> evidencia y la remediación. Me gustaría no llegar ahí: dime si hay algún
> problema con la factura.

### Día +15 · Suspensión

> Hola [nombre]: vencidos los 15 días, queda suspendido el servicio de
> [periodo]. Lo ya entregado sigue siendo tuyo y accesible. En cuanto se
> regularice el pago, reactivamos el mismo día.

### Día +30 · Cierre

> Hola [nombre]: doy por cerrado el alcance acordado. Si quieren retomar,
> lo hacemos con alcance y tarifa actualizados. Sin problema de mi parte:
> entiendo que las prioridades cambian.

---

## Cómo evitar el impago antes de que ocurra

| Prevención | Cómo |
|---|---|
| Que el que firma sea el que paga | En el SOW pon el contacto de facturación, no solo el técnico |
| Poca fricción de pago | Dos medios como máximo, datos completos en la factura |
| Factura pequeña y frecuente | Un retainer de US$ 1.200 se paga solo; un proyecto de US$ 15.000 se discute |
| Relación con alguien de finanzas | El correo técnico se archiva; el de cuentas por pagar se procesa |
| Entrega visible todos los meses | El informe de evidencia es la prueba de que el mes existió |

---

## Métricas de cobranza que miras cada mes

| Métrica | Sano |
|---|---|
| DSO (días de cobro promedio) | < 20 días |
| % de facturas pagadas a término | > 85 % |
| Facturas vencidas > 30 días | 0 |
| MRR cobrado vs. facturado | 100 % |

Si el MRR facturado es US$ 9.000 y el cobrado US$ 7.200, **no tienes un negocio
de US$ 9.000: tienes uno de US$ 7.200 con carga extra.** Esa es la métrica que
más se maquilla y la que más duele.

---

## Regla final

**El cliente que no paga no es un cliente: es un pasatiempo caro.**
Suspende a tiempo, sin culpa y sin discusión. Cada hora que le dedicas al que no
paga es una hora que no le dedicas al que sí.
