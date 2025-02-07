import streamlit as st
import requests
import json

st.title("Buscador de Información con LangSearch API")

st.write("""
Esta aplicación utiliza la API de LangSearch para realizar búsquedas web y obtener resúmenes de los resultados.

Para utilizarla, necesitas una clave API de LangSearch.
""")

api_key = st.text_input("Introduce tu API Key de LangSearch", type="password")
query = st.text_input("Ingresa tu consulta de búsqueda", "tell me the highlights from Apple 2024 ESG report")
count = st.slider("Número de resultados", 1, 20, 10)

if st.button("Buscar"):
    if not api_key:
        st.error("Por favor, introduce tu API Key.")
    elif not query:
        st.error("Por favor, introduce una consulta de búsqueda.")
    else:
        with st.spinner("Buscando..."):
            url = "https://api.langsearch.com/v1/web-search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "query": query,
                "freshness": "noLimit",
                "summary": True,
                "count": count
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                results = response.json()
                st.success("Búsqueda completada con éxito!")
                
                for idx, item in enumerate(results.get("results", []), start=1):
                    st.subheader(f"{idx}. {item.get('title', 'Sin título')}")
                    st.write(item.get("summary", "No hay resumen disponible."))
                    st.write(f"[Leer más]({item.get('url', '#')})")
                    st.write("---")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
