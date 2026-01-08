import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="SEO Publisher Pro", layout="wide")

def get_best_model(client):
    try:
        available = [m.id for m in client.models.list().data]
        priority = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8k-instant"]
        for m in priority:
            if m in available: return m
        return available[0]
    except: return "llama-3.1-8k-instant"

# --- INTERFAZ DE CONFIGURACIÓN ---
with st.sidebar:
    st.title("⚙️ Panel de Control")
    api_key = st.text_input("Ingresa tu Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)
        if 'active_model' not in st.session_state:
            st.session_state.active_model = get_best_model(client)
        st.success(f"Modelo en uso: {st.session_state.active_model}")

st.title("🚀 Sistema de Publicación SEO")
st.markdown("Investigación de Keywords + Redacción Pro + Imágenes Estables.")

# --- FLUJO DE TRABAJO ---
tema_input = st.text_input("Tema central:", placeholder="Ej: Estrategias de ahorro para 2026")

if tema_input and api_key:
    # 1. INVESTIGACIÓN DE KEYWORDS
    if st.button("🔍 Investigar Mercado SEO"):
        try:
            with st.spinner("Analizando tendencias..."):
                prompt_kw = f"Eres experto SEO. Genera 5 keywords long-tail para '{tema_input}'. Devuelve SOLO JSON: {{'data': [{{'kw': '...', 'vol': '...', 'dif': '...'}}]}}"
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_kw}],
                    model=st.session_state.active_model,
                    response_format={"type": "json_object"}
                )
                st.session_state.kw_list = json.loads(response.choices[0].message.content)['data']
        except Exception as e:
            st.error(f"Error en Keywords: {e}")

    # 2. SELECCIÓN Y REDACCIÓN
    if 'kw_list' in st.session_state:
        st.subheader("📊 Selección de Keyword")
        df_kw = pd.DataFrame(st.session_state.kw_list)
        st.table(df_kw)
        
        seleccionada = st.selectbox("Elige la keyword ganadora:", [i['kw'] for i in st.session_state.kw_list])

        if st.button("✨ Generar Post para Blogger"):
            try:
                with st.spinner("Redactando contenido de alta calidad..."):
                    prompt_art = f"""
                    Eres un redactor SEO Senior. Escribe en ESPAÑOL NEUTRO sobre '{seleccionada}'.
                    ENTREGA UN JSON CON:
                    - h1, slug, meta (150 caracteres).
                    - intro (párrafo potente).
                    - desarrollo (mínimo 3 secciones con h2 y párrafos HTML).
                    - conclusion.
                    - faq: [{{q: pregunta, a: respuesta}}] (3 items).
                    - img_keywords: [3 conceptos de 2 palabras en INGLÉS para imágenes, ej: 'modern office', 'business meeting'].
                    - alt_texts: [3 textos descriptivos].
                    - social: {{ig: 'texto instagram', x: 'hilo x'}}.
                    """
                    response_art = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt_art}],
                        model=st.session_state.active_model,
                        response_format={"type": "json_object"}
                    )
                    art = json.loads(response_art.choices[0].message.content)

                    # --- PROCESAMIENTO DE IMÁGENES (SISTEMA SEGURO) ---
                    def create_safe_url(concept, seed):
                        # Limpieza extrema para que Blogger no se confunda
                        clean = re.sub(r'[^a-zA-Z]', '-', concept).lower()
                        return f"https://pollinations.ai/p/{clean}?width=1080&height=720&seed={seed}&model=flux&nologo=true"

                    imgs = [create_safe_url(art['img_keywords'][i], i+500) for i in range(3)]

                    # --- CONSTRUCCIÓN DEL HTML PARA BLOGGER ---
                    # Usamos una estructura limpia de tablas/divs que Blogger respeta
                    html_final = f"""
<div style="text-align: center; margin-bottom: 25px;">
    <img alt="{art['alt_texts'][0]}" src="{imgs[0]}" style="width: 100%; max-width: 800px; height: auto; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
</div>

<p style="font-size: 1.1em; line-height: 1.6;">{art['intro']}</p>

<div style="text-align: center; margin: 25px 0;">
    <img alt="{art['alt_texts'][1]}" src="{imgs[1]}" style="width: 100%; max-width: 800px; height: auto; border-radius: 15px;" />
</div>

<div class="post-body" style="line-height: 1.6;">
{art['desarrollo']}
</div>

<div style="text-align: center; margin-top: 25px;">
    <img alt="{art['alt_texts'][2]}" src="{imgs[2]}" style="width: 100%; max-width: 800px; height: auto; border-radius: 15px;" />
</div>

<p style="font-size: 1.1em; line-height: 1.6; font-style: italic;">{art['conclusion']}</p>

<div style="background-color: #f9f9f9; padding: 25px; border-radius: 12px; margin-top: 40px; border-left: 5px solid #1a73e8;">
    <h2 style="margin-top: 0;">Preguntas Frecuentes</h2>
    {''.join([f"<div style='margin-bottom:15px;'><strong>{f['q']}</strong><p>{f['a']}</p></div>" for f in art['faq']])}
</div>
"""

                    # --- RESULTADOS ---
                    t1, t2 = st.tabs(["📝 Blog (Blogger)", "📸 Redes Sociales"])
                    
                    with t1:
                        st.info("Copia el código de abajo y pégalo en la pestaña 'VISTA HTML' de Blogger.")
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.text_input("Título H1", art['h1'])
                            st.text_area("Meta Descripción", art['meta'], height=100)
                            st.download_button("💾 Descargar HTML", html_final, file_name=f"{art['slug']}.html")
                        with col_b:
                            st.markdown("### Vista Previa")
                            st.markdown(html_final, unsafe_allow_html=True)
                        st.divider()
                        st.code(html_final, language="html")

                    with t2:
                        st.subheader("Copia para Instagram")
                        st.write(art['social']['ig'])
                        st.subheader("Copia para X (Twitter)")
                        st.write(art['social']['x'])

            except Exception as e:
                st.error(f"Error en Generación: {e}")
