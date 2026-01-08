import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Publisher v9", layout="wide")

def clean_json_output(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if (start != -1 and end != 0) else None
    except: return None

# --- PERSISTENCIA ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None
if 'img_seed' not in st.session_state: st.session_state.img_seed = random.randint(1, 99999)

with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Publicador SEO Pro v9")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema:", placeholder="Ej: Negocios en Argentina 2026")

if tema_input and api_key:
    if st.button("🔍 1. Buscar Keywords"):
        prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN ---
        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido profundo..."):
                prompt_art = f"""Escribe un artículo SEO experto sobre '{seleccion}'.
                REQUISITOS: >1000 palabras, HTML profesional, Slug SEO y Marcado Schema.
                IMPORTANTE: En 'img_keyword' usa SOLO 1 palabra simple en inglés.
                Responde JSON: {{"titulo": "..", "slug": "..", "meta": "..", "intro": "..", "cuerpo": "..", "faq": "..", "tags": "..", "img_keyword": ".."}}"""
                
                res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))

# --- PASO 3: RESULTADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # URL de Imagen Ultra-Simplificada
    word = art['img_keyword'].strip().replace(" ", "")
    url_img = f"https://pollinations.ai/p/{word}?width=1024&height=768&seed={st.session_state.img_seed}&nologo=true"

    tab_code, tab_seo = st.tabs(["📄 CÓDIGO BLOGGER", "⚙️ SEO & PREVIEW"])

    with tab_code:
        # Schema y HTML unificado
        schema_markup = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d")
        }
        
        full_code = f"""<script type="application/ld+json">{json.dumps(schema_markup)}</script>
<div style="text-align:center;"><img src="{url_img}" alt="{art['titulo']}" style="width:100%; max-width:850px; border-radius:15px;"/></div>
<h1>{art['titulo']}</h1>
<p>{art['intro']}</p>
{art['cuerpo']}
{art['faq']}"""
        
        st.subheader("Código para 'Vista HTML' en Blogger:")
        st.code(full_code, language="html")

    with tab_seo:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Slug sugerido:**")
            st.code(art['slug'])
            st.write("**Etiquetas:**")
            st.info(art['tags'])
            if st.button("🔄 Cambiar Imagen"):
                st.session_state.img_seed = random.randint(1, 99999)
                st.rerun()
        with col2:
            st.write("**Vista Previa Imagen:**")
            st.image(url_img)
            st.caption(f"URL: {url_img}")
