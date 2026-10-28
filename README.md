# Prototipo de Sistema de Gestión del Conocimiento – Spotify

Avance del proyecto de la materia **Sistemas y tecnologías de administración del conocimiento** (Universidad Tecmilenio).

Es un prototipo para el área de desarrollo de software de Spotify con dos funciones:

1. **Clasificación automática de documentos.** Convierte el texto en vectores TF-IDF y lo clasifica con Naive Bayes en 5 categorías. También compara este modelo con Regresión Logística.
2. **Búsqueda semántica.** Convierte una pregunta en lenguaje natural en un vector TF-IDF y devuelve los documentos más parecidos según la similitud coseno.

## Contenido del repositorio

| Archivo | Qué contiene |
|---|---|
| `SGC_Spotify_Prototipo.ipynb` | Todo el código, paso a paso y ya ejecutado. Los pasos 1 a 6 son la clasificación, los pasos 7 a 12 son la búsqueda semántica y al final vienen dos extras: la matriz de confusión y el mapa del conocimiento. |
| `documentos_prueba.csv` | Los 46 documentos de prueba: 40 etiquetados para entrenar y evaluar (8 por categoría) y 6 nuevos sin etiqueta. |
| `ontologia_sgc_spotify.owl` | Ontología del dominio en formato OWL. Contiene áreas, equipos, servicios, incidentes y los 5 tipos de documento, con los 46 documentos como individuos. Se puede abrir en Protégé. |
| `grafo_conceptual.png` | Grafo conceptual que relaciona áreas, tipos de documento y conceptos. |

> Los documentos son **simulados**. Los escribimos para el proyecto con base en información pública sobre cómo trabaja Spotify; no son documentos internos reales.

## Cómo ejecutarlo

1. Entra a [Google Colab](https://colab.research.google.com) y abre el cuaderno desde **Archivo > Abrir cuaderno > GitHub** pegando el enlace de este repositorio. También puedes descargarlo y usar **Subir cuaderno**.
2. Ejecuta las celdas en orden con ▶. No hay que instalar nada: Colab ya trae scikit-learn, numpy, pandas y matplotlib, y los documentos vienen dentro del cuaderno. El contenido es el mismo que el de `documentos_prueba.csv`.

## Resultados

- Validación cruzada de 5 partes: Naive Bayes obtuvo **90.0 %** y Regresión Logística **87.5 %**.
- Prueba con 10 documentos que el modelo no vio al entrenar: **10 de 10** correctos.
- Los 6 documentos nuevos quedaron en la categoría esperada. La confianza más baja fue de 75 %, en una política sobre datos para entrenar modelos.
- Matriz de confusión con los 40 documentos: **36 de 40** aciertos. La mayoría de los errores fueron entre documentación técnica y reportes de incidente.
- En los cuatro ejemplos de búsqueda, el primer resultado es el documento que responde la pregunta.

## Equipo

- Jorge Emilio Quiroga López
- Adriana Matilda Cruz Rito
- Juan Pablo Espinosa
