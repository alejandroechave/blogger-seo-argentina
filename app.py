import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Publisher Pro v7", layout="wide")

def fix_json(text):
    """Extrae el JSON puro eliminando texto basura alrededor."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group(0) if match else None
    except:
        return None

# --- ESTADO DE SESIÓN ---
if 'kw_list' not in st.session_state: st.session_state.kw_list = None
if 'art_data' not in st.session_state: st.session_state.art_data = None

with st.sidebar:
    st.title("🔑 Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("✍️ Publicador SEO Profesional 2026")

# --- PASO 1: KEYWORDS ---
tema_input = st.text_input("Tema base:", placeholder="Ej: Negocios rentables 2026")

if tema_input and api_key:
    if st.button("🔍 1. Analizar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. Responde solo el objeto JSON: {{'data': [{{'kw': 'keyword', 'vol': 'alto', 'dif': 'baja'}}]}}"
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(res.choices[0].message.content)['data']
        except Exception as e:
            st.error(f"Error en keywords: {e}")

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona la keyword:", [i['kw'] for i in st.session_state.kw_list])

        # --- PASO 2: GENERACIÓN ---
        if st.button("📝 2. Generar Artículo Completo"):
            with st.spinner("Redactando artículo y Schema..."):
                prompt_art = f"""Escribe un artículo SEO de >800 palabras sobre '{seleccion}'. 
                Responde EXCLUSIVAMENTE en formato JSON con estas llaves:
                "h1", "meta", "slug", "intro", "cuerpo_html", "faq_html", "img_prompt", "tags".
                En 'img_prompt' pon solo 2 palabras en inglés."""
                
                res_art = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_art}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                st.session_state.art_data = json.loads(res_art.choices[0].message.content)

# --- PASO 3: RESULTADOS ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Generar URL de imagen válida
    img_word = art['img_prompt'].strip().replace(" ", "-")
    seed = random.randint(1, 9999)
    url_img = f"https://pollinations.ai/p/{img_word}.jpg?width=1024&height=768&seed={seed}&nologo=true"

    tab1, tab2 = st.tabs(["📄 CÓDIGO PARA BLOGGER", "👁️ VISTA PREVIA"])

    with tab1:
        # Schema Markup
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['h1'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "description": art['meta']
        }
        
        # HTML Consolidado
        html_final = f"""<script type="application/ld+json">{json.dumps(schema)}</script>
<div style="text-align:center;"><img src="{url_img}" alt="{art['h1']}" style="width:100%; max-width:800px; border-radius:15px;"/></div>
<h1>{art['h1']}</h1>
<p>{art['intro']}</p>
{art['cuerpo_html']}
{art['faq_html']}"""
        
        st.subheader("Copia este código:")
        st.code(html_final, language="html")
        
        st.divider()
        st.write(f"**Slug:** `{art['slug']}`")
        st.write(f"**Tags:** {art['tags']}")

    with tab2:
        st.header(art['h1'])
        st.image(url_img)
        st.markdown(f"**Meta descripción:** {art['meta']}")
        st.markdown(art['intro'], unsafe_allow_html=True)
        st.markdown(art['cuerpo_html'], unsafe_allow_html=True)
