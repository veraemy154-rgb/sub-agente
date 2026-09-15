# Plan de 90 dias — de cero a ingreso recurrente

**Director: el objetivo no es "encontrar vulnerabilidades". Es llegar al dia 90 con
6 retainers que sumen entre US$ 9.000 y US$ 15.000 mensuales.** Todo lo demas es ruido.

---

## Semana 0 (hoy) — Montar la fabrica

Ya esta construido en este repo. Lo unico que falta es que lo corras.

```bash
git pull && docker build -t sub-agente . && docker run -p 8000:8000 sub-agente
# o en local:
pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Endpoints listos:
- `GET /scan?repo=owner/nombre` → auditoria + informe + precio
- `POST /leads` → descubre, audita y prioriza prospectos (P1/P2/P3)
- `POST /outreach` → secuencia de 5 toques lista para enviar
- `POST /task` → router del sub-agente (area `seguridad` ya enrutada)

**Entregable de la semana:** 50 prospectos P1/P2 en `out/leads.json`.
Tarea literal, no aspiracional: corre `/leads` con distintos lenguajes hasta
juntar 50. A 5–10 prospectos por corrida, son 6 corridas.

---

## Dias 1–14 — Comprar credibility

No tienes portfolio, asi que tu primer producto son **3 casos de estudio**, no dinero.

| Dia | Accion |
|---|---|
| 1–2 | 50 prospectos cargados. Elegir 12 P1 con senal enterprise (SaaS con clientes, no repos de tools sueltas). |
| 3 | Preparar identidad minima: dominio, firma de mail, LinkedIn con titulo claro ("Ayudo a SaaS a pasar SOC 2 / cuestionarios de seguridad"). |
| 4 | Enviar los primeros 12 toques. Volumen bajo, mensaje manual y personalizado. |
| 5–10 | Seguir la secuencia. Responder en menos de 2 h. Registrar todo en un CSV simple: repo, contacto, dia, estado. |
| 8–14 | Cerrar **3 diagnosticos a US$ 290** a cambio de testimonio + permiso de nombrarlos. Entregar en 48 h, impecables. |

**Meta de la quincena: US$ 870 y 3 testimonios.** Poco dinero, activo enorme.
Los testimonios son lo que te permite cobrar US$ 490 y despues US$ 750.

> Nota del director: si al dia 14 no tienes 3 testimonios, el problema no es el
> precio ni el nicho: es que enviaste pocos mensajes o elegiste malos prospectos.
> Sube el volumen antes de cambiar el discurso.

---

## Dias 15–30 — Primer dinero real

| Metrica | Objetivo |
|---|---|
| Mensajes enviados por semana | 40–60 |
| Diagnosticos vendidos | 6–8 |
| Precio | US$ 490 |
| Conversion diagnostico → remediación | 1 de cada 3 |
| **Facturacion del mes** | **US$ 2.500 – 4.000** |

Ritmo semanal obligatorio:
- **Lunes:** correr `/leads`, cargar 15 prospectos nuevos, mandar 20 mensajes.
- **Martes–jueves:** seguimientos. El 80 % de las respuestas llegan en el toque 3–5.
- **Viernes:** entregar diagnosticos y escribir el caso de estudio de la semana.

**Al dia 30 subes el diagnostico a US$ 750.** Ya tienes testimonios.

---

## Dias 31–60 — Subir el ticket

Aqui dejas de vender informes y empiezas a vender implementacion.

| Metrica | Objetivo |
|---|---|
| Remediaciones cerradas | 3–4 a US$ 1.800–3.500 |
| Retainers firmados | 2 a US$ 1.200/mes |
| Diagnostico | US$ 750 |
| **Facturacion del mes** | **US$ 6.000 – 9.000** |

La llave: **no entregues el diagnostico y te vayas.** Cierra siempre con
"esto son 14 horas de implementacion, te lo hago en dos sprints por US$ X".
El diagnostico es la cerradura; la remediación es la venta.

En paralelo, monta el retainer: escaneo en CI + informe mensual de evidencia.
Es lo mismo que ya haces, empaquetado y recurrente.

---

## Dias 61–90 — Recurrencia

| Metrica | Objetivo |
|---|---|
| Retainers activos | 6 |
| Ingreso recurrente | US$ 9.000 – 15.000/mes |
| Ticket promedio de remediación | US$ 3.000+ |
| Prospeccion | Delegada o automatizada |

Con 6 retainers, tu trabajo semanal es: 6 informes (automatizables al 80 %) +
remediación puntual + nuevas ventas. Ahi decides si contratas un tecnico junior
para la ejecucion y te quedas tu con la venta.

---

## Metricas que miras cada semana (solo estas cuatro)

1. **Mensajes enviados** — es lo unico que controlas al 100 %.
2. **Tasa de respuesta** — sana: 8–15 %. Debajo de 5 %, cambia el asunto.
3. **Tasa de cierre de diagnostico** — sana: 10–20 % de los que responden.
4. **Ticket promedio** — tiene que subir cada mes. Si no sube, estas estancado.

Referencia de embudo: 50 mensajes → 5 respuestas → 1 diagnostico → 33 % remediación.
**Cada 50 mensajes valen alrededor de US$ 600–900.** Internaliza ese numero:
es lo que te dice cuanto vale tu hora de prospeccion.

---

## Errores que te van a costar dinero (evitalos)

1. **Cazar bugs en lugar de cazar compradores.** Un repo con 3 estrellas no tiene tarjeta de credito.
2. **Revelar un hallazgo explotable en el primer mail.** Ademas de poco etico, mata la venta: ya les diste el valor gratis.
3. **Cobrar por hora.** Te pone un techo a tu propia velocidad.
4. **Perseguir el bug bounty como ingreso principal.** Es loteria. Tenlo como hobby que genera credenciales.
5. **No subir el precio.** El cliente que te dice "que barato" es el que mas problemas da.
6. **Trabajar sin autorizacion escrita.** Ver `docs/legal-y-etica.md`. No es negociable.

---

## Por que este nicho y no otro

Vendemos a **startups SaaS que estan en SOC 2, o a las que un cliente grande les
acaba de mandar un cuestionario de seguridad**. Tres razones y son las que deciden:

1. **El presupuesto ya existe.** No hay que convencer de que la seguridad importa; hay que convencer de quien lo ejecuta.
2. **Hay fecha limite.** La auditoria tiene fecha. La urgencia la pone el calendario, no tu discurso de ventas.
3. **Es recurrente.** SOC 2 se renueva cada ano. Un cliente bien atendido vuelve solo.

El que vende "seguridad" en abstracto compite con Snyk y con la IA. El que vende
"pasas tu auditoria en 6 semanas" no tiene competencia.
