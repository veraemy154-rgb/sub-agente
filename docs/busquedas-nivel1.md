# Búsquedas de nivel 1: encontrar al que ya se quejó

Aquí no buscas código: buscas **gente que ya dijo en público que tiene el
problema**. No hay que convencerla de nada, solo aparecer.

```bash
python run.py fuentes --nivel 1     # enlaces listos para hacer clic
```

---

## Las frases que delatan a un comprador

Esto es lo que buscas. Si alguien escribió una de estas, **tiene el problema,
una fecha y presupuesto**. Cópialas tal cual en el buscador:

### Dolor con fecha (las mejores)

| Frase | Qué significa |
|---|---|
| `"security questionnaire" enterprise client` | Ya se lo pidieron. Está trabado |
| `"SOC 2" "how long"` | Calculando si llega. Tu momento exacto |
| `client is asking for SOC 2` | Le acaba de llegar. Urgencia máxima |
| `we need SOC 2 by` | Tiene fecha. Vende solo |
| `SOC 2 is killing` | Dolor activo y público |
| `failed our SOC 2 audit` | Necesita remediación YA |
| `SOC 2 evidence` | Ya sabe que el problema es la evidencia, no la seguridad |

### Dolor de estructura

| Frase | Qué significa |
|---|---|
| `we don't have a security team` | No tiene a nadie. Eres tú o nadie |
| `first security hire startup` | Presupuesto aprobado, puesto vacío |
| `who owns security` | Nadie. Oportunidad limpia |
| `ISO 27001 startup` | Mismo problema, otro sello |
| `vendor security review` | Un cliente grande lo está evaluando ahora |
| `due diligence security startup` | Hay una compra o una ronda en juego |

### En español (menos volumen, menos competencia)

| Frase |
|---|
| `auditoría de seguridad cliente enterprise` |
| `cuestionario de seguridad proveedor` |
| `certificación ISO 27001 startup` |
| `cómo implementar SOC 2` |

---

## Reddit

### Los subreddits que valen

| Subreddit | Por qué |
|---|---|
| **r/SaaS** | Fundadores con clientes enterprise. El mejor |
| **r/startups** | Más ruido, pero sale de todo |
| **r/devops** | Quien implementa, no quien decide: útil para llegar al CTO |
| **r/cybersecurity** | Mucho profesional, menos comprador |
| **r/ExperiencedDevs** | Gente senior con presupuesto de herramientas |
| **r/msp** | Revendedores: pueden ser socios, no clientes |
| **r/engineeringmanagers** | Quien responde el cuestionario |
| **r/aws** / **r/node** / **r/django** / **r/golang** | Por stack, si quieres acotar |

### Cómo buscar dentro de un subreddit

```
reddit.com/r/SaaS/search/?q=SOC+2&restrict_sr=1&sort=new
```

Cambia `r/SaaS` por el subreddit y `SOC+2` por la frase. **`sort=new` es
clave**: una queja de hace tres meses ya tiene el problema resuelto o
contrataron a alguien.

### Búsqueda global ordenada por reciente

```
reddit.com/search/?q=%22security+questionnaire%22+startup&sort=new
```

### Cómo trabajarlo

1. Busca una frase, filtra por **new**.
2. Lee el hilo. Si el problema es de verdad, **responde con la solución en el propio hilo** — sin enlaces, sin vender.
3. Después, y solo si aportaste algo, le escribes al DM.

**Nunca llegues vendiendo al hilo.** Te borran y te ganas mala fama en una
comunidad pequeña donde todos se conocen.

---

## LinkedIn

### Publicaciones (lo más caliente)

```
linkedin.com/search/results/content/?keywords=SOC%202&sortBy=%22date_posted%22
```

Filtra por **Publicaciones** y por **última semana**. Busca también:
`security questionnaire`, `SOC 2 journey`, `ISO 27001`.

### Personas

```
linkedin.com/search/results/people/?keywords=SOC%202%20CTO
linkedin.com/search/results/people/?keywords=%22Head%20of%20Engineering%22%20security
```

### Ofertas de empleo (señal de presupuesto)

```
linkedin.com/jobs/search?keywords=SOC%202&f_TPR=r604800
```

`f_TPR=r604800` = última semana. **La empresa que busca su primer ingeniero de
seguridad es tu cliente ideal**: tiene el dinero aprobado y no tiene a nadie.

### Grupos

Busca grupos de *SaaS Founders*, *CTO*, *Startup CTO* y únete a tres o cuatro.
No publiques: **responde preguntas de seguridad durante un mes**. Llegan solos.

---

## Rutina diaria: 20 minutos

| Minuto | Qué |
|---|---|
| 0–8 | Reddit: dos frases, `sort=new`, leer y responder donde aportes |
| 8–15 | LinkedIn: publicaciones de la última semana, comentar con sustancia |
| 15–20 | Los que te interesaron de verdad: al pipeline |

```bash
python run.py pipeline add <lo-que-sea> --contacto ... --canal reddit --nota "queja publica SOC 2"
```

**Veinte minutos al día, todos los días.** Es lo único de todo el sistema que
no se puede automatizar, y es lo que más produce.

---

## Qué hacer con lo que encuentres

El mensaje no es el de prospección fría. Es el **#4 de
`templates/mensaje-lanzamiento.md`**: le ofreces gratis los tres puntos que ves
en su repo, sin vender nada.

```
Vi lo que escribiste sobre SOC 2. Justo trabajo en eso.
No te vendo nada por este mensaje: te mando gratis los 3 puntos que veo
en [su repo] para que veas el formato.
```

Valor primero. El que recibe algo útil responde; el que recibe una oferta, no.

---

## Errores

1. **Vender en el hilo.** Te borran y quedas marcado.
2. **Buscar sin filtrar por fecha.** Una queja de hace seis meses no vale nada.
3. **Perseguir a otros consultores de seguridad.** En r/cybersecurity hay más
   colegas que clientes. Esos pueden ser **socios**, no prospectos.
4. **Responder con un enlace.** En Reddit y LinkedIn los enlaces externos
   hunden el alcance. Escribe la respuesta en el propio comentario.
5. **No anotar nada.** Si no va al pipeline, en 48 horas se te olvidó.

---

## La métrica

**Mensajes enviados y respuestas.** Nada más.

Si en una semana enviaste 10 mensajes a gente que se quejó y no tuviste ni una
respuesta, el problema es el mensaje: cámbialo y vuelve a mandar 10. Si no
enviaste ninguno, el problema no es el mensaje.
