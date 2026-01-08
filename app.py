import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Master Pro - Groq Edition", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("Obtén tu llave gratis en [Groq Cloud](https://console.groq.com/)")
    api_key = st.text_input("Pegá tu Groq API Key:", type="password")
    
def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    client = Groq(api_key=api_key)

st.title("🚀 Generador SEO (Powered by Groq)")
st.markdown("Contenido **Español Neutro** | Imágenes | Marcado Schema JSON-LD")

idea_usuario = st.text_input("Tema del artículo:", placeholder="Ej: Guía de inversión en criptomonedas")

if idea_usuario and api_key:
    if st.button("✨ Generar Contenido Completo"):
        try:
            with st.spinner("Redactando a ultra velocidad con Llama 3..."):
                # Groq es mucho más rápido, no necesitamos esperar tanto
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
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192", # Modelo potente de Meta disponible en Groq
                    response_format={"type": "json_object"} # Groq soporta modo JSON nativo
                )
                
                data = json.loads(chat_completion.choices[0].message.content)
                
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
                    st.code(html_blogger, language="html")
                with t2:
                    st.write("Instagram:", data['social']['ig'])
                    st.write("X:", data['social']['x'])

        except Exception as e:
            st.error(f"Error: {e}")
