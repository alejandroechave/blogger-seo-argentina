import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="Blogger SEO Master AR", layout="wide")

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela en aistudio.google.com")

def buscar_modelo():
    try:
        # Listamos los modelos disponibles para tu clave
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return None
    return None

if api_key:
    genai.configure(api_key=api_key)
    # Autodetectamos el modelo disponible
    modelo_detectado = buscar_modelo()
    
    if modelo_detectado:
        st.sidebar.success(f"Modelo activo: {modelo_detectado}")
        model = genai.GenerativeModel(modelo_detectado)
    else:
        st.sidebar.error("No se encontraron modelos disponibles. ¿Es válida la API Key?")
else:
    st.warning("Cargá tu API Key en la barra lateral.")

st.title("🚀 Generador SEO Blogger - Modo Argentina")

idea_usuario = st.text_input("Introducí tu idea:")

if idea_usuario and api_key and 'model' in locals():
    try:
        # PASO 1: Keywords
        if 'keywords' not in st.session_state:
            with st.spinner("Buscando keywords..."):
                prompt_kw = f"Generá 5 palabras clave de cola larga para Argentina sobre: '{idea_usuario}'. Devolvé SOLO un JSON: {{\"kw\": [\"1\", \"2\", \"3\", \"4\", \"5\"]}}"
                response = model.generate_content(prompt_kw)
                match_kw = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match_kw:
                    st.session_state.keywords = json.loads(match_kw.group())['kw']

        if 'keywords' in st.session_state:
            seleccion = st.radio("Elegí una palabra clave:", st.session_state.keywords)

            if st.button("Generar Artículo"):
                with st.spinner("Redactando post argentino..."):
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
                        with col2:
                            st.subheader("Vista Previa")
                            st.markdown(data.get('html', ''), unsafe_allow_html=True)
                        st.divider()
                        st.code(data.get('html', ''), language="html")
    except Exception as e:
        st.error(f"Error detectado: {e}")
