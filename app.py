import streamlit as st
import requests
import pandas as pd
import re

st.title("Buscador de Contactos Profesionales por País")

st.write("""
Esta aplicación utiliza la API de LangSearch para buscar información de contacto (correos electrónicos) 
de profesionales en un país específico.

Para utilizarla, necesitas configurar tu clave API en los secretos de Streamlit.
""")

# Obtener la API Key desde los secretos de Streamlit
api_key = st.secrets["LANGSEARCH_API_KEY"]
profesion = st.text_input("Ingresa la profesión o industria", "Ingenieros de software")
pais = st.text_input("Ingresa el país", "España")
count = st.slider("Número de resultados", 1, 50, 10)

email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extraer_emails(texto):
    return list(set(re.findall(email_pattern, texto)))

if st.button("Buscar"):
    if not api_key:
        st.error("La API Key no está configurada en los secretos de Streamlit.")
    elif not profesion or not pais:
        st.error("Por favor, introduce una profesión y un país.")
    else:
        with st.spinner("Buscando..."):
            url = "https://api.langsearch.com/v1/web-search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            query = f"{profesion} en {pais} contacto email"
            data = {
                "query": query,
                "freshness": "noLimit",
                "summary": True,
                "count": count
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                results = response.json()
                contactos = []
                
                for item in results.get("results", []):
                    emails = extraer_emails(item.get("summary", ""))
                    for email in emails:
                        contactos.append({
                            "Nombre": item.get("title", "Desconocido"),
                            "Email": email,
                            "Fuente": item.get("url", "#")
                        })
                
                if contactos:
                    df = pd.DataFrame(contactos)
                    st.success("Búsqueda completada con éxito!")
                    st.dataframe(df)
                else:
                    st.warning("No se encontraron correos electrónicos en los resultados.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
