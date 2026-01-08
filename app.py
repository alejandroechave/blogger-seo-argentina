import streamlit as st
from groq import Groq
import json
import re

st.set_page_config(page_title="Blogger SEO Fix", layout="wide")

# --- FUNCIONES DE APOYO ---
def get_model(client):
    return "llama-3.3-70b-versatile" # Forzamos el mejor modelo

def clean_url(text):
    # Limpia el texto para que la URL de la imagen sea ultra simple
    return re.sub(r'[^a-z]', '-', text.lower()).strip('-')

# --- CONFIGURACIÓN ---
with st.sidebar:
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Redactor Pro para Blogger (LiteSpot Fix)")

tema = st.text_input("Tema del post:")

if tema and api_key:
    if st.button("Generar Post e Imágenes"):
        try:
            with st.spinner("Creando contenido..."):
                prompt = f"""Escribe un post SEO sobre '{tema}'. 
                Responde SOLO con un JSON: 
                {{
                  "titulo": "...", 
                  "cuerpo": "HTML con h2 y p", 
                  "img_keyword": "2 palabras en ingles para la foto",
                  "meta": "resumen 150 carac"
                }}"""
                
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(res.choices[0].message.content)
                
                # --- GENERADOR DE IMAGEN ULTRA-SIMPLE (FIX PARA LITESPOT) ---
                kw_limpia = clean_url(data['img_keyword'])
                # Usamos una URL de pollinations sin parámetros complejos que rompan el feed de Blogger
                img_url = f"https://pollinations.ai/p/{kw_limpia}.jpg" 

                # --- HTML FINAL COMPATIBLE CON BLOGGER ---
                # Importante: Usamos la estructura que Blogger prefiere para miniaturas
                html_blogger = f"""
<div class="separator" style="clear: both; text-align: center;">
<a href="{img_url}" imageanchor="1" style="margin-left: 1em; margin-right: 1em;">
<img border="0" src="{img_url}" width="640" height="480" data-original-width="1024" data-original-height="768" />
</a>
</div>

<br/>
{data['cuerpo']}

<p><strong>Resumen:</strong> {data['meta']}</p>
"""
                
                st.subheader(data['titulo'])
                st.markdown(html_blogger, unsafe_allow_html=True)
                
                st.divider()
                st.subheader("📋 Código para copiar en Blogger")
                st.info("Copia el código de abajo. En Blogger, crea una 'Nueva Entrada', cambia a 'Vista HTML' y pega esto.")
                st.code(html_blogger, language="html")

        except Exception as e:
            st.error(f"Error: {e}")
