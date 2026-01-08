import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador SEO Profesional", layout="wide")

def limpiar_json(texto):
    """Extrae el bloque JSON del texto de la IA."""
    try:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        return match.group(0) if match else None
    except: return None

def get_best_model(client):
    """Detecta qué modelo de Groq está disponible para evitar el error 404."""
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
st.title("🚀 Redactor SEO Profesional")
st.markdown("Investigación de Keywords + Artículo HTML + Marcado Schema + Imágenes.")

tema = st.text_input("¿Sobre qué quieres escribir?", placeholder="Ej: Beneficios de la meditación")

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

    # MOSTRAR RESULTADOS INVESTIGACIÓN
    if 'kw_list' in st.session_state:
        st.subheader("📊 Keywords Encontradas")
        df = pd.DataFrame(st.session_state.kw_list)
        st.table(df)
        
        seleccion = st.selectbox("Elige la keyword para tu artículo:", [i['kw'] for i in st.session_state.kw_list])

        # PASO 2: REDACCIÓN
        if st.button("✨ Paso 2: Generar Artículo Completo"):
            try:
                with st.spinner("Redactando post optimizado..."):
                    prompt_art = f"""
                    Eres un redactor SEO senior. Escribe en ESPAÑOL NEUTRO sobre '{seleccion}'.
                    Regla: No uses voseo ni regionalismos.
                    Devuelve un JSON con:
                    - h1, slug, meta (150 carac).
                    - intro, desarrollo (HTML con h2), conclusion.
                    - faq: [{{q: pregunta, a: respuesta}}] (3 items).
                    - img_prompts: [3 prompts en inglés para imágenes realistas].
                    - alt_texts: [3 textos alt en español].
                    - social: {{ig: post, x: hilo}}.
                    """
                    response_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    art = json.loads(limpiar_json(response_art.choices[0].message.content))

                    # --- LÓGICA DE IMÁGENES ---
                    def img_url(p, seed):
                        p_enc = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={seed}&model=flux"

                    imgs = [img_url(art['img_prompts'][i], i+10) for i in range(3)]

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

                    # --- HTML FINAL ---
                    html = f"""{schema}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{art['alt_texts'][0]}" style="width:100%; border-radius:10px;"/></div>
<p>{art['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{art['alt_texts'][1]}" style="width:100%; border-radius:10px; margin:20px 0;"/></div>
{art['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{art['alt_texts'][2]}" style="width:100%; border-radius:10px; margin-top:20px;"/></div>
<p>{art['conclusion']}</p>
<div class="faq-section"><h2>Preguntas Frecuentes</h2>{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in art['faq']])}</div>
"""

                    # --- MOSTRAR RESULTADOS ---
                    tab1, tab2 = st.tabs(["📝 Blogger HTML", "📸 Redes Sociales"])
                    with tab1:
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.text_input("Título H1", art['h1'])
                            st.text_area("Meta Descripción", art['meta'])
                            st.download_button("💾 Bajar HTML", html, file_name=f"{art['slug']}.html")
                        with c2:
                            st.markdown(html, unsafe_allow_html=True)
                        st.divider()
                        st.subheader("Código para copiar en Blogger")
                        st.code(html, language="html")
                    
                    with tab2:
                        st.subheader("Instagram")
                        st.write(art['social']['ig'])
                        st.subheader("X (Twitter)")
                        st.write(art['social']['x'])

            except Exception as e:
                st.error(f"Error en redacción: {e}")

else:
    st.info("Por favor, ingresa tu API Key de Groq en la barra lateral para comenzar.")
