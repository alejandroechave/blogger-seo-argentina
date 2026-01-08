import streamlit as st
from groq import Groq
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Hub Pro - Groq Edition", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("1. Obtené tu llave en [Groq Cloud](https://console.groq.com/keys)")
    api_key = st.text_input("Pegá tu Groq API Key:", type="password")
    st.info("Groq es 10x más rápido y tiene límites más amplios.")

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    client = Groq(api_key=api_key)

st.title("🚀 Generador SEO Internacional (Groq + Llama 3)")
st.markdown("Contenido en **Español Neutro** | Imágenes | Marcado Schema JSON-LD")

idea_usuario = st.text_input("¿Qué tema desea investigar hoy?", placeholder="Ej: Estrategias de marketing digital 2026")

if idea_usuario and api_key:
    if st.button("✨ Generar Contenido Profesional"):
        try:
            with st.spinner("Redactando a ultra velocidad..."):
                # Groq es tan rápido que el spinner casi ni se verá
                prompt = f"""
                Actúe como experto SEO Senior. Idioma: ESPAÑOL NEUTRO (sin voseo ni regionalismos). 
                Tema: '{idea_usuario}'.
                
                ENTREGUE ÚNICAMENTE UN JSON CON:
                {{
                  "h1": "Título", 
                  "slug": "url-amigable", 
                  "meta": "descripción de 150 caracteres",
                  "intro": "párrafo inicial atractivo", 
                  "desarrollo": "cuerpo html con etiquetas h2 y párrafos", 
                  "conclusion": "párrafo final",
                  "faq": [
                    {{"q": "pregunta 1", "a": "respuesta 1"}},
                    {{"q": "pregunta 2", "a": "respuesta 2"}},
                    {{"q": "pregunta 3", "a": "respuesta 3"}}
                  ],
                  "img_prompts": ["prompt1 inglés", "prompt2 inglés", "prompt3 inglés"],
                  "alt_texts": ["alt1", "alt2", "alt3"],
                  "social": {{"ig": "post para instagram", "x": "hilo para X/Twitter"}}
                }}
                """
                
                # Llamada a Groq usando Llama 3
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(chat_completion.choices[0].message.content)
                
                # --- GENERACIÓN DE URLs DE IMAGEN ---
                def get_img(p, s):
                    p_enc = urllib.parse.quote(p)
                    return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={s}&model=flux"

                imgs = [get_img(data['img_prompts'][i], i+500) for i in range(3)]
                
                # --- MARCADO SCHEMA JSON-LD ---
                faq_entities = [f'{{ "@type": "Question", "name": "{f["q"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["a"]}" }} }}' for f in data['faq']]
                
                schema_code = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{data['h1']}",
  "description": "{data['meta']}",
  "image": "{imgs[0]}",
  "author": {{ "@type": "Person", "name": "Admin" }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{", ".join(faq_entities)}]
}}
</script>"""

                # --- HTML FINAL PARA BLOGGER ---
                html_blogger = f"""{schema_code}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{data['alt_texts'][0]}" style="width:100%; border-radius:12px;"/></div>
<p>{data['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{data['alt_texts'][1]}" style="width:100%; border-radius:12px; margin:20px 0;"/></div>
{data['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{data['alt_texts'][2]}" style="width:100%; border-radius:12px; margin-top:20px;"/></div>
<p>{data['conclusion']}</p>
<div class="faq-section">
    <h2>Preguntas Frecuentes</h2>
    {''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in data['faq']])}
</div>"""

                # --- INTERFAZ DE RESULTADOS ---
                st.success("¡Generado con éxito en segundos!")
                t1, t2, t3 = st.tabs(["📝 Post Blogger", "📸 Social Media", "📊 SEO Data"])
                
                with t1:
                    col_edit, col_prev = st.columns([1, 2])
                    with col_edit:
                        st.text_input("H1", data['h1'])
                        st.text_input("Slug", data['slug'])
                        st.text_area("Meta Descripción", data['meta'], height=100)
                        st.download_button("💾 Bajar archivo .html", html_blogger, file_name=f"{data['slug']}.html")
                    with col_prev:
                        st.markdown(f"<h1>{data['h1']}</h1>", unsafe_allow_html=True)
                        st.markdown(html_blogger, unsafe_allow_html=True)
                    st.divider()
                    st.subheader("Código HTML (Pegar en Blogger)")
                    st.code(html_blogger, language="html")
                
                with t2:
                    st.subheader("Instagram / Facebook")
                    st.write(data['social']['ig'])
                    st.subheader("X (Twitter)")
                    st.write(data['social']['x'])
                    
                with t3:
                    st.json(data)

        except Exception as e:
            st.error(f"Error: {e}")
