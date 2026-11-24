"""Componente 2: recomendación de documentos.

Dos mecanismos:
1. Por similitud semántica: dado un documento, sugiere los más parecidos
   (similitud coseno) y muestra los términos y conceptos que comparten.
2. Por historial / contexto de búsqueda: junta las consultas recientes del
   usuario (las más nuevas pesan más), arma un "perfil de interés" y sugiere
   documentos que todavía no ha abierto, indicando qué consulta los motivó.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .buscador import UMBRAL_MINIMO


class Recomendador:
    def __init__(self, indice, grafo=None):
        self.indice = indice
        self.grafo = grafo          # para explicar con conceptos de la ontología

    def _conceptos_comunes(self, id_a, id_b):
        if self.grafo is None:
            return []
        return sorted(set(self.grafo.conceptos_de(id_a)) & set(self.grafo.conceptos_de(id_b)))

    def relacionados(self, doc_id, k=3):
        """Documentos más parecidos a doc_id."""
        idx = self.indice
        i = idx.pos[doc_id]
        sims = idx.similitudes_documento(doc_id)
        sims[i] = -1
        salida = []
        for j in np.argsort(sims)[::-1][:k]:
            if sims[j] < UMBRAL_MINIMO:
                break
            d = idx.docs[j]
            salida.append({**d, "similitud": float(sims[j]),
                           "terminos": idx.terminos_comunes(idx.mp[i], j),
                           "conceptos": self._conceptos_comunes(doc_id, d["id"]),
                           "motivo": f"parecido a {doc_id}"})
        return salida

    def por_historial(self, consultas, vistos=(), k=3, ventana=5):
        """consultas: lista de textos, de la más antigua a la más reciente."""
        recientes = [c for c in consultas if c.strip()][-ventana:]
        if not recientes:
            return []
        idx = self.indice
        pesos = np.array([0.5 ** (len(recientes) - 1 - t) for t in range(len(recientes))])  # la última pesa 1, la anterior 0.5...
        pesos = pesos / pesos.sum()
        matriz = np.vstack([idx.similitudes_consulta(c) for c in recientes])   # consultas x documentos
        puntaje = pesos @ matriz
        salida = []
        for j in np.argsort(puntaje)[::-1]:
            if len(salida) == k or puntaje[j] < UMBRAL_MINIMO / 2:
                break
            d = idx.docs[j]
            if d["id"] in vistos:
                continue
            t = int(np.argmax(matriz[:, j] * pesos))
            vp, _ = idx.vector_consulta(recientes[t])
            salida.append({**d, "similitud": float(puntaje[j]),
                           "terminos": idx.terminos_comunes(vp, j),
                           "conceptos": self.grafo.conceptos_de(d["id"]) if self.grafo else [],
                           "motivo": f'porque buscaste: "{recientes[t]}"'})
        return salida
