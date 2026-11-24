"""Carga del repositorio de documentos y constantes compartidas por todos los componentes."""
from pathlib import Path
import json
import unicodedata

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DOCUMENTOS = RAIZ / "data" / "documentos.csv"
RUTA_ONTOLOGIA = RAIZ / "data" / "ontologia.json"

# Las cinco categorías del clasificador (tipos de documento de la ontología)
CATEGORIAS = [
    "Documentación técnica",
    "Reporte de incidente",
    "Resultado de experimento A/B",
    "Política interna",
    "Investigación de usuarios",
]
CORTOS = {
    "Documentación técnica": "Doc. técnica",
    "Reporte de incidente": "Incidente",
    "Resultado de experimento A/B": "Experimento A/B",
    "Política interna": "Política",
    "Investigación de usuarios": "Investigación",
}
COLORES = {
    "Documentación técnica": "#1f77b4",
    "Reporte de incidente": "#d62728",
    "Resultado de experimento A/B": "#9467bd",
    "Política interna": "#ff7f0e",
    "Investigación de usuarios": "#1DB954",
}

STOPWORDS_ES = """
a al algo algunas algunos ante antes como con contra cual cuando de del desde
donde durante e el ella ellas ellos en entre era es esa esas ese eso esos esta
estas este esto estos fue fueron ha han hasta hay la las le les lo los mas
me mi mientras muy no nos o otra otras otro otros para pero poco por porque que
se sea ser si sin sobre son su sus tiene todo todos tras un una
uno unos y ya cada debe deben puede pueden segun cual cuales mismo misma
tambien
""".split()


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar palabras clave."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def cargar_documentos(ruta=RUTA_DOCUMENTOS) -> pd.DataFrame:
    """Devuelve los 46 documentos: 40 etiquetados y 6 nuevos sin categoría."""
    df = pd.read_csv(ruta, encoding="utf-8")
    df["categoria"] = df["categoria"].fillna("")
    df["etiquetado"] = df["tipo"].eq("entrenamiento")
    return df


def cargar_ontologia(ruta=RUTA_ONTOLOGIA) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)
