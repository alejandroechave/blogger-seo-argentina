import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Redactor SEO Profesional", layout="wide")

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela en aistudio.google.com")

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
    modelo_detectado = buscar_modelo()
    if modelo_detectado:
        st.sidebar.success(f"Modelo activo: {modelo_detectado}")
        model = genai.GenerativeModel(modelo_detectado)
    else:
        st.sidebar.error("No se encontraron modelos disponibles.")
else:
    st.warning("Cargá tu API Key en la barra lateral.")

st.title("🚀 Redactor SEO Profesional (Tono Equilibrado)")
st.markdown("Contenido optimizado con voseo sutil, ideal para blogs profesionales de Argentina.")

idea_usuario = st.text_input("¿Sobre qué querés escribir hoy?")

if idea_usuario and api_key and 'model' in locals():
    try:
        # PASO 1: Keywords
        if 'keywords' not in st.session_state:
            with st.spinner("Analizando tendencias..."):
                prompt_kw = f"""Generá 5 palabras clave de cola larga para el mercado argentino sobre: '{idea_usuario}'. 
                Buscá términos que la gente realmente use en buscadores. 
                Devolvé SOLO un JSON: {{"kw": ["1", "2", "3", "4", "5"]}}"""
                
                response = model.generate_content(prompt_kw)
                match_kw = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match_kw:
                    st.session_state.keywords = json.loads(match_kw.group())['kw']

        if 'keywords' in st.session_state:
            seleccion = st.radio("Elegí el enfoque SEO:", st.session_state.keywords)

            if st.button("Generar Artículo"):
                with st.spinner("Redactando contenido profesional..."):
                    # EL PROMPT AJUSTADO (MÁS NEUTRO/PROFESIONAL)
                    prompt_art = f"""
                    Actuá como un redactor senior de un portal de noticias o blog profesional en Argentina.
                    Escribí un post optimizado para SEO sobre: '{seleccion}'.

                    REGLAS DE ESTILO:
                    1. Usá voseo sutil (ej: 'tenés', 'podés', 'buscás'). Es obligatorio pero no debe ser informal.
                    2. Tono: Profesional, informativo y serio. Evitá modismos como 'che', 'laburo', 'plata', 'copado' o 'canchero'.
                    3. Estructura: Introducción clara, subtítulos (H2, H3) informativos y una conclusión con llamado a la acción.
                    4. Prohibido: Usar frases trilladas de IA como 'en el vasto mundo de' o 'es fundamental recordar'.

                    FORMATO DE SALIDA: Devolvé EXCLUSIVAMENTE un JSON con estas llaves:
                    h1, slug (url amigable), meta (descripción SEO), labels (etiquetas), html (el cuerpo del post).
                    """
                    
                    res_final = model.generate_content(prompt_final if 'prompt_final' in locals() else prompt_art)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        st.divider()
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.subheader("Configuración")
                            st.text_input("Título H1", data.get('h1', ''))
                            st.text_input("Slug/URL", data.get('slug', ''))
                            st.text_area("Meta Descripción", data.get('meta', ''), height=120)
                            st.text_input("Etiquetas", data.get('labels', ''))
                        with col2:
                            st.subheader("Vista Previa")
                            st.markdown(data.get('html', ''), unsafe_allow_html=True)
                        st.divider()
                        st.subheader("Código HTML para copiar en Blogger")
                        st.code(data.get('html', ''), language="html")
                    else:
                        st.error("La IA no devolvió el formato esperado. Por favor, intentá de nuevo.")
    except Exception as e:
        st.error(f"Error: {e}")

elif not api_key:
    st.info("Ingresá tu API Key para comenzar a trabajar.")
