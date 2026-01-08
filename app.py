import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Publisher v8", layout="wide")

def clean_json_output(text):
    """Extrae el JSON de forma ultra-segura."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return text[start:end]
    except:
        return None
    return None

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("✍️ Publicador SEO de Alta Gama")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema base:", placeholder="Ej: Mini PC de oficina 2026")

if tema_input and api_key:
    if st.button("🔍 1. Analizar Keywords"):
        prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. Devuelve SOLO un objeto JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword ganadora:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: GENERACIÓN DE CONTENIDO ---
        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido de alta calidad..."):
                prompt_art = f"""Escribe un artículo SEO experto sobre '{seleccion}'.
                REQUISITOS:
                - Extensión: >1000 palabras.
                - Formato: HTML profesional (H2, H3, tablas, listas).
                - Incluye un SLUG optimizado para la URL.
                - Incluye Marcado Schema JSON-LD.
                
                Responde EXCLUSIVAMENTE en JSON con estas llaves:
                "titulo", "slug", "meta", "intro", "cuerpo", "faq", "tags", "img_prompt"."""
                
                res_art = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_art}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))

# --- PASO 3: RESULTADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Construcción de imagen ultra-limpia
    clean_kw = urllib.parse.quote(art['img_prompt'].strip().replace(" ", "-"))
    seed = random.randint(1, 99999)
    url_img = f"https://pollinations.ai/p/{clean_kw}.jpg?width=1024&height=768&seed={seed}&nologo=true"

    tab_blogger, tab_seo = st.tabs(["📄 CÓDIGO BLOGGER", "⚙️ DATOS SEO"])

    with tab_blogger:
        # Marcado Schema.org
        schema_json = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Alejandro Echave"}
        }
        
        # Bloque HTML unificado
        html_final = f"""<script type="application/ld+json">{json.dumps(schema_json)}</script>
<div style="text-align:center; margin-bottom:25px;">
    <img src="{url_img}" alt="{art['titulo']}" style="width:100%; max-width:850px; border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>
</div>
<h1>{art['titulo']}</h1>
<p>{art['intro']}</p>
{art['cuerpo']}
<section><h2>Preguntas Frecuentes</h2>{art['faq']}</section>"""
        
        st.subheader("Copia el código completo aquí:")
        st.code(html_html := html_final, language="html")

    with tab_seo:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Slug (URL):**")
            st.code(art['slug'])
            st.write("**Etiquetas:**")
            st.info(art['tags'])
        with col2:
            st.write("**Meta Descripción:**")
            st.info(art['meta'])
            st.write("**Vista Previa Imagen:**")
            st.image(url_img)
