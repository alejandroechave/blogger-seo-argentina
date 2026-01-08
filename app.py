import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN Y UTILIDADES ---
st.set_page_config(page_title="SEO Publisher Pro v6", layout="wide")

def generate_slug(text):
    """Crea un slug amigable para URL."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def fix_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0).replace('),', '},').replace(')]', '}]') if match else None

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("✍️ Publicador SEO Profesional 2026")
st.markdown("Genera artículos con **Schema.org**, **Slug optimizado** y **SEO On-Page** completo.")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema base:", placeholder="Ej: Negocios rentables en Argentina")

if tema_input and api_key:
    if st.button("🔍 1. Analizar Keywords"):
        prompt_kw = f"Busca 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(fix_json(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword ganadora:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: GENERACIÓN COMPLETA ---
        if st.button("📝 2. Generar Artículo Completo"):
            with st.spinner("Redactando y generando marcado Schema..."):
                current_date = datetime.now().strftime("%Y-%m-%d")
                prompt_art = f"""Escribe un artículo SEO de >800 palabras sobre '{seleccion}'.
                Devuelve SOLO JSON con esta estructura exacta:
                {{
                  "h1": "Título impactante",
                  "meta": "Meta descripción 155 carac",
                  "slug": "slug-optimizado-aqui",
                  "introduccion": "Párrafo largo",
                  "cuerpo_html": "Mínimo 4 secciones H2 extensas",
                  "faq_html": "5 preguntas en HTML",
                  "img_prompt": "2 palabras en ingles",
                  "etiquetas": "tag1, tag2",
                  "schema_desc": "Breve resumen para JSON-LD"
                }}"""
                
                res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                st.session_state.art_data = json.loads(fix_json(res_art.choices[0].message.content))

# --- PASO 3: EXPORTACIÓN PROFESIONAL ---
if st.session_state.art_data:
    art = st.session_state.art_data
    st.divider()
    
    # Lógica de Imagen mejorada para evitar el error de las capturas
    seed = random.randint(1, 99999)
    img_kw = art['img_prompt'].strip().replace(" ", "-")
    url_img = f"https://pollinations.ai/p/{img_kw}.jpg?width=1024&height=768&seed={seed}&nologo=true"

    tab1, tab2, tab3 = st.tabs(["📄 CÓDIGO BLOGGER", "🛠️ CONFIGURACIÓN SEO", "👁️ VISTA PREVIA"])

    with tab1:
        # CONSTRUCCIÓN DEL SCHEMA JSON-LD
        schema_json = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['h1'],
            "description": art['meta'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Redactor Pro"}
        }
        
        # Bloque de código final para Blogger
        img_html = f'<div style="text-align:center;"><img src="{url_img}" alt="{art["h1"]}" style="width:100%; max-width:850px; border-radius:15px; margin-bottom:20px;" /></div>'
        schema_html = f'<script type="application/ld+json">\n{json.dumps(schema_json, indent=2)}\n</script>'
        
        full_code = f"{schema_html}\n{img_html}\n<h1>{art['h1']}</h1>\n<p>{art['introduccion']}</p>\n\n{art['cuerpo_html']}\n<section><h2>Preguntas Frecuentes</h2>{art['faq_html']}</section>"
        
        st.success("Copia el código de abajo (incluye Imagen y Schema)")
        st.code(full_code, language="html")

    with tab2:
        st.subheader("⚙️ Parámetros de Publicación")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Slug sugerido:**")
            st.code(art['slug'])
            st.write("**Etiquetas:**")
            st.info(art['etiquetas'])
        with col2:
            st.write("**Meta Descripción:**")
            st.info(art['meta'])

    with tab3:
        st.markdown(f"**Slug:** `{art['slug']}`")
        st.markdown(full_code, unsafe_allow_html=True)
