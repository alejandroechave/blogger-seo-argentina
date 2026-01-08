import streamlit as st
import google.generativeai as genai
import json
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Creador de Contenido 360", layout="wide")

# Estilo personalizado para mejorar la visualización
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextArea textarea {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela gratis en: [aistudio.google.com](https://aistudio.google.com)")

# Función para encontrar el modelo disponible en tu cuenta
def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return None
    return None

# Lógica de Inicialización
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        modelo_nombre = buscar_modelo()
        if modelo_nombre:
            model = genai.GenerativeModel(modelo_nombre)
            st.sidebar.success(f"Modelo activo: {modelo_nombre}")
        else:
            st.sidebar.error("No se encontraron modelos disponibles.")
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Generador Multi-Canal")
st.markdown("Escribí un artículo para tu **Blog** y obtené automáticamente los posteos para **Redes Sociales**.")

idea_usuario = st.text_input("¿Sobre qué tema querés crear contenido?", placeholder="Ej: Cómo invertir en Cedears desde Argentina")

if idea_usuario and model:
    try:
        # PASO 1: Investigación de Keywords (SEO)
        if 'keywords' not in st.session_state:
            with st.spinner("Buscando las mejores keywords para Argentina..."):
                prompt_kw = f"""Actuá como experto SEO. Generá 5 palabras clave de cola larga para Argentina sobre: '{idea_usuario}'. 
                Devolvé SOLO un objeto JSON: {{"kw": ["opcion1", "opcion2", "opcion3", "opcion4", "opcion5"]}}"""
                
                response = model.generate_content(prompt_kw)
                match_kw = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match_kw:
                    st.session_state.keywords = json.loads(match_kw.group())['kw']

        if 'keywords' in st.session_state:
            st.subheader("1. Elegí el enfoque SEO")
            seleccion = st.radio("Sugerencias de búsqueda real:", st.session_state.keywords)

            if st.button("✨ Generar Contenido Completo"):
                with st.spinner("Redactando artículo y redes sociales..."):
                    # EL PROMPT MAESTRO: Blog + IG + X
                    prompt_final = f"""
                    Sos un redactor profesional senior de Argentina. 
                    Tema: '{seleccion}'.

                    REGLAS DE ESTILO:
                    - Usá voseo profesional (vos, tenés, podés). 
                    - Tono: Educativo, serio y confiable. Sin modismos exagerados (nada de "che" o "laburo").

                    ENTREGÁ EXCLUSIVAMENTE UN JSON CON ESTAS LLAVES:
                    - h1: Título impactante para el blog.
                    - html: Cuerpo del post para Blogger (usá h2, h3, p, strong, ul, li).
                    - meta: Meta descripción de 150 caracteres para Google.
                    - ig_post: Post para Instagram/FB con emojis, ganchos de lectura y hashtags.
                    - x_thread: Un hilo de X (Twitter) de 3 o 4 tweets numerados que resuma el post.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        
                        st.divider()
                        
                        # --- PRESENTACIÓN EN PESTAÑAS ---
                        tab_blog, tab_ig, tab_x = st.tabs(["📝 Artículo Blogger", "📸 Instagram / FB", "🐦 X (Twitter)"])

                        with tab_blog:
                            st.header(data.get('h1', ''))
                            st.info(f"**Meta Descripción:** {data.get('meta', '')}")
                            st.markdown(data.get('html', ''), unsafe_allow_html=True)
                            st.divider()
                            st.subheader("Código HTML (Pegar en Blogger)")
                            st.code(data.get('html', ''), language="html")

                        with tab_ig:
                            st.subheader("Post para Instagram o Facebook")
                            st.text_area("Copiá el texto:", data.get('ig_post', ''), height=400)
                            st.caption("Tip: Usá una imagen llamativa que combine con este texto.")

                        with tab_x:
                            st.subheader("Hilo para X (Twitter)")
                            st.text_area("Copiá el hilo:", data.get('x_thread', ''), height=400)
                            st.success("¡Contenido generado con éxito!")

                    else:
                        st.error("La IA no devolvió el formato correcto. Probá clickear el botón de nuevo.")
    
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

elif not api_key:
    st.warning("⚠️ Por favor, ingresá tu API Key en la barra lateral para comenzar.")
