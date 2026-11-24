"""Evaluación del sistema: clasificación, recuperación (búsqueda/chatbot) y recomendaciones.

Los conjuntos de prueba de recuperación y recomendación se definieron a mano:
para cada consulta (o documento) se anotó qué documentos del repositorio la
responden. Esa anotación es el "juicio de relevancia" contra el que se mide.
"""
import numpy as np

from .buscador import Indice

# consulta -> documentos que la responden
CONSULTAS_PRUEBA = [
    ("¿Qué pasó con los cobros duplicados a los suscriptores?", {"RI08"}),
    ("¿Cómo despliego una nueva versión de un servicio en Kubernetes?", {"DT01", "NUEVO01"}),
    ("¿Por qué los usuarios cancelan su suscripción Premium?", {"IU01"}),
    ("Reglas para usar datos personales al entrenar modelos de inteligencia artificial", {"NUEVO04", "PO03", "PO01"}),
    ("¿Qué hago si se activa una alerta en un servicio?", {"NUEVO06", "DT05"}),
    ("¿Qué incidentes fueron causados por un certificado o una credencial vencida?", {"RI01", "RI05"}),
    ("Resultados sobre el consumo de podcasts", {"EX04", "IU02"}),
    ("¿Quién aprueba los permisos para entrar a los sistemas internos?", {"PO07"}),
    ("Problemas de accesibilidad con lector de pantalla", {"IU05"}),
    ("¿Por qué falló el inicio de sesión en la app móvil?", {"RI02"}),
    ("¿Cuánto tiempo se guardan los registros de actividad de los usuarios?", {"PO04"}),
    ("¿Conviene bajar el precio del plan familiar?", {"EX06"}),
    ("¿Cómo escuchan música los usuarios en México y Brasil?", {"IU06"}),
    ("Pasos para migrar la base de datos del servicio de cuentas", {"DT07"}),
    ("¿Qué se aprendió cuando la búsqueda devolvió resultados vacíos?", {"RI07"}),
]

# documento -> documentos que un ingeniero consideraría útiles al leerlo
RECOMENDACIONES_PRUEBA = [
    ("RI01", {"RI08", "RI05", "DT01"}, "Caída de pagos: otros incidentes de pagos o de certificados vencidos, y la guía del servicio"),
    ("RI02", {"DT02", "NUEVO06", "NUEVO02"}, "Error de login: arquitectura de autenticación, manual de alertas de cuentas, otro error tras despliegue"),
    ("EX04", {"IU02", "IU07"}, "Experimento de podcasts: investigación de hábitos de podcasts y satisfacción con recomendaciones"),
    ("IU07", {"DT06", "EX04", "IU04"}, "Satisfacción con recomendaciones: modelo de datos de recomendaciones y estudios relacionados"),
    ("PO01", {"NUEVO04", "PO04", "PO03"}, "Privacidad: política de datos para modelos, retención de registros, uso de IA"),
    ("RI07", {"NUEVO01", "EX05"}, "Caída del buscador: guía del servicio de búsqueda y prueba del orden de resultados"),
    ("IU01", {"EX01", "EX03", "EX06"}, "Cancelaciones de Premium: experimentos de renovación, prueba gratuita y precio"),
    ("NUEVO06", {"DT05", "DT02", "RI02"}, "Alertas de cuentas: manual de monitoreo, arquitectura de autenticación, incidente de login"),
    ("DT01", {"RI01", "RI08", "DT07"}, "Despliegue de pagos: incidentes del servicio de pagos y otro procedimiento con reversión"),
    ("IU02", {"EX04", "NUEVO05"}, "Hábitos de podcasts: experimento de podcasts y entrevistas de audiolibros"),
]

# historial de consultas -> documentos que deberían aparecer como sugerencia
HISTORIALES_PRUEBA = [
    (["caída del servicio de pagos", "certificado vencido"], {"RI01", "RI05", "DT01", "RI08"}),
    (["podcasts", "recomendaciones semanales"], {"IU02", "EX04", "IU07", "DT06"}),
    (["datos personales", "entrenar modelos"], {"NUEVO04", "PO01", "PO03", "DT06"}),
]


def evaluar_recuperacion(documentos, k=3, modo="mixto"):
    idx = Indice(documentos, modo=modo)
    filas = []
    for consulta, relevantes in CONSULTAS_PRUEBA:
        res = [r["id"] for r in idx.buscar(consulta, k=k)]
        aciertos = [r for r in res if r in relevantes]
        rango = next((i + 1 for i, r in enumerate(res) if r in relevantes), None)
        filas.append({
            "consulta": consulta, "relevantes": sorted(relevantes), "devueltos": res,
            "precision@k": len(aciertos) / k,
            "precision_devueltos": len(aciertos) / len(res) if res else 0.0,
            "recall@k": len(aciertos) / len(relevantes),
            "acierto@1": 1.0 if res and res[0] in relevantes else 0.0,
            "rr": 1 / rango if rango else 0.0,
        })
    resumen = {m: float(np.mean([f[m] for f in filas]))
               for m in ["precision@k", "precision_devueltos", "recall@k", "acierto@1", "rr"]}
    return filas, resumen


def evaluar_recomendaciones(recomendador, k=3):
    filas = []
    for doc, esperados, descripcion in RECOMENDACIONES_PRUEBA:
        rec = recomendador.relacionados(doc, k=k)
        ids = [r["id"] for r in rec]
        acierto = [i for i in ids if i in esperados]
        filas.append({"documento": doc, "descripcion": descripcion, "esperados": sorted(esperados),
                      "recomendados": ids, "similitudes": [round(r["similitud"], 3) for r in rec],
                      "conceptos": [r["conceptos"] for r in rec],
                      "precision@k": len(acierto) / k, "recall@k": len(acierto) / len(esperados),
                      "al_menos_uno": 1.0 if acierto else 0.0})
    hist = []
    for consultas, esperados in HISTORIALES_PRUEBA:
        rec = recomendador.por_historial(consultas, k=k)
        ids = [r["id"] for r in rec]
        acierto = [i for i in ids if i in esperados]
        hist.append({"historial": consultas, "esperados": sorted(esperados), "recomendados": ids,
                     "motivos": [r["motivo"] for r in rec],
                     "precision@k": len(acierto) / k, "al_menos_uno": 1.0 if acierto else 0.0})
    resumen = {
        "precision@k": float(np.mean([f["precision@k"] for f in filas])),
        "recall@k": float(np.mean([f["recall@k"] for f in filas])),
        "al_menos_uno": float(np.mean([f["al_menos_uno"] for f in filas])),
        "historial_precision@k": float(np.mean([h["precision@k"] for h in hist])),
        "historial_al_menos_uno": float(np.mean([h["al_menos_uno"] for h in hist])),
    }
    return filas, hist, resumen
