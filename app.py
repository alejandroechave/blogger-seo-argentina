# --- PASO 3: EXPORTACIÓN (CORREGIDO PARA EVITAR ERRORES HTML) ---
if st.session_state.art_data:
    art = st.session_state.art_data
    
    # Lógica Unsplash con API Real
    url_img = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1000" 
    if api_key_unsplash:
        try:
            query = art['img_keyword']
            response = requests.get(f"https://api.unsplash.com/search/photos?query={query}&client_id={api_key_unsplash}&per_page=1")
            data = response.json()
            if data['results']:
                url_img = data['results'][0]['urls']['regular']
        except:
            st.warning("Error conectando con Unsplash, usando imagen por defecto.")

    tab_code, tab_preview = st.tabs(["📄 CÓDIGO BLOGGER (HTML)", "👁️ VISTA PREVIA"])

    with tab_code:
        # Construcción segura del Schema
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": art['titulo'],
            "description": art['meta_desc'],
            "image": url_img,
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "author": {"@type": "Person", "name": "Redacción SEO"}
        }
        
        # HTML FINAL - Limpiamos posibles errores de la IA
        schema_script = f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script>'
        
        # Encapsulamos el contenido para que no rompa el diseño
        full_html = (
            f"{schema_script}\n"
            f'<div style="text-align:center; margin-bottom:25px;">\n'
            f'  <img src="{url_img}" alt="{art["titulo"]}" style="width:100%; max-width:850px; border-radius:15px;"/>\n'
            f'</div>\n'
            f'<h1>{art["titulo"]}</h1>\n'
            f'<p><strong>{art["intro"]}</strong></p>\n'
            f'\n'
            f'{art["cuerpo"]}\n'
            f'<section>\n'
            f'  <h2>Preguntas Frecuentes</h2>\n'
            f'  {art["faq"]}\n'
            f'</section>'
        )
        
        st.subheader("Copia este código y pégalo en Blogger (Vista HTML)")
        st.code(full_html, language="html")

    with tab_preview:
        st.write(f"**Slug Sugerido:** `{art['slug']}`")
        st.write(f"**Meta Descripción:** {art['meta_desc']}")
        st.divider()
        # Renderizado de seguridad para la vista previa
        st.markdown(full_html, unsafe_allow_html=True)
