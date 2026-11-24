"""Corre la evaluación completa y guarda la evidencia en la carpeta evidencias/.

Uso:  python scripts/evaluar_sistema.py
Genera:
  evidencias/metricas.json            (lo lee la pestaña "Evaluación" de la app)
  evidencias/1_clasificacion.md       comparación de modelos, precisión y recall, documentos nuevos
  evidencias/2_recomendaciones.md     10 casos por similitud + 3 por historial de búsqueda
  evidencias/3_chatbot.md             respuestas del chatbot con sus fuentes
  evidencias/4_grafo.md               tamaño del grafo y ejemplos de conexiones
  evidencias/5_busqueda.md            precisión y recall de la búsqueda con 15 consultas
  evidencias/matriz_confusion.png, evidencias/grafo_conocimiento.png, evidencias/grafo_conocimiento.html
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sgc.clasificador import (NOMBRE_MODELO_FINAL, comparar_modelos, crear_modelo_final,
                              evaluar_por_categoria, modelos_candidatos)
from sgc.datos import CATEGORIAS, CORTOS, RAIZ, cargar_documentos
from sgc.evaluacion import evaluar_recomendaciones, evaluar_recuperacion
from sgc.grafo import ESTILO
from sgc.sistema import SistemaConocimiento

SALIDA = RAIZ / "evidencias"
SALIDA.mkdir(exist_ok=True)

PRUEBA_AVANCE = ["IU03", "RI04", "DT07", "EX07", "DT04", "IU08", "EX02", "RI05", "PO02", "PO04"]

PREGUNTAS_CHATBOT = [
    "¿Qué pasó con los cobros duplicados a los suscriptores?",
    "¿Cómo despliego una nueva versión de un servicio en Kubernetes?",
    "¿Qué hago si se activa una alerta en un servicio?",
    "¿Qué incidentes fueron causados por un certificado vencido?",
    "¿Puedo trabajar desde otro país?",
    "muéstrame los postmortems",
    "qué documentos hay sobre Servicio de pagos",
    "¿Cuál es la receta de la paella?",
]


def pct(x):
    return f"{x:.1%}"


def tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    lineas += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    return "\n".join(lineas)


def main():
    df = cargar_documentos()
    ent = df[df["etiquetado"]]
    X, y = ent["texto"].tolist(), ent["categoria"].tolist()
    s = SistemaConocimiento(df)
    metricas = {}

    # ---------------- 1. Clasificación ----------------
    print("1/5 Clasificación...")
    comparacion = comparar_modelos(X, y)
    base = evaluar_por_categoria(X, y, modelos_candidatos()["Naive Bayes · palabras (avance)"])
    final = evaluar_por_categoria(X, y)
    # los mismos 10 documentos de prueba que usó el cuaderno del avance (paso 5)
    prueba = ent["id"].isin(PRUEBA_AVANCE).to_numpy()
    idx_p = np.where(prueba)[0]
    m = crear_modelo_final().fit([X[i] for i in np.where(~prueba)[0]], [y[i] for i in np.where(~prueba)[0]])
    pred_p = m.predict([X[i] for i in idx_p])
    aciertos_prueba = int(sum(pred_p[j] == y[i] for j, i in enumerate(idx_p)))
    nuevos = [{"id": d["id"], "titulo": d["titulo"], "categoria": d["categoria"], "confianza": d["confianza"]}
              for d in s.documentos if d["nuevo"]]
    metricas["clasificacion"] = {
        "modelo_final": NOMBRE_MODELO_FINAL,
        "comparacion": [{k: (float(v) if k != "modelo" else v) for k, v in f.items()} for f in comparacion],
        "avance": {"exactitud": base["exactitud"], "macro": base["macro"]},
        "final": {"exactitud": final["exactitud"], "macro": final["macro"],
                  "por_categoria": [{k: (float(v) if k != "categoria" else v) for k, v in c.items()} for c in final["por_categoria"]],
                  "matriz": final["matriz"].tolist()},
        "errores": [{"id": ent["id"].iloc[i], "titulo": ent["titulo"].iloc[i], "real": y[i], "predicha": str(final["predicciones"][i])}
                    for i in range(len(y)) if y[i] != final["predicciones"][i]],
        "prueba_25": {"aciertos": aciertos_prueba, "total": len(idx_p)},
        "nuevos": nuevos,
    }

    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    mc = final["matriz"]
    ax.imshow(mc, cmap="Greens")
    cortos = [CORTOS[c] for c in CATEGORIAS]
    ax.set_xticks(range(5), cortos, rotation=25, ha="right")
    ax.set_yticks(range(5), cortos)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, mc[i, j], ha="center", va="center", color="white" if mc[i, j] > 4 else "black", fontsize=12)
    ax.set_xlabel("Categoría predicha")
    ax.set_ylabel("Categoría real")
    ax.set_title(f"Matriz de confusión · {NOMBRE_MODELO_FINAL}\n(validación cruzada, 40 documentos)", fontsize=10)
    plt.tight_layout()
    plt.savefig(SALIDA / "matriz_confusion.png", dpi=160)
    plt.close()

    md = ["# Evidencia 1 · Clasificación automática", "",
          "Datos de evaluación: los 40 documentos etiquetados (8 por categoría). Cada documento lo clasifica un modelo "
          "que no lo vio al entrenar (validación cruzada estratificada de 5 partes, semilla 42). La columna de 10 repeticiones "
          "promedia 10 particiones distintas para que el resultado no dependa del azar.", "",
          tabla(["Modelo", "Exactitud (5 partes)", "Exactitud (5 partes × 10 repeticiones)"],
                [(f["modelo"], pct(f["exactitud_cv5"]), pct(f["exactitud_cv5x10"])) for f in comparacion]), "",
          f"Modelo elegido: **{NOMBRE_MODELO_FINAL}** (da probabilidad por categoría, que se muestra como confianza).", "",
          "## Precisión y recall por categoría (modelo final)", "",
          tabla(["Categoría", "Precisión", "Recall", "F1", "Documentos"],
                [(c["categoria"], pct(c["precision"]), pct(c["recall"]), pct(c["f1"]), c["documentos"]) for c in final["por_categoria"]]),
          "", f"Promedio macro: precisión {pct(final['macro']['precision'])}, recall {pct(final['macro']['recall'])}, "
              f"F1 {pct(final['macro']['f1'])}. Exactitud: {pct(final['exactitud'])}.", "",
          f"Modelo del avance con los mismos datos: precisión {pct(base['macro']['precision'])}, recall {pct(base['macro']['recall'])}, "
          f"exactitud {pct(base['exactitud'])}.", "",
          "## Errores del modelo final", "",
          tabla(["id", "Título", "Categoría real", "El modelo dijo"],
                [(e["id"], e["titulo"], e["real"], e["predicha"]) for e in metricas["clasificacion"]["errores"]]), "",
          f"Prueba con los mismos 10 documentos reservados en el avance (25 %): {aciertos_prueba} de {len(idx_p)} correctos.", "",
          "## Documentos nuevos (sin etiqueta)", "",
          tabla(["id", "Título", "Categoría asignada", "Confianza"],
                [(n["id"], n["titulo"], n["categoria"], pct(n["confianza"])) for n in nuevos]), "",
          "![Matriz de confusión](matriz_confusion.png)"]
    (SALIDA / "1_clasificacion.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- 2. Recomendaciones ----------------
    print("2/5 Recomendaciones...")
    rec, hist, res_rec = evaluar_recomendaciones(s.recomendador)
    metricas["recomendaciones"] = {"casos": rec, "historial": hist, "resumen": res_rec}
    md = ["# Evidencia 2 · Recomendación de documentos", "",
          "Cada caso se ejecutó con `Recomendador.relacionados(id, k=3)`. Los documentos esperados se anotaron a mano "
          "antes de correr la prueba (son los que un ingeniero consideraría útiles al leer el documento de origen).", ""]
    for f in rec:
        md += [f"### {f['documento']} · {s.doc(f['documento'])['titulo']}", f"*{f['descripcion']}*", "",
               tabla(["#", "Recomendado", "Similitud", "Conceptos en común", "¿Esperado?"],
                     [(k + 1, f"[{i}] {s.doc(i)['titulo']}", f["similitudes"][k], ", ".join(f["conceptos"][k]) or "—",
                       "sí" if i in f["esperados"] else "no") for k, i in enumerate(f["recomendados"])]), ""]
    md += ["## Recomendaciones por historial de búsqueda", ""]
    for h in hist:
        md += [f"**Historial:** {' → '.join(h['historial'])}", "",
               tabla(["Recomendado", "Motivo", "¿Esperado?"],
                     [(f"[{i}] {s.doc(i)['titulo']}", h["motivos"][k], "sí" if i in h["esperados"] else "no")
                      for k, i in enumerate(h["recomendados"])]), ""]
    md += ["## Resumen", "",
           tabla(["Métrica", "Valor"], [
               ("Precisión@3 (por similitud)", pct(res_rec["precision@k"])),
               ("Recall@3 (por similitud)", pct(res_rec["recall@k"])),
               ("Casos con al menos una recomendación esperada", pct(res_rec["al_menos_uno"])),
               ("Precisión@3 (por historial)", pct(res_rec["historial_precision@k"]))])]
    (SALIDA / "2_recomendaciones.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- 3. Chatbot ----------------
    print("3/5 Chatbot...")
    md = ["# Evidencia 3 · Chatbot", "",
          "Cada respuesta se generó con `Chatbot.responder(pregunta)`. El texto citado sale de los documentos; "
          "la tabla muestra los documentos recuperados y su similitud.", ""]
    chat = []
    for q in PREGUNTAS_CHATBOT:
        r = s.chatbot.responder(q)
        fuentes = [(f["id"], f["titulo"], round(f.get("similitud", 0), 3)) for f in r["fuentes"]]
        chat.append({"pregunta": q, "intencion": r["intencion"], "respuesta": r["respuesta"], "fuentes": fuentes})
        md += [f"## Pregunta: {q}", f"Tipo de intención detectada: `{r['intencion']}`", "", r["respuesta"], ""]
        if r["intencion"] == "contenido":
            md += [tabla(["Documento recuperado", "Similitud"], [(f"[{i}] {t}", sim) for i, t, sim in fuentes]), ""]
    metricas["chatbot"] = chat
    (SALIDA / "3_chatbot.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- 4. Grafo ----------------
    print("4/5 Grafo...")
    g = s.grafo
    resumen = g.resumen()
    metricas["grafo"] = resumen
    (SALIDA / "grafo_conocimiento.html").write_text(g.html(alto=800), encoding="utf-8")
    H = g.subgrafo(incluir_similares=True)
    U = nx.Graph(H)
    pos = nx.spring_layout(U, seed=7, k=0.32, iterations=200)
    fig, ax = plt.subplots(figsize=(15, 11))
    nx.draw_networkx_edges(U, pos, ax=ax, alpha=0.25, width=0.7, edge_color="#888")
    from sgc.datos import COLORES
    for tipo, e in ESTILO.items():
        nodos = [n for n in U if U.nodes[n]["tipo"] == tipo]
        colores = [COLORES[U.nodes[n]["categoria"]] if tipo == "documento" else e["color"] for n in nodos]
        nx.draw_networkx_nodes(U, pos, nodelist=nodos, node_color=colores, ax=ax,
                               node_size={"area": 900, "categoria": 900, "clase": 600, "concepto": 220, "documento": 90}[tipo],
                               node_shape={"area": "s", "categoria": "s", "clase": "o", "concepto": "o", "documento": "s"}[tipo],
                               edgecolors="#333", linewidths=0.5, label=e["nombre"])
    etiquetas = {n: U.nodes[n]["etiqueta"] for n in U if U.nodes[n]["tipo"] in ("area", "categoria", "clase")}
    nx.draw_networkx_labels(U, pos, etiquetas, font_size=9, font_weight="bold", ax=ax)
    etiquetas_c = {n: U.nodes[n]["etiqueta"] for n in U if U.nodes[n]["tipo"] == "concepto"}
    nx.draw_networkx_labels(U, pos, etiquetas_c, font_size=6.5, font_color="#234", ax=ax)
    ax.legend(loc="lower left", fontsize=10, markerscale=0.6)
    ax.set_title(f"Grafo de conocimiento: {resumen['nodos']} nodos y {resumen['aristas']} relaciones", fontsize=14)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(SALIDA / "grafo_conocimiento.png", dpi=130)
    plt.close()
    md = ["# Evidencia 4 · Grafo de conocimiento", "",
          f"Nodos: {resumen['nodos']} · Relaciones: {resumen['aristas']}", "",
          tabla(["Tipo de nodo", "Cantidad"], [(ESTILO[t]["nombre"], n) for t, n in resumen["por_tipo"].items()]), "",
          tabla(["Relación", "Cantidad"], sorted(resumen["por_relacion"].items(), key=lambda x: -x[1])), "",
          "## Ejemplo de exploración: conexiones del concepto «Credencial o certificado vencido»", "",
          tabla(["Dirección", "Relación", "Nodo", "Tipo"], g.conexiones("concepto:Credencial o certificado vencido")), "",
          "## Ejemplo: conexiones del documento RI02", "",
          tabla(["Dirección", "Relación", "Nodo", "Tipo"], g.conexiones("documento:RI02")), "",
          "![Grafo](grafo_conocimiento.png)", "",
          "La versión interactiva está en `grafo_conocimiento.html` y en la pestaña «Grafo» de la app."]
    (SALIDA / "4_grafo.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- 5. Búsqueda ----------------
    print("5/5 Búsqueda...")
    filas, res = evaluar_recuperacion(s.documentos)
    filas_p, res_p = evaluar_recuperacion(s.documentos, modo="palabras")
    max_prec = float(np.mean([min(len(f["relevantes"]), 3) / 3 for f in filas]))
    metricas["busqueda"] = {"consultas": filas, "resumen": res, "resumen_solo_palabras": res_p, "precision_maxima@3": max_prec}
    md = ["# Evidencia 5 · Precisión y recall de la búsqueda (la usa también el chatbot)", "",
          "Datos de evaluación: 15 preguntas escritas para la prueba. Para cada una se anotó qué documentos la responden. "
          "Se toman los 3 primeros resultados (k = 3).", "",
          tabla(["Consulta", "Relevantes", "Devueltos", "P@3", "R@3", "¿1.º correcto?"],
                [(f["consulta"], ", ".join(f["relevantes"]), ", ".join(f["devueltos"]), pct(f["precision@k"]),
                  pct(f["recall@k"]), "sí" if f["acierto@1"] else "no") for f in filas]), "",
          tabla(["Métrica", "Índice mixto (final)", "Solo palabras (avance)"], [
              ("Precisión@3", pct(res["precision@k"]), pct(res_p["precision@k"])),
              ("Precisión sobre resultados mostrados", pct(res["precision_devueltos"]), pct(res_p["precision_devueltos"])),
              ("Recall@3", pct(res["recall@k"]), pct(res_p["recall@k"])),
              ("Primer resultado correcto", pct(res["acierto@1"]), pct(res_p["acierto@1"])),
              ("MRR", f"{res['rr']:.3f}", f"{res_p['rr']:.3f}")]), "",
          f"Nota: como la mayoría de las preguntas tiene uno o dos documentos relevantes, la precisión@3 máxima posible es {pct(max_prec)}."]
    (SALIDA / "5_busqueda.md").write_text("\n".join(md), encoding="utf-8")

    (SALIDA / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("Listo. Evidencia guardada en", SALIDA)


if __name__ == "__main__":
    main()
