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
        # Usamos el nombre completo del modelo para evitar el error NotFound
        model = genai.GenerativeModel('models/gemini-1.5-flash')
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
            prompt_kw = f"""Actuá como experto SEO. Basado en: '{idea_usuario}', generá 5 palabras clave de cola larga (long-tail) para Argentina. 
            Devolveme SOLO un JSON con este formato: {{"kw": ["opcion1", "opcion2", "opcion3", "opcion4", "opcion5"]}}"""
            
            response = model.generate_content(prompt_kw)
            # Limpieza del JSON
            clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
            st.session_state.keywords = json.loads(clean_json)['kw']

        # --- PASO 2: SELECCIÓN ---
        st.subheader("1. Elegí la palabra clave para trabajar:")
        seleccion = st.radio("Sugerencias de cola larga:", st.session_state.keywords)

        if st.button("Generar Artículo Completo"):
            with st.spinner("Redactando con onda argentina..."):
                # --- PASO 3: GENERACIÓN FINAL ---
                prompt_final = f"""
                Sos un redactor senior argentino. Escribí un post para Blogger sobre: '{seleccion}'.
                REGLAS:
                1. Usá voseo (vos, tenés, hacé). Tono cercano y experto.
                2. Prohibido: 'adentrarse', 'crucial', 'vasto mundo'.
                3. Formato: JSON estricto.
                {{
                    "h1": "Título magnético",
                    "slug": "url-amigable-sin-conectores",
                    "meta": "Descripción 150 caracteres con CTA",
                    "labels": "etiqueta1, etiqueta2, etiqueta3",
                    "html": "Contenido en HTML usando h2, h3, p, strong, ul, li. Sin etiquetas html ni body."
                }}
                """
                
                res_final = model.generate_content(prompt_final)
                data_json = re.search(r'\{.*\}', res_final.text, re.DOTALL).group()
                data = json.loads(data_json)

                # --- PASO 4: RESULTADOS ---
                st.divider()
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.subheader("Datos de Configuración")
                    st.text_input("Título (H1)", data['h1'], key="h1_out")
                    st.text_input("Enlace (Slug)", data['slug'], key="slug_out")
                    st.text_area("Meta Descripción", data['meta'], height=100)
                    st.text_input("Etiquetas", data['labels'])
                    
                with col2:
                    st.subheader("Vista Previa (HTML)")
                    st.markdown(data['html'], unsafe_allow_html=True)
                
                st.divider()
                st.subheader("Código HTML para Blogger")
                st.code(data['html'], language="html")
                st.success("¡Listo! Copiá y pegá en la vista HTML de tu entrada de Blogger.")
    
    except Exception as e:
        st.error(f"Hubo un problema al procesar la solicitud: {e}")
        st.info("Asegurate de que tu API Key sea válida y que tengas conexión a internet.")

elif not api_key:
    st.warning("Por favor, cargá tu API Key en la barra lateral para empezar.")
