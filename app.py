import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Master Pro", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    
def obtener_modelo_disponible():
    """Busca dinámicamente el mejor modelo disponible en tu cuenta."""
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioridad: 2.0 Flash -> 1.5 Flash -> Pro
        for target in ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']:
            if target in modelos:
                return target
        return modelos[0] if modelos else None
    except:
        return None

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    genai.configure(api_key=api_key)
    modelo_final = obtener_modelo_disponible()
    if modelo_final:
        model = genai.GenerativeModel(modelo_final)
        st.sidebar.success(f"Conectado a: {modelo_final}")
    else:
        st.sidebar.error("No se detectaron modelos disponibles.")

st.title("🚀 Generador SEO Profesional")
st.markdown("Contenido **Español Neutro** | Imágenes | Marcado Schema JSON-LD")

idea_usuario = st.text_input("Tema del artículo:", placeholder="Ej: Guía de inversión en criptomonedas")

if idea_usuario and api_key and 'model' in locals():
    if st.button("✨ Generar Contenido Completo"):
        try:
            with st.spinner("Investigando y redactando (esto ahorra cuota diaria)..."):
                prompt = f"""
                Actúe como experto SEO Senior. Idioma: ESPAÑOL NEUTRO. Tema: '{idea_usuario}'.
                Entregue ÚNICAMENTE un JSON con:
                {{
                  "h1": "Título", "slug": "url-amigable", "meta": "descripción 150 caracteres",
                  "intro": "párrafo inicial", "desarrollo": "cuerpo html con h2 y párrafos", "conclusion": "párrafo final",
                  "faq": [{{"q": "pregunta", "a": "respuesta"}}],
                  "img_prompts": ["prompt1 inglés", "prompt2 inglés", "prompt3 inglés"],
                  "alt_texts": ["alt1", "alt2", "alt3"],
                  "social": {{"ig": "post ig", "x": "hilo x"}}
                }}
                """
                
                response = model.generate_content(prompt)
                data = json.loads(limpiar_json(response.text))
                
                # --- IMÁGENES ---
                imgs = [f"https://pollinations.ai/p/{urllib.parse.quote(data['img_prompts'][i])}?width=1024&height=768&seed={i+42}" for i in range(3)]
                
                # --- SCHEMA ---
                faq_schema = ", ".join([f'{{ "@type": "Question", "name": "{f["q"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["a"]}" }} }}' for f in data['faq']])
                schema_code = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{data['h1']}",
  "image": "{imgs[0]}",
  "author": {{ "@type": "Person", "name": "Admin" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{faq_schema}]
}}
</script>"""

                # --- HTML PARA BLOGGER ---
                html_blogger = f"""{schema_code}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{data['alt_texts'][0]}" style="width:100%; border-radius:12px;"/></div>
<p>{data['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{data['alt_texts'][1]}" style="width:100%; border-radius:12px; margin:20px 0;"/></div>
{data['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{data['alt_texts'][2]}" style="width:100%; border-radius:12px; margin-top:20px;"/></div>
<p>{data['conclusion']}</p>
<div class="faq-section"><h2>Preguntas Frecuentes</h2>{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in data['faq']])}</div>"""

                # --- VISTA ---
                t1, t2 = st.tabs(["📝 Blog (Blogger HTML)", "📸 Redes Sociales"])
                with t1:
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.text_input("H1", data['h1'])
                        st.text_input("Slug", data['slug'])
                        st.text_area("Meta", data['meta'])
                        st.download_button("💾 Bajar HTML", html_blogger, file_name=f"{data['slug']}.html")
                    with c2:
                        st.markdown(html_blogger, unsafe_allow_html=True)
                    st.divider()
                    st.subheader("Copiar código HTML")
                    st.code(html_blogger, language="html")
                with t2:
                    st.subheader("Instagram")
                    st.write(data['social']['ig'])
                    st.subheader("X")
                    st.write(data['social']['x'])

        except Exception as e:
            st.error(f"Error: {e}. Si persiste, espera 60 segundos por el límite de cuota.")
