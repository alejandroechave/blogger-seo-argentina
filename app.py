import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Master Pro - Canva Workflow", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Groq API Key:", type="password")

def get_best_model(client):
    try:
        available_models = [m.id for m in client.models.list().data]
        priority = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8k-instant"]
        for model_id in priority:
            if model_id in available_models: return model_id
        return available_models[0]
    except: return "llama-3.1-8k-instant"

if api_key:
    client = Groq(api_key=api_key)
    if 'active_model' not in st.session_state:
        st.session_state.active_model = get_best_model(client)

st.title("🚀 SEO Hub: Contenido Pro + Guía Canva")

idea_usuario = st.text_input("Tema de investigación:", placeholder="Ej: Decoración de interiores minimalista")

if idea_usuario and api_key:
    # PASO 1: KEYWORDS
    if 'kw_data' not in st.session_state or st.session_state.get('last_topic') != idea_usuario:
        if st.button("🔍 Analizar Keywords"):
            try:
                prompt_kw = f"Genera 5 keywords long-tail para '{idea_usuario}'. JSON: {{ 'data': [ {{ 'kw': '...', 'vol': '...', 'dif': '...' }} ] }}"
                res_kw = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model=st.session_state.active_model,
                    response_format={"type": "json_object"}
                )
                st.session_state.kw_data = json.loads(res_kw.choices[0].message.content)['data']
                st.session_state.last_topic = idea_usuario
            except Exception as e: st.error(f"Error: {e}")

    if 'kw_data' in st.session_state:
        st.table(pd.DataFrame(st.session_state.kw_data))
        seleccion = st.selectbox("Keyword principal:", [item['kw'] for item in st.session_state.kw_data])

        # PASO 2: REDACCIÓN
        if st.button("✨ Generar Post y Prompts de Diseño"):
            try:
                with st.spinner("Creando contenido..."):
                    prompt_art = f"""
                    Actúe como experto SEO. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    Entregue un JSON con: h1, slug, meta, intro, desarrollo (HTML), conclusion, 
                    faq (q y a), social (ig, x), 
                    canva_prompts: [3 prompts detallados en inglés para generar imágenes artísticas en Canva Magic Media],
                    alt_texts: [3 textos alt en español].
                    """
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    data = json.loads(res_art.choices[0].message.content)

                    # --- IMÁGENES AUTOMÁTICAS (FLUX) ---
                    # Esto asegura que el HTML no esté vacío
                    def get_img(p, s):
                        p_enc = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={s}&model=flux"

                    imgs = [get_img(data['canva_prompts'][i], i+99) for i in range(3)]
                    
                    # Marcado Schema
                    faq_entities = [f'{{ "@type": "Question", "name": "{f["q"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["a"]}" }} }}' for f in data['faq']]
                    schema_code = f"""<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "Article", "headline": "{data['h1']}", "image": "{imgs[0]}", "author": {{ "@type": "Person", "name": "Admin" }} }}</script>
<script type="application/ld+json">{{ "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{", ".join(faq_entities)}] }}</script>"""

                    html_blogger = f"""{schema_code}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{data['alt_texts'][0]}" style="width:100%; border-radius:12px;"/></div>
<p>{data['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{data['alt_texts'][1]}" style="width:100%; border-radius:12px; margin:20px 0;"/></div>
{data['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{data['alt_texts'][2]}" style="width:100%; border-radius:12px; margin-top:20px;"/></div>
<p>{data['conclusion']}</p>
<div class="faq-section"><h2>Preguntas Frecuentes</h2>{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in data['faq']])}</div>"""

                    # --- TABS DE RESULTADO ---
                    t1, t2, t3 = st.tabs(["📝 Blogger HTML", "🎨 Guía Canva Pro", "📸 Social"])
                    
                    with t1:
                        st.download_button("💾 Descargar HTML", html_blogger, file_name=f"{data['slug']}.html")
                        st.markdown(html_blogger, unsafe_allow_html=True)
                        st.code(html_blogger, language="html")
                    
                    with t2:
                        st.subheader("🖼️ Crea imágenes Pro en Canva")
                        st.write("Copia estos prompts en la herramienta **Magic Media** de Canva para un estilo superior:")
                        for i, p in enumerate(data['canva_prompts']):
                            st.info(f"**Prompt para Imagen {i+1}:**\n\n{p}")
                    
                    with t3:
                        st.write("**Instagram:**", data['social']['ig'])
                        st.write("**X:**", data['social']['x'])

            except Exception as e: st.error(f"Error: {e}")
