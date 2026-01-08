import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import time
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Hub Pro - Ultra-Fast", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.warning("⚠️ Límite de cuota: Si ves el error 429, esperá al menos 30 segundos. Esta versión usa la mitad de recursos.")

def buscar_modelo():
    try:
        # Intentamos usar el modelo 1.5 Flash que suele tener cuotas más amplias que el 2.0
        return 'gemini-1.5-flash'
    except: return None

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 Hub SEO Internacional: Paso Único")
st.markdown("Generación completa de Keywords, Artículo, Schema e Imágenes en **un solo clic**.")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Avances en medicina robótica")

if idea_usuario and api_key:
    if st.button("✨ Generar Todo el Contenido (Ahorro de Cuota)"):
        try:
            with st.spinner("Procesando investigación y redacción..."):
                # PROMPT CONSOLIDADO: Una sola llamada para todo
                prompt_unico = f"""
                Actúe como experto SEO Senior. Idioma: ESPAÑOL NEUTRO. Tema base: '{idea_usuario}'.
                
                REALICE LO SIGUIENTE Y ENTREGUE ÚNICAMENTE UN JSON:
                1. 3 Keywords de cola larga con volumen est. y dificultad.
                2. Un artículo (H1, Slug, Meta descripción).
                3. Cuerpo del post: Introducción, Desarrollo (con H2) y Conclusión.
                4. 3 Preguntas Frecuentes (FAQ).
                5. 3 Prompts de imagen en INGLÉS y 3 Textos ALT en español.
                6. Posts para IG y X.
                
                JSON ESTRUCTURA:
                {{
                  "keywords": [{{"kw": "...", "vol": "...", "dif": "..."}}],
                  "h1": "...", "slug": "...", "meta": "...",
                  "intro": "...", "desarrollo": "...", "conclusion": "...",
                  "faq": [{{"q": "...", "a": "..."}}],
                  "img_prompts": ["...", "...", "..."],
                  "alt_texts": ["...", "...", "..."],
                  "social": {{"ig": "...", "x": "..."}}
                }}
                """
                
                response = model.generate_content(prompt_unico)
                data_str = limpiar_json(response.text)
                
                if data_str:
                    data = json.loads(data_str)
                    
                    # --- LÓGICA DE IMÁGENES ---
                    def get_img(p, s):
                        p_enc = urllib.parse.quote(p)
                        return f"https://pollinations.ai/p/{p_enc}?width=1024&height=768&seed={s}"

                    imgs = [get_img(data['img_prompts'][i], i+100) for i in range(3)]
                    
                    # --- SCHEMA JSON-LD ---
                    faq_list = data.get('faq', [])
                    faq_schema = ", ".join([f'{{ "@type": "Question", "name": "{f["q"]}", "acceptedAnswer": {{ "@type": "Answer", "text": "{f["a"]}" }} }}' for f in faq_list])
                    
                    schema_block = f"""
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
  "mainEntity": [{faq_schema}]
}}
</script>"""

                    # --- CONSTRUCCIÓN HTML BLOGGER ---
                    html_blogger = f"""
{schema_block}
<div class="separator" style="text-align: center;"><img src="{imgs[0]}" alt="{data['alt_texts'][0]}" style="width:100%; border-radius:12px;"/></div>
<p>{data['intro']}</p>
<div class="separator" style="text-align: center;"><img src="{imgs[1]}" alt="{data['alt_texts'][1]}" style="width:100%; border-radius:12px; margin:20px 0;"/></div>
{data['desarrollo']}
<div class="separator" style="text-align: center;"><img src="{imgs[2]}" alt="{data['alt_texts'][2]}" style="width:100%; border-radius:12px; margin-top:20px;"/></div>
<p>{data['conclusion']}</p>
<div class="faq-section"><h2>Preguntas Frecuentes</h2>{''.join([f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in faq_list])}</div>
                    """

                    # --- VISTA ---
                    st.success("¡Contenido generado con éxito!")
                    
                    tab1, tab2, tab3 = st.tabs(["📝 Blogger & SEO", "📊 Keywords", "📸 Social"])
                    
                    with tab1:
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.subheader("SEO & Slug")
                            st.text_input("H1", data['h1'])
                            st.text_input("Slug", data['slug'])
                            st.text_area("Meta", data['meta'])
                            st.download_button("💾 Bajar HTML", html_blogger, file_name=f"{data['slug']}.html")
                        with c2:
                            st.markdown(html_blogger, unsafe_allow_html=True)
                        st.divider()
                        st.subheader("Código para Blogger")
                        st.code(html_blogger, language="html")
                        
                    with tab2:
                        st.table(pd.DataFrame(data['keywords']))
                    
                    with tab3:
                        st.subheader("Instagram")
                        st.write(data['social']['ig'])
                        st.subheader("X (Twitter)")
                        st.write(data['social']['x'])

        except Exception as e:
            st.error(f"Error: {e}. Probablemente la cuota diaria se agotó. Intenta mañana o usa otra API Key.")
