import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd # Agregamos pandas para la tablita

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Master Pro AR", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela en [aistudio.google.com](https://aistudio.google.com)")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return None
    return None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre: model = genai.GenerativeModel(modelo_nombre)

st.title("🚀 SEO Content Hub Profesional")
st.markdown("Investigación de palabras clave y redacción multicanal.")

idea_usuario = st.text_input("¿Qué tema querés investigar?", placeholder="Ej: Mejores tarjetas de crédito Argentina")

if idea_usuario and 'model' in locals():
    try:
        # PASO 1: KEYWORD RESEARCH CON MÉTRICAS
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando mercado y competencia..."):
                prompt_kw = f"""Actuá como herramienta SEO (tipo Semrush). 
                Para el tema '{idea_usuario}' en Argentina, generá 5 variaciones de cola larga.
                Para cada una, estimá:
                1. Volumen mensual de búsquedas (ej: 1.5k).
                2. Dificultad SEO (0-100%).
                
                Devolvé SOLO un JSON estrictamente así:
                {{"data": [
                    {{"kw": "ejemplo 1", "vol": "1.2k", "dif": "25%"}},
                    {{"kw": "ejemplo 2", "vol": "800", "dif": "40%"}}
                ]}}"""
                
                response = model.generate_content(prompt_kw)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    st.session_state.kw_data = json.loads(match.group())['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Análisis de Palabras Clave (Estimado)")
            df = pd.DataFrame(st.session_state.kw_data)
            df.columns = ["Palabra Clave", "Vol. Búsqueda", "Dificultad (KD)"]
            st.table(df) # Mostramos la tabla linda

            # Selección de la Keyword
            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Elegí la Keyword para el artículo:", opciones)

            if st.button("✨ Generar Contenido Completo"):
                with st.spinner("Redactando artículo y posts sociales..."):
                    prompt_final = f"""
                    Redactor profesional argentino. Tema: '{seleccion}'.
                    Generá un JSON con:
                    - h1: Título SEO.
                    - html: Post para Blogger (profesional, voseo sutil).
                    - meta: Meta descripción.
                    - ig_post: Post para Instagram.
                    - x_thread: Hilo de Twitter.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        st.divider()
                        t1, t2, t3 = st.tabs(["📝 Blog", "📸 Instagram", "🐦 X"])
                        with t1:
                            st.header(data.get('h1'))
                            st.markdown(data.get('html'), unsafe_allow_html=True)
                            st.code(data.get('html'), language="html")
                        with t2:
                            st.text_area("Copiá para IG:", data.get('ig_post'), height=300)
                        with t3:
                            st.text_area("Copiá para X:", data.get('x_thread'), height=300)

    except Exception as e:
        st.error(f"Error: {e}")
