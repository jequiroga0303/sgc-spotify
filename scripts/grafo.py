"""Componente 4 · Grafo de conocimiento.

Uso:
  python scripts/grafo.py                       # resumen y archivo grafo_conocimiento.html
  python scripts/grafo.py "concepto:Servicio de pagos"   # conexiones de un nodo
"""
import sys
import _ruta  # noqa: F401
from sgc.datos import RAIZ
from sgc.sistema import SistemaConocimiento

s = SistemaConocimiento()
g = s.grafo
if len(sys.argv) > 1:
    for fila in g.conexiones(sys.argv[1]):
        print("  ", *fila)
    sys.exit()
r = g.resumen()
print(f"Nodos: {r['nodos']}  Relaciones: {r['aristas']}")
print("Por tipo:", r["por_tipo"])
print("Por relación:", r["por_relacion"])
salida = RAIZ / "evidencias" / "grafo_conocimiento.html"
salida.parent.mkdir(exist_ok=True)
salida.write_text(g.html(alto=800), encoding="utf-8")
print("Grafo interactivo guardado en", salida)
