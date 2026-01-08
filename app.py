import streamlit as st
from groq import Groq
import json
import re
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Redactor SEO Pro", layout="wide")

def clean_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

# --- APP ---
st.title("🚀 Redactor SEO con Imágenes Estables")

tema = st.text_input("¿Qué quieres escribir hoy?", placeholder="Ej: Mejores herramientas IA 2026")

if tema and api_key:
    # 1. KEYWORDS
    if st.button("🔍 1. Buscar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
            chat_kw = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(clean_json(chat_kw.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error en keywords: {e}")

    if 'kw_list' in st.session_state:
        st.subheader("📊 Keywords Sugeridas")
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Selecciona la Keyword Principal:", [i['kw'] for i in st.session_state.kw_list])

        # 2. ARTÍCULO E IMÁGENES
        if st.button("✨ 2. Generar Artículo Completo"):
            try:
                with st.spinner("Redactando y diseñando imágenes..."):
                    prompt_art = f"""
                    Actúa como Redactor SEO. Escribe sobre '{seleccion}'.
                    Devuelve SOLO JSON con:
                    - h1: título
                    - intro: párrafo
                    - desarrollo: HTML (h2 y p)
                    - slug: url-amigable
                    - img_concept: concepto de 2 palabras en INGLES (ej: 'modern laptop')
                    - alt: texto alternativo
                    """
                    chat_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    art = json.loads(clean_json(chat_art.choices[0].message.content))

                    # --- SISTEMA DE IMAGEN ESTABLE ---
                    # Limpiamos el concepto para que la URL sea infalible
                    clean_concept = re.sub(r'[^a-zA-Z]', '-', art['img_concept']).lower()
                    # Usamos una URL de Pollinations que Blogger acepta mejor
                    img_url = f"https://pollinations.ai/p/{clean_concept}?width=1080&height=720&nologo=true"

                    # --- CONSTRUCCIÓN HTML ---
                    html_final = f"""
<div style="text-align: center; margin-bottom: 20px;">
    <img alt="{art['alt']}" src="{img_url}" style="width: 100%; max-width: 800px; border-radius: 10px;" />
</div>

<h2>{art['h1']}</h2>
<p><i>{art['intro']}</i></p>

{art['development'] if 'development' in art else art['desarrollo']}

<div style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px;">
    <p><strong>Palabra Clave:</strong> {seleccion}</p>
</div>
"""

                    # --- VISTA DE RESULTADOS ---
                    st.divider()
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Vista Previa")
                        st.markdown(html_final, unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("Código para Blogger")
                        st.info("Copia esto y pégalo en la 'Vista HTML' de tu entrada.")
                        st.code(html_final, language="html")

            except Exception as e:
                st.error(f"Error en redacción: {e}")

else:
    st.info("Ingresa tu API Key de Groq y un tema para empezar.")
