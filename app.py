import streamlit as st
from groq import Groq
import json
import re
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SEO Master Content Gen", layout="wide")

def clean_json(text):
    # Elimina posibles textos fuera de las llaves y corrige errores comunes de sintaxis
    text = re.search(r'\{.*\}', text, re.DOTALL)
    if not text: return None
    content = text.group(0)
    # Corregir error específico de la IA (paréntesis en vez de llave)
    content = content.replace('),', '},').replace(')]', '}]')
    return content

# --- SESSION STATE ---
if 'art_data' not in st.session_state: st.session_state.art_data = None
if 'kw_list' not in st.session_state: st.session_state.kw_list = None

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

st.title("🚀 Generador de Contenido SEO Profesional")

tema = st.text_input("Tema a tratar:", placeholder="Ej: Redes sociales para PYMES")

if tema and api_key:
    # 1. KEYWORDS
    if st.button("🔍 1. Investigar Keywords"):
        try:
            prompt_kw = f"Genera 5 keywords long-tail para '{tema}'. Responde solo JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
            chat_kw = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_kw}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            st.session_state.kw_list = json.loads(clean_json(chat_kw.choices[0].message.content))['data']
        except Exception as e: st.error(f"Error: {e}")

    if st.session_state.kw_list:
        st.subheader("📊 Estrategia de Keywords")
        st.table(pd.DataFrame(st.session_state.kw_list))
        seleccion = st.selectbox("Keyword para el artículo:", [i['kw'] for i in st.session_state.kw_list])

        # 2. ARTÍCULO
        if st.button("📝 2. Redactar Artículo Extenso"):
            try:
                with st.spinner("Redactando artículo premium..."):
                    prompt_art = f"""Escribe un artículo SEO extenso (>800 palabras) sobre '{seleccion}'. 
                    Responde EXCLUSIVAMENTE en formato JSON con esta estructura exacta:
                    {{
                      "h1": "título",
                      "meta": "descripción 150 carac",
                      "introduccion": "párrafo largo",
                      "cuerpo_html": "Mínimo 4 secciones H2 con párrafos extensos y listas",
                      "faq_html": "Lista de 5 preguntas frecuentes en HTML",
                      "img_prompts": ["3 prompts detallados en INGLÉS", "ej: 'realistic office social media marketing'"],
                      "social": {{"ig": "post texto", "x": "hilo"}}
                    }}"""
                    
                    chat_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    
                    raw_content = chat_art.choices[0].message.content
                    cleaned_content = clean_json(raw_content)
                    st.session_state.art_data = json.loads(cleaned_content)
            except Exception as e:
                st.error(f"Error en redacción: {e}")
                st.expander("Ver error técnico").code(raw_content)

    # 3. MOSTRAR RESULTADOS
    if st.session_state.art_data:
        art = st.session_state.art_data
        tab_blog, tab_imgs, tab_social = st.tabs(["📝 Artículo para Blogger", "🖼️ Imágenes", "📱 Redes"])

        with tab_blog:
            html_final = f"<h1>{art['h1']}</h1>\n{art['introduccion']}\n{art['cuerpo_html']}\n{art['faq_html']}"
            st.markdown(html_final, unsafe_allow_html=True)
            st.divider()
            st.subheader("Código para copiar en Vista HTML de Blogger")
            st.code(html_final, language="html")

        with tab_imgs:
            st.subheader("🖼️ Imágenes para tu post")
            prompts = art.get('img_prompts', [])
            cols = st.columns(len(prompts)) if prompts else st.columns(1)
            
            for idx, p in enumerate(prompts):
                with cols[idx]:
                    # Limpieza para Pollinations
                    p_url = re.sub(r'[^a-zA-Z]', '-', p).lower()
                    img_url = f"https://pollinations.ai/p/{p_url}?width=1024&height=768&seed={idx+42}&nologo=true"
                    st.image(img_url, caption=f"Prompt: {p}")
                    st.code(f'<div style="text-align:center;"><img src="{img_url}" style="width:100%; max-width:800px; border-radius:10px;" /></div>', language="html")

        with tab_social:
            st.write("**Instagram:**", art['social']['ig'])
            st.divider()
            st.write("**X (Twitter):**", art['social']['x'])
