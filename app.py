import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SEO Writer Ultra 2026", layout="wide")

def fix_json(text):
    """Extrae y corrige el JSON de la respuesta de la IA."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            content = match.group(0)
            # Corrige errores comunes de cierre de llaves/paréntesis
            content = content.replace('),', '},').replace(')]', '}]')
            return content
    except:
        return None
    return None

# --- PERSISTENCIA DE DATOS ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔑 Acceso API")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Redactor SEO Profesional")
st.info("Genera artículos de >800 palabras con imágenes que SÍ cargan en Blogger.")

# --- PASO 1: INVESTIGACIÓN DE KEYWORDS ---
st.subheader("1. Investigación de Keywords Long-Tail")
tema_input = st.text_input("¿Sobre qué quieres escribir?", placeholder="Ej: Mejores Mini PC 2026")

if tema_input and api_key:
    if st.button("🔍 Buscar Oportunidades"):
        try:
            with st.spinner("Analizando competencia..."):
                prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                st.session_state.kw_list = json.loads(fix_json(res.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error en keywords: {e}")

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona tu Keyword Principal:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN ---
        st.subheader("2. Redacción del Artículo")
        if st.button("📝 Generar Artículo Premium"):
            try:
                with st.spinner("Escribiendo guía extensa y optimizada..."):
                    prompt_art = f"""Escribe un artículo SEO de más de 800 palabras sobre '{seleccion}'.
                    REQUERIMIENTOS:
                    - Estructura con H2 y H3 detallados.
                    - Sección de FAQ con 5 preguntas.
                    - Etiquetas (tags) separadas por comas.
                    - 'img_keyword': SOLO 2 palabras en INGLÉS (ej: 'modern-pc').
                    
                    RESPONDE SOLO EN JSON:
                    {{
                      "titulo": "...",
                      "meta": "...",
                      "intro": "...",
                      "cuerpo": "HTML completo",
                      "preguntas": "FAQ HTML",
                      "img_keyword": "2 palabras ingles",
                      "etiquetas": "tag1, tag2, tag3"
                    }}"""
                    
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    st.session_state.art_data = json.loads(fix_json(res_art.choices[0].message.content))
            except Exception as e:
                st.error(f"Error en redacción: {e}")

# --- PASO 3: RESULTADOS ORGANIZADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    st.divider()
    
    tab_html, tab_img, tab_config = st.tabs(["📄 CÓDIGO BLOGGER", "🖼️ IMAGEN (FIX)", "🏷️ ETIQUETAS Y META"])

    with tab_html:
        # Combinamos todo el HTML
        full_html = f"<h1>{art['titulo']}</h1>\n<p>{art['intro']}</p>\n\n{art['cuerpo']}\n<section><h3>Preguntas Frecuentes</h3>{art['preguntas']}</section>"
        st.success("✅ Copia este código en la 'Vista HTML' de tu entrada.")
        st.code(full_html, language="html")

    with tab_img:
        # Lógica de imagen ultra-estable
        kw_clean = urllib.parse.quote(art['img_keyword'].strip().replace(" ", "-"))
        # Añadimos .jpg para forzar la compatibilidad
        url_final = f"https://pollinations.ai/p/{kw_clean}.jpg?width=1024&height=768&nologo=true"
        
        st.subheader("Previsualización de Imagen")
        st.image(url_final)
        
        st.subheader("Código para la Imagen")
        img_code = f'<div style="text-align:center; margin-bottom:20px;"><img src="{url_final}" style="width:100%; max-width:850px; border-radius:15px;" alt="{seleccion}" /></div>'
        st.code(img_code, language="html")
        st.caption("Pega esto al principio de tu post en Blogger.")

    with tab_config:
        st.subheader("Configuración Lateral de Blogger")
        st.write("**Etiquetas:**")
        st.info(art['etiquetas'])
        st.write("**Meta Descripción:**")
        st.info(art['meta'])
