"""Interfaz del Sistema de Gestión del Conocimiento (SGC) – Spotify.

Ejecutar localmente:  streamlit run app.py
Integra en una sola aplicación: chatbot, búsqueda semántica, recomendaciones,
clasificación de documentos nuevos, grafo de conocimiento y evaluación.
"""
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from sgc.datos import CATEGORIAS, COLORES, RAIZ, cargar_documentos
from sgc.estilo import CSS, MARCA, hero
from sgc.grafo import ESTILO
from sgc.sistema import SistemaConocimiento

st.set_page_config(page_title="SGC Spotify · Gestión del conocimiento con IA", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

EJEMPLOS_CHAT = [
    "¿Qué pasó con los cobros duplicados a los suscriptores?",
    "¿Cómo despliego una nueva versión de un servicio en Kubernetes?",
    "¿Qué incidentes fueron causados por un certificado vencido?",
    "muéstrame los postmortems",
]
EJEMPLO_DOC = (
    "Postmortem: falla en la reproducción de podcasts",
    "Durante una hora los usuarios no pudieron reproducir episodios de podcasts. La causa raíz fue un certificado "
    "vencido en el servidor de entrega de contenido. El squad renovó el certificado, agregó una alerta preventiva "
    "y documentó la lección aprendida.",
)


# ---------------- estado de la sesión ----------------
@st.cache_data
def documentos_base():
    return cargar_documentos()


def sistema() -> SistemaConocimiento:
    if "sistema" not in st.session_state:
        st.session_state.sistema = SistemaConocimiento(documentos_base())
    return st.session_state.sistema


for clave, valor in {"historial": [], "chat": [], "vistos": [], "doc_sel": None, "centro_grafo": None}.items():
    st.session_state.setdefault(clave, valor)


def registrar_consulta(texto):
    if texto and (not st.session_state.historial or st.session_state.historial[-1] != texto):
        st.session_state.historial.append(texto)


def abrir_documento(doc_id):
    st.session_state.doc_sel = doc_id
    if doc_id not in st.session_state.vistos:
        st.session_state.vistos.append(doc_id)


def etiqueta_categoria(cat):
    return f"<span class='chip' style='background:{COLORES.get(cat, '#999')}'>{cat}</span>"


def tarjeta(d, clave, mostrar_motivo=False):
    """Muestra un documento recuperado con la información usada para encontrarlo."""
    with st.container(border=True):
        nuevo = "<span class='chip-borde'>nuevo</span>" if d.get("nuevo") else ""
        sim = f"<span class='sim'>similitud <b>{d['similitud']:.3f}</b></span>" if "similitud" in d else ""
        st.markdown(f"**[{d['id']}] {d['titulo']}**  \n{etiqueta_categoria(d['categoria'])}{sim}{nuevo}", unsafe_allow_html=True)
        info = []
        if mostrar_motivo and d.get("motivo"):
            info.append(d["motivo"])
        if d.get("terminos"):
            info.append("Términos en común: " + ", ".join(f"`{t}`" for t in d["terminos"]))
        if d.get("conceptos"):
            info.append("Conceptos del grafo: " + ", ".join(d["conceptos"]))
        if info:
            st.caption("  \n".join(info))
        if st.button("Abrir documento y ver relacionados", key=clave):
            abrir_documento(d["id"])
            st.rerun()


s = sistema()

st.markdown(hero(len(s.documentos), s.grafo.G.number_of_nodes(), s.grafo.G.number_of_edges()), unsafe_allow_html=True)

tab_chat, tab_busq, tab_clas, tab_grafo, tab_eval, tab_repo = st.tabs(
    ["Chatbot", "Búsqueda y recomendaciones", "Clasificar documento", "Grafo de conocimiento", "Evaluación", "Repositorio"])

# ---------------- chatbot ----------------
with tab_chat:
    st.subheader("Pregúntale al repositorio")
    st.caption("El asistente busca en los documentos, cita de dónde saca cada respuesta y agrega el contexto del grafo. No inventa información.")
    st.markdown("<div class='titulo-seccion'>Prueba con</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    pregunta_ejemplo = None
    for i_ej, ej in enumerate(EJEMPLOS_CHAT):
        c = cols[i_ej % 2]
        if c.button(ej, key=f"ej_{ej}", use_container_width=True):
            pregunta_ejemplo = ej
    with st.form("form_chat", clear_on_submit=True):
        escrita = st.text_input("Escribe tu pregunta", placeholder="Ej. ¿qué hago si se activa una alerta en un servicio?")
        enviar = st.form_submit_button("Preguntar")
    pregunta = pregunta_ejemplo or (escrita.strip() if enviar else "")
    if pregunta:
        r = s.chatbot.responder(pregunta)
        if r["intencion"] in ("contenido", "sin_resultado"):
            registrar_consulta(pregunta)
        st.session_state.chat.append({"pregunta": pregunta, **r})
    for i, turno in enumerate(reversed(st.session_state.chat)):
        with st.chat_message("user"):
            st.write(turno["pregunta"])
        with st.chat_message("assistant"):
            st.markdown(turno["respuesta"])
            if turno["intencion"] == "contenido" and turno["fuentes"]:
                with st.expander("Documentos recuperados y similitud"):
                    st.dataframe(pd.DataFrame([{"id": f["id"], "título": f["titulo"], "categoría": f["categoria"],
                                                "similitud": round(f["similitud"], 3),
                                                "términos en común": ", ".join(f["terminos"])} for f in turno["fuentes"]]),
                                 hide_index=True, use_container_width=True)

# ---------------- búsqueda y recomendaciones ----------------
with tab_busq:
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        st.subheader("Búsqueda semántica")
        with st.form("form_busq"):
            consulta = st.text_input("¿Qué necesitas encontrar?", placeholder="Ej. reglas para usar datos personales al entrenar modelos")
            k = st.slider("Número de resultados", 1, 8, 3)
            buscar = st.form_submit_button("Buscar")
        if buscar and consulta.strip():
            registrar_consulta(consulta.strip())
            st.session_state.ultima_busqueda = (consulta.strip(), k)
        if st.session_state.get("ultima_busqueda"):
            q, k = st.session_state.ultima_busqueda
            res = s.indice.buscar(q, k=k)
            st.caption(f'Resultados para "{q}" · la similitud coseno va de 0 (nada en común) a 1 (idénticos)')
            if not res:
                st.info("No hay documentos relacionados con esa consulta. Prueba con el nombre del servicio o de la funcionalidad.")
            for j, d in enumerate(res):
                tarjeta({**d, "conceptos": s.grafo.conceptos_de(d["id"])}, f"b_{j}_{d['id']}")
    with der:
        st.subheader("Documento abierto")
        sel = st.session_state.doc_sel
        if sel:
            d = s.doc(sel)
            st.markdown(f"**[{d['id']}] {d['titulo']}**  \n{etiqueta_categoria(d['categoria'])}", unsafe_allow_html=True)
            st.write(d["texto"])
            ctx = s.grafo.contexto_ontologico(sel)
            st.caption(f"Área que lo genera: {ctx['area']} · Lo consultan: {ctx['usuarios']}  \n"
                       f"Conceptos: {', '.join(ctx['conceptos']) or '—'}")
            if st.button("Ver este documento en el grafo"):
                st.session_state.centro_grafo = f"documento:{sel}"
                st.info("Abre la pestaña «Grafo de conocimiento»: ya está centrado en este documento.")
            st.markdown("<div class='titulo-seccion'>Documentos relacionados</div>", unsafe_allow_html=True)
            st.caption("Recomendados por similitud semántica con el documento abierto.")
            for j, r in enumerate(s.recomendador.relacionados(sel, k=3)):
                tarjeta(r, f"r_{j}_{r['id']}")
        else:
            st.caption("Abre un resultado para leerlo y ver los documentos relacionados.")
        st.markdown("<div class='titulo-seccion'>Según tu historial</div>", unsafe_allow_html=True)
        recs = s.recomendador.por_historial(st.session_state.historial, vistos=st.session_state.vistos, k=3)
        if recs:
            for j, r in enumerate(recs):
                tarjeta(r, f"h_{j}_{r['id']}", mostrar_motivo=True)
        else:
            st.caption("Haz una búsqueda o una pregunta al chatbot para recibir sugerencias.")

# ---------------- clasificación ----------------
with tab_clas:
    st.subheader("Agregar y clasificar un documento nuevo")
    st.caption("El clasificador (TF-IDF de caracteres + Regresión Logística) asigna la categoría. Después el documento se agrega "
               "al índice de búsqueda, al grafo y al chatbot.")
    if st.button("Cargar un ejemplo"):
        st.session_state.titulo_nuevo, st.session_state.texto_nuevo = EJEMPLO_DOC
    with st.form("form_clas"):
        titulo = st.text_input("Título", key="titulo_nuevo")
        texto = st.text_area("Texto del documento", key="texto_nuevo", height=150)
        agregar = st.form_submit_button("Clasificar y agregar al repositorio")
    if agregar:
        if len(texto.split()) < 8 or not titulo.strip():
            st.warning("Escribe un título y al menos un par de oraciones para que el modelo tenga de dónde decidir.")
        else:
            d, r = s.agregar_documento(titulo.strip(), texto.strip())
            st.session_state.ultimo_agregado = (d["id"], r)
    if st.session_state.get("ultimo_agregado"):
        doc_id, r = st.session_state.ultimo_agregado
        d = s.doc(doc_id)
        st.success(f"Documento **{doc_id}** agregado como **{r['categoria']}** (confianza {r['confianza']:.0%}). "
                   "Ya puedes encontrarlo en el chatbot, la búsqueda y el grafo.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Probabilidad por categoría**")
            prob = [(r["categoria"], r["confianza"])] + r["alternativas"]
            for cat, p in prob:
                st.progress(p, text=f"{cat}: {p:.0%}")
            st.markdown("**Conceptos detectados (enlaces nuevos en el grafo)**")
            st.write(", ".join(s.grafo.conceptos_de(doc_id)) or "Ninguno de la ontología")
        with c2:
            st.markdown("**Documentos relacionados**")
            for j, rel in enumerate(s.recomendador.relacionados(doc_id, k=3)):
                tarjeta(rel, f"c_{j}_{rel['id']}")

# ---------------- grafo ----------------
with tab_grafo:
    st.subheader("Grafo de conocimiento")
    st.caption("Amplía el grafo conceptual de la fase I: áreas → tipos de documento → documentos → conceptos → clases de la ontología. "
               "Pasa el cursor sobre un nodo para ver su descripción y haz clic para listar sus conexiones.")
    nombres = {k: v["nombre"] for k, v in ESTILO.items()}
    f1, f2, f3 = st.columns([3, 2, 2])
    tipos = f1.multiselect("Tipos de nodo", list(nombres), default=list(nombres), format_func=nombres.get)
    categoria = f2.selectbox("Documentos de", ["Todas las categorías"] + CATEGORIAS)
    similares = f3.toggle("Mostrar documentos similares", value=True)
    opciones = sorted(s.grafo.G.nodes, key=lambda n: (s.grafo.G.nodes[n]["tipo"], n))
    centro_def = st.session_state.centro_grafo
    c1, c2 = st.columns([3, 1])
    centro = c1.selectbox("Centrar en un nodo (opcional)", ["(todo el grafo)"] + opciones,
                          index=opciones.index(centro_def) + 1 if centro_def in opciones else 0,
                          format_func=lambda n: n if n == "(todo el grafo)" else
                          f"{nombres[s.grafo.G.nodes[n]['tipo']]}: {s.grafo.G.nodes[n]['etiqueta']}"
                          + (f" – {s.grafo.G.nodes[n]['titulo']}" if s.grafo.G.nodes[n]['tipo'] == 'documento' else ""))
    radio = c2.slider("Distancia", 1, 3, 1, disabled=centro == "(todo el grafo)")
    H = s.grafo.subgrafo(tipos=tuple(tipos), incluir_similares=similares,
                         categoria=None if categoria == "Todas las categorías" else categoria,
                         centro=None if centro == "(todo el grafo)" else centro, radio=radio)
    st.caption(f"Mostrando {H.number_of_nodes()} nodos y {H.number_of_edges()} relaciones.")
    components.html(s.grafo.html(H, alto=600, resaltar=None if centro == "(todo el grafo)" else centro), height=720, scrolling=True)
    if centro != "(todo el grafo)":
        st.markdown(f"**Conexiones de {s.grafo.G.nodes[centro]['etiqueta']}**")
        st.dataframe(pd.DataFrame(s.grafo.conexiones(centro), columns=["dirección", "relación", "nodo", "tipo"]),
                     hide_index=True, use_container_width=True)

# ---------------- evaluación ----------------
with tab_eval:
    ruta = RAIZ / "evidencias" / "metricas.json"
    if not ruta.exists():
        st.warning("Ejecuta `python scripts/evaluar_sistema.py` para generar las métricas.")
    else:
        m = json.loads(ruta.read_text(encoding="utf-8"))
        cl, bu, re_ = m["clasificacion"], m["busqueda"], m["recomendaciones"]
        st.subheader("Resultados de la evaluación")
        st.caption("Calculados con `scripts/evaluar_sistema.py` sobre los documentos del repositorio. El detalle está en la carpeta evidencias/.")
        a, b, c, d = st.columns(4)
        a.metric("Clasificación · precisión (macro)", f"{cl['final']['macro']['precision']:.1%}",
                 f"{cl['final']['macro']['precision'] - cl['avance']['macro']['precision']:+.1%} vs. avance")
        b.metric("Clasificación · recall (macro)", f"{cl['final']['macro']['recall']:.1%}",
                 f"{cl['final']['macro']['recall'] - cl['avance']['macro']['recall']:+.1%} vs. avance")
        c.metric("Búsqueda · recall@3", f"{bu['resumen']['recall@k']:.1%}")
        d.metric("Búsqueda · 1.er resultado correcto", f"{bu['resumen']['acierto@1']:.0%}")
        st.markdown("#### Clasificación (validación cruzada con los 40 documentos etiquetados)")
        st.dataframe(pd.DataFrame(cl["comparacion"]).rename(columns={
            "modelo": "Modelo", "exactitud_cv5": "Exactitud (5 partes)", "exactitud_cv5x10": "Exactitud (5 partes × 10)"})
            .style.format({"Exactitud (5 partes)": "{:.1%}", "Exactitud (5 partes × 10)": "{:.1%}"}),
            hide_index=True, use_container_width=True)
        x, y = st.columns(2)
        x.dataframe(pd.DataFrame(cl["final"]["por_categoria"]).rename(columns={"categoria": "Categoría", "precision": "Precisión",
                    "recall": "Recall", "f1": "F1", "documentos": "Docs"})
                    .style.format({"Precisión": "{:.1%}", "Recall": "{:.1%}", "F1": "{:.1%}"}), hide_index=True, use_container_width=True)
        y.image(str(RAIZ / "evidencias" / "matriz_confusion.png"), use_container_width=True)
        st.markdown("#### Búsqueda y chatbot (15 preguntas con respuesta conocida, k = 3)")
        st.dataframe(pd.DataFrame(bu["consultas"])[["consulta", "relevantes", "devueltos", "precision@k", "recall@k", "acierto@1"]]
                     .style.format({"precision@k": "{:.0%}", "recall@k": "{:.0%}", "acierto@1": "{:.0%}"}),
                     hide_index=True, use_container_width=True)
        st.caption(f"Precisión@3 {bu['resumen']['precision@k']:.1%} (máximo posible {bu['precision_maxima@3']:.1%}, porque casi todas "
                   f"las preguntas tienen uno o dos documentos correctos) · MRR {bu['resumen']['rr']:.2f}")
        st.markdown("#### Recomendaciones (10 casos por similitud y 3 por historial)")
        st.dataframe(pd.DataFrame(re_["casos"])[["documento", "descripcion", "esperados", "recomendados", "similitudes", "precision@k"]]
                     .style.format({"precision@k": "{:.0%}"}), hide_index=True, use_container_width=True)
        r = re_["resumen"]
        st.caption(f"Por similitud: precisión@3 {r['precision@k']:.1%}, recall@3 {r['recall@k']:.1%}, "
                   f"{r['al_menos_uno']:.0%} de los casos con al menos una sugerencia esperada · "
                   f"Por historial: precisión@3 {r['historial_precision@k']:.0%}")

# ---------------- repositorio ----------------
with tab_repo:
    st.subheader("Repositorio de documentos")
    tabla = pd.DataFrame([{"id": d["id"], "título": d["titulo"], "categoría": d["categoria"],
                           "origen": "clasificado por el sistema" if d["nuevo"] else "etiquetado",
                           "conceptos": ", ".join(s.grafo.conceptos_de(d["id"]))} for d in s.documentos])
    filtro = st.multiselect("Filtrar por categoría", CATEGORIAS)
    if filtro:
        tabla = tabla[tabla["categoría"].isin(filtro)]
    st.dataframe(tabla, hide_index=True, use_container_width=True, height=520)
    st.download_button("Descargar CSV", tabla.to_csv(index=False).encode("utf-8"), "repositorio_sgc.csv", "text/csv")


# ---------------- barra lateral ----------------
def barra_lateral():
    """Se dibuja al final para que refleje la consulta que se acaba de hacer."""
    with st.sidebar:
        st.markdown(MARCA, unsafe_allow_html=True)
        st.caption("Prototipo de gestión del conocimiento con IA para el área de desarrollo de software. "
                   "Documentos simulados con fines académicos.")
        c1, c2 = st.columns(2)
        c1.metric("Documentos", len(s.documentos))
        c2.metric("Nodos en el grafo", s.grafo.G.number_of_nodes())
        st.markdown("### Tu contexto de búsqueda")
        if st.session_state.historial:
            for q in st.session_state.historial[-5:][::-1]:
                st.markdown(f"- {q}")
        else:
            st.caption("Aún no has hecho consultas. Lo que preguntes en el chatbot o en la búsqueda se usa para recomendarte documentos.")
        if st.session_state.vistos:
            st.caption("Documentos abiertos: " + ", ".join(st.session_state.vistos))
        if st.button("Borrar historial"):
            for k in ("historial", "chat", "vistos"):
                st.session_state[k] = []
            st.session_state.doc_sel = None
            st.rerun()
        st.markdown("### Recomendado para ti")
        recs = s.recomendador.por_historial(st.session_state.historial, vistos=st.session_state.vistos, k=3)
        if recs:
            for r in recs:
                st.markdown(f"**[{r['id']}]** {r['titulo']}  \n<small>{r['motivo']} · similitud {r['similitud']:.3f}</small>",
                            unsafe_allow_html=True)
        else:
            st.caption("Aparecerán aquí cuando hagas tu primera consulta.")


barra_lateral()
