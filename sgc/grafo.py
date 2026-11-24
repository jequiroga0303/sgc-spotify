"""Componente 4: grafo de conocimiento.

Amplía el grafo conceptual de la fase I. Tiene cinco tipos de nodo:
  Área -> Tipo de documento (categoría) -> Documento -> Concepto (instancia) -> Clase de la ontología
y estas relaciones:
  área "genera" categoría · categoría "documenta / analiza / evalúa / regula / protege / describe" clase
  documento "pertenece a" categoría · documento "menciona" concepto · concepto "es un" clase
  clase -> clase (relaciones de la ontología) · concepto -> concepto (dependencias)
  documento "similar a" documento (similitud coseno del índice)
"""
import json
import re

import networkx as nx
import numpy as np

from .datos import COLORES, cargar_ontologia, normalizar

ESTILO = {
    "area":      {"color": "#B39DDB", "shape": "box",      "tam": 22, "nombre": "Área"},
    "categoria": {"color": "#FFD54F", "shape": "box",      "tam": 22, "nombre": "Tipo de documento"},
    "clase":     {"color": "#64B5F6", "shape": "ellipse",  "tam": 20, "nombre": "Clase de la ontología"},
    "concepto":  {"color": "#90CAF9", "shape": "dot",      "tam": 14, "nombre": "Concepto"},
    "documento": {"color": "#BDBDBD", "shape": "square",   "tam": 9,  "nombre": "Documento"},
}
UMBRAL_SIMILAR = 0.10


def nid(tipo, nombre):
    return f"{tipo}:{nombre}"


class GrafoConocimiento:
    def __init__(self, documentos, indice=None, ontologia=None):
        self.onto = ontologia or cargar_ontologia()
        self.G = nx.MultiDiGraph()
        self._patrones = {
            nombre: [re.compile(r"\b" + re.escape(p)) for p in info["palabras"]]
            for nombre, info in self.onto["instancias"].items()
        }
        self._construir_ontologia()
        for d in documentos:
            self.agregar_documento(d)
        if indice is not None:
            self.agregar_similitudes(indice)

    # ---------- construcción ----------
    def _nodo(self, tipo, nombre, **extra):
        n = nid(tipo, nombre)
        if n not in self.G:
            self.G.add_node(n, tipo=tipo, etiqueta=nombre, **extra)
        return n

    def _arista(self, a, b, relacion):
        if not any(d.get("relacion") == relacion for d in self.G.get_edge_data(a, b, default={}).values()):
            self.G.add_edge(a, b, relacion=relacion)

    def _construir_ontologia(self):
        o = self.onto
        for clase, desc in o["clases"].items():
            self._nodo("clase", clase, descripcion=desc)
        for a, rel, b in o["relaciones_clases"]:
            self._arista(nid("clase", a), nid("clase", b), rel)
        for cat, info in o["categorias"].items():
            self._nodo("categoria", cat, descripcion=info["contenido"])
            for rel, clase in info["relaciones"]:
                self._arista(nid("categoria", cat), nid("clase", clase), rel)
        for area, info in o["areas"].items():
            self._nodo("area", area)
            for cat in info["genera"]:
                self._arista(nid("area", area), nid("categoria", cat), "genera")
        for nombre, info in o["instancias"].items():
            self._nodo("concepto", nombre, clase=info["clase"])
            self._arista(nid("concepto", nombre), nid("clase", info["clase"]), "es un")
        for a, rel, b in o["relaciones_instancias"]:
            self._arista(nid("concepto", a), nid("concepto", b), rel)

    def detectar_conceptos(self, texto):
        t = normalizar(texto)
        return [nombre for nombre, pats in self._patrones.items() if any(p.search(t) for p in pats)]

    def agregar_documento(self, d):
        n = self._nodo("documento", d["id"], titulo=d["titulo"], categoria=d["categoria"],
                       nuevo=bool(d.get("nuevo")))
        self._arista(n, nid("categoria", d["categoria"]), "pertenece a")
        for c in self.detectar_conceptos(d["titulo"] + ". " + d["texto"]):
            self._arista(n, nid("concepto", c), "menciona")
        return n

    def agregar_similitudes(self, indice, umbral=UMBRAL_SIMILAR):
        """Une cada documento con su vecino más parecido si la similitud supera el umbral."""
        for d in indice.docs:
            sims = indice.similitudes_documento(d["id"])
            sims[indice.pos[d["id"]]] = -1
            j = int(np.argmax(sims))
            if sims[j] >= umbral:
                a, b = nid("documento", d["id"]), nid("documento", indice.docs[j]["id"])
                if not self.G.has_edge(b, a):
                    self._arista(a, b, f"similar a ({sims[j]:.2f})")

    # ---------- consultas ----------
    def conceptos_de(self, doc_id):
        n = nid("documento", doc_id)
        if n not in self.G:
            return []
        return [self.G.nodes[v]["etiqueta"] for _, v, r in self.G.out_edges(n, data="relacion")
                if r == "menciona"]

    def documentos_de_concepto(self, concepto):
        n = nid("concepto", concepto)
        return [self.G.nodes[u]["etiqueta"] for u, _, r in self.G.in_edges(n, data="relacion") if r == "menciona"]

    def conexiones(self, nodo):
        """Lista legible de todas las relaciones que entran y salen de un nodo."""
        filas = []
        for _, v, r in self.G.out_edges(nodo, data="relacion"):
            filas.append(("→", r, self.G.nodes[v]["etiqueta"], self.G.nodes[v]["tipo"]))
        for u, _, r in self.G.in_edges(nodo, data="relacion"):
            filas.append(("←", r, self.G.nodes[u]["etiqueta"], self.G.nodes[u]["tipo"]))
        return filas

    def contexto_ontologico(self, doc_id):
        """Área que genera el documento, para qué sirve y qué conceptos toca (lo usa el chatbot)."""
        n = nid("documento", doc_id)
        cat = self.G.nodes[n]["categoria"]
        area = [self.G.nodes[u]["etiqueta"] for u, _, r in self.G.in_edges(nid("categoria", cat), data="relacion")
                if r == "genera"]
        conceptos = self.conceptos_de(doc_id)
        relacionados = set()
        for c in conceptos:
            for _, v, r in self.G.out_edges(nid("concepto", c), data="relacion"):
                if self.G.nodes[v]["tipo"] == "concepto":
                    relacionados.add(f"{c} {r} {self.G.nodes[v]['etiqueta']}")
        return {"categoria": cat, "area": area[0] if area else "",
                "usuarios": self.onto["categorias"][cat]["usuarios"],
                "conceptos": conceptos, "relaciones": sorted(relacionados)}

    def resumen(self):
        tipos = {}
        for _, t in self.G.nodes(data="tipo"):
            tipos[t] = tipos.get(t, 0) + 1
        rels = {}
        for *_, r in self.G.edges(data="relacion"):
            r = "similar a" if r.startswith("similar a") else r
            rels[r] = rels.get(r, 0) + 1
        return {"nodos": self.G.number_of_nodes(), "aristas": self.G.number_of_edges(),
                "por_tipo": tipos, "por_relacion": rels}

    # ---------- visualización ----------
    def subgrafo(self, tipos=("area", "categoria", "clase", "concepto", "documento"),
                 incluir_similares=True, categoria=None, centro=None, radio=1):
        nodos = {n for n, t in self.G.nodes(data="tipo") if t in tipos}
        if categoria:
            nodos = {n for n in nodos if self.G.nodes[n]["tipo"] != "documento"
                     or self.G.nodes[n]["categoria"] == categoria}
        H = self.G.subgraph(nodos).copy()
        if not incluir_similares:
            H.remove_edges_from([(u, v, k) for u, v, k, r in H.edges(keys=True, data="relacion")
                                 if r.startswith("similar a")])
        if centro and centro in H:
            cerca = nx.ego_graph(H.to_undirected(as_view=True), centro, radius=radio).nodes
            H = H.subgraph(cerca).copy()
        return H

    def html(self, H=None, alto=650, resaltar=None):
        """Página HTML interactiva con vis-network (la librería que usa PyVis por dentro)."""
        H = H if H is not None else self.G
        nodos = []
        for n, a in H.nodes(data=True):
            e = ESTILO[a["tipo"]]
            color = e["color"]
            if a["tipo"] == "documento":
                color = COLORES.get(a["categoria"], color)
            titulo = f"{e['nombre']}: {a['etiqueta']}"
            if a["tipo"] == "documento":
                titulo += f"\n{a['titulo']}\nCategoría: {a['categoria']}" + ("\n(clasificado por el sistema)" if a.get("nuevo") else "")
            elif a.get("descripcion"):
                titulo += f"\n{a['descripcion']}"
            nodos.append({"id": n, "label": a["etiqueta"], "title": titulo, "shape": e["shape"],
                          "size": e["tam"], "color": color, "tipo": e["nombre"],
                          "borderWidth": 4 if n == resaltar else (3 if a.get("nuevo") else 1),
                          "font": {"size": 16 if a["tipo"] in ("area", "categoria", "clase") else 12}})
        aristas = []
        for u, v, r in H.edges(data="relacion"):
            sim = r.startswith("similar a")
            aristas.append({"from": u, "to": v, "label": "" if sim or r in ("pertenece a", "menciona") else r,
                            "title": r, "arrows": "" if sim else "to", "dashes": sim,
                            "color": {"color": "#E57373" if sim else "#9E9E9E"}})
        leyenda = "".join(
            f'<span style="margin-right:14px"><span style="display:inline-block;width:12px;height:12px;'
            f'background:{e["color"]};border-radius:2px;margin-right:4px"></span>{e["nombre"]}</span>'
            for e in ESTILO.values())
        return PLANTILLA_HTML.replace("__NODOS__", json.dumps(nodos, ensure_ascii=False)) \
                             .replace("__ARISTAS__", json.dumps(aristas, ensure_ascii=False)) \
                             .replace("__ALTO__", str(alto)).replace("__LEYENDA__", leyenda)


PLANTILLA_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>body{margin:0;font-family:sans-serif;font-size:13px;color:#222}
#red{height:__ALTO__px;border:1px solid #ddd;border-radius:6px}
#info{padding:8px 4px;min-height:40px}#ley{padding:6px 4px;color:#444}</style></head><body>
<div id="ley">__LEYENDA__ · <span style="color:#E57373">- - -</span> documentos similares · borde grueso = documento clasificado por el sistema</div>
<div id="red"></div><div id="info">Haz clic en un nodo para ver sus conexiones. Usa la rueda del ratón para acercar.</div>
<script>
const nodos=new vis.DataSet(__NODOS__), aristas=new vis.DataSet(__ARISTAS__);
const red=new vis.Network(document.getElementById('red'),{nodes:nodos,edges:aristas},{
 physics:{solver:'forceAtlas2Based',forceAtlas2Based:{gravitationalConstant:-60,springLength:90},stabilization:{iterations:250}},
 edges:{font:{size:10,align:'middle'},smooth:false},interaction:{hover:true,tooltipDelay:120}});
red.on('click',p=>{if(!p.nodes.length)return;const id=p.nodes[0],n=nodos.get(id);
 const filas=aristas.get().filter(e=>e.from===id||e.to===id).map(e=>{
  const otro=nodos.get(e.from===id?e.to:e.from);const dir=e.from===id?'→':'←';
  return '<li>'+dir+' <i>'+e.title+'</i> '+otro.label+' <span style="color:#888">('+otro.tipo+')</span></li>'});
 document.getElementById('info').innerHTML='<b>'+n.tipo+': '+n.label+'</b> · '+filas.length+' conexiones<ul style="margin:4px 0">'+filas.join('')+'</ul>';});
</script></body></html>"""
