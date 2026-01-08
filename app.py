import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime
import requests

# 1. CONFIGURACIÓN INICIAL (DEBE IR PRIMERO)
st.set_page_config(page_title="SEO Master Pro v16", layout="wide")

# 2. INICIALIZACIÓN DE SESSION STATE (EVITA EL NAMEERROR)
if 'kw_list' not in st.session_state:
    st.session_state.kw_list = None
if 'art_data' not in st.session_state:
    st.session_state.art_data = None

# 3. FUNCIONES DE APOYO
def clean_json_output(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if (start != -1 and end != 0) else None
    except:
        return None

# 4. BARRA LATERAL (CONFIGURACIÓN)
with st.sidebar:
    st.title("🔑 Configuración")
    api_key_groq = st.text_input("Groq API Key:", type="password")
    api_key_unsplash = st.text_input("Unsplash Access Key:", type="password")
    st.info("Obtén tu clave en: unsplash.com/developers")
    
    if api_key_groq:
        client = Groq(api_key=api_key_groq)

# 5. CUERPO PRINCIPAL
st.title("🚀 Generador SEO de Alta Gama")

tema_input = st.text_input("Tema a posicionar:", placeholder="Ej: Inversiones 2026")

if tema_input and api_key_groq:
    if st.button("🔍 1. Analizar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_kw}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
            st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error en Keywords: {e}")

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona la Keyword Principal:", [i['kw'] for i in st.session_state.kw_list])

        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido profundo..."):
                try:
                    prompt_art = f"""Escribe un artículo SEO de >1000 palabras sobre '{seleccion}'.
                    REQUISITOS:
                    - 'meta_desc': Máximo 150 caracteres sin comillas internas.
                    - 'img_keyword': Una palabra técnica en inglés para Unsplash.
                    - Formato HTML rico (H2, H3, FAQ).
                    Responde EXCLUSIVAMENTE en JSON:
                    {{"titulo": "..", "slug": "..", "meta_desc": "..", "intro": "..", "cuerpo": "..", "faq": "..", "tags": "..", "img_keyword": ".."}}"""
                    
                    res_art = client.chat.completions.create(messages=[{"role": "user", "content": prompt_art}], model="llama-3.3-70b-versatile", response_format={"type": "json_object"})
                    st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))
                except Exception as e:
                    st.error(f"Error en Redacción: {e}")

# 6. RESULTADOS (ESTE BLOQUE YA NO DARÁ NAMEERROR)
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Lógica de Imagen Unsplash
    url_img = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1000"
    if api_key_unsplash:
        try:
            response = requests.get(f"https://api.unsplash.com/search/photos?query={art['img_keyword']}&client_id={api_key_unsplash}&per_page=1")
            data = response.json()
            if data['results']:
                url_img = data['results'][0]['urls']['regular']
        except:
            pass

    tab1, tab2 = st.tabs(["📄 CÓDIGO BLOGGER", "👁️ VISTA PREVIA"])

    with tab1:
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta_desc'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d")
        }
        
        full_html = (
            f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script>\n'
            f'<div style="text-align:center; margin-bottom:25px;"><img src="{url_img}" alt="{art["titulo"]}" style="width:100%; max-width:850px; border-radius:15px;"/></div>\n'
            f'<h1>{art["titulo"]}</h1>\n<p><strong>{art["intro"]}</strong></p>\n\n'
            f'{art["cuerpo"]}\n<section><h2>Preguntas Frecuentes</h2>{art["faq"]}</section>'
        )
        st.code(full_html, language="html")

    with tab2:
        st.write(f"**Slug:** `{art['slug']}` | **Meta:** {art['meta_desc']}")
        st.markdown(full_html, unsafe_allow_html=True)
