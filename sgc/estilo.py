"""Estilo visual de la app: paleta inspirada en Spotify (negro, gris carbón y verde),
tipografía Figtree y animaciones suaves de entrada y al pasar el cursor."""

VERDE = "#1DB954"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap');

:root {
  --verde: #1DB954;
  --verde-claro: #1ED760;
  --negro: #121212;
  --carbon: #181818;
  --tarjeta: #1F1F1F;
  --tarjeta-hover: #282828;
  --borde: #2A2A2A;
  --texto: #FFFFFF;
  --texto-suave: #B3B3B3;
}

html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select {
  font-family: 'Figtree', 'Helvetica Neue', Arial, sans-serif !important;
}

/* fondo general con un degradado verde muy tenue arriba, como las páginas de playlist */
.stApp {
  background: radial-gradient(1200px 500px at 20% -10%, rgba(29,185,84,0.22), transparent 60%),
              linear-gradient(180deg, #121212 0%, #0d0d0d 100%);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; max-width: 1280px; }

/* entrada animada de cada bloque */
@keyframes aparecer {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.block-container [data-testid="stVerticalBlock"] > div { animation: aparecer .45s ease-out both; }

/* barra lateral */
[data-testid="stSidebar"] {
  background: #000000;
  border-right: 1px solid var(--borde);
}
[data-testid="stSidebar"] h3 {
  font-size: .78rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--texto-suave); margin-top: 1.4rem;
}
.marca { display: flex; align-items: center; gap: .6rem; margin-bottom: .4rem; }
.marca-logo {
  width: 34px; height: 34px; border-radius: 50%; background: var(--verde);
  display: flex; align-items: flex-end; justify-content: center; gap: 3px; padding-bottom: 9px;
  box-shadow: 0 0 18px rgba(29,185,84,.45);
}
.marca-logo span { width: 3px; background: #000; border-radius: 2px; animation: barra 1s ease-in-out infinite; }
.marca-logo span:nth-child(1) { height: 8px;  animation-delay: -.2s; }
.marca-logo span:nth-child(2) { height: 14px; animation-delay: -.5s; }
.marca-logo span:nth-child(3) { height: 10px; animation-delay: -.8s; }
.marca-nombre { font-weight: 800; font-size: 1.15rem; color: var(--texto); letter-spacing: -.01em; }

/* encabezado principal */
.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #1DB954 0%, #138a3f 45%, #0f3d22 100%);
  border-radius: 18px; padding: 2.1rem 2.4rem 2rem; margin-bottom: 1.6rem;
  box-shadow: 0 18px 48px rgba(0,0,0,.45);
  animation: aparecer .6s ease-out both;
}
.hero-etiqueta { font-size: .8rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: rgba(0,0,0,.65); }
.hero h1 {
  font-size: 2.6rem !important; font-weight: 800 !important; line-height: 1.08 !important;
  color: #000 !important; margin: .35rem 0 .6rem !important; letter-spacing: -.02em; max-width: 780px; padding: 0 !important;
}
.hero p { color: rgba(0,0,0,.78); font-size: 1.02rem; max-width: 720px; margin: 0; font-weight: 500; }
.ecualizador {
  position: absolute; right: 2.4rem; bottom: 1.6rem; display: flex; align-items: flex-end; gap: 7px; height: 90px; opacity: .9;
}
.ecualizador span { width: 9px; background: #000; border-radius: 5px; animation: barra 1.2s ease-in-out infinite; }
.ecualizador span:nth-child(1) { animation-delay: -.1s; }
.ecualizador span:nth-child(2) { animation-delay: -.5s; }
.ecualizador span:nth-child(3) { animation-delay: -.9s; }
.ecualizador span:nth-child(4) { animation-delay: -.3s; }
.ecualizador span:nth-child(5) { animation-delay: -.7s; }
.ecualizador span:nth-child(6) { animation-delay: -1.1s; }
@keyframes barra { 0%,100% { height: 22%; } 50% { height: 100%; } }
.hero-cifras { display: flex; gap: 2.2rem; margin-top: 1.3rem; }
.hero-cifras div { color: #000; font-weight: 800; font-size: 1.5rem; line-height: 1; }
.hero-cifras small { display: block; font-size: .75rem; font-weight: 600; color: rgba(0,0,0,.65); margin-top: .3rem; letter-spacing: .03em; }

/* pestañas tipo "chips" */
.stTabs [data-baseweb="tab-list"] { gap: .5rem; border-bottom: none; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] {
  background: var(--tarjeta); border-radius: 999px; padding: .45rem 1.1rem; height: auto;
  color: var(--texto); font-weight: 600; border: none; transition: background .2s, transform .2s;
}
.stTabs [data-baseweb="tab"]:hover { background: var(--tarjeta-hover); transform: translateY(-1px); }
.stTabs [aria-selected="true"] { background: var(--texto) !important; color: #000 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem; }

/* títulos */
h2, h3, h4 { color: var(--texto) !important; font-weight: 700 !important; letter-spacing: -.01em; }
[data-testid="stCaptionContainer"], .stCaption { color: var(--texto-suave) !important; }

/* botones redondeados como los de Spotify */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 999px; font-weight: 700; padding: .45rem 1.3rem;
  background: transparent; color: var(--texto); border: 1px solid #727272;
  transition: transform .15s ease, border-color .2s, background .2s;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: scale(1.04); border-color: var(--texto); color: var(--texto); background: rgba(255,255,255,.04);
}
.stFormSubmitButton > button {
  background: var(--verde); color: #000; border: none;
}
.stFormSubmitButton > button:hover { background: var(--verde-claro); transform: scale(1.04); color: #000; }

/* tarjetas (contenedores con borde) */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--tarjeta); border: 1px solid var(--borde) !important; border-radius: 14px !important;
  transition: background .2s, transform .2s, box-shadow .2s;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  background: var(--tarjeta-hover); transform: translateY(-2px); box-shadow: 0 10px 28px rgba(0,0,0,.4);
}

/* formularios */
[data-testid="stForm"] { background: var(--carbon); border: 1px solid var(--borde); border-radius: 14px; }
.stTextInput input, .stTextArea textarea {
  background: #2A2A2A !important; border-radius: 10px !important; border: 1px solid transparent !important; color: var(--texto) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--verde) !important; box-shadow: 0 0 0 1px var(--verde) !important; }

/* métricas */
[data-testid="stMetric"] {
  background: var(--tarjeta); border-radius: 14px; padding: .9rem 1.1rem; border: 1px solid var(--borde);
}
[data-testid="stMetricValue"] { color: var(--verde) !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: var(--texto-suave) !important; }

/* chat */
[data-testid="stChatMessage"] {
  background: var(--carbon); border-radius: 14px; border: 1px solid var(--borde); padding: 1rem 1.2rem;
  animation: aparecer .4s ease-out both;
}
[data-testid="stChatMessage"] blockquote { border-left: 3px solid var(--verde); color: #E6E6E6; }

/* barras de progreso */
.stProgress > div > div > div > div { background: var(--verde) !important; }

/* expanders y tablas */
[data-testid="stExpander"] { border: 1px solid var(--borde) !important; border-radius: 12px; background: var(--carbon); }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* etiquetas de categoría y de documento nuevo */
.chip {
  display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .74rem; font-weight: 700;
  color: #000; letter-spacing: .02em;
}
.chip-borde {
  display: inline-block; padding: 1px 9px; border-radius: 999px; font-size: .72rem; font-weight: 600;
  color: var(--verde); border: 1px solid var(--verde); margin-left: .35rem;
}
.sim { color: var(--texto-suave); font-size: .85rem; margin-left: .35rem; }
.sim b { color: var(--verde); }
.titulo-seccion {
  font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
  color: var(--texto-suave); margin: 1.4rem 0 .6rem;
}

/* barra de desplazamiento discreta */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 10px; }
</style>
"""


def hero(documentos, nodos, relaciones):
    return f"""
<div class="hero">
  <div class="hero-etiqueta">Gestión del conocimiento con IA</div>
  <h1>Todo lo que el área de desarrollo ya sabe, en un solo lugar</h1>
  <p>Pregunta, busca, clasifica y explora documentos técnicos, postmortems, pruebas A/B, políticas e investigaciones.
  Todos los componentes comparten el mismo repositorio.</p>
  <div class="hero-cifras">
    <div>{documentos}<small>documentos</small></div>
    <div>{nodos}<small>nodos en el grafo</small></div>
    <div>{relaciones}<small>relaciones</small></div>
  </div>
  <div class="ecualizador"><span></span><span></span><span></span><span></span><span></span><span></span></div>
</div>
"""


MARCA = """
<div class="marca">
  <div class="marca-logo"><span></span><span></span><span></span></div>
  <div class="marca-nombre">SGC Spotify</div>
</div>
"""
