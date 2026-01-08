import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SEO Master Pro - Blogger Fix", layout="wide")

def limpiar_json(texto):
    try:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        return match.group(0) if match else None
    except: return None

def get_best_model(client):
    try:
        available = [m.id for m in client.models.list().data]
        priority = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8k-instant"]
        for m in priority:
            if m in available: return m
        return available[0]
    except: return "llama-3.1-8k-instant"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)
        if 'active_model' not in st.session_state:
            st.session_state.active_model = get_best_model(client)
        st.success(f"Modelo: {st.session_state.active_model}")

# --- APP PRINCIPAL ---
st.title("🚀 Redactor SEO para Blogger")
st.markdown("Genera contenido con imágenes que **sí funcionan** en plantillas externas.")

tema = st.text_input("¿Sobre qué quieres investigar?", placeholder="Ej: Estrategias de marketing para PYMES")

if tema and api_key:
    # PASO 1: INVESTIGACIÓN
    if st.button("🔍 Paso 1: Investigar Keywords"):
        try:
            with st.spinner("Buscando keywords ganadoras..."):
                prompt_kw = f"Actúa como experto SEO. Genera 5 keywords long-tail para '{tema}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model=st.session_state.active_model,
                    response_format={"type": "json_object"}
                )
                data_kw = json.loads(limpiar_json(response.choices[0].message.content))
                st.session_state.kw_list = data_kw['data']
        except Exception as e:
            st.error(f"Error en investigación: {e}")

    # MOSTRAR RESULTADOS
    if 'kw_list' in st.session_state:
        st.subheader("📊 Keywords Sugeridas")
        st.table(pd.DataFrame(st.session_state.kw_list))
        
        seleccion = st.selectbox("Elige la keyword principal:", [i['kw'] for i in st.session_state.kw_list])

        # PASO 2: REDACCIÓN
        if st.button("✨ Paso 2: Generar Artículo con Imágenes Fix"):
            try:
                with st.spinner("Redactando post profesional..."):
                    prompt_art = f"""
                    Eres un redactor SEO senior. Escribe en ESPAÑOL NEUTRO sobre '{seleccion}'.
                    Devuelve un JSON con:
                    - h1, slug, meta (150 carac).
                    - intro, desarrollo (HTML con h2 y p), conclusion.
                    - faq: [{{q: pregunta, a: respuesta}}] (3 items).
                    - img_prompts: [3 prompts en inglés detallados para fotos realistas].
                    - alt_texts: [3 textos alt en español].
                    - social: {{ig: post, x: hilo}}.
                    """
                    response_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    art = json.loads(limpiar_json(response_art.choices[0].message.content))

                    # --- LÓGICA DE IMÁGENES (SISTEMA ANTIBLOQUEO) ---
                    def img_url(p, seed):
                        # Limpiamos el prompt para URL
                        p_safe = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_safe}?width=1024&height=768&seed={seed}&model=flux&nologo=true"

                    imgs = [img_url(art['img_prompts'][i], i+50) for i in range(3)]

                    # --- SCHEMA JSON-LD ---
                    faq_json = ", ".join([f'{{"@type":"Question","name":"{f["q"]}","acceptedAnswer":{{"@type":"Answer","text":"{f["a"]}"}}}}' for f in art['faq']])
                    schema = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{art['h1']}",
  "description": "{art['meta']}",
  "image": "{imgs[0]}",
  "author": {{ "@type": "Person", "name": "Admin" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{faq_json}]
}}
</script>"""

                    # --- HTML FINAL (OPTIMIZADO PARA BLOGGER) ---
                    # Usamos etiquetas <a> y style clear para que la plantilla LiteSpot no las oculte
                    html_blogger = f"""{schema}
<div class="separator" style="text-align: center; clear: both;">
<a href="{imgs[0]}" style="margin-left: 1em; margin-right: 1em;">
<img border="0" data-original-height="768" data-original-width="1024" src="{imgs[0]}" alt="{art['alt_texts'][0]}" style="width: 100%; max-width: 800px; border-radius: 12px;" />
</a>
</div>

<p>{art['intro']}</p>

<div class="separator" style="text-align: center; clear: both;">
<a href="{imgs[1]}" style="margin-left: 1em; margin-right: 1em;">
<img border="0" data-original-height="768" data-original-width="1024" src="{imgs[1]}" alt="{art['alt_texts'][1]}" style="width: 100%; max-width: 800px; border-radius: 12px; margin: 20px 0;" />
</a>
</div>

{art['desarrollo']}

<div class="separator" style="text-align: center; clear: both;">
<a href="{imgs[2]}" style="margin-left: 1em; margin-right: 1em;">
<img border="0" data-original-height="768" data-original-width="1024" src="{imgs[2]}" alt="{art['alt_texts'][2]}" style="width: 100%; max-width: 800px; border-radius: 12px; margin-top: 20px;" />
</a>
</div>

<p>{art['conclusion']}</p>

<div class="faq-section" style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px;">
<h2>Preguntas Frecuentes</h2>
{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in art['faq']])}
</div>
"""

                    # --- VISTA DE RESULTADOS ---
                    tab1, tab2 = st.tabs(["📝 Blogger HTML", "📸 Redes Sociales"])
                    with tab1:
                        col_info, col_prev = st.columns([1, 2])
                        with col_info:
                            st.text_input("Título H1", art['h1'])
                            st.text_area("Meta Descripción", art['meta'], height=100)
                            st.download_button("💾 Bajar HTML", html_blogger, file_name=f"{art['slug']}.html")
                        with col_prev:
                            st.markdown("### Vista Previa")
                            st.markdown(html_blogger, unsafe_allow_html=True)
                        
                        st.subheader("Código para copiar (Usar Vista HTML en Blogger)")
                        st.code(html_blogger, language="html")
                    
                    with tab2:
                        st.subheader("Contenido para Redes")
                        st.write("**Instagram:**", art['social']['ig'])
                        st.write("**X (Twitter):**", art['social']['x'])

            except Exception as e:
                st.error(f"Error en redacción: {e}")
else:
    st.warning("⚠️ Introduce tu API Key y un tema para comenzar.")
