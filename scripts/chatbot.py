"""Componente 3 · Chatbot en la terminal.

Uso:
  python scripts/chatbot.py                        # conversación (escribe 'salir' para terminar)
  python scripts/chatbot.py "¿Qué pasó con los cobros duplicados?"
"""
import sys
import _ruta  # noqa: F401
from sgc.sistema import SistemaConocimiento

s = SistemaConocimiento()


def mostrar(pregunta):
    r = s.chatbot.responder(pregunta)
    print("\nBot:", r["respuesta"].replace("**", ""))
    if r["intencion"] == "contenido":
        print("\n  Fuentes:", "; ".join(f"{f['id']} ({f['similitud']:.3f})" for f in r["fuentes"]))


if len(sys.argv) > 1:
    mostrar(" ".join(sys.argv[1:]))
else:
    print("Chatbot del SGC. Escribe tu pregunta ('salir' para terminar).")
    while (q := input("\nTú: ").strip()).lower() not in ("salir", "exit", ""):
        mostrar(q)
