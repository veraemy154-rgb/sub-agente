# Facturacion — plantilla y reglas

La factura la genera `app/facturacion.py` y la emite automáticamente
`scripts/evidencia_mensual.py`. Este documento es la doctrina: **cómo cobrar
para que te paguen a tiempo.**

---

## Las cinco reglas

1. **Se factura el día 1, se cobra por adelantado.** El servicio de septiembre
   se paga en septiembre, no en octubre. Si facturas a mes vencido, estás
   financiando a tu cliente con tu trabajo.
2. **USD. Siempre USD.** Nunca cotices ni aceptes pago en moneda local con
   "ajuste por inflación". El que paga en moneda débil te está pagando menos
   cada semana.
3. **Pago a 8 días.** Más plazo es financiación gratis; menos parece desesperación.
4. **Nunca empieces el mes siguiente con el mes anterior impago.** Primera vez
   es un descuido; segunda vez es una política, y la pusiste tú.
5. **El que no paga, no recibe informe.** Se suspende el servicio, no la relación.
   Sin rencor, sin drama: es una cláusula, no una discusión.

---

## Estructura de la factura

| Bloque | Contenido | Por qué está |
|---|---|---|
| Emisor | nombre, ID fiscal/RIF, dirección, contacto | Sin esto no es factura, es un recado |
| Cliente | razón social, persona de contacto | Que llegue a quien paga, no a quien usa |
| Periodo | `YYYY-MM` | Amarra la factura al informe de evidencia del mismo mes |
| Vencimiento | fecha concreta | "A 8 días" se discute; "el 8 de octubre" no |
| Detalle | concepto, cantidad, precio, importe | Una línea por servicio. Nunca "varios" |
| Alcance | repos incluidos, SLA, horas | Para que no pidan trabajo fuera de alcance gratis |
| Formas de pago | tabla con medios y datos | Cuantas más fricciones, más tardan |
| Condiciones | 5 cláusulas | Es lo que se usa si hay que cobrar por las malas |

---

## Rieles de cobro

Ordenados por conveniencia para cobrar en USD desde Venezuela. Rellena tus datos
reales en `app/facturacion.py` (`RIELES_DEFAULT`) o pásalos por parámetro.

| Medio | Acreditación | Cuándo usarlo |
|---|---|---|
| **Zelle** | mismo día | Clientes en EE. UU. Es el más rápido y sin comisión |
| **USDT (TRC20)** | mismo día | Cuando el cliente no tiene banca en USD. Comisión baja |
| **Wise** | 1–2 días | Europa y clientes que pagan por plataforma |
| **Payoneer** | 1–2 días | Alternativa a Wise |
| **Transferencia USD** | 2–5 días | Clientes corporativos grandes; suelen exigirla |

### PayPal: cómo usarlo bien (y su trampa)

Es el medio que más confianza genera en un cliente nuevo: no tiene que darte sus
datos bancarios, paga en dos clics y tiene protección al comprador. **Pero tiene
una trampa operativa si operas desde Venezuela.**

| Lo bueno | Lo malo |
|---|---|
| El cliente paga sin fricción | Comisión internacional alta (~4,99 % + fijo) |
| Acreditación inmediata | **No permite retiro a bancos venezolanos** |
| Protección al vendedor si entregas con respaldo | Puede retener fondos 21 días en cuentas nuevas |
| Se integra como botón en la landing | Cierres y limitaciones automáticas por movimientos atípicos |

**Lo que hay que hacer:**

1. **Abre una cuenta en USD donde PayPal sí pueda retirar** (banco en EE. UU. o
   Puerto Rico; varios se abren con pasaporte y RIF). Sin esto, el dinero entra
   pero no sale.
2. **Retira con frecuencia.** No dejes saldo acumulado en PayPal: una limitación
   de cuenta puede dejar fondos congelados por meses.
3. **Ten siempre un segundo medio listo.** Si PayPal limita la cuenta, la
   factura siguiente sale por Zelle o USDT. Que el cliente ya sepa que existen.
4. **No muevas volumen atípico de golpe.** Los bloqueos se disparan por
   movimientos que no encajan con el historial de la cuenta.
5. **Usa datos reales y consistentes** (nombre, dirección, tarjeta a tu nombre).
   La mayoría de las limitaciones permanentes vienen de perfiles inconsistentes.

**La comisión la paga el cliente.** La landing ya la suma al importe
(`RECARGO_PCT = 5.5`) y `app/facturacion.py` tiene `con_recargo()` para lo mismo.
Si no la sumas, tu margen se lo come la pasarela: en un diagnóstico de US$ 290
son US$ 16 menos en cada venta.

### Regla general de medios de pago

**Regla:** ofrece dos medios como máximo. Cuantas más opciones pones, más tiempo
tarda el cliente en decidir.

**Truco que funciona:** el medio alternativo (cripto) lo mencionas solo si el
cliente dice que no puede transferir. Si lo pones en la factura desde el principio,
algunos clientes corporativos lo leen como falta de formalidad.

---

## Numeración y control

- Formato: `F-2026-09-ACME` (periodo + 6 caracteres del cliente).
- Un registro en planilla por factura: número, cliente, periodo, monto, emitida,
  vencimiento, cobrada, días de atraso.
- La función `estado_cuenta()` de `app/facturacion.py` clasifica automáticamente
  en **al día / por vencer / vencido / crítico**.

---

## Secuencia de cobranza (dunning)

Se activa sola. No es personal, es un proceso.

| Día | Acción | Tono |
|---|---|---|
| −3 al vencimiento | Recordatorio con la factura adjunta | Informativo |
| Vencimiento | "La factura vence hoy", enlace de pago | Neutro |
| +3 | "Quedó pendiente, ¿todo bien?" | Preocupado, no acusador |
| +7 | "Recordatorio: sin pago se suspende el servicio a los 15 días" | Formal |
| +15 | **Suspensión del servicio.** Sin informe, sin remediación | Firme y corto |
| +30 | Cierre de alcance, propuesta de reactivación | Definitivo |

**El día +3 es el que cobra.** La mayoría de los impagos son despistes, no
decisiones. Un mensaje a tiempo resuelve el 80 %.

**El día +15 es el que te respeta.** Si no suspendes nunca, has enseñado que
trabajar gratis es una opción disponible.

---

## Qué hacer con el que no paga

1. Suspende. Sin excepciones.
2. Guarda todo: facturas, correos, entregables enviados.
3. No borres su acceso ni destruyas nada: eso puede volverse en tu contra.
4. Reactiva si paga. El rencor no factura: el cliente moroso que paga es mejor
   que el cliente perfecto que no existe.

---

## Errores que cuestan dinero

| Error | Consecuencia |
|---|---|
| Facturar a mes vencido | Financias al cliente y cobras 45 días después de trabajar |
| No poner fecha de vencimiento | "A 30 días" empieza a contar cuando al cliente le conviene |
| Aceptar pago parcial sin acuerdo escrito | Se vuelve la norma |
| Trabajar horas extra no facturadas | El cliente las considera incluidas; las discute después |
| No suspender nunca | Enseñas que no pagar no tiene consecuencia |
| Dejar el precio fijo dos años | Facturas lo mismo mientras tu trabajo vale más |

---

## Subir precios

- **Cada 5 clientes nuevos**, sube el diagnóstico.
- **Cada 12 meses**, sube el retainer a los clientes existentes. Aviso con 60 días.
- Los clientes que llevan más de un año contigo son los que menos se quejan: ya
  vieron el valor. El que se queja por US$ 200 no es al que quieres retener.

Comunicación de subida, textual:

> "A partir de marzo el plan Pro pasa a US$ 2.000. Llevamos 14 meses trabajando
> juntos y el alcance creció de 2 a 5 repos. Si prefieres mantener la tarifa
> actual, reducimos el alcance a 2 repos. Lo que no puedo es seguir absorbiendo
> la diferencia."

Ofreces reducir alcance. Casi nadie lo elige: **el alcance es la palanca, no el precio.**
