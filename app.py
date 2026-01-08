import streamlit as st
from groq import Groq
import json
import re
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SEO Writer Pro", layout="wide")

def fix_json_syntax(text):
    """Limpia y corrige errores comunes de la IA en el JSON."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match: return None
    content = match.group(0)
    # Corrige el error común de cerrar con paréntesis en lugar de llaves
    content = content.replace('),', '},').replace(')]', '}]')
    return content

# --- PERSISTENCIA DE DATOS ---
if 'art_data' not in st.session_state: st.session_state.art_data = None
if 'kw_list' not in st.session_state: st.session_state.kw_list = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔑 Credenciales")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

# --- APLICACIÓN ---
st.title("✍️ Redactor SEO de Alto Impacto")
st.markdown("Genera artículos extensos (>800 palabras) con gestión de imágenes independiente.")

tema = st.text_input("Tema principal del artículo:", placeholder="Ej: Guía de Ciberseguridad para 2026")

if tema and api_key:
    # 1. PASO DE KEYWORDS
    if st.button("🔍 Investigar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema}'. Responde solo JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(res.choices[0].message.content)['data']
        except Exception as e:
            st.error(f"Error en Keywords: {e}")

    if st.session_state.kw_list:
        df = pd.DataFrame(st.session_state.kw_list)
        st.table(df)
        seleccion = st.selectbox("Elige tu keyword principal:", [i['kw'] for i in st.session_state.kw_list])

        # 2. PASO DE REDACCIÓN
        if st.button("📝 Generar Artículo Extenso"):
            try:
                with st.spinner("Redactando contenido profundo... esto puede tardar unos segundos..."):
                    prompt_art = f"""Escribe un artículo SEO de más de 800 palabras sobre '{seleccion}'.
                    Usa un tono profesional. Responde únicamente en JSON con estas llaves:
                    - h1: Titulo
                    - meta: Meta descripción
                    - introduccion: Párrafo largo y cautivador
                    - contenido_html: El cuerpo del artículo con al menos 4 H2, listas de puntos y párrafos detallados.
                    - faq_html: 5 preguntas y respuestas en formato HTML.
                    - prompts_imagenes: [3 descripciones cortas en INGLÉS para fotos realistas].
                    - redes: {{"ig": "copy para instagram", "x": "hilo para x"}}
                    """
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    
                    raw_json = res_art.choices[0].message.content
                    fixed_json = fix_json_syntax(raw_json)
                    st.session_state.art_data = json.loads(fixed_json)
            except Exception as e:
                st.error("Error al procesar el artículo. Reintenta.")
                st.expander("Detalle del error").code(str(e))

    # 3. INTERFAZ DE RESULTADOS (PESTAÑAS)
    if st.session_state.art_data:
        art = st.session_state.art_data
        tab1, tab2, tab3 = st.tabs(["📄 Contenido para Blogger", "🖼️ Imágenes Generadas", "📱 Redes Sociales"])

        with tab1:
            # Construimos el código final una sola vez
            full_html = f"<h1>{art['h1']}</h1>\n{art['introduccion']}\n{art['contenido_html']}\n{art['faq_html']}"
            
            st.success("✅ Artículo generado. Copia el código al final de esta pestaña.")
            st.markdown("### Vista Previa del Artículo")
            st.markdown(full_html, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📋 Código Fuente (Pegar en Vista HTML de Blogger)")
            st.code(full_html, language="html")

        with tab2:
            st.subheader("🖼️ Galería de Imágenes")
            st.info("Estas imágenes se basan en los prompts generados para tu artículo.")
            
            prompts = art.get('prompts_imagenes', [])
            cols = st.columns(len(prompts)) if prompts else st.columns(1)
            
            for i, p in enumerate(prompts):
                with cols[i]:
                    p_url = re.sub(r'[^a-zA-Z]', '-', p).lower()
                    img_url = f"https://pollinations.ai/p/{p_url}?width=1024&height=768&seed={i+77}&nologo=true"
                    st.image(img_url, caption=f"Imagen {i+1}")
                    st.caption("Código para insertar esta imagen:")
                    st.code(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; max-width:800px; border-radius:12px;" /></div>', language="html")

        with tab3:
            st.subheader("📱 Copys para Redes")
            st.write("**Instagram:**", art['redes']['ig'])
            st.divider()
            st.write("**X (Twitter):**", art['redes']['x'])
