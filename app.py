import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Master Pro - Multi-Model", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("Obtené tu llave en [Groq Cloud](https://console.groq.com/keys)")
    api_key = st.text_input("Pegá tu Groq API Key:", type="password")

def get_best_model(client):
    """Busca un modelo disponible para evitar el error 404."""
    try:
        available_models = [m.id for m in client.models.list().data]
        # Lista de prioridad de modelos estables en Groq
        priority = [
            "llama-3.3-70b-versatile", 
            "llama-3.3-70b-specdec",
            "llama-3.1-70b-versatile",
            "llama-3.1-8k-instant",
            "mixtral-8x7b-32768"
        ]
        for model_id in priority:
            if model_id in available_models:
                return model_id
        return available_models[0]
    except:
        return "llama-3.1-8k-instant"

if api_key:
    client = Groq(api_key=api_key)
    # Detectamos el modelo una sola vez por sesión
    if 'active_model' not in st.session_state:
        st.session_state.active_model = get_best_model(client)
    st.sidebar.success(f"Modelo activo: {st.session_state.active_model}")

st.title("🚀 Hub SEO Internacional: Investigación + Post")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Avances en inteligencia artificial")

if idea_usuario and api_key:
    # PASO 1: INVESTIGACIÓN DE KEYWORDS
    if 'kw_data' not in st.session_state or st.session_state.get('last_topic') != idea_usuario:
        if st.button("🔍 Investigar Keywords Long-Tail"):
            try:
                with st.spinner("Analizando mercado SEO..."):
                    prompt_kw = f"""
                    Actúe como experto SEO. Para el tema '{idea_usuario}', genere 5 keywords long-tail.
                    Devuelva SOLO un JSON: {{ "data": [ {{ "kw": "...", "vol": "...", "dif": "..." }} ] }}
                    """
                    res_kw = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_kw}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    st.session_state.kw_data = json.loads(res_kw.choices[0].message.content)['data']
                    st.session_state.last_topic = idea_usuario
            except Exception as e:
                st.error(f"Error en investigación: {e}")

    # MOSTRAR TABLA Y SELECCIÓN
    if 'kw_data' in st.session_state:
        st.subheader("📊 Sugerencias de Keywords")
        st.table(pd.DataFrame(st.session_state.kw_data))
        
        opciones = [item['kw'] for item in st.session_state.kw_data]
        seleccion = st.selectbox("Seleccione la Keyword principal:", opciones)

        # PASO 2: GENERACIÓN DEL ARTÍCULO
        if st.button("✨ Generar Post Completo"):
            try:
                with st.spinner("Redactando contenido optimizado..."):
                    prompt_art = f"""
                    Actúe como redactor SEO Senior. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    Entregue un JSON con: h1, slug, meta, intro, desarrollo (HTML con h2), conclusion, 
                    faq (q y a), img_prompts (inglés), alt_texts (español), social (ig y x).
                    """
                    res_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    data = json.loads(res_art.choices[0].message.content)

                    # --- IMÁGENES & SCHEMA ---
                    def get_img(p, s):
                        p_enc = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={s}&model=flux"

                    imgs = [get_img(data['img_prompts'][i], i+55) for i in range(3)]
                    
                    faq_entities = [f'{{ "@type": "Question", "name": "{f["q"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["a"]}" }} }}' for f in data['faq']]
                    schema_code = f"""
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "Article", "headline": "{data['h1']}", "image": "{imgs[0]}", "author": {{ "@type": "Person", "name": "Admin" }} }}
</script>
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{", ".join(faq_entities)}] }}
</script>"""

                    html_blogger = f"""{schema_code}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{data['alt_texts'][0]}" style="width:100%; border-radius:12px;"/></div>
<p>{data['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{data['alt_texts'][1]}" style="width:100%; border-radius:12px; margin:20px 0;"/></div>
{data['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{data['alt_texts'][2]}" style="width:100%; border-radius:12px; margin-top:20px;"/></div>
<p>{data['conclusion']}</p>
<div class="faq-section"><h2>Preguntas Frecuentes</h2>{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in data['faq']])}</div>"""

                    # --- RESULTADOS ---
                    t1, t2 = st.tabs(["📝 Blogger HTML", "📸 Social Media"])
                    with t1:
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.text_input("H1", data['h1'])
                            st.text_area("Meta", data['meta'])
                            st.download_button("💾 Bajar HTML", html_blogger, file_name=f"{data['slug']}.html")
                        with c2:
                            st.markdown(html_blogger, unsafe_allow_html=True)
                        st.code(html_blogger, language="html")
                    with t2:
                        st.write("**Instagram:**", data['social']['ig'])
                        st.write("**X:**", data['social']['x'])

            except Exception as e:
                st.error(f"Error en generación: {e}")
