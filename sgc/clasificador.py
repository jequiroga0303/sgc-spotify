"""Componente 1: clasificación automática de documentos.

Fase de avance: TF-IDF de palabras + Naive Bayes (90.0 % en validación cruzada).
Fase final: se agregan n-gramas de caracteres, que reconocen raíces comunes
("despliegue" / "desplegar", "migración" / "migrar"), y se elige el modelo con
mejor exactitud en validación cruzada. Regresión Logística da además una
probabilidad por categoría, que la interfaz muestra como nivel de confianza.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .datos import CATEGORIAS, STOPWORDS_ES

SEMILLA = 42


def vectorizador_palabras():
    """El mismo vectorizador del avance (palabras y pares de palabras)."""
    return TfidfVectorizer(lowercase=True, strip_accents="unicode", stop_words=STOPWORDS_ES,
                           ngram_range=(1, 2), sublinear_tf=True)


def vectorizador_caracteres():
    """Fragmentos de 3 a 5 letras dentro de cada palabra."""
    return TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="char_wb",
                           ngram_range=(3, 5), sublinear_tf=True)


def modelos_candidatos():
    return {
        "Naive Bayes · palabras (avance)": Pipeline([("tfidf", vectorizador_palabras()), ("modelo", MultinomialNB(alpha=0.1))]),
        "Regresión Logística · palabras (avance)": Pipeline([("tfidf", vectorizador_palabras()), ("modelo", LogisticRegression(C=10, max_iter=3000))]),
        "Naive Bayes · caracteres": Pipeline([("tfidf", vectorizador_caracteres()), ("modelo", MultinomialNB(alpha=0.1))]),
        "SVM lineal · caracteres": Pipeline([("tfidf", vectorizador_caracteres()), ("modelo", LinearSVC(C=1))]),
        "Regresión Logística · caracteres": Pipeline([("tfidf", vectorizador_caracteres()), ("modelo", LogisticRegression(C=100, max_iter=5000))]),
    }


NOMBRE_MODELO_FINAL = "Regresión Logística · caracteres"


def crear_modelo_final():
    return modelos_candidatos()[NOMBRE_MODELO_FINAL]


def comparar_modelos(textos, etiquetas, repeticiones=10):
    """Exactitud con validación cruzada de 5 partes (misma partición del avance)
    y promedio de 10 particiones distintas, para que el resultado no dependa del azar."""
    filas = []
    for nombre, modelo in modelos_candidatos().items():
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
        base = cross_val_score(modelo, textos, etiquetas, cv=cv).mean()
        rep = np.mean([cross_val_score(modelo, textos, etiquetas,
                                       cv=StratifiedKFold(5, shuffle=True, random_state=s)).mean()
                       for s in range(repeticiones)])
        filas.append({"modelo": nombre, "exactitud_cv5": base, "exactitud_cv5x10": rep})
    return filas


def evaluar_por_categoria(textos, etiquetas, modelo=None):
    """Cada documento lo clasifica un modelo que no lo vio (validación cruzada de 5 partes).
    Devuelve precisión, recall y F1 por categoría, la matriz de confusión y los errores."""
    modelo = modelo or crear_modelo_final()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    pred = cross_val_predict(modelo, textos, etiquetas, cv=cv)
    p, r, f, s = precision_recall_fscore_support(etiquetas, pred, labels=CATEGORIAS, zero_division=0)
    por_cat = [{"categoria": c, "precision": p[i], "recall": r[i], "f1": f[i], "documentos": int(s[i])}
               for i, c in enumerate(CATEGORIAS)]
    pm, rm, fm, _ = precision_recall_fscore_support(etiquetas, pred, average="macro", zero_division=0)
    return {
        "por_categoria": por_cat,
        "macro": {"precision": pm, "recall": rm, "f1": fm},
        "exactitud": float(np.mean(np.array(pred) == np.array(etiquetas))),
        "matriz": confusion_matrix(etiquetas, pred, labels=CATEGORIAS),
        "predicciones": list(pred),
    }


class Clasificador:
    """Modelo final entrenado con los 40 documentos etiquetados."""

    def __init__(self, textos, etiquetas):
        self.modelo = crear_modelo_final()
        self.modelo.fit(textos, etiquetas)
        self.clases = list(self.modelo.classes_)

    def clasificar(self, texto):
        prob = self.modelo.predict_proba([texto])[0]
        orden = np.argsort(prob)[::-1]
        return {
            "categoria": str(self.clases[orden[0]]),
            "confianza": float(prob[orden[0]]),
            "alternativas": [(str(self.clases[j]), float(prob[j])) for j in orden[1:3]],
        }
