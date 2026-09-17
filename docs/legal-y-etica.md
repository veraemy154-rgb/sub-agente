# Linea roja: legal y etica

**Esto no es un descargo de responsabilidad. Es la condicion para que el negocio
exista.** Un solo paso en falso aqui no te cuesta un cliente: te cuesta el negocio,
y posiblemente mas.

---

## Lo que SI hacemos

- Leer **informacion publica**: repos abiertos en GitHub, documentacion publica, certificados, cabeceras HTTP de sitios publicos.
- Observar de forma **pasiva y de solo lectura**. El scanner de este repo no descarga contenidos de archivos sospechosos: mira nombres de archivo y metadatos.
- Emitir un **informe** sobre esa informacion publica.
- Contactar al propietario para **ofrecer ayuda**.

## Lo que NO hacemos nunca

- Escanear, probar o explotar un sistema **sin autorizacion escrita previa**.
- Descargar, copiar o guardar archivos que parezcan contener credenciales. Si encontramos uno, lo reportamos: no lo abrimos.
- Autenticarnos, crear cuentas, o usar credenciales ajenas para "verificar" algo.
- Publicar un hallazgo, aunque sea de un repo publico, antes de que el propietario tenga un plazo razonable para corregirlo.
- Amenazar, insinuar un pago para "no divulgar", o fijar una fecha de publicacion como presion comercial. Eso es extorsion, no consultoria.
- Tocar infraestructura de terceros que aparezca referenciada en el repo (bases de datos, buckets, endpoints internos).

---

## Marco legal (orientativo, no es asesoria legal)

Casi todas las jurisdicciones penalizan el **acceso no autorizado**, con independencia
de la intencion. El "yo lo hacia para ayudar" no es defensa.

- **Venezuela:** Ley Especial contra los Delitos Informaticos tipifica el acceso indebido, la sabotaje y la revelacion indebida de informacion. Aplica aunque el sistema sea tecnicamente alcanzable.
- **Estados Unidos:** Computer Fraud and Abuse Act (CFAA) y sus equivalentes estatales.
- **Union Europea / Espana:** Convenio de Budapest; en Espana, art. 197 y 264 del Codigo Penal.
- **Clientes internacionales:** si vendes a una empresa de EE. UU. o la UE, su contrato y su jurisdiccion te alcanzan aunque tu operes desde otro pais.

**Si vas a vender en serio, contrata una hora con un abogado local y haz revisar
tu SOW.** Una hora de abogado cuesta menos que un problema.

---

## La regla de los tres documentos

Ningun trabajo de remediación empieza sin estos tres:

1. **Autorizacion de pruebas / SOW** — firmado, con alcance, sistemas incluidos y excluidos, ventana temporal y persona de contacto. Plantilla: `templates/sow-autorizacion.md`.
2. **Acuerdo de confidencialidad (NDA)** — vas a ver codigo y arquitectura.
3. **Regla de divulgacion acordada** — quien dice que, cuando, y con que plazo de gracia (90 dias es el estandar razonable).

Si un cliente quiere que empieces "rapido y sin papeles", esa es la senal mas clara
de que ese cliente te va a traer problemas. No empieces.

---

## El primer mensaje: protocolo

El mayor riesgo legal y etico esta en el cold outreach, porque es donde mas
tentacion hay de "demostrar que encontre algo".

**Se menciona la ausencia de un control. Nunca un hallazgo explotable.**

| Correcto | Incorrecto |
|---|---|
| "El pipeline de CI no incluye escaneo de vulnerabilidades en dependencias" | "Encontre una inyeccion SQL en /api/login" |
| "La rama principal acepta pushes directos" | "Puedo extraer la base de usuarios" |
| "No hay politica publica de divulgacion" | "Tienen una clave AWS expuesta en config.py:456" |

Razones: el primer grupo son hechos publicos y verificables, no ponen en riesgo a
nadie, y siguen generando suficiente curiosidad para que respondan. El segundo
grupo es entregar valor gratis *y* asumir riesgo legal. El codigo en
`app/outreach.py` sigue esta regla y solo usa el gancho correspondiente a
ausencia de control.

---

## Si encuentras algo grave en un repo publico

1. **No lo descargues, no lo explotes, no lo compartas.**
2. Busca `SECURITY.md` o la politica de divulgacion y siguela.
3. Si no hay politica, contacta por un canal privado con un aviso de buena fe: que viste, donde, y ofrece ayuda. Sin plazos de publicacion.
4. Da un plazo razonable (90 dias) antes de cualquier mencion publica.
5. Si hay datos de terceros expuestos (clientes, pacientes, menores), no los toques: notifica y apartate.

---

## Reputacion

En este oficio la reputacion es el activo. Un informe honesto, un hallazgo que no
se exagera, un "esto no es un problema" dicho a tiempo: eso es lo que hace que te
recomienden. El tecnico que infla severidades para vender trabaja una vez.
