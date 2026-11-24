"""Componente 3: chatbot de consultas en lenguaje natural.

Funciona por recuperación de contexto (no inventa texto):
1. Detecta con reglas simples si la pregunta es un saludo, una petición de ayuda,
   una pregunta sobre el repositorio o una lista de documentos de un tipo o concepto.
2. Si es una pregunta de contenido, recupera los documentos más parecidos con el
   índice semántico, elige dentro de ellos las oraciones que mejor responden y
   arma la respuesta citando cada fuente con su similitud.
3. Agrega contexto del grafo de conocimiento: qué área genera ese tipo de
   documento y qué conceptos de la ontología menciona.
"""
import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .buscador import dividir_oraciones
from .datos import CATEGORIAS, normalizar

UMBRAL_SEGURO = 0.12      # por debajo, el bot avisa que no está seguro

SINONIMOS_CATEGORIA = {
    "Documentación técnica": ["documentacion tecnica", "guias", "guia tecnica", "manuales", "documentacion"],
    "Reporte de incidente": ["postmortem", "postmortems", "incidentes", "reportes de incidente", "fallas"],
    "Resultado de experimento A/B": ["experimentos", "pruebas a/b", "prueba a/b", "a/b"],
    "Política interna": ["politicas", "politica", "lineamientos"],
    "Investigación de usuarios": ["investigaciones", "investigacion de usuarios", "estudios", "entrevistas"],
}
PIDE_LISTA = re.compile(r"\b(lista|listar|muestrame|muestra|ensename|cuales son|que documentos|dame los|ver los|ver las)\b")


class Chatbot:
    def __init__(self, sistema):
        self.s = sistema   # SistemaConocimiento: da acceso al índice, al grafo y a los documentos

    # ---------- intenciones por reglas ----------
    def _intencion(self, pregunta):
        t = normalizar(pregunta).strip(" ¿?¡!.")
        if re.fullmatch(r"(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|que tal)( .*)?", t) and len(t.split()) <= 4:
            return "saludo", None
        if re.search(r"\b(ayuda|que puedes hacer|como funcionas|que sabes)\b", t):
            return "ayuda", None
        if re.search(r"\b(cuantos documentos|que categorias|tipos de documento|que hay en el repositorio)\b", t):
            return "inventario", None
        if PIDE_LISTA.search(t):
            for cat, sins in SINONIMOS_CATEGORIA.items():
                if any(re.search(r"\b" + re.escape(s) + r"\b", t) for s in sins):
                    return "lista_categoria", cat
            for concepto in self.s.grafo.onto["instancias"]:
                if normalizar(concepto) in t:
                    return "lista_concepto", concepto
        return "contenido", None

    # ---------- respuestas ----------
    def responder(self, pregunta):
        intencion, dato = self._intencion(pregunta)
        if intencion == "saludo":
            return self._salida(intencion, "¡Hola! Soy el asistente del repositorio de conocimiento de desarrollo de software. "
                                "Pregúntame, por ejemplo, *¿qué pasó con los cobros duplicados?* o *¿cómo despliego un servicio en Kubernetes?*")
        if intencion == "ayuda":
            return self._salida(intencion, "Puedo responder preguntas usando los documentos del repositorio (guías técnicas, "
                                "postmortems, pruebas A/B, políticas e investigaciones de usuarios). Siempre te digo de qué documento "
                                "saqué la respuesta. También puedo listar documentos de un tipo (*muéstrame los postmortems*) "
                                "o de un concepto (*qué documentos hay sobre Servicio de pagos*).")
        if intencion == "inventario":
            conteo = {c: sum(d["categoria"] == c for d in self.s.documentos) for c in CATEGORIAS}
            lineas = "\n".join(f"- {c}: {n}" for c, n in conteo.items())
            return self._salida(intencion, f"El repositorio tiene **{len(self.s.documentos)} documentos**:\n{lineas}")
        if intencion == "lista_categoria":
            docs = [d for d in self.s.documentos if d["categoria"] == dato]
            lineas = "\n".join(f"- [{d['id']}] {d['titulo']}" for d in docs)
            return self._salida(intencion, f"Estos son los documentos de **{dato}** ({len(docs)}):\n{lineas}", fuentes=docs)
        if intencion == "lista_concepto":
            ids = self.s.grafo.documentos_de_concepto(dato)
            docs = [self.s.doc(i) for i in ids]
            lineas = "\n".join(f"- [{d['id']}] {d['titulo']} · {d['categoria']}" for d in docs)
            return self._salida(intencion, f"Según el grafo de conocimiento, **{len(docs)} documentos** mencionan *{dato}*:\n{lineas}",
                                fuentes=docs)
        return self._responder_contenido(pregunta)

    def _mejores_oraciones(self, pregunta, doc, n):
        idx = self.s.indice
        oraciones = [o for o in dividir_oraciones(doc["texto"]) if normalizar(o).rstrip(".") != normalizar(doc["titulo"])]
        if not oraciones:
            return []
        vp, vc = idx.vector_consulta(pregunta)
        sp = cosine_similarity(vp, idx.vp.transform(oraciones))[0]
        sc = cosine_similarity(vc, idx.vc.transform(oraciones))[0]
        puntaje = idx._mezcla(sp, sc)
        elegidas = sorted(np.argsort(puntaje)[::-1][:n])   # se respetan en el orden del documento
        return [oraciones[i] for i in elegidas]

    def _responder_contenido(self, pregunta):
        resultados = self.s.indice.buscar(pregunta, k=3)
        if not resultados:
            return self._salida("sin_resultado", "No encontré documentos que respondan esa pregunta. "
                                "Prueba con otras palabras (por ejemplo, el nombre del servicio o de la funcionalidad).")
        top = resultados[0]
        partes = []
        if top["similitud"] < UMBRAL_SEGURO:
            partes.append("No encontré una respuesta directa, pero esto es lo más cercano que hay en el repositorio:")
        partes.append(f"Según **[{top['id']}] {top['titulo']}** ({top['categoria']}, similitud {top['similitud']:.2f}):")
        partes.append("> " + " ".join(self._mejores_oraciones(pregunta, top, 2)))
        if len(resultados) > 1 and resultados[1]["similitud"] >= 0.6 * top["similitud"]:
            seg = resultados[1]
            partes.append(f"También te puede servir **[{seg['id']}] {seg['titulo']}** (similitud {seg['similitud']:.2f}): "
                          + " ".join(self._mejores_oraciones(pregunta, seg, 1)))
        # el grafo agrega documentos que comparten la misma causa raíz o práctica, aunque usen otras palabras
        vecinos = self._vecinos_en_grafo(top["id"], {r["id"] for r in resultados[:2]})
        if vecinos:
            partes.append("*Conectados en el grafo:* " + "; ".join(
                f"[{d['id']}] {d['titulo']} (comparte «{c}»)" for d, c in vecinos))
        ctx = self.s.grafo.contexto_ontologico(top["id"])
        extra = f"*Contexto del grafo:* este tipo de documento lo genera **{ctx['area']}** y lo consultan {ctx['usuarios']}."
        if ctx["conceptos"]:
            extra += f" Conceptos relacionados: {', '.join(ctx['conceptos'])}."
        partes.append(extra)
        return self._salida("contenido", "\n\n".join(partes), fuentes=resultados)

    def _vecinos_en_grafo(self, doc_id, excluir, maximo=2):
        g = self.s.grafo
        salida = []
        for c in g.conceptos_de(doc_id):
            if g.G.nodes[f"concepto:{c}"]["clase"] != "Causa raíz":
                continue
            for otro in g.documentos_de_concepto(c):
                if otro != doc_id and otro not in excluir and len(salida) < maximo:
                    salida.append((self.s.doc(otro), c))
        return salida

    @staticmethod
    def _salida(intencion, texto, fuentes=()):
        return {"intencion": intencion, "respuesta": texto, "fuentes": list(fuentes)}
