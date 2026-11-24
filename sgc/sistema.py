"""Integración de los cuatro componentes sobre un mismo repositorio de documentos.

Flujo:
  repositorio (CSV) -> clasificador (asigna categoría a los documentos sin etiqueta)
  -> índice semántico (búsqueda) -> grafo de conocimiento (ontología + documentos)
  -> recomendador y chatbot (usan el índice y el grafo)
Cuando un usuario agrega un documento desde la interfaz, el clasificador le pone
categoría y el índice, el grafo, el recomendador y el chatbot se actualizan.
"""
from .buscador import Indice
from .chatbot import Chatbot
from .clasificador import Clasificador
from .datos import cargar_documentos
from .grafo import GrafoConocimiento
from .recomendador import Recomendador


class SistemaConocimiento:
    def __init__(self, df=None):
        df = df if df is not None else cargar_documentos()
        etiquetados = df[df["etiquetado"]]
        self.clasificador = Clasificador(etiquetados["texto"].tolist(), etiquetados["categoria"].tolist())
        self.documentos = []
        for _, f in df.iterrows():
            d = {"id": f["id"], "titulo": f["titulo"], "texto": f["texto"], "categoria": f["categoria"], "nuevo": False}
            if not f["etiquetado"]:
                r = self.clasificador.clasificar(f["texto"])
                d.update(categoria=r["categoria"], confianza=r["confianza"], nuevo=True)
            self.documentos.append(d)
        self._reconstruir()

    def _reconstruir(self):
        self.indice = Indice(self.documentos)
        self.grafo = GrafoConocimiento(self.documentos, self.indice)
        self.recomendador = Recomendador(self.indice, self.grafo)
        self.chatbot = Chatbot(self)

    def doc(self, doc_id):
        return next(d for d in self.documentos if d["id"] == doc_id)

    def agregar_documento(self, titulo, texto):
        """Clasifica un documento nuevo y lo incorpora a todos los componentes."""
        r = self.clasificador.clasificar(f"{titulo}. {texto}")
        n = sum(d["id"].startswith("USR") for d in self.documentos) + 1
        d = {"id": f"USR{n:02d}", "titulo": titulo, "texto": f"{titulo}. {texto}",
             "categoria": r["categoria"], "confianza": r["confianza"], "nuevo": True}
        self.documentos.append(d)
        self._reconstruir()
        return d, r
