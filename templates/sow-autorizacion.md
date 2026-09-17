# Autorizacion de evaluacion de seguridad y orden de trabajo

> Plantilla. Completar, firmar ambas partes y **no empezar sin esto firmado**.
> Revisar con un abogado local antes del primer uso comercial.

---

**Documento:** SOW-2026-___
**Fecha:** ______________

## 1. Partes

**Proveedor:** _________________________________ (en adelante, "el Proveedor")
C.I. / RIF: __________________ · Correo: __________________

**Cliente:** _________________________________ (en adelante, "el Cliente")
Representante legal: __________________ · Cargo: __________________

## 2. Autorizacion expresa

El Cliente, en su calidad de propietario legitimo de los sistemas descritos en la
seccion 3, **autoriza expresamente al Proveedor** a realizar las actividades de
evaluacion de seguridad detalladas en este documento, sobre los sistemas incluidos
en el alcance y durante la vigencia aqui establecida.

El Cliente declara que tiene facultad para otorgar esta autorizacion y que los
sistemas objeto de la evaluacion son de su propiedad o se encuentran bajo su
responsabilidad operativa.

## 3. Alcance

### 3.1 Sistemas INCLUIDOS

| Repositorio / sistema | URL o identificador | Tipo de acceso |
|---|---|---|
| | | |
| | | |

### 3.2 Sistemas EXCLUIDOS (el Proveedor no tocara estos bajo ninguna circunstancia)

- _________________________________
- Infraestructura, endpoints, bases de datos o servicios de terceros referenciados en el codigo.
- Cualquier sistema no listado expresamente en 3.1.

### 3.3 Actividades autorizadas

- [ ] Revision de codigo fuente (estatica / lectura)
- [ ] Analisis de dependencias y busqueda de vulnerabilidades conocidas
- [ ] Revision de configuracion de CI/CD y de control de acceso al repositorio
- [ ] Analisis de configuracion de infraestructura como codigo
- [ ] Pruebas de seguridad sobre entorno de **staging / preproduccion** (si aplica)
- [ ] Pruebas de seguridad sobre **produccion** — solo si se marca expresamente: [ ] SI [ ] NO

### 3.4 Actividades NO autorizadas

Ingenieria social, ataques de denegacion de servicio, pruebas fisicas, acceso a
datos de terceros, y cualquier actividad no listada en 3.3.

## 4. Vigencia

Desde __________ hasta __________ (maximo recomendado: 30 dias).
Toda actividad fuera de este periodo requiere nueva autorizacion por escrito.

## 5. Contactos y escalamiento

| Rol | Nombre | Telefono | Correo |
|---|---|---|---|
| Contacto tecnico del Cliente | | | |
| Contacto de seguridad 24/7 | | | |
| Contacto del Proveedor | | | |

Ante cualquier impacto no intencional sobre disponibilidad o datos, el Proveedor
notificara al contacto de seguridad en un plazo maximo de **2 horas**.

## 6. Manejo de informacion y confidencialidad

- El Proveedor firmara el NDA adjunto como Anexo A.
- Los hallazgos se entregan unicamente a los contactos listados en la seccion 5.
- El Proveedor no conservara copias de codigo ni de datos del Cliente una vez
  finalizado el trabajo, y lo acreditara por escrito.
- El Proveedor no divulgara, publicara ni mencionara ningun hallazgo a terceros
  sin autorizacion escrita del Cliente.

## 7. Divulgacion

Las partes acuerdan un periodo de gracia de **90 dias** desde la entrega del
informe final, durante el cual ninguna de las partes hara publica informacion
sobre los hallazgos. Transcurrido ese plazo, el Proveedor podra mencionar el
trabajo de forma generica ("auditoria de seguridad a empresa del sector X")
solo con autorizacion escrita del Cliente.

## 8. Entregables y condiciones comerciales

| Entregable | Fecha | Monto (USD) |
|---|---|---|
| Diagnostico de exposicion + plan priorizado | | |
| Implementacion de remediaciones | | |
| Informe mensual de evidencia (si hay retainer) | | |

**Condiciones de pago:** 50 % a la firma, 50 % contra entrega/merge.
**Moneda:** dolares estadounidenses (USD).

## 9. Limitaciones

El Proveedor ejecutara las actividades con diligencia profesional, pero **no
garantiza** la ausencia total de vulnerabilidades. La seguridad es un proceso,
no un estado. La responsabilidad del Proveedor se limita al monto efectivamente
facturado por este trabajo.

El Proveedor no sera responsable de interrupciones derivadas de pruebas
realizadas dentro del alcance autorizado.

## 10. Ley aplicable

Este documento se rige por la ley de __________________. Las partes se someten a
los tribunales de __________________.

---

**Firmas**

Proveedor: __________________________  Fecha: __________

Cliente: ____________________________  Fecha: __________

---

### Checklist antes de empezar

- [ ] Seccion 3.1 completa y sin ambiguedades ("todo el repo X", no "nuestros sistemas")
- [ ] Seccion 3.2 con exclusiones explicitas
- [ ] NDA firmado (Anexo A)
- [ ] Contacto de seguridad 24/7 con telefono real
- [ ] 50 % del pago recibido
- [ ] Si tocan produccion, regla adicional: nunca en horario pico y siempre con ventana acordada
