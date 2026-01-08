import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Blogger SEO Master AR", layout="wide")

# Sidebar para la API Key
with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela gratis en aistudio.google.com")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Este es el nombre exacto que Google pide en 2026
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"Error al configurar la API: {e}")

st.title("🚀 Generador SEO Blogger - Modo Argentina")
st.markdown("Generá artículos que rankean, con voseo y listos para publicar.")

# --- PASO 1: INPUT ---
idea_usuario = st.text_input("Introducí tu idea o el link de referencia:", placeholder="Ej: Las mejores billeteras virtuales 2026")

if idea_usuario and api_key:
    try:
        # Lógica de Investigación de Keywords
        if 'keywords' not in st.session_state:
            prompt_kw = f"""Generá 5 palabras clave de cola larga para Argentina sobre: '{idea_usuario}'. 
            Devolvé SOLO un JSON: {{"kw": ["opcion1", "opcion2", "opcion3", "opcion4", "opcion5"]}}"""
            
            response = model.generate_content(prompt_kw)
            clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
            st.session_state.keywords = json.loads(clean_json)['kw']

        # --- PASO 2: SELECCIÓN ---
        st.subheader("1. Elegí la palabra clave para trabajar:")
        seleccion = st.radio("Sugerencias de cola larga:", st.session_state.keywords)

        if st.button("Generar Artículo Completo"):
            with st.spinner("Redactando con onda argentina..."):
                prompt_final = f"""
                Actuá como redactor argentino (usá voseo: vos, tenés, hacé). 
                Escribí un post para Blogger sobre: '{seleccion}'. 
                No uses clichés de IA. Devolvé SOLO un JSON con estas llaves: 
                h1, slug, meta, labels, html.
                """
                
                res_final = model.generate_content(prompt_final)
                match = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                if match:
                    data = json.loads(match.group())

                    st.divider()
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("Datos de Configuración")
                        st.text_input("Título (H1)", data.get('h1', ''), key="h1_out")
                        st.text_input("Enlace (Slug)", data.get('slug', ''), key="slug_out")
                        st.text_area("Meta Descripción", data.get('meta', ''), height=100)
                        st.text_input("Etiquetas", data.get('labels', ''))
                        
                    with col2:
                        st.subheader("Vista Previa")
                        st.markdown(data.get('html', ''), unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("Código HTML para Blogger")
                    st.code(data.get('html', ''), language="html")
                    st.success("¡Listo! Copiá y pegá en la vista HTML de Blogger.")
    
    except Exception as e:
        st.error(f"Error: {e}")

elif not api_key:
    st.warning("Por favor, cargá tu API Key en la barra lateral.")
