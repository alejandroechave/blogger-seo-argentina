import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Blogger SEO Master AR", layout="wide")

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela gratis en aistudio.google.com")

if api_key:
    try:
        # Forzamos la configuración básica
        genai.configure(api_key=api_key)
        # Usamos el nombre más simple del modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")

st.title("🚀 Generador SEO Blogger - Modo Argentina")

idea_usuario = st.text_input("Introducí tu idea o el link de referencia:")

if idea_usuario and api_key:
    try:
        # PASO 1: Keywords
        if 'keywords' not in st.session_state:
            prompt_kw = f"Generá 5 palabras clave de cola larga para Argentina sobre: '{idea_usuario}'. Devolvé SOLO un JSON: {{\"kw\": [\"1\", \"2\", \"3\", \"4\", \"5\"]}}"
            response = model.generate_content(prompt_kw)
            
            # Buscamos el JSON de forma más robusta
            match_kw = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match_kw:
                st.session_state.keywords = json.loads(match_kw.group())['kw']
            else:
                st.error("No se pudo obtener el formato de palabras clave. Intentá de nuevo.")

        if 'keywords' in st.session_state:
            seleccion = st.radio("Elegí una palabra clave:", st.session_state.keywords)

            if st.button("Generar Artículo"):
                with st.spinner("Redactando..."):
                    prompt_art = f"Actuá como redactor argentino (usá voseo). Escribí un post para Blogger sobre: '{seleccion}'. Devolvé SOLO un JSON con: h1, slug, meta, labels, html."
                    res_final = model.generate_content(prompt_art)
                    
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    if match_art:
                        data = json.loads(match_art.group())
                        
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Título (H1)", data.get('h1', ''))
                            st.text_input("Slug", data.get('slug', ''))
                            st.text_area("Meta", data.get('meta', ''))
                            st.text_input("Etiquetas", data.get('labels', ''))
                        with col2:
                            st.subheader("Vista Previa")
                            st.markdown(data.get('html', ''), unsafe_allow_html=True)
                        
                        st.divider()
                        st.code(data.get('html', ''), language="html")
                    else:
                        st.error("Error en el formato del artículo.")

    except Exception as e:
        # Si el error es 404, probamos con el nombre alternativo automáticamente
        if "404" in str(e):
            st.error("Error de conexión con el modelo. Intentá cambiar 'gemini-1.5-flash' por 'gemini-pro' en el código.")
        else:
            st.error(f"Error: {e}")

elif not api_key:
    st.warning("Cargá tu API Key en la barra lateral.")
