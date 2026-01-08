import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Publisher Pro v10", layout="wide")

def clean_json_output(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if (start != -1 and end != 0) else None
    except: return None

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None
if 'img_seed' not in st.session_state: st.session_state.img_seed = random.randint(1, 99999)

with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Publicador SEO v10 (API Pollinations)")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema:", placeholder="Ej: Mejores drones para fotografía 2026")

if tema_input and api_key:
    if st.button("🔍 1. Buscar Keywords"):
        prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
        st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword Ganadora:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: REDACCIÓN ---
        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido profundo (>1000 palabras)..."):
                prompt_art = f"""Escribe un artículo SEO experto sobre '{seleccion}'.
                REQUISITOS:
                - Extensión: >1000 palabras reales.
                - Estructura: H2, H3, FAQ, Introducción profunda.
                - Genera un SLUG amigable (ej: mejores-drones-2026).
                - En 'img_prompt' describe una imagen profesional en INGLÉS.
                
                Responde JSON: {{"titulo": "..", "slug": "..", "meta": "..", "intro": "..", "cuerpo": "..", "faq": "..", "tags": "..", "img_prompt": ".."}}"""
                
                res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))

# --- PASO 3: RESULTADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Construcción de la URL de imagen vía API oficial
    # Documentación: https://pollinations.ai/p/{prompt}
    encoded_prompt = urllib.parse.quote(art['img_prompt'])
    url_img = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=768&seed={st.session_state.img_seed}&model=flux&nologo=true"

    tab_code, tab_preview = st.tabs(["📄 CÓDIGO BLOGGER", "👁️ VISTA PREVIA & SEO"])

    with tab_code:
        # Schema Markup JSON-LD
        schema_markup = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Alejandro Echave"}
        }
        
        # Bloque HTML unificado para Blogger
        full_code = f"""<script type="application/ld+json">{json.dumps(schema_markup)}</script>
<div style="text-align:center; margin-bottom:30px;">
    <img src="{url_img}" alt="{art['titulo']}" style="width:100%; max-width:850px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);"/>
</div>
<h1>{art['titulo']}</h1>
<p><strong>{art['intro']}</strong></p>
{art['cuerpo']}
<hr>
<section><h2>Preguntas Frecuentes</h2>{art['faq']}</section>"""
        
        st.subheader("Copia este código en 'Vista HTML' de Blogger:")
        st.code(full_code, language="html")

    with tab_preview:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("**Datos de Publicación:**")
            st.success(f"**Slug:** {art['slug']}")
            st.info(f"**Etiquetas:** {art['tags']}")
            st.write(f"**Meta descripción:** {art['meta']}")
            if st.button("🔄 Regenerar Imagen"):
                st.session_state.img_seed = random.randint(1, 99999)
                st.rerun()
        
        with col2:
            st.write("**Imagen Generada:**")
            st.image(url_img, caption="Previsualización de Pollinations.ai")
            st.caption(f"Prompt usado: {art['img_prompt']}")
