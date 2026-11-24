"""Índice semántico compartido por la búsqueda, el recomendador y el chatbot.

Cada documento se representa con dos vectores TF-IDF: uno de palabras (permite
explicar el resultado con los términos en común) y otro de fragmentos de
caracteres (relaciona formas distintas de la misma palabra, por ejemplo
"despliego" y "despliegue"). La similitud final es una mezcla de ambas.
"""
import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .clasificador import vectorizador_caracteres, vectorizador_palabras

PESO_PALABRAS = 0.6      # peso de la similitud por palabras en la mezcla
UMBRAL_MINIMO = 0.05     # por debajo de esto el documento no se considera relacionado


class Indice:
    def __init__(self, documentos, modo="mixto"):
        """documentos: lista de dicts con id, titulo, texto y categoria."""
        self.docs = documentos
        self.modo = modo
        textos = [d["texto"] for d in documentos]
        self.vp = vectorizador_palabras()
        self.mp = self.vp.fit_transform(textos)
        self.terminos = self.vp.get_feature_names_out()
        self.vc = vectorizador_caracteres()
        self.mc = self.vc.fit_transform(textos)
        self.pos = {d["id"]: i for i, d in enumerate(documentos)}

    # ---------- similitudes ----------
    def _mezcla(self, sim_p, sim_c):
        if self.modo == "palabras":
            return sim_p
        # la similitud por caracteres siempre es algo mayor que cero (fragmentos como "cion");
        # solo cuenta si la consulta ya comparte alguna palabra o fragmento significativo
        return PESO_PALABRAS * sim_p + (1 - PESO_PALABRAS) * np.clip(sim_c - 0.10, 0, None)

    def vector_consulta(self, texto):
        return self.vp.transform([texto]), self.vc.transform([texto])

    def similitudes_consulta(self, texto):
        vp, vc = self.vector_consulta(texto)
        return self._mezcla(cosine_similarity(vp, self.mp)[0], cosine_similarity(vc, self.mc)[0])

    def similitudes_documento(self, doc_id):
        i = self.pos[doc_id]
        return self._mezcla(cosine_similarity(self.mp[i], self.mp)[0], cosine_similarity(self.mc[i], self.mc)[0])

    def terminos_comunes(self, vec_palabras, i, n=4):
        aporte = vec_palabras.multiply(self.mp[i]).toarray()[0]
        orden = np.argsort(aporte)[::-1][:n]
        return [self.terminos[j] for j in orden if aporte[j] > 0]

    # ---------- búsqueda ----------
    def buscar(self, consulta, k=3, excluir=()):
        vp, _ = self.vector_consulta(consulta)
        sims = self.similitudes_consulta(consulta)
        resultados = []
        for i in np.argsort(sims)[::-1]:
            if len(resultados) == k or sims[i] < UMBRAL_MINIMO:
                break
            d = self.docs[i]
            if d["id"] in excluir:
                continue
            resultados.append({**d, "similitud": float(sims[i]),
                               "terminos": self.terminos_comunes(vp, i)})
        return resultados


def dividir_oraciones(texto):
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [p for p in partes if len(p.split()) >= 4]
