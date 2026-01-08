import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SEO Global & Multi-Image AI", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Pegá tu Gemini API Key:", type="password")
    st.info("Obtenela en [aistudio.google.com](https://aistudio.google.com)")

def buscar_modelo():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        return None
    return None

if api_key:
    genai.configure(api_key=api_key)
    modelo_nombre = buscar_modelo()
    if modelo_nombre:
        model = genai.GenerativeModel(modelo_nombre)
    else:
        st.sidebar.error("No se encontró el modelo.")

st.title("🚀 Hub SEO Internacional con IA Visual (Múltiples Imágenes)")
st.markdown("Generación de artículos en **español neutro** con **3 imágenes automáticas**.")

idea_usuario = st.text_input("¿Qué tema desea investigar?", placeholder="Ej: Las maravillas del océano profundo")

if idea_usuario and api_key and 'model' in locals():
    try:
        if 'kw_data' not in st.session_state:
            with st.spinner("Analizando métricas..."):
                prompt_kw = f"""Actúe como una herramienta SEO profesional. 
                Para el tema '{idea_usuario}', genere 5 palabras clave de cola larga.
                Estime volumen global y dificultad. Devuelva SOLO JSON:
                {{"data": [{{"kw": "ejemplo", "vol": "1k", "dif": "20%"}}]}}"""
                
                response = model.generate_content(prompt_kw)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    st.session_state.kw_data = json.loads(match.group())['data']

        if 'kw_data' in st.session_state:
            st.subheader("📊 Análisis de Palabras Clave")
            df = pd.DataFrame(st.session_state.kw_data)
            df.columns = ["Palabra Clave", "Vol. Búsqueda", "Dificultad (KD)"]
            st.table(df)

            opciones = [item['kw'] for item in st.session_state.kw_data]
            seleccion = st.selectbox("Seleccione la palabra clave:", opciones)

            if st.button("✨ Generar Contenido y Imágenes"):
                with st.spinner("Redactando y generando arte visual para 3 imágenes..."):
                    prompt_final = f"""
                    Actúe como experto SEO global y generador de imágenes. Idioma: ESPAÑOL NEUTRO (sin regionalismos ni mención a países).
                    Tema: '{seleccion}'.
                    
                    ENTREGUE UN JSON CON:
                    - h1: Título.
                    - slug: URL amigable.
                    - meta: Meta descripción (150 caracteres).
                    - html: Contenido en HTML (h2, h3, p, ul).
                    - img_data: Un array de 3 objetos, cada uno con:
                        - 'prompt': Una descripción detallada en INGLÉS para generar la imagen (ej: 'underwater coral reef, vibrant colors, fish swimming, photorealistic').
                        - 'alt': Texto ALT para SEO correspondiente a esa imagen.
                    - ig_post: Post para Instagram.
                    - x_thread: Hilo de Twitter.
                    """
                    
                    res_final = model.generate_content(prompt_final)
                    match_art = re.search(r'\{.*\}', res_final.text, re.DOTALL)
                    
                    if match_art:
                        data = json.loads(match_art.group())
                        
                        # --- GENERACIÓN DE IMÁGENES ---
                        generated_images = []
                        for i, img_info in enumerate(data.get('img_data', [])):
                            prompt_img = urllib.parse.quote(img_info['prompt'])
                            # Usamos un 'seed' diferente para cada imagen para mayor variedad
                            url_imagen = f"https://pollinations.ai/p/{prompt_img}?width=800&height=450&seed={i+1}&model=flux"
                            generated_images.append({'url': url_imagen, 'alt': img_info['alt']})
                        
                        # --- INSERTAR IMÁGENES EN EL HTML ---
                        final_html = data.get('html', '')
                        if generated_images:
                            # Divide el HTML en 3 partes para insertar las imágenes de forma equitativa
                            partes = re.split(r'(<h2>.*?</h2>)', final_html, maxsplit=2) # Busca los primeros 2 H2
                            
                            html_con_imagenes = ""
                            img_idx = 0
                            
                            # Inserta la primera imagen después del primer párrafo
                            if len(partes) > 0:
                                # Busca el primer párrafo después de la intro o del H1
                                match_p = re.search(r'(<p>.*?</p>)', partes[0], re.DOTALL)
                                if match_p and img_idx < len(generated_images):
                                    img_tag = f'<img src="{generated_images[img_idx]["url"]}" alt="{generated_images[img_idx]["alt"]}" style="width:100%; border-radius:8px; margin: 20px 0;"><br><p style="font-style: italic; text-align: center;">{generated_images[img_idx]["alt"]}</p>'
                                    final_html = final_html.replace(match_p.group(0), match_p.group(0) + img_tag, 1)
                                    img_idx += 1
                                # else: si no encuentra párrafo para la primera imagen, la pone al principio
                                #    if img_idx < len(generated_images):
                                #        img_tag = f'<img src="{generated_images[img_idx]["url"]}" alt="{generated_images[img_idx]["alt"]}" style="width:100%; border-radius:8px; margin: 20px 0;"><br><p style="font-style: italic; text-align: center;">{generated_images[img_idx]["alt"]}</p>'
                                #        final_html = img_tag + final_html
                                #        img_idx += 1


                            # Intenta insertar las imágenes restantes después de los siguientes H2
                            if img_idx < len(generated_images):
                                # Busca el texto entre el primer y segundo H2 (si existen)
                                match_h2 = re.search(r'<h2>.*?</h2>(.*?)<h2>.*?</h2>', final_html, re.DOTALL)
                                if match_h2:
                                    # Busca un párrafo dentro de esa sección para insertar la segunda imagen
                                    match_p_mid = re.search(r'(<p>.*?</p>)', match_h2.group(1), re.DOTALL)
                                    if match_p_mid and img_idx < len(generated_images):
                                        img_tag = f'<img src="{generated_images[img_idx]["url"]}" alt="{generated_images[img_idx]["alt"]}" style="width:100%; border-radius:8px; margin: 20px 0;"><br><p style="font-style: italic; text-align: center;">{generated_images[img_idx]["alt"]}</p>'
                                        final_html = final_html.replace(match_p_mid.group(0), match_p_mid.group(0) + img_tag, 1)
                                        img_idx += 1
                                # Si no encuentra otro H2 o párrafo, la inserta al final de la primera parte.
                                # else:
                                #    if img_idx < len(generated_images):
                                #        img_tag = f'<img src="{generated_images[img_idx]["url"]}" alt="{generated_images[img_idx]["alt"]}" style="width:100%; border-radius:8px; margin: 20px 0;"><br><p style="font-style: italic; text-align: center;">{generated_images[img_idx]["alt"]}</p>'
                                #        final_html += img_tag
                                #        img_idx += 1
                            
                            # Si queda una tercera imagen y no se insertó, se inserta al final
                            if img_idx < len(generated_images):
                                img_tag = f'<img src="{generated_images[img_idx]["url"]}" alt="{generated_images[img_idx]["alt"]}" style="width:100%; border-radius:8px; margin: 20px 0;"><br><p style="font-style: italic; text-align: center;">{generated_images[img_idx]["alt"]}</p>'
                                final_html += img_tag


                        t1, t2, t3 = st.tabs(["📝 Blog & SEO", "📸 Instagram", "🐦 X"])
                        
                        with t1:
                            col_a, col_b = st.columns([1, 2])
                            with col_a:
                                st.subheader("Parámetros SEO")
                                st.text_input("Título H1", data.get('h1', ''))
                                st.text_input("URL Slug", data.get('slug', ''))
                                st.text_area("Meta Descripción", data.get('meta', ''), height=100)
                                
                                st.subheader("Imágenes y ALT")
                                for i, img_info in enumerate(generated_images):
                                    st.image(img_info['url'], caption=f"Imagen {i+1}", width=150)
                                    st.text_area(f"ALT Imagen {i+1}", img_info['alt'], height=70, key=f"alt_edit_{i}")
                            
                            with col_b:
                                st.subheader("Vista Previa")
                                st.markdown(f"<h1>{data.get('h1', '')}</h1>", unsafe_allow_html=True)
                                st.markdown(final_html, unsafe_allow_html=True)
                            
                            st.divider()
                            st.subheader("Código HTML para Blogger")
                            st.code(final_html, language="html")
                            
                        with t2:
                            st.text_area("Instagram/FB", data.get('ig_post', ''), height=400)
                            
                        with t3:
                            st.text_area("Twitter Thread", data.get('x_thread', ''), height=400)
    except Exception as e:
        st.error(f"Error: {e}")
