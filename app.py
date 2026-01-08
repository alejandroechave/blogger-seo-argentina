import streamlit as st
from groq import Groq
import json
import re

# Configuración de página
st.set_page_config(page_title="SEO Writer Pro", layout="centered")

def limpiar_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else None

# Interfaz
st.title("🚀 Redactor SEO Premium")
st.markdown("Genera artículos profesionales para Blogger sin errores de código.")

with st.sidebar:
    api_key = st.text_input("Groq API Key:", type="password")
    if api_key:
        client = Groq(api_key=api_key)

tema = st.text_input("Tema del artículo:")

if tema and api_key:
    if st.button("Escribir Artículo Ahora"):
        try:
            with st.spinner("Redactando contenido de alta calidad..."):
                prompt = f"""Escribe un artículo SEO extenso sobre '{tema}'. 
                Responde ÚNICAMENTE en JSON con esta estructura:
                {{
                  "titulo": "...",
                  "meta": "...",
                  "html_completo": "Cuerpo del post con h2, h3 y párrafos largos",
                  "prompt_imagen": "descripción en inglés",
                  "redes": "texto redes"
                }}"""
                
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                datos = json.loads(limpiar_json(res.choices[0].message.content))
                
                # --- PRESENTACIÓN SIN DUPLICADOS ---
                st.divider()
                st.header(datos['titulo'])
                
                tab1, tab2, tab3 = st.tabs(["📄 CÓDIGO PARA BLOGGER", "👁️ VISTA PREVIA", "🖼️ IMAGEN"])

                with tab1:
                    st.warning("⚠️ COPIA SOLO EL CONTENIDO DEL CUADRO NEGRO DE ABAJO")
                    # Este es el único código que debes copiar para Blogger
                    codigo_final = f"<h1>{datos['titulo']}</h1>\n{datos['html_completo']}\n<p><strong>Resumen:</strong> {datos['meta']}</p>"
                    st.code(codigo_final, language="html")

                with tab2:
                    st.markdown("### Así se verá en tu blog:")
                    st.markdown(codigo_final, unsafe_allow_html=True)

                with tab3:
                    p_limpio = re.sub(r'[^a-zA-Z]', '-', datos['prompt_imagen']).lower()
                    img_url = f"https://pollinations.ai/p/{p_limpio}?width=1024&height=768&nologo=true"
                    st.image(img_url, caption="Imagen sugerida")
                    st.markdown(f"**Código de imagen:**")
                    st.code(f'<img src="{img_url}" style="width:100%; border-radius:10px;" />')

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    st.info("Introduce tu API Key y el tema para empezar.")
