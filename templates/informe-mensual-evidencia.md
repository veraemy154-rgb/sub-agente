# Informe mensual de evidencia — el producto que sostiene el retainer

**Por qué existe este documento:** el auditor de SOC 2 no te pide que no tengas
vulnerabilidades. Te pide que **demuestres que las gestionas**. Un informe mensual
con fechas, responsables, cierres y excepciones aceptadas es exactamente esa
evidencia. Y el cliente lo necesita **todos los meses**, no una vez.

Es el activo que convierte una venta única de US$ 2.500 en US$ 1.200–2.500
recurrentes durante años. Sin él, el retainer es "un técnico al que le pago por
mirar": se cancela en el mes tres. Con él, es "la prueba que necesito para el
auditor": no se cancela nunca.

---

## Cómo se genera

```bash
python run.py evidencia --cliente "Acme SaaS" --repos acme/api,acme/web
python run.py evidencia --demo        # informe de ejemplo para mostrar al prospecto
```

También desde la API: `POST /evidence`.

El esqueleto lo genera `app/evidence.py`. **Tú solo rellenas los datos del mes y
firmas.** Si tardas más de 30 minutos por cliente, el retainer no escala.

---

## Estructura y por qué cada parte importa

| Sección | Para quién es | Para qué sirve |
|---|---|---|
| 1. Resumen para dirección | El CTO / el fundador | Que en 30 segundos sepa si está bien. Nadie lee 12 páginas. |
| 2. Estado de los controles | **El auditor** | La tabla que busca: control → evidencia → estado. Es la sección que más se fotocopia. |
| 3. Hallazgos cerrados | El auditor y el cliente | Demuestra capacidad de ejecución y velocidad de respuesta. |
| 4. Hallazgos abiertos y plan | El cliente | Evita la sensación de que se acumula deuda en silencio. |
| 5. **Excepciones aceptadas** | **El auditor** | La sección que más discusiones evita. |
| 6. Actividad del periodo | El auditor | Volumen de trabajo: que se vea que pasó algo. |
| Anexo | El auditor | Los artefactos crudos por si los pide. |

---

## La sección 5 es la más valiosa del informe

**Un auditor no exige riesgo cero. Exige riesgo documentado.**

La diferencia entre "tenemos esta librería vulnerable" y "tenemos esta librería
vulnerable, no existe versión parcheada, la mitigamos con WAF, no está expuesta
externamente, lo aprobó el CTO y lo revisamos el 1 de diciembre" es la diferencia
entre una observación y un hallazgo.

Formato de cada excepción:

| Campo | Contenido |
|---|---|
| ID | `EXC-001`, correlativo, para poder seguirlo en el tiempo |
| Riesgo | Qué está abierto y dónde |
| Justificación | Por qué no se cierra ahora (sin versión parcheada, rompe compatibilidad, riesgo aceptado) |
| Aprobado por | **Persona con nombre y cargo.** "Aprobado por el CTO", no "aprobado" |
| Revisión | Fecha concreta de reevaluación. Sin fecha, la excepción es eterna y el auditor lo sabe |

---

## Métricas que se reportan (y sus umbrales)

| Métrica | Definición | Objetivo |
|---|---|---|
| Cobertura de escaneo | % de repos productivos con escaneo en CI | 100 % |
| Tasa de cierre | cerrados / (cerrados + abiertos) | > 70 % |
| MTTR | días promedio entre detección y cierre | ≤ 14 días |
| Altos/críticos abiertos | severidad alta o crítica sin cerrar | 0 |
| Hallazgos nuevos | detectados en el periodo | informativo |

**Nunca maquilles estas cifras.** Un mes malo bien explicado (con plan y fechas)
pasa una auditoría. Una cifra inflada que el auditor descubre no la pasa, y te
cuesta el cliente y la reputación.

---

## Ritual operativo del retainer

| Cuándo | Qué haces |
|---|---|
| Día 1 de mes | Generas el esqueleto con `run.py evidencia` |
| Día 1–2 | Rellenas cierres (PRs del mes) y abiertos |
| Día 2 | Revisas excepciones: ¿siguen vigentes? ¿vence alguna? |
| Día 3 | Envías + llamada de 15 min si el mes fue movido |
| Cada trimestre | Revisión de alcance: ¿entraron repos nuevos? Si sí, se ajusta el fee |

Cuatro horas al mes por cliente, facturadas a US$ 1.200–2.500.
**A seis clientes son 24 horas al mes por US$ 7.200–15.000.** Ese es el negocio.

---

## Cómo venderlo (cuándo sacar el tema)

No al principio. El orden es:

1. **Diagnóstico (US$ 490).** Entregas el informe.
2. **Remediación (US$ 1.8k–4.5k).** Implementas y cierras los hallazgos.
3. **Cuando entregas la remediación**, dices:
   *"Esto queda resuelto hoy. Pero el auditor no te pregunta por hoy: te pregunta
   por los últimos doce meses. Necesitas evidencia mensual. Te lo dejo montado
   por US$ 1.200 al mes."*

Ese momento —justo después de que vieras working software y antes de que se
olviden del tema— es el de mayor conversión de todo el embudo. No lo desperdicies
entregando el informe final por email y desapareciendo.

---

## Escala de precios del retainer

| Plan | Precio | Contenido |
|---|---|---|
| Base | US$ 1.200 | Escaneo en CI + informe mensual + triage |
| Pro | US$ 1.800 | Base + SLA 72 h en críticos + 8 h/mes de remediación |
| Enterprise | US$ 2.500 | Pro + 20 h/mes + acompañamiento en la entrevista con el auditor |

Sube el precio cuando el cliente tenga más repos en alcance. El alcance es la
palanca, no el tiempo.
