import streamlit as st
from groq import Groq
import json
import re
import urllib.parse
import pandas as pd
import random
from datetime import datetime
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SEO Publisher Pro v17", layout="wide")

# 2. INICIALIZACIÓN DE ESTADOS (Evita NameError)
if 'kw_list' not in st.session_state:
    st.session_state.kw_list = None
if 'art_data' not in st.session_state:
    st.session_state.art_data = None

# 3. FUNCIONES DE LIMPIEZA
def clean_json_output(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if (start != -1 and end != 0) else None
    except:
        return None

# 4. BARRA LATERAL (APIs)
with st.sidebar:
    st.title("🔑 Configuración")
    api_key_groq = st.text_input("Groq API Key:", type="password")
    api_key_unsplash = st.text_input("Unsplash Access Key:", type="password")
    st.info("Consigue tu Access Key en: unsplash.com/developers")
    
    if api_key_groq:
        client = Groq(api_key=api_key_groq)

st.title("🚀 Generador SEO de Alta Gama")
st.markdown("Contenido de +1000 palabras con Títulos Magnéticos y Marcado Schema.")

# 5. PASO 1: KEYWORDS
tema_input = st.text_input("¿Sobre qué quieres posicionar hoy?", placeholder="Ej: Negocios digitales 2026")

if tema_input and api_key_groq:
    if st.button("🔍 1. Investigar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema_input}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': 'alto', 'dif': 'baja'}}]}}"
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}], 
                model="llama-3.3-70b-versatile", 
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(clean_json_output(res.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error al analizar keywords: {e}")

    if st.session_state.kw_list:
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona la Keyword Ganadora:", [i['kw'] for i in st.session_state.kw_list])

        # 6. PASO 2: REDACCIÓN CREATIVA
        if st.button("📝 2. Generar Artículo Maestro"):
            with st.spinner("Redactando contenido magnético y profundo..."):
                try:
                    prompt_art = f"""Escribe un artículo SEO experto sobre '{seleccion}'.
                    
                    ESTILO DE REDACCIÓN:
                    - TÍTULO (h1): Prohibido usar 'Introducción a' o 'Guía de'. Crea un título magnético, provocador o de autoridad (ej: 'El Lado Oscuro de...', 'Por qué el 90% falla en...', 'La Verdadera Revolución de...').
                    - SUBTÍTULOS (h2, h3): Deben ser ganchos de curiosidad, no descriptivos.
                    - EXTENSIÓN: >1000 palabras reales.
                    - META DESCRIPCIÓN: Un gancho persuasivo de máximo 150 caracteres.
                    - FORMATO: HTML rico, Slug SEO y Marcado Schema Article.
                    
                    Responde EXCLUSIVAMENTE en JSON:
                    {{
                      "titulo": "..",
                      "slug": "..",
                      "meta_desc": "..",
                      "intro": "..",
                      "cuerpo": "..",
                      "faq": "..",
                      "tags": "..",
                      "img_keyword": "2 palabras en ingles para Unsplash"
                    }}"""
                    
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}], 
                        model="llama-3.3-70b-versatile", 
                        response_format={"type": "json_object"}
                    )
                    st.session_state.art_data = json.loads(clean_json_output(res_art.choices[0].message.content))
                except Exception as e:
                    st.error(f"Error en la redacción: {e}")

# 7. RESULTADOS Y EXPORTACIÓN
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Lógica de Imagen Unsplash (API Oficial)
    url_img = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1000"
    if api_key_unsplash:
        try:
            response = requests.get(f"https://api.unsplash.com/search/photos?query={art['img_keyword']}&client_id={api_key_unsplash}&per_page=1")
            data = response.json()
            if data['results']:
                url_img = data['results'][0]['urls']['regular']
        except:
            pass

    tab1, tab2 = st.tabs(["📄 CÓDIGO FINAL (HTML)", "👁️ VISTA PREVIA SEO"])

    with tab1:
        # Marcado Schema Seguro (evita errores de eñes y acentos)
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta_desc'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Redacción Experta"}
        }
        
        full_html = (
            f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script>\n'
            f'<div style="text-align:center; margin-bottom:25px;">\n'
            f'  <img src="{url_img}" alt="{art["titulo"]}" style="width:100%; max-width:850px; border-radius:15px;"/>\n'
            f'</div>\n'
            f'<h1>{art["titulo"]}</h1>\n'
            f'<p><strong>{art["intro"]}</strong></p>\n'
            f'\n'
            f'{art["cuerpo"]}\n'
            f'<section>\n'
            f'  <h2>Preguntas Frecuentes</h2>\n'
            f'  {art["faq"]}\n'
            f'</section>'
        )
        st.subheader("Copia este código en la 'Vista HTML' de tu entrada:")
        st.code(full_html, language="html")

    with tab2:
        st.write(f"**Slug (URL):** `{art['slug']}`")
        st.write(f"**Etiquetas:** {art['tags']}")
        st.info(f"**Meta descripción:** {art['meta_desc']}")
        st.divider()
        # Renderizado exacto
        st.markdown(full_html, unsafe_allow_html=True)
