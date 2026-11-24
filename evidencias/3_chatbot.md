# Evidencia 3 · Chatbot

Cada respuesta se generó con `Chatbot.responder(pregunta)`. El texto citado sale de los documentos; la tabla muestra los documentos recuperados y su similitud.

## Pregunta: ¿Qué pasó con los cobros duplicados a los suscriptores?
Tipo de intención detectada: `contenido`

Según **[RI08] Postmortem: cobro duplicado a suscriptores** (Reporte de incidente, similitud 0.34):

> Un reintento automático en el servicio de pagos generó cobros duplicados a un grupo de suscriptores Premium. Se reembolsó a los usuarios afectados, se corrigió la lógica de reintentos con un identificador único por transacción y se agregaron pruebas que simulan fallas del proveedor.

*Contexto del grafo:* este tipo de documento lo genera **Ingeniería de plataforma** y lo consultan ingeniería y liderazgo técnico. Conceptos relacionados: Servicio de pagos, Premium y suscripciones, Pruebas automatizadas.

| Documento recuperado | Similitud |
|---|---|
| [RI08] Postmortem: cobro duplicado a suscriptores | 0.341 |

## Pregunta: ¿Cómo despliego una nueva versión de un servicio en Kubernetes?
Tipo de intención detectada: `contenido`

Según **[DT01] Guía de despliegue del servicio de pagos** (Documentación técnica, similitud 0.27):

> Esta guía explica cómo desplegar una nueva versión del servicio de pagos. Después se actualiza el manifiesto de Kubernetes y se monitorean las métricas de latencia durante treinta minutos.

*Contexto del grafo:* este tipo de documento lo genera **Ingeniería de plataforma** y lo consultan ingenieros de otros squads y personal de guardia. Conceptos relacionados: Servicio de pagos, Kubernetes, Contenedores, Pruebas automatizadas, Reversión de cambios, Monitoreo y alertas.

| Documento recuperado | Similitud |
|---|---|
| [DT01] Guía de despliegue del servicio de pagos | 0.274 |
| [NUEVO01] Guía de instalación del servicio de búsqueda | 0.13 |
| [DT07] Procedimiento de migración de base de datos | 0.108 |

## Pregunta: ¿Qué hago si se activa una alerta en un servicio?
Tipo de intención detectada: `contenido`

Según **[NUEVO06] Manual de respuesta ante alertas del servicio de cuentas** (Documentación técnica, similitud 0.31):

> Cuando se activa una alerta del servicio de cuentas, el ingeniero de guardia debe revisar el tablero de monitoreo, consultar los registros y verificar las dependencias con el servicio de autenticación. El manual indica los umbrales de error y a quién escalar la alerta.

*Contexto del grafo:* este tipo de documento lo genera **Ingeniería de plataforma** y lo consultan ingenieros de otros squads y personal de guardia. Conceptos relacionados: Servicio de autenticación, Servicio de cuentas, Ingeniero de guardia, Monitoreo y alertas.

| Documento recuperado | Similitud |
|---|---|
| [NUEVO06] Manual de respuesta ante alertas del servicio de cuentas | 0.306 |
| [DT05] Manual de monitoreo y alertas de la plataforma | 0.115 |
| [RI01] Postmortem: caída del servicio de pagos | 0.092 |

## Pregunta: ¿Qué incidentes fueron causados por un certificado vencido?
Tipo de intención detectada: `contenido`

Según **[RI01] Postmortem: caída del servicio de pagos** (Reporte de incidente, similitud 0.24):

> La causa raíz fue un certificado vencido en la conexión con el proveedor de pagos. Como acciones correctivas se automatizó la renovación de certificados y se agregó una alerta preventiva.

*Contexto del grafo:* este tipo de documento lo genera **Ingeniería de plataforma** y lo consultan ingeniería y liderazgo técnico. Conceptos relacionados: Servicio de pagos, Premium y suscripciones, Usuarios de América Latina, Credencial o certificado vencido, Monitoreo y alertas.

| Documento recuperado | Similitud |
|---|---|
| [RI01] Postmortem: caída del servicio de pagos | 0.236 |
| [RI05] Reporte de incidente: falla en notificaciones push | 0.055 |

## Pregunta: ¿Puedo trabajar desde otro país?
Tipo de intención detectada: `contenido`

Según **[PO08] Política de trabajo remoto y uso de equipos** (Política interna, similitud 0.26):

> Los colaboradores pueden trabajar de forma remota siempre que usen equipos administrados por la empresa y una conexión segura mediante la red privada virtual. La política define los horarios de colaboración, el cuidado de los equipos asignados y las reglas para trabajar desde otro país por periodos cortos.

*Contexto del grafo:* este tipo de documento lo genera **Legal y seguridad** y lo consultan todos los colaboradores. Conceptos relacionados: Conducta y trabajo remoto.

| Documento recuperado | Similitud |
|---|---|
| [PO08] Política de trabajo remoto y uso de equipos | 0.265 |

## Pregunta: muéstrame los postmortems
Tipo de intención detectada: `lista_categoria`

Estos son los documentos de **Reporte de incidente** (9):
- [RI01] Postmortem: caída del servicio de pagos
- [RI02] Postmortem: errores al iniciar sesión en la app móvil
- [RI03] Reporte de incidente: latencia alta en la reproducción
- [RI04] Postmortem: playlists que desaparecieron
- [RI05] Reporte de incidente: falla en notificaciones push
- [RI06] Postmortem: error en el conteo de reproducciones
- [RI07] Reporte de incidente: caída del buscador
- [RI08] Postmortem: cobro duplicado a suscriptores
- [NUEVO02] Postmortem: interrupción de descargas sin conexión

## Pregunta: qué documentos hay sobre Servicio de pagos
Tipo de intención detectada: `lista_concepto`

Según el grafo de conocimiento, **4 documentos** mencionan *Servicio de pagos*:
- [DT01] Guía de despliegue del servicio de pagos · Documentación técnica
- [EX01] Resultado de prueba A/B: recordatorio de renovación · Resultado de experimento A/B
- [RI01] Postmortem: caída del servicio de pagos · Reporte de incidente
- [RI08] Postmortem: cobro duplicado a suscriptores · Reporte de incidente

## Pregunta: ¿Cuál es la receta de la paella?
Tipo de intención detectada: `sin_resultado`

No encontré documentos que respondan esa pregunta. Prueba con otras palabras (por ejemplo, el nombre del servicio o de la funcionalidad).
