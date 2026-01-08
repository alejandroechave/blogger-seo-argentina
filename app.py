import streamlit as st
from groq import Groq
import json
import re
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Content Gen", layout="wide")

def clean_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else None

# --- SESSION STATE PARA PERSISTENCIA ---
if 'art_data' not in st.session_state:
    st.session_state.art_data = None
if 'kw_list' not in st.session_state:
    st.session_state.kw_list = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

# --- APP PRINCIPAL ---
st.title("🚀 Generador de Contenido SEO de Alta Calidad")

tema = st.text_input("¿Qué tema profundo quieres tratar?", placeholder="Ej: Guía definitiva de Inversiones en 2026")

if tema and api_key:
    # 1. INVESTIGACIÓN DE KEYWORDS
    if st.button("🔍 1. Investigar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail de alto volumen para '{tema}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
            chat_kw = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(clean_json(chat_kw.choices[0].message.content))['data']
        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.kw_list:
        st.subheader("📊 Estrategia de Keywords")
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword para el artículo:", [i['kw'] for i in st.session_state.kw_list])

        # 2. GENERACIÓN DEL ARTÍCULO EXTENSO
        if st.button("📝 2. Redactar Artículo Profesional"):
            try:
                with st.spinner("Redactando contenido extenso y optimizado..."):
                    prompt_art = f"""
                    Actúa como Redactor SEO Senior. Escribe un artículo de más de 800 palabras sobre '{seleccion}'.
                    Debe incluir:
                    - H1 impactante.
                    - Introducción con gancho (copywriting).
                    - Mínimo 4 secciones H2 extensas con H3 internos.
                    - FAQ con 5 preguntas frecuentes (Schema.org ready).
                    - Conclusión potente.
                    - Meta-descripción de 155 caracteres.
                    - 3 Prompts de imagen detallados en INGLÉS (descripciones realistas).
                    - Texto para Instagram y X.
                    Devuelve TODO en un JSON estructurado.
                    """
                    chat_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    st.session_state.art_data = json.loads(clean_json(chat_art.choices[0].message.content))
            except Exception as e:
                st.error(f"Error en redacción: {e}")

    # --- MOSTRAR RESULTADOS EN PESTAÑAS ---
    if st.session_state.art_data:
        art = st.session_state.art_data
        
        tab_blog, tab_imgs, tab_social = st.tabs(["📝 Artículo para Blogger", "🖼️ Generador de Imágenes", "📱 Redes Sociales"])

        with tab_blog:
            st.subheader(art.get('h1', 'Artículo'))
            # Construcción del HTML
            html_content = f"""
<h2>{art.get('h1')}</h2>
{art.get('intro', '')}
{art.get('desarrollo', art.get('content', ''))}
<div class="faq-section">
    <h3>Preguntas Frecuentes</h3>
    {art.get('faq', '')}
</div>
<p><strong>Meta:</strong> {art.get('meta', '')}</p>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.divider()
            st.subheader("Código HTML para Blogger")
            st.code(html_content, language="html")

        with tab_imgs:
            st.subheader("🖼️ Galería de Imágenes")
            prompts = art.get('img_prompts', art.get('img_keywords', []))
            
            cols = st.columns(len(prompts)) if prompts else st.columns(1)
            
            for idx, p in enumerate(prompts):
                with cols[idx]:
                    # Limpiamos el prompt para la URL
                    p_clean = re.sub(r'[^a-zA-Z]', '-', p).lower()
                    img_url = f"https://pollinations.ai/p/{p_clean}?width=1024&height=768&seed={idx+100}&nologo=true"
                    
                    st.image(img_url, caption=f"Opción {idx+1}")
                    st.code(f'<img src="{img_url}" style="width:100%;" />', language="html")
                    st.caption(f"Prompt original: {p}")

        with tab_social:
            st.subheader("📱 Contenido para Redes")
            soc = art.get('social', {})
            st.write("**Instagram:**", soc.get('ig', 'No generado'))
            st.divider()
            st.write("**X (Twitter):**", soc.get('x', 'No generado'))

else:
    st.info("Configura tu API y elige un tema para empezar.")
