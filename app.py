import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import time
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Hub Pro - Schema Edition", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Nota: Esta versión incluye Marcado Schema JSON-LD para SEO avanzado.")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods: return m.name
    except: return None
    return None

def llamar_gemini_con_reintento(prompt, model, max_retries=3):
    for i in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                time.sleep(i + 5)
                continue
            raise e

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre: model = genai.GenerativeModel(modelo_nombre)

st.title("🚀 Generador SEO con Marcado Schema")
st.markdown("Contenido en **español neutro** + Imágenes + **Datos Estructurados JSON-LD**.")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Guía de alimentación saludable")

if idea_usuario and api_key and 'model' in locals():
    try:
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando Keywords..."):
                prompt_kw = f"Actúe como experto SEO. Para '{idea_usuario}', genere 5 long-tail keywords. Deuelva SOLO JSON: {{'data': [{{'kw': 'ejemplo', 'vol': '1k', 'dif': '20%'}}]}}"
                response = llamar_gemini_con_reintento(prompt_kw, model)
                clean_kw = limpiar_json(response.text)
                if clean_kw: st.session_state.kw_data = json.loads(clean_kw)['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Tabla de Keywords")
            df = pd.DataFrame(st.session_state.kw_data)
            st.table(df)

            seleccion = st.selectbox("Seleccione su Keyword:", [item['kw'] for item in st.session_state.kw_data])

            if st.button("✨ Generar Post con Schema"):
                with st.spinner("Redactando contenido con datos estructurados..."):
                    prompt_final = f"""
                    Actúe como redactor SEO senior. Idioma: ESPAÑOL NEUTRO. Tema: '{seleccion}'.
                    REGLA: No mencione países ni use voseo.
                    ENTREGUE UN JSON ESTRICTO CON:
                    - h1, slug, meta.
                    - intro, desarrollo, conclusion.
                    - faq: Un array de 3 objetos con 'pregunta' y 'respuesta'.
                    - img_p1, img_p2, img_p3 (prompts en inglés).
                    - alt_texts: Lista de 3 textos ALT en español.
                    - ig_post, x_thread.
                    """
                    
                    res_final = llamar_gemini_con_reintento(prompt_final, model)
                    data = json.loads(limpiar_json(res_final.text))
                    
                    # --- LÓGICA DE IMÁGENES ---
                    def get_img_url(p, s):
                        p_enc = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={s}&model=flux"

                    img1 = get_img_url(data['img_p1'], 11)
                    img2 = get_img_url(data['img_p2'], 22)
                    img3 = get_img_url(data['img_p3'], 33)

                    # --- CONSTRUCCIÓN DEL MARCADO SCHEMA JSON-LD ---
                    preguntas_faq = data.get('faq', [])
                    faq_entities = [f'{{ "@type": "Question", "name": "{f["pregunta"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["respuesta"]}" }} }}' for f in preguntas_faq]
                    
                    schema_json = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{data['h1']}",
  "description": "{data['meta']}",
  "image": "{img1}",
  "author": {{ "@type": "Person", "name": "Admin" }},
  "publisher": {{ "@type": "Organization", "name": "Blog SEO" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{", ".join(faq_entities)}]
}}
</script>
                    """

                    # --- CONSTRUCCIÓN DEL HTML PARA BLOGGER ---
                    html_blogger = f"""
{schema_json}
<div class="separator" style="clear: both; text-align: center;">
    <img border="0" src="{img1}" alt="{data['alt_texts'][0]}" style="width: 100%; border-radius: 10px;" />
</div>
<p>{data['intro']}</p>

<div class="separator" style="clear: both; text-align: center;">
    <img border="0" src="{img2}" alt="{data['alt_texts'][1]}" style="width: 100%; border-radius: 10px; margin: 20px 0;" />
</div>
{data['desarrollo']}

<div class="separator" style="clear: both; text-align: center;">
    <img border="0" src="{img3}" alt="{data['alt_texts'][2]}" style="width: 100%; border-radius: 10px; margin-top: 20px;" />
</div>
<p>{data['conclusion']}</p>

<div class="faq-section">
    <h2>Preguntas Frecuentes</h2>
    {''.join([f"<h3>{f['pregunta']}</h3><p>{f['respuesta']}</p>" for f in preguntas_faq])}
</div>
                    """

                    # --- INTERFAZ ---
                    tab1, tab2 = st.tabs(["📝 Blog & Schema", "📸 Social Media"])
                    with tab1:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.subheader("SEO Avanzado")
                            st.text_input("Título", data['h1'])
                            st.text_input("Slug", data['slug'])
                            st.text_area("Meta", data['meta'])
                            st.download_button("💾 Bajar HTML", html_blogger, file_name=f"{data['slug']}.html")
                        with col2:
                            st.markdown(f"<h1>{data['h1']}</h1>", unsafe_allow_html=True)
                            st.markdown(html_blogger, unsafe_allow_html=True)
                        st.divider()
                        st.subheader("Código HTML con Schema (Pegar en Blogger)")
                        st.code(html_blogger, language="html")

                    with tab2:
                        st.text_area("Instagram", data['ig_post'], height=200)
                        st.text_area("X Hilo", data['x_thread'], height=200)

    except Exception as e:
        st.error(f"Error: {e}")
