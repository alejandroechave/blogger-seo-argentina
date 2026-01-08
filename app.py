import streamlit as st
from groq import Groq
import json
import re
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Pro 2026", layout="wide")

def clean_json_logic(text):
    """Limpia errores de sintaxis comunes de la IA."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match: return None
    content = match.group(0)
    content = content.replace('),', '},').replace(')]', '}]')
    return content

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

# --- FLUJO DE TRABAJO ---
st.title("🚀 Estratega SEO: De Keyword a Post Extenso")

# PASO 1: EXPLORACIÓN DE LONG TAILS
st.header("1. Exploración de Keywords Long-Tail")
tema_base = st.text_input("Tema semilla:", placeholder="Ej: Redes sociales para pequeños negocios")

if tema_base and api_key:
    if st.button("🔍 Investigar Long-Tails"):
        try:
            with st.spinner("Buscando oportunidades de posicionamiento..."):
                prompt_kw = f"""Analiza '{tema_base}' y genera 5 keywords 'long-tail' con intención de búsqueda informativa.
                Responde solo JSON: {{'data': [{{'kw': 'keyword', 'vol': 'volumen estimado', 'dif': 'dificultad'}}]}}"""
                
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                st.session_state.kw_list = json.loads(res.choices[0].message.content)['data']
        except Exception as e: st.error(f"Error en Keywords: {e}")

    if st.session_state.kw_list:
        st.subheader("🎯 Oportunidades Encontradas")
        df = pd.DataFrame(st.session_state.kw_list)
        st.table(df)
        
        # PASO 2: SELECCIÓN Y REDACCIÓN
        st.header("2. Redacción de Contenido de Alta Calidad")
        seleccionada = st.selectbox("Elige la keyword ganadora:", [i['kw'] for i in st.session_state.kw_list])
        
        if st.button("📝 Generar Artículo Extenso (>800 palabras)"):
            try:
                with st.spinner("Redactando guía profesional..."):
                    prompt_art = f"""Escribe una guía SEO maestra sobre '{seleccionada}'. 
                    REQUISITOS: Más de 800 palabras, tono experto, estructura H2 y H3.
                    Responde SOLO JSON con estas llaves:
                    - h1: Titulo SEO
                    - meta: Meta descripción 155 carac.
                    - intro: Introducción profunda
                    - cuerpo: HTML con al menos 4 secciones H2 extensas
                    - faq: 5 preguntas frecuentes en HTML
                    - img_prompt: Descripción de imagen en INGLÉS
                    - social: {{'ig': 'post instagram', 'x': 'hilo twitter'}}
                    """
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    st.session_state.art_data = json.loads(clean_json_logic(res_art.choices[0].message.content))
            except Exception as e: st.error(f"Error en Redacción: {e}")

# PASO 3: RESULTADOS ORGANIZADOS
if st.session_state.art_data:
    art = st.session_state.art_data
    st.divider()
    
    # PESTAÑAS PARA EVITAR "DOBLE CÓDIGO"
    tab_blog, tab_imgs, tab_social = st.tabs(["📄 CÓDIGO BLOGGER", "🖼️ IMÁGENES", "📱 REDES SOCIALES"])

    with tab_blog:
        # Aquí solo el código para copiar
        html_para_blogger = f"<h1>{art['h1']}</h1>\n{art['intro']}\n{art['cuerpo']}\n{art['faq']}"
        st.subheader("Código HTML (Copia esto en la Vista HTML de Blogger)")
        st.code(html_para_blogger, language="html")
        
        st.divider()
        with st.expander("👁️ Ver Vista Previa (Cómo se verá en el blog)"):
            st.markdown(html_para_blogger, unsafe_allow_html=True)

    with tab_imgs:
        st.subheader("🖼️ Generador Visual")
        p_desc = art['img_prompt']
        p_url = re.sub(r'[^a-zA-Z]', '-', p_desc).lower()
        img_url = f"https://pollinations.ai/p/{p_url}?width=1024&height=768&nologo=true"
        
        st.image(img_url, caption="Imagen generada para el post")
        st.info("Copia este código donde quieras que aparezca la imagen:")
        st.code(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; max-width:800px; border-radius:12px;" /></div>', language="html")

    with tab_social:
        st.subheader("📱 Copys Promocionales")
        st.write("**Instagram:**", art['social']['ig'])
        st.divider()
        st.write("**X (Twitter):**", art['social']['x'])
