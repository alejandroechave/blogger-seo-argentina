import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import time # Importante para la espera entre reintentos

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Global Pro", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Error 429? Esperá 60 segundos y reintentá. La versión gratuita tiene límites de velocidad.")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return None
    return None

def llamar_gemini_con_reintento(prompt, model, max_retries=3):
    """Función para manejar el error 429 y reintentar automáticamente."""
    for i in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                st.warning(f"Límite de velocidad alcanzado. Reintentando en {i+2} segundos...")
                time.sleep(i + 2)
            else:
                raise e

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre: model = genai.GenerativeModel(modelo_nombre)

st.title("🚀 Hub SEO Internacional")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Energía limpia")

if idea_usuario and api_key and 'model' in locals():
    try:
        # PASO 1: KEYWORDS
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas (respetando límites de la API)..."):
                prompt_kw = f"Actúe como experto SEO. Para '{idea_usuario}', genere 5 long-tail keywords. Deuelva SOLO JSON: {{'data': [{{'kw': 'ejemplo', 'vol': '1k', 'dif': '20%'}}]}}"
                response = llamar_gemini_con_reintento(prompt_kw, model)
                clean_kw = limpiar_json(response.text)
                if clean_kw: st.session_state.kw_data = json.loads(clean_kw)['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Investigación de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Elija la keyword:", opciones)

            if st.button("✨ Generar Contenido"):
                with st.spinner("Redactando post... Esto puede tardar por los límites de la API."):
                    prompt_final = f"""
                    Actúe como experto SEO. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    ENTREGUE UN JSON CON:
                    - h1, slug, meta.
                    - html_intro, html_desarrollo, html_conclusion.
                    - img_prompts: Lista de 3 frases en INGLÉS para imágenes IA.
                    - alt_texts: Lista de 3 textos ALT en español.
                    - ig_post, x_thread.
                    """
                    
                    res_final = llamar_gemini_con_reintento(prompt_final, model)
                    data = json.loads(limpiar_json(res_final.text))
                    
                    # --- PRESENTACIÓN ---
                    t1, t2 = st.tabs(["📝 Blog & SEO", "📸 Redes Sociales"])
                    
                    with t1:
                        html_vireview = f"<h3>{data['h1']}</h3><p>{data['html_intro']}</p>{data['html_desarrollo']}<p>{data['html_conclusion']}</p>"
                        st.text_input("Slug", data['slug'])
                        st.text_area("Meta", data['meta'])
                        st.markdown(html_vireview, unsafe_allow_html=True)
                        st.code(html_vireview, language="html")
                        
                    with t2:
                        st.subheader("Instagram")
                        st.write(data['ig_post'])
                        st.subheader("Twitter")
                        st.write(data['x_thread'])
    except Exception as e:
        if "429" in str(e):
            st.error("La API de Google está muy ocupada. Por favor, espera 1 minuto completo antes de hacer clic de nuevo.")
        else:
            st.error(f"Error: {e}")
