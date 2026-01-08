import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Pro v14", layout="wide")

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
    st.title("🔑 Configuración")
    api_key_groq = st.text_input("Groq API Key:", type="password")
    # NUEVO: Campo para la API de Unsplash
    api_key_unsplash = st.text_input("Unsplash Access Key:", type="password")
    st.info("Obtén tu clave en: unsplash.com/developers")
    
    if api_key_groq:
        client = Groq(api_key=api_key_groq)

st.title("🚀 Generador SEO de Alta Gama")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema a posicionar:", placeholder="Ej: Estrategias de inversión 2026")

if tema_input and api_key_groq:
    if st.button("🔍 1. Analizar Keywords"):
        prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword Principal:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN ---
        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido profundo..."):
                # Ajuste en el prompt para asegurar meta descripción correcta
                prompt_art = f"""Escribe un artículo SEO de >1000 palabras sobre '{seleccion}'.
                REQUISITOS:
                - 'meta_desc': Una sola frase de máximo 150 caracteres, sin saltos de línea ni comillas dobles internas.
                - 'img_keyword': Una palabra técnica en inglés para buscar en Unsplash.
                - Estructura HTML rica, Slug SEO y Marcado Schema.
                
                Responde EXCLUSIVAMENTE en JSON:
                {{"titulo": "..", "slug": "..", "meta_desc": "..", "intro": "..", "cuerpo": "..", "faq": "..", "tags": "..", "img_keyword": ".."}}"""
                
                res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))

# --- PASO 3: EXPORTACIÓN ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Lógica Unsplash con API Real
    url_img = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1000" # Imagen por defecto
    if api_key_unsplash:
        try:
            query = art['img_keyword']
            response = requests.get(f"https://api.unsplash.com/search/photos?query={query}&client_id={api_key_unsplash}&per_page=1")
            data = response.json()
            if data['results']:
                url_img = data['results'][0]['urls']['regular']
        except:
            pass

    tab_code, tab_seo = st.tabs(["📄 CÓDIGO BLOGGER", "⚙️ DATOS SEO"])

    with tab_code:
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta_desc'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d")
        }
        
        full_html = f"""<script type="application/ld+json">{json.dumps(schema)}</script>
<div style="text-align:center; margin-bottom:25px;"><img src="{url_img}" alt="{art['titulo']}" style="width:100%; max-width:850px; border-radius:15px;"/></div>
<h1>{art['titulo']}</h1>
<p>{art['intro']}</p>
{art['cuerpo']}
{art['faq']}"""
        
        st.code(full_html, language="html")

    with tab_seo:
        st.write(f"**Slug:** `{art['slug']}`")
        st.write(f"**Etiquetas:** `{art['tags']}`")
        st.write("**Meta Descripción:**")
        st.info(art['meta_desc'])
        st.image(url_img, caption="Imagen desde Unsplash API")
