# Evidencia 2 · Recomendación de documentos

Cada caso se ejecutó con `Recomendador.relacionados(id, k=3)`. Los documentos esperados se anotaron a mano antes de correr la prueba (son los que un ingeniero consideraría útiles al leer el documento de origen).

### RI01 · Postmortem: caída del servicio de pagos
*Caída de pagos: otros incidentes de pagos o de certificados vencidos, y la guía del servicio*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [RI08] Postmortem: cobro duplicado a suscriptores | 0.152 | Premium y suscripciones, Servicio de pagos | sí |
| 2 | [NUEVO02] Postmortem: interrupción de descargas sin conexión | 0.151 | Monitoreo y alertas | no |
| 3 | [DT01] Guía de despliegue del servicio de pagos | 0.103 | Monitoreo y alertas, Servicio de pagos | sí |

### RI02 · Postmortem: errores al iniciar sesión en la app móvil
*Error de login: arquitectura de autenticación, manual de alertas de cuentas, otro error tras despliegue*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [NUEVO02] Postmortem: interrupción de descargas sin conexión | 0.132 | Error introducido en un despliegue, Reversión de cambios | sí |
| 2 | [DT02] Arquitectura del servicio de autenticación | 0.11 | Servicio de autenticación | sí |
| 3 | [DT01] Guía de despliegue del servicio de pagos | 0.094 | Pruebas automatizadas, Reversión de cambios | no |

### EX04 · Experimento con recomendaciones de podcasts
*Experimento de podcasts: investigación de hábitos de podcasts y satisfacción con recomendaciones*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [IU02] Investigación sobre hábitos de escucha de podcasts | 0.172 | Podcasts, Sistema de recomendaciones | sí |
| 2 | [EX02] Experimento: nuevo diseño de la pantalla de inicio | 0.148 | Playlists | no |
| 3 | [NUEVO03] Resultado de prueba A/B: botón de mezcla aleatoria | 0.084 | — | no |

### IU07 · Encuesta de satisfacción con las recomendaciones
*Satisfacción con recomendaciones: modelo de datos de recomendaciones y estudios relacionados*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [IU04] Entrevistas con artistas emergentes | 0.072 | Artistas, Sistema de recomendaciones | sí |
| 2 | [IU02] Investigación sobre hábitos de escucha de podcasts | 0.066 | Sistema de recomendaciones | no |
| 3 | [IU01] Estudio: por qué los usuarios cancelan Premium | 0.06 | — | no |

### PO01 · Política de privacidad y protección de datos de usuarios
*Privacidad: política de datos para modelos, retención de registros, uso de IA*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [NUEVO04] Política de uso de datos para entrenar modelos | 0.168 | Datos personales, Protección de datos (reglamento europeo) | sí |
| 2 | [PO02] Política de seguridad de la información | 0.105 | — | no |
| 3 | [PO06] Política de licencias y derechos de autor del catálogo | 0.103 | — | no |

### RI07 · Reporte de incidente: caída del buscador
*Caída del buscador: guía del servicio de búsqueda y prueba del orden de resultados*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [NUEVO01] Guía de instalación del servicio de búsqueda | 0.118 | Servicio de búsqueda | sí |
| 2 | [RI03] Reporte de incidente: latencia alta en la reproducción | 0.089 | — | no |
| 3 | [RI02] Postmortem: errores al iniciar sesión en la app móvil | 0.08 | Error introducido en un despliegue, Reversión de cambios | no |

### IU01 · Estudio: por qué los usuarios cancelan Premium
*Cancelaciones de Premium: experimentos de renovación, prueba gratuita y precio*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [EX06] Experimento: precio del plan familiar | 0.1 | Premium y suscripciones | sí |
| 2 | [NUEVO05] Hallazgos de entrevistas con usuarios de audiolibros | 0.092 | — | no |
| 3 | [IU08] Estudio etnográfico: la música en el trabajo | 0.067 | — | no |

### NUEVO06 · Manual de respuesta ante alertas del servicio de cuentas
*Alertas de cuentas: manual de monitoreo, arquitectura de autenticación, incidente de login*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [DT05] Manual de monitoreo y alertas de la plataforma | 0.285 | Ingeniero de guardia, Monitoreo y alertas | sí |
| 2 | [DT02] Arquitectura del servicio de autenticación | 0.15 | Servicio de autenticación, Servicio de cuentas | sí |
| 3 | [DT07] Procedimiento de migración de base de datos | 0.067 | Servicio de cuentas | no |

### DT01 · Guía de despliegue del servicio de pagos
*Despliegue de pagos: incidentes del servicio de pagos y otro procedimiento con reversión*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [DT07] Procedimiento de migración de base de datos | 0.129 | Reversión de cambios | sí |
| 2 | [NUEVO01] Guía de instalación del servicio de búsqueda | 0.116 | Contenedores, Kubernetes | no |
| 3 | [RI01] Postmortem: caída del servicio de pagos | 0.103 | Monitoreo y alertas, Servicio de pagos | sí |

### IU02 · Investigación sobre hábitos de escucha de podcasts
*Hábitos de podcasts: experimento de podcasts y entrevistas de audiolibros*

| # | Recomendado | Similitud | Conceptos en común | ¿Esperado? |
|---|---|---|---|---|
| 1 | [EX04] Experimento con recomendaciones de podcasts | 0.172 | Podcasts, Sistema de recomendaciones | sí |
| 2 | [IU07] Encuesta de satisfacción con las recomendaciones | 0.066 | Sistema de recomendaciones | no |
| 3 | [IU06] Investigación sobre el uso en América Latina | 0.063 | — | no |

## Recomendaciones por historial de búsqueda

**Historial:** caída del servicio de pagos → certificado vencido

| Recomendado | Motivo | ¿Esperado? |
|---|---|---|
| [RI01] Postmortem: caída del servicio de pagos | porque buscaste: "certificado vencido" | sí |
| [DT01] Guía de despliegue del servicio de pagos | porque buscaste: "caída del servicio de pagos" | sí |
| [RI08] Postmortem: cobro duplicado a suscriptores | porque buscaste: "caída del servicio de pagos" | sí |

**Historial:** podcasts → recomendaciones semanales

| Recomendado | Motivo | ¿Esperado? |
|---|---|---|
| [IU07] Encuesta de satisfacción con las recomendaciones | porque buscaste: "recomendaciones semanales" | sí |
| [EX04] Experimento con recomendaciones de podcasts | porque buscaste: "podcasts" | sí |
| [IU02] Investigación sobre hábitos de escucha de podcasts | porque buscaste: "podcasts" | sí |

**Historial:** datos personales → entrenar modelos

| Recomendado | Motivo | ¿Esperado? |
|---|---|---|
| [NUEVO04] Política de uso de datos para entrenar modelos | porque buscaste: "entrenar modelos" | sí |
| [DT06] Modelo de datos del sistema de recomendaciones | porque buscaste: "entrenar modelos" | sí |
| [PO01] Política de privacidad y protección de datos de usuarios | porque buscaste: "datos personales" | sí |

## Resumen

| Métrica | Valor |
|---|---|
| Precisión@3 (por similitud) | 46.7% |
| Recall@3 (por similitud) | 51.7% |
| Casos con al menos una recomendación esperada | 100.0% |
| Precisión@3 (por historial) | 100.0% |