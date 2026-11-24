"""Componente 2 · Recomendaciones.

Uso:
  python scripts/recomendar.py RI01                              # documentos relacionados con RI01
  python scripts/recomendar.py --historial "pagos" "certificado vencido"   # según un historial de búsqueda
"""
import sys
import _ruta  # noqa: F401
from sgc.sistema import SistemaConocimiento

s = SistemaConocimiento()
args = sys.argv[1:] or ["RI01"]
if args[0] == "--historial":
    recs = s.recomendador.por_historial(args[1:], k=3)
    print("Historial:", " → ".join(args[1:]))
else:
    d = s.doc(args[0])
    print(f"Documento: [{d['id']}] {d['titulo']}")
    recs = s.recomendador.relacionados(args[0], k=3)
for r in recs:
    print(f"\n  [{r['id']}] {r['titulo']}  ({r['categoria']})")
    print(f"     similitud {r['similitud']:.3f} · {r['motivo']}")
    print(f"     términos en común: {', '.join(r['terminos']) or '—'}")
    print(f"     conceptos del grafo: {', '.join(r['conceptos']) or '—'}")
