# El análisis público: credibilidad sin clientes

Es la vía más rápida para tener credenciales cuando no tienes clientes. Y no
cuesta dinero: cuesta un sábado.

```bash
python run.py analisis owner/repo                    # borrador del análisis
python run.py analisis owner/repo --anonimo          # sin nombrar el proyecto
python run.py analisis owner/repo --linkedin         # post nativo para LinkedIn
python run.py analisis owner/repo > out/analisis.md  # a editar
```

---

## Qué es (y qué no es)

| Es | No es |
|---|---|
| Una demostración de criterio | Una demostración de que eres listo |
| Una lectura de ausencias de control | Un listado de fallos explotables |
| Un recurso que el lector puede aplicar hoy | Una crítica a un equipo |
| Escrito como un colega que ayuda | Escrito como un fiscal que acusa |

**El objetivo exacto:** que el lector llegue al final pensando *"este sabe
exactamente qué me falta y cómo arreglarlo"*, no *"qué listo es"*. El segundo
admira; el primero contrata.

---

## Lo que NUNCA publicas

Esto no es negociable, y es lo que separa un análisis profesional de una
denuncia que te puede costar un problema legal y la reputación:

1. **Nada explotable.** Ni cómo reproducirlo, ni el endpoint, ni el parámetro.
2. **Ninguna ruta concreta de posible credencial.** Dices "hay 3 archivos con
   nombre de credencial en el árbol", no "el `.env` en `config/prod/`".
3. **Nada que humille.** Ni "increíble que no tengan X", ni ironía, ni
   comparaciones despectivas.
4. **Nada de datos de terceros.** Si ves algo que afecte a clientes, usuarios o
   pacientes del proyecto: no lo mencionas, se lo reportas al proyecto en privado.
5. **Ningún nombre de persona.** El análisis es del repositorio, no del
   desarrollador que cometió el error.

El generador (`app/analisis.py`) ya aplica las reglas 1, 2 y 5 por construcción.
Las 3 y 4 dependen de tu edición: **lee el borrador antes de publicarlo.**

---

## Protocolo antes de publicar

| Paso | Qué haces |
|---|---|
| 1 | Genera el borrador y edítalo |
| 2 | **Avisa al proyecto.** Un correo corto: "hice un análisis público de tu repo, va en tono constructivo, te lo mando antes por si quieres corregir algo" |
| 3 | Espera 48–72 h |
| 4 | Publica. Si te piden que no, no publiques: no vale la pena |
| 5 | Si hay algo sensible real, no lo publiques: repórtalo en privado y da 90 días |

Avisar antes no es cortesía: es **estrategia**. Un proyecto al que avisas
compartirá tu análisis. Uno al que sorprendes se lo tomará como un ataque y te
va a discutir públicamente. Lo primero te da alcance; lo segundo te lo quita.

---

## Estructura que funciona

```
1. Gancho            el dato que sorprende ("ninguno es una vulnerabilidad grave")
2. Metodología       qué revisaste y qué NO hiciste (desarma la defensiva)
3. Los hallazgos     cada uno con su control y su arreglo ejecutable
4. El patrón         la generalización: por qué le importa al lector
5. Una tarde         el plan mínimo en 4 pasos
6. CTA               suave, sin vender
```

**La sección 4 es la que convierte.** Los hallazgos demuestran que sabes buscar;
el patrón demuestra que sabes pensar. Y se contrata al que piensa.

**La sección 5 es la que se comparte.** La gente comparte lo que puede aplicar
hoy, no lo que le hace sentir mal.

---

## Distribución

| Canal | Formato | Nota |
|---|---|---|
| **LinkedIn** | Post nativo, texto completo | Los enlaces externos pierden alcance: pega el análisis entero |
| **Blog propio** | Versión larga con código | Tu activo permanente. El post de LinkedIn manda aquí |
| **X** | Hilo de 6–8 tuits | Uno por hallazgo, con el arreglo |
| **Indie Hackers** | Post con el ángulo de fundador | Bien recibido si no vendes |
| **Reddit** | Comentario útil, con enlace solo si te lo piden | Si llegas vendiendo, te borran |

El orden importa: **publicas el blog primero** (para tener el activo), y después
el post de LinkedIn que manda al blog en el primer comentario.

---

## El CTA (y cómo no arruinarlo)

Mal CTA: *"¿Necesitas ayuda con esto? Contrátame."* — mata el alcance y la
confianza que acabas de construir.

Buen CTA:

> Hago esto por encargo para equipos que se preparan para SOC 2. Si estás en esa
> situación y quieres ver cómo queda el tuyo, escríbeme y te mando el mismo
> análisis de tu repo.

La diferencia: el bueno **da algo** (el análisis de su repo), no **pide algo**.
Y el que responde a ese CTA llega pre-calificado y con interés real.

---

## La serie de 3

Un análisis aislado se olvida. Tres seguidos construyen una reputación.

| # | Análisis | Ángulo |
|---|---|---|
| 1 | Un repo de tu stack | Los controles básicos que faltan |
| 2 | Un repo que SÍ tiene seguridad resuelta | "Qué hacen bien y por qué funciona" |
| 3 | Tu propio repositorio | El más valioso: te pones del lado del examinado |

**El tercero es el que más confianza genera.** Analizarte en público, con tus
propios huecos a la vista, dice más de tu honestidad que veinte análisis ajenos.
Y desarma la objeción obvia: "fácil es criticar el repo de otro".

---

## Qué hacer con quien te discuta

Va a pasar. Alguien dirá "eso no es una vulnerabilidad" o "estás exagerando".

1. **No te defiendas: agradece y matiza.** "Tienes razón en que no es explotable;
   el punto es que no se puede evidenciar el control, que es distinto."
2. **Corrige en público si te equivocaste.** Un análisis con una corrección
   honesta al pie tiene más credibilidad que uno perfecto.
3. **Nunca respondas con sarcasmo.** El que discute te está dando alcance; no
   conviertas eso en una pelea.

---

## Métricas

| Métrica | Qué indica |
|---|---|
| Guardados | Mucho mejor que likes: alguien lo quiere para después |
| Comentarios de gente de producto | Los que importan. Los de otros técnicos halagan pero no contratan |
| Mensajes privados en 72 h | La métrica real |
| Visitas al blog desde LinkedIn | Si funciona, publicas el siguiente |

**Un análisis que genera dos conversaciones privadas vale más que uno con mil
likes.** No te dejes distraer por el número grande.

---

## Lo que esto hace por el negocio

En orden de valor:

1. **Te da algo que mostrar** cuando no tienes clientes. Tu respuesta a "¿tienes
   ejemplos?" deja de ser una excusa.
2. **Pre-califica prospectos.** El que te escribe ya vio cómo trabajas y cómo
   piensas: llega a la llamada convencido.
3. **Es el contenido del nivel 1 de prospección.** Publicas y contestas: la misma
   hora de trabajo produce credibilidad y prospectos.
4. **Sostiene el análisis público como hábito.** Cada dos semanas, uno nuevo. A
   los seis meses tienes doce piezas que trabajan por ti.

---

## Regla final

**Publica para ayudar, no para demostrar.** Se nota la diferencia en la primera
frase, y el lector decide en esa frase si confía en ti o no.
