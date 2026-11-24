# Evidencia 5 · Precisión y recall de la búsqueda (la usa también el chatbot)

Datos de evaluación: 15 preguntas escritas para la prueba. Para cada una se anotó qué documentos la responden. Se toman los 3 primeros resultados (k = 3).

| Consulta | Relevantes | Devueltos | P@3 | R@3 | ¿1.º correcto? |
|---|---|---|---|---|---|
| ¿Qué pasó con los cobros duplicados a los suscriptores? | RI08 | RI08 | 33.3% | 100.0% | sí |
| ¿Cómo despliego una nueva versión de un servicio en Kubernetes? | DT01, NUEVO01 | DT01, NUEVO01, DT07 | 66.7% | 100.0% | sí |
| ¿Por qué los usuarios cancelan su suscripción Premium? | IU01 | IU01, RI08, EX01 | 33.3% | 100.0% | sí |
| Reglas para usar datos personales al entrenar modelos de inteligencia artificial | NUEVO04, PO01, PO03 | PO03, NUEVO04, DT06 | 66.7% | 66.7% | sí |
| ¿Qué hago si se activa una alerta en un servicio? | DT05, NUEVO06 | NUEVO06, DT05, RI01 | 66.7% | 100.0% | sí |
| ¿Qué incidentes fueron causados por un certificado o una credencial vencida? | RI01, RI05 | RI05, RI01 | 66.7% | 100.0% | sí |
| Resultados sobre el consumo de podcasts | EX04, IU02 | EX04, IU02, EX05 | 66.7% | 100.0% | sí |
| ¿Quién aprueba los permisos para entrar a los sistemas internos? | PO07 | PO07 | 33.3% | 100.0% | sí |
| Problemas de accesibilidad con lector de pantalla | IU05 | IU05, EX08, EX02 | 33.3% | 100.0% | sí |
| ¿Por qué falló el inicio de sesión en la app móvil? | RI02 | RI02, EX02 | 33.3% | 100.0% | sí |
| ¿Cuánto tiempo se guardan los registros de actividad de los usuarios? | PO04 | PO04, DT07, NUEVO06 | 33.3% | 100.0% | sí |
| ¿Conviene bajar el precio del plan familiar? | EX06 | EX06, IU01 | 33.3% | 100.0% | sí |
| ¿Cómo escuchan música los usuarios en México y Brasil? | IU06 | IU06, EX04, NUEVO05 | 33.3% | 100.0% | sí |
| Pasos para migrar la base de datos del servicio de cuentas | DT07 | DT07, DT02, NUEVO06 | 33.3% | 100.0% | sí |
| ¿Qué se aprendió cuando la búsqueda devolvió resultados vacíos? | RI07 | RI07, EX05, NUEVO01 | 33.3% | 100.0% | sí |

| Métrica | Índice mixto (final) | Solo palabras (avance) |
|---|---|---|
| Precisión@3 | 44.4% | 44.4% |
| Precisión sobre resultados mostrados | 57.8% | 58.9% |
| Recall@3 | 97.8% | 97.8% |
| Primer resultado correcto | 100.0% | 100.0% |
| MRR | 1.000 | 1.000 |

Nota: como la mayoría de las preguntas tiene uno o dos documentos relevantes, la precisión@3 máxima posible es 46.7%.