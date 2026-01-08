import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Global & Multi-Image AI", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela en [aistudio.google.com](https://aistudio.google.com)")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return None
    return None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre:
        model = genai.GenerativeModel(modelo_nombre)
    else:
        st.sidebar.error("No se encontró el modelo.")

st.title("🚀 Hub SEO Internacional con Imágenes Automáticas")
st.markdown("Generación de artículos en **español neutro** con **3 imágenes reales** integradas.")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Avances en energía renovable")

if idea_usuario and api_key and 'model' in locals():
    try:
        # PASO 1: KEYWORDS (Corregido el error de f-string)
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas..."):
                # Usamos llaves dobles {{ }} para que Python no las confunda con variables
                prompt_kw = f"Actúe como experto SEO. Para '{idea_usuario}', genere 5 long-tail keywords. Devuelva SOLO JSON: {{'data': [{{'kw': 'ejemplo', 'vol': '1k', 'dif': '20%'}}]}}"
                response = model.generate_content(prompt_kw)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    st.session_state.kw_data = json.loads(match.group())['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Análisis de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            df.columns = ["Palabra Clave", "Vol. Búsqueda", "Dificultad (KD)"]
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Seleccione la palabra clave:", opciones)

            if st.button("✨ Generar Contenido e Imágenes"):
                with st.spinner("Redactando y creando 3 imágenes..."):
                    # Prompt final corregido con dobles llaves
                    prompt_final = f"""
                    Actúe como experto SEO global. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    No mencione países. 
                    ENTREGUE UN JSON CON:
                    - h1: Título.
                    - slug: URL amigable.
                    - meta: Meta descripción.
                    - html_intro: Párrafo de introducción.
                    - html_desarrollo: Cuerpo del post con h2 y párrafos.
                    - html_conclusion: Conclusión final.
                    - img_prompts: Lista de 3 frases en INGLÉS para generar imágenes.
                    - alt_texts: Lista de 3 textos ALT en español.
                    - ig_post: Post para Instagram.
                    - x_thread: Hilo de Twitter.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        
                        # --- GENERAR LAS 3 URLs DE IMÁGENES ---
                        imgs = []
                        for i, p in enumerate(data.get('img_prompts', [])):
                            encoded_prompt = urllib.parse.quote(p)
                            url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=768&seed={i+50}&model=flux"
                            imgs.append({{"url": url, "alt": data.get('alt_texts', ["Imagen SEO"]*3)[i]}})

                        # --- CONSTRUIR EL HTML FINAL ---
                        html_completo = f"""
                        <p>{data.get('html_intro', '')}</p>
                        <img src="{imgs[0]['url']}" alt="{imgs[0]['alt']}" style="width:100%; border-radius:10px; margin:20px 0;">
                        {data.get('html_desarrollo', '')}
                        <img src="{imgs[1]['url']}" alt="{imgs[1]['alt']}" style="width:100%; border-radius:10px; margin:20px 0;">
                        <img src="{imgs[2]['url']}" alt="{imgs[2]['alt']}" style="width:100%; border-radius:10px; margin:20px 0;">
                        <p>{data.get('html_conclusion', '')}</p>
                        """

                        t1, t2, t3 = st.tabs(["📝 Blog & SEO", "📸 Instagram", "🐦 X"])
                        
                        with t1:
                            col_a, col_b = st.columns([1, 2])
                            with col_a:
                                st.subheader("Parámetros SEO")
                                st.text_input("H1", data.get('h1'))
                                st.text_input("Slug", data.get('slug'))
                                st.text_area("Meta", data.get('meta'))
                            
                            with col_b:
                                st.subheader("Vista Previa")
                                st.markdown(f"<h1>{data.get('h1')}</h1>", unsafe_allow_html=True)
                                st.markdown(html_completo, unsafe_allow_html=True)
                            
                            st.divider()
                            st.subheader("Código HTML para Blogger")
                            st.code(html_completo, language="html")

                        with t2:
                            st.text_area("Instagram", data.get('ig_post'), height=300)
                        with t3:
                            st.text_area("Twitter", data.get('x_thread'), height=300)
    except Exception as e:
        st.error(f"Error: {e}")
