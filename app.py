import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Global Pro", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return None
    return None

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre: model = genai.GenerativeModel(modelo_nombre)

st.title("🚀 Hub SEO Internacional: Texto + Estrategia Visual")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Energía nuclear segura")

if idea_usuario and api_key and 'model' in locals():
    try:
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas..."):
                prompt_kw = f"Actúe como experto SEO. Para '{idea_usuario}', genere 5 long-tail keywords. Deuelva SOLO JSON: {{'data': [{{'kw': 'ejemplo', 'vol': '1k', 'dif': '20%'}}]}}"
                response = model.generate_content(prompt_kw)
                clean_kw = limpiar_json(response.text)
                if clean_kw: st.session_state.kw_data = json.loads(clean_kw)['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Investigación de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Elija la keyword:", opciones)

            if st.button("✨ Generar Contenido y Guía Visual"):
                with st.spinner("Redactando post profesional..."):
                    prompt_final = f"""
                    Actúe como experto SEO. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    
                    ENTREGUE UN JSON CON:
                    - h1, slug, meta.
                    - html_intro, html_desarrollo, html_conclusion.
                    - img_prompts: Lista de 3 frases en INGLÉS detalladas para generar imágenes IA.
                    - alt_texts: Lista de 3 textos ALT en español.
                    - ig_post, x_thread.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    data = json.loads(limpiar_json(res_final.text))
                    
                    t1, t2, t3, t4 = st.tabs(["📝 Blog & SEO", "🎨 Guía de Imágenes", "📸 Instagram", "🐦 X"])
                    
                    with t1:
                        # Marcadores de posición visuales
                        placeholder_img = "https://placehold.co/800x450/2c3e50/ffffff?text="
                        
                        html_final = f"""
                        <div style="background:#eee; padding:20px; text-align:center; border-radius:10px;">[IMAGEN PRINCIPAL: {data['alt_texts'][0]}]</div>
                        <p>{data['html_intro']}</p>
                        <div style="background:#eee; padding:20px; text-align:center; border-radius:10px; margin:20px 0;">[IMAGEN 2: {data['alt_texts'][1]}]</div>
                        {data['html_desarrollo']}
                        <div style="background:#eee; padding:20px; text-align:center; border-radius:10px; margin:20px 0;">[IMAGEN 3: {data['alt_texts'][2]}]</div>
                        <p>{data['html_conclusion']}</p>
                        """
                        
                        col_i, col_p = st.columns([1, 2])
                        with col_i:
                            st.text_input("H1", data['h1'])
                            st.text_input("Slug", data['slug'])
                            st.text_area("Meta", data['meta'])
                            st.download_button("💾 Descargar HTML", html_final, file_name=f"{data['slug']}.html")
                        with col_p:
                            st.markdown(f"<h1>{data['h1']}</h1>", unsafe_allow_html=True)
                            st.markdown(html_final, unsafe_allow_html=True)
                        st.code(html_final, language="html")

                    with t2:
                        st.subheader("🖼️ Instrucciones para generar tus imágenes")
                        st.write("Copiá estos prompts en [Leonardo.ai](https://leonardo.ai/) o [Bing Image Creator](https://www.bing.com/images/create):")
                        for i, p in enumerate(data['img_prompts']):
                            st.info(f"**Imagen {i+1}:** {p}")
                            st.caption(f"Texto ALT recomendado: {data['alt_texts'][i]}")

                    with t3: st.text_area("IG", data['ig_post'], height=300)
                    with t4: st.text_area("X", data['x_thread'], height=300)
    except Exception as e:
        st.error(f"Error: {e}")
