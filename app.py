import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Hub Pro - Internacional", layout="wide")

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
    if match:
        return match.group(0)
    return None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre: model = genai.GenerativeModel(modelo_nombre)

st.title("🚀 Hub SEO Internacional: Texto + Imágenes")
st.markdown("Contenido en **español neutro** con métricas y descarga de archivos.")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Importancia de la ciberseguridad")

if idea_usuario and api_key and 'model' in locals():
    try:
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas globales..."):
                prompt_kw = f"Actúe como experto SEO. Para '{idea_usuario}', genere 5 long-tail keywords. Deuelva SOLO JSON: {{'data': [{{'kw': 'ejemplo', 'vol': '1k', 'dif': '20%'}}]}}"
                response = model.generate_content(prompt_kw)
                clean_kw = limpiar_json(response.text)
                if clean_kw:
                    st.session_state.kw_data = json.loads(clean_kw)['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Investigación de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Elija la keyword para su artículo:", opciones)

            if st.button("✨ Generar Contenido Completo"):
                with st.spinner("Redactando contenido y generando 3 imágenes..."):
                    prompt_final = f"""
                    Actúe como redactor SEO senior. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    No mencione países ni use modismos locales.
                    
                    ENTREGUE UN JSON ESTRICTO CON:
                    - h1: Título optimizado.
                    - slug: URL amigable (solo minúsculas y guiones).
                    - meta: Meta descripción.
                    - html_intro: Párrafo inicial potente.
                    - html_desarrollo: Cuerpo con h2 y párrafos (use comillas simples para citas).
                    - html_conclusion: Conclusión.
                    - img_prompts: 3 frases en INGLÉS para imágenes (estilo cinemático, alta calidad).
                    - alt_texts: 3 textos ALT en español neutro.
                    - ig_post: Post para Instagram.
                    - x_thread: Hilo de Twitter.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    clean_art = limpiar_json(res_final.text)
                    
                    if clean_art:
                        data = json.loads(clean_art)
                        
                        # --- PROCESAMIENTO DE IMÁGENES ---
                        imgs = []
                        for i, p in enumerate(data.get('img_prompts', [])):
                            p_safe = urllib.parse.quote(p)
                            url = f"https://pollinations.ai/p/{p_safe}?width=1024&height=768&seed={i+99}&model=flux"
                            imgs.append({"url": url, "alt": data.get('alt_texts', ["Imagen SEO"]*3)[i]})

                        # --- CONSTRUCCIÓN DEL HTML ---
                        html_final = f"""
                        <img src="{imgs[0]['url']}" alt="{imgs[0]['alt']}" style="width:100%; border-radius:12px; margin-bottom:20px;">
                        <p>{data.get('html_intro', '')}</p>
                        <img src="{imgs[1]['url']}" alt="{imgs[1]['alt']}" style="width:100%; border-radius:12px; margin:25px 0;">
                        {data.get('html_desarrollo', '')}
                        <img src="{imgs[2]['url']}" alt="{imgs[2]['alt']}" style="width:100%; border-radius:12px; margin:25px 0;">
                        <p>{data.get('html_conclusion', '')}</p>
                        """

                        t1, t2, t3 = st.tabs(["📝 Blog & SEO", "📸 Instagram", "🐦 X"])
                        
                        with t1:
                            col_info, col_prev = st.columns([1, 2])
                            with col_info:
                                st.subheader("Datos de Publicación")
                                st.text_input("H1 (Título)", data.get('h1'), key="h1_res")
                                st.text_input("Slug (URL)", data.get('slug'), key="slug_res")
                                st.text_area("Meta descripción", data.get('meta'), height=100)
                                
                                # BOTÓN DE DESCARGA
                                st.download_button(
                                    label="💾 Descargar HTML del Post",
                                    data=html_final,
                                    file_name=f"{data.get('slug', 'post')}.html",
                                    mime="text/html"
                                )
                            
                            with col_prev:
                                st.subheader("Vista Previa")
                                st.markdown(f"<h1>{data.get('h1')}</h1>", unsafe_allow_html=True)
                                st.markdown(html_final, unsafe_allow_html=True)
                            
                            st.divider()
                            st.subheader("Código para pegar en Blogger (Vista HTML)")
                            st.code(html_final, language="html")

                        with t2: st.text_area("Instagram", data.get('ig_post'), height=350)
                        with t3: st.text_area("Twitter", data.get('x_thread'), height=350)

    except Exception as e:
        st.error(f"Error detectado: {e}. Por favor, intente de nuevo con el botón 'Generar'.")
