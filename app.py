import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Pro 2026", layout="wide")

def fix_json_error(text):
    """Limpia el texto para extraer solo el JSON válido."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            content = match.group(0)
            content = content.replace('),', '},').replace(')]', '}]')
            return content
    except:
        return None
    return None

# --- PERSISTENCIA ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

with st.sidebar:
    st.title("🔑 Acceso")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Redactor SEO de Alto Rendimiento")

# --- PASO 1: KEYWORDS ---
st.subheader("1. Investigación de Keywords")
tema_input = st.text_input("Tema a posicionar:", placeholder="Ej: Estrategias de trading 2026")

if tema_input and api_key:
    if st.button("🔍 Buscar Oportunidades Long-Tail"):
        try:
            with st.spinner("Buscando keywords..."):
                prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. Devuelve SOLO un JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                st.session_state.kw_list = json.loads(fix_json_error(res.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error en keywords: {e}")

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona tu Keyword Principal:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN ---
        st.subheader("2. Creación de Contenido")
        if st.button("📝 Generar Artículo Extenso (+800 palabras)"):
            try:
                with st.spinner("Redactando contenido profundo..."):
                    prompt_art = f"""Escribe un artículo SEO profesional sobre '{seleccion}'.
                    REQUERIMIENTOS:
                    - Más de 800 palabras con estructura rica (H2, H3).
                    - Incluye una sección de FAQ con 5 preguntas.
                    - Genera 5 etiquetas (tags) cortas separadas por comas.
                    
                    RESPONDE SOLO EN JSON:
                    {{
                      "titulo": "H1 Title",
                      "meta_desc": "Descripción SEO",
                      "introduccion": "Párrafo intro largo",
                      "cuerpo": "HTML completo (H2, H3, P, UL, LI)",
                      "preguntas": "Sección FAQ en HTML",
                      "img_idea": "3 palabras clave en inglés",
                      "etiquetas": "tag1, tag2, tag3, tag4, tag5"
                    }}"""
                    
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    st.session_state.art_data = json.loads(fix_json_error(res_art.choices[0].message.content))
            except Exception as e:
                st.error(f"Error en redacción: {e}")

# --- PASO 3: RESULTADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    st.divider()
    
    tab_html, tab_img, tab_labels = st.tabs(["📄 CÓDIGO BLOGGER", "🖼️ IMAGEN", "🏷️ ETIQUETAS Y META"])

    with tab_html:
        full_code = f"<h1>{art['titulo']}</h1>\n<p>{art['introduccion']}</p>\n\n{art['cuerpo']}\n<section><h3>Preguntas Frecuentes</h3>{art['preguntas']}</section>"
        st.success("Copia este código y pégalo en la 'Vista HTML' de Blogger.")
        st.code(full_code, language="html")

    with tab_img:
        keyword_limpia = urllib.parse.quote(art['img_idea'].strip())
        url_imagen = f"https://pollinations.ai/p/{keyword_limpia}?width=1024&height=768&nologo=true"
        st.image(url_imagen, caption=f"Imagen para: {seleccion}")
        img_code = f'<div style="text-align:center; margin-bottom:20px;"><img src="{url_imagen}" style="width:100%; max-width:850px; border-radius:15px;" alt="{seleccion}" /></div>'
        st.subheader("Código de Imagen")
        st.code(img_code, language="html")

    with tab_labels:
        st.subheader("📋 Datos de Configuración para Blogger")
        st.write("**Etiquetas sugeridas:**")
        st.info(art['etiquetas'])
        st.caption("Copia estas etiquetas en el apartado 'Etiquetas' de la barra lateral de tu entrada en Blogger.")
        
        st.divider()
        st.write("**Meta Descripción:**")
        st.info(art['meta_desc'])
        st.caption("Copia esto en 'Descripción de búsqueda' en la barra lateral de Blogger.")

else:
    st.info("Configura tu API y escribe un tema para empezar.")
