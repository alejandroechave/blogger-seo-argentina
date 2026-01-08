import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Creador de Contenido Visual + Imágenes", layout="wide")

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

st.title("🚀 Centro de Contenido Visual y SEO Profesional")
st.markdown("Investigación de palabras clave, redacción neutra, y **generación de imágenes**.")

idea_usuario = st.text_input("¿Sobre qué quiere crear contenido visual y escrito?", placeholder="Ej: Las maravillas del universo en la era espacial")

if idea_usuario and 'model' in locals():
    try:
        # PASO 1: KEYWORD RESEARCH CON MÉTRICAS
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas de búsqueda..."):
                prompt_kw = f"""Actúe como una herramienta de análisis SEO profesional. 
                Para el tema '{idea_usuario}', genere 5 variaciones de palabras clave de cola larga.
                Para cada una, estime:
                1. Volumen mensual de búsquedas globales.
                2. Dificultad SEO (0-100%).
                
                Devuelva ÚNICAMENTE un objeto JSON con este formato:
                {{"data": [
                    {{"kw": "palabra clave", "vol": "cantidad", "dif": "porcentaje"}},
                    ...
                ]}}"""
                
                response = model.generate_content(prompt_kw)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    st.session_state.kw_data = json.loads(match.group())['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Análisis de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            df.columns = ["Palabra Clave", "Vol. Búsqueda Est.", "Dificultad (KD)"]
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Seleccione la palabra clave para su artículo:", opciones)

            if st.button("✨ Generar Contenido + Imágenes..."):
                with st.spinner("Creando artículo, redes e imágenes mágicamente..."):
                    prompt_final = f"""
                    Actúe como un redactor SEO profesional y generador de contenido visual. 
                    Tema: '{seleccion}'.

                    REGLAS DE REDACCIÓN:
                    1. Idioma: ESPAÑOL NEUTRO (evite regionalismos, voseo o términos locales).
                    2. No mencione a ningún país o región específica. El contenido debe ser global.
                    3. Tono: Informativo, profesional y directo.

                    ENTREGUE EXCLUSIVAMENTE UN OBJETO JSON CON ESTAS LLAVES:
                    - h1: Título optimizado para SEO.
                    - slug: URL amigable sin conectores o preposiciones.
                    - meta: Meta descripción de máximo 155 caracteres, con llamado a la acción.
                    - labels: 3 o 4 etiquetas relevantes separadas por comas.
                    - html: Cuerpo del post usando etiquetas HTML (h2, h3, p, strong, ul, li).
                      **IMPORTANTE:** Inserte el tag `http://googleusercontent.com/image_generation_content/1

` en cada lugar donde iría una imagen (mínimo 3, máximo 5 imágenes). Después de cada `http://googleusercontent.com/image_generation_content/2

` debe ir una descripción de imagen con el formato `<p>Alt: Descripción detallada para la imagen de arriba.</p>`.
                    - ig_post: Post para Instagram con emojis y hashtags.
                    - x_thread: Hilo de Twitter (mínimo 3 tweets numerados).
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        
                        st.divider()
                        
                        # --- PRESENTACIÓN DE RESULTADOS ---
                        tab_blog, tab_ig, tab_x = st.tabs(["📝 Blog & SEO", "📸 Instagram", "🐦 X (Twitter)"])
                        
                        with tab_blog:
                            col_seo, col_preview = st.columns([1, 2])
                            with col_seo:
                                st.subheader("Parámetros SEO")
                                st.text_input("Título H1", data.get('h1', ''))
                                st.text_input("URL Slug", data.get('slug', ''))
                                st.text_area("Meta Descripción", data.get('meta', ''), height=100)
                                st.text_input("Etiquetas / Labels", data.get('labels', ''))
                                
                                st.subheader("Descripciones de Imágenes")
                                # Extraer y mostrar los textos ALT
                                alt_texts = re.findall(r'<p>Alt: (.*?)</p>', data.get('html', ''))
                                for i, alt_text in enumerate(alt_texts):
                                    st.text_area(f"Imagen {i+1} (ALT)", alt_text, height=70, key=f"alt_img_{i}")
                            
                            with col_preview:
                                st.subheader("Vista Previa del Blog")
                                st.markdown(f"<h1>{data.get('h1', '')}</h1>", unsafe_allow_html=True)
                                
                                # Reemplazar el tag `
` con la imagen generada
                                final_html = data.get('html', '')
                                # No necesitamos el reemplazo del `
` aquí, el modelo lo manejará automáticamente.
                                # El importante es que el tag `
` esté en el HTML que se envía.
                                st.markdown(final_html, unsafe_allow_html=True) # El modelo se encarga de reemplazar el `
`

                            st.divider()
                            st.subheader("Código HTML para Blogger (¡Con imágenes!)")
                            st.code(data.get('html', ''), language="html")
                        
                        with tab_ig:
                            st.subheader("Contenido para Redes Sociales")
                            st.text_area("Copia para Instagram/FB:", data.get('ig_post', ''), height=300)
                        
                        with tab_x:
                            st.subheader("Hilo para X")
                            st.text_area("Copié el hilo:", data.get('x_thread', ''), height=300)

                    else:
                        st.error("La IA no devolvió el formato correcto. Por favor, intente de nuevo.")
    
    except Exception as e:
        st.error(f"Se produjo un error al procesar la solicitud: {e}")
