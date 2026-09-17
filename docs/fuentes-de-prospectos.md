# Dónde conseguir prospectos

La pregunta no es *"dónde hay código con vulnerabilidades"*. Es
**"dónde hay una empresa con presupuesto, un problema reconocido y una fecha encima"**.
Son preguntas distintas, y la respuesta a la segunda casi nunca es GitHub.

```bash
python run.py fuentes              # todos los enlaces listos
python run.py fuentes --nivel 1     # solo los de mayor conversión
python run.py fuentes --md > out/fuentes.md
```

---

## El principio que ordena todo

**No hay que convencer a nadie de que la seguridad importa. Hay que aparecer
cuando ya están convencidos y no tienen a quién contratar.**

El que publicó "SOC 2 me está matando" ya pasó por las tres etapas que más
trabajo cuestan: reconoció el problema, le puso presupuesto y tiene una fecha.
Con él no vendes: respondes. Con un repo frío tienes que explicarle por qué
debería importarle algo de lo que nunca oyó hablar.

**Corolario:** la tasa de respuesta de un mensaje a alguien que se quejó en
público es de 3 a 5 veces la de un mensaje en frío. Es el mismo trabajo por
cinco veces el resultado.

---

## Los cuatro niveles

| Nivel | Qué es | Conversión | Volumen | Cuánto tiempo le dedicas |
|---|---|---|---|---|
| **1** | Ya dijeron que tienen el problema | Alta | Bajo | 1 h/semana |
| **2** | Señal de presupuesto | Media | Medio | 1 h/semana |
| **3** | Volumen con la herramienta | Baja | Alto | Automatizado |
| **4** | Comunidades y socios | Lenta | Compuesto | 1 h/semana |

La mayoría hace exactamente al revés: empieza por el nivel 3 porque es el único
que se puede automatizar, y se pasa seis semanas sin clientes. **Los niveles 1 y
2 son los que dan de comer las primeras ocho semanas.** El 3 es para llenar el
embudo cuando ya tengas testimonios y puedas permitirte que te ignoren.

---

## Nivel 1 — Los que ya hablaron

| Fuente | Por qué funciona |
|---|---|
| **X/Twitter**: búsqueda de quejas sobre SOC 2 | La señal más caliente que existe. Responde en menos de 24 h |
| **Reddit** (r/SaaS, r/startups, r/devops) | Gente resolviendo el problema en público, ahora mismo |
| **LinkedIn**: publicaciones recientes | Filtra por fecha. Comenta con sustancia antes de escribir al DM |
| **Hacker News** | Fundadores técnicos. Los hilos viejos también sirven: saca los nombres |
| **Auditores y consultores SOC 2** | El canal más infravalorado, abajo desarrollado |

**Regla de oro del nivel 1: respondes, no vendes.** Das la respuesta útil en
público y dejas que el perfil hable. El que quiera más, te escribe. Vender en el
primer mensaje a alguien que pidió ayuda es la forma más rápida de que te
bloqueen.

---

## Nivel 2 — La señal de presupuesto

| Fuente | Qué te dice |
|---|---|
| **Ofertas de empleo de seguridad/compliance** | Hay presupuesto aprobado y dolor reconocido |
| **Empresa que busca su PRIMER ingeniero de seguridad** | Tu cliente perfecto: no tiene nadie y tiene prisa |
| **Rondas de financiación recientes** | Dinero hoy; cuestionario de seguridad en seis meses |
| **Wellfound** (11–50 empleados) | El directorio más limpio de empresas reales |
| **Product Hunt** (productos "for teams") | Producto B2B nuevo con repo público |

El truco del nivel 2 es **el momento**: una empresa que acaba de levantar una
ronda no te necesita hoy. Te va a necesitar cuando su primer cliente enterprise
le mande el cuestionario. Anótala, y cuando llegue el momento, ya sabes quién es.

---

## Nivel 3 — El volumen (nuestra herramienta)

Aquí es donde entra `python run.py leads`. Dos usos:

```bash
# 1. Automático: descubre, califica, audita y prioriza
python run.py leads --lang python,javascript,typescript --top 20

# 2. Manual: pasa por el filtro los repos que mencionen cumplimiento
python run.py scan empresa/repo
```

**La búsqueda de GitHub que más vale no es la de vulnerabilidades, es esta:**

```
"SOC 2" in:readme
```

Un README que menciona SOC 2, HIPAA o PCI significa que **esa empresa ya está en
modo auditoría**. Tiene presupuesto, tiene fecha y está buscando quién le resuelva.
Es la señal más caliente que da GitHub, y casi nadie la busca.

---

## Nivel 4 — Socios de referencia (el canal que casi nadie usa)

Un auditor de SOC 2 tiene un problema estructural: **sus clientes necesitan
arreglar código y él no lo implementa.** Le arruina el cronograma y no le
compensa. Tú eres exactamente la pieza que le falta.

Lo mismo con:
- **Agencias de desarrollo**: tienen clientes con el problema y cero capacidad de seguridad. Ofréceles white-label.
- **Contadores y consultores de cumplimiento**: mismos clientes, misma necesidad.
- **vCISOs sobrecargados**: les sobra trabajo de implementación.

**Ventaja estructural:** un socio te manda clientes pre-calificados, con la
confianza ya transferida. No tienes que prospectar ni convencer: solo ejecutar.
Tres socios activos valen más que mil mensajes en frío.

Cómo activarlos: no les pidas trabajo, **resuélveles su cuello de botella**. El
mensaje está en `templates/mensaje-lanzamiento.md`, sección 5.

---

## Rutina semanal (4 horas)

| Día | Hora | Qué |
|---|---|---|
| Lunes | 1 h | Nivel 1: buscar quejas nuevas en X/Reddit/LinkedIn y responder en público |
| Martes | 1 h | Nivel 2: ofertas de empleo y rondas nuevas. Anotar 10 empresas |
| Miércoles | 30 min | Correr `run.py leads` y mandar 20 mensajes a los P1/P2 nuevos |
| Jueves | 1 h | Seguimientos. El 80 % de las respuestas llegan en el toque 3–5 |
| Viernes | 30 min | Nivel 4: nutrir socios. Un café virtual a la semana |

**Lo que no se automatiza es lo que produce.** Los niveles 1, 2 y 4 requieren que
escribas tú. Precisamente por eso funcionan: nadie más lo hace.

---

## Matemática del embudo por fuente

| Fuente | Mensajes | Respuesta | Cierre | Resultado |
|---|---|---|---|---|
| Nivel 1 (quejas públicas) | 10 | 40 % → 4 | 25 % → 1 | **1 cliente / 10 mensajes** |
| Nivel 4 (socios) | 5 | 60 % → 3 | 50 % → 1.5 | **1.5 clientes / 5 mensajes** |
| Nivel 2 (señal presupuesto) | 20 | 15 % → 3 | 20 % → 0.6 | 0.6 clientes / 20 mensajes |
| Nivel 3 (GitHub frío) | 50 | 8 % → 4 | 15 % → 0.6 | 0.6 clientes / 50 mensajes |

Fíjate en la última fila: **50 mensajes en frío producen menos que 10 mensajes a
quien ya se quejó en público.** Haz primero lo que produce.

---

## Errores al buscar prospectos

1. **Empezar por GitHub** porque es lo único que se puede automatizar. Es el camino más largo.
2. **Perseguir empresas grandes.** Tienen equipo de seguridad propio y un proceso de compras de tres meses.
3. **Ignorar tu propia red.** Para los tres primeros testimonios, tu red es el 90 % de la solución.
4. **No volver al nivel 1 cada semana.** La señal se enfría en 48 horas: el que se quejó el martes ya contrató a alguien el viernes.
5. **Medir el volumen en lugar de la calidad.** 50 mensajes mal dirigidos valen menos que 10 bien dirigidos.
6. **No anotar las empresas del nivel 2.** Hoy no te necesitan. En seis meses sí, y si las apuntaste, les escribes el día correcto.

---

## Regla final

**Los primeros 3 clientes salen de tu red.** Los siguientes 10, de los niveles 1
y 2. A partir de ahí, de los socios de referencia. GitHub es el relleno, no la
fuente principal.

Si llevas dos semanas y solo has tocado GitHub, estás haciendo el trabajo cómodo
en lugar del trabajo que paga.
