"""Componente 1 · Clasificación automática.

Uso:
  python scripts/clasificar.py                       # compara modelos y clasifica los 6 documentos nuevos
  python scripts/clasificar.py "Título" "Texto..."   # clasifica un documento propio
"""
import sys
import _ruta  # noqa: F401
from sgc.clasificador import Clasificador, comparar_modelos, evaluar_por_categoria
from sgc.datos import cargar_documentos

df = cargar_documentos()
ent = df[df["etiquetado"]]
X, y = ent["texto"].tolist(), ent["categoria"].tolist()
modelo = Clasificador(X, y)

if len(sys.argv) >= 3:
    r = modelo.clasificar(f"{sys.argv[1]}. {sys.argv[2]}")
    print(f"Categoría: {r['categoria']} (confianza {r['confianza']:.0%})")
    for c, p in r["alternativas"]:
        print(f"  alternativa: {c} {p:.0%}")
    sys.exit()

print("Comparación de modelos (validación cruzada, 40 documentos):")
for f in comparar_modelos(X, y):
    print(f"  {f['modelo']:42s} {f['exactitud_cv5']:.1%}   (10 repeticiones: {f['exactitud_cv5x10']:.1%})")
ev = evaluar_por_categoria(X, y)
print("\nPrecisión y recall por categoría (modelo final):")
for c in ev["por_categoria"]:
    print(f"  {c['categoria']:30s} precisión {c['precision']:.1%}  recall {c['recall']:.1%}")
print(f"  {'Promedio macro':30s} precisión {ev['macro']['precision']:.1%}  recall {ev['macro']['recall']:.1%}")
print("\nDocumentos nuevos:")
for _, f in df[~df["etiquetado"]].iterrows():
    r = modelo.clasificar(f["texto"])
    print(f"  {f['id']:8s} {r['categoria']:30s} {r['confianza']:.0%}  {f['titulo']}")
