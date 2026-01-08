import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Pro v13", layout="wide")

def clean_json_output(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if (start != -1 and end != 0) else None
    except: return None

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

with st.sidebar:
    st.title("🔑 Configuración SEO")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Generador de Artículos para Posicionamiento")
st.info("Optimizado para Blogger con Imágenes Profesionales y Marcado Schema.")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema a posicionar:", placeholder="Ej: Mejores Mini PC para oficina 2026")

if tema_input and api_key:
    if st.button("🔍 1. Analizar Intención de Búsqueda"):
        prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword Principal (Target):", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN SEO ---
        if st.button("📝 2. Generar Artículo de Alta Calidad"):
            with st.spinner("Redactando contenido profundo (>1000 palabras)..."):
                prompt_art = f"""Actúa como experto en SEO. Escribe un artículo sobre '{seleccion}' para Blogger.
                REQUISITOS DE CALIDAD:
                - Más de 1000 palabras.
                - Tono profesional y persuasivo.
                - Marcado Schema JSON-LD incluido.
                - Slug optimizado.
                - Cuerpo con H2, H3, tablas comparativas y listas.
                - img_keyword: 1 sola palabra en INGLÉS que describa el tema (ej: 'computer', 'office', 'drone').
                
                Responde JSON: {{"titulo": "..", "slug": "..", "meta": "..", "intro": "..", "cuerpo": "..", "faq": "..", "tags": "..", "img_keyword": ".."}}"""
                
                res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))

# --- PASO 3: EXPORTACIÓN ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # SISTEMA DE IMAGEN PROFESIONAL (UNSPLASH) - 100% Estable
    # Usamos source.unsplash.com o la API directa de búsqueda por palabra clave
    img_word = art['img_keyword'].strip().lower()
    url_img = f"https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1000&q=80" # Default tech
    
    # Generamos una URL de búsqueda dinámica de Unsplash
    url_img = f"https://source.unsplash.com/featured/1024x768?{img_word}"

    tab_code, tab_seo = st.tabs(["📄 CÓDIGO BLOGGER (VISTA HTML)", "⚙️ CONFIGURACIÓN SEO"])

    with tab_code:
        # Schema JSON-LD para Google
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Alejandro Echave"}
        }
        
        # HTML Estructurado para Blogger
        html_blogger = f"""<script type="application/ld+json">{json.dumps(schema)}</script>
<div style="text-align:center; margin-bottom:25px;">
    <img src="{url_img}" alt="{art['titulo']}" style="width:100%; max-width:850px; border-radius:15px;"/>
</div>
<h1>{art['titulo']}</h1>
<p>{art['intro']}</p>
{art['cuerpo']}
<section><h2>Preguntas Frecuentes</h2>{art['faq']}</section>"""
        
        st.success("✅ Artículo generado con éxito. Copia el código abajo.")
        st.code(html_blogger, language="html")

    with tab_seo:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Slug sugerido:**")
            st.code(art['slug'])
            st.write("**Etiquetas:**")
            st.info(art['tags'])
            st.write("**Meta Descripción:**")
            st.info(art['meta'])
        with col2:
            st.write("**Imagen Seleccionada:**")
            st.image(url_img, caption=f"Tema de imagen: {img_word}")
            st.caption("Esta imagen es de alta resolución y se adapta automáticamente al tema.")
