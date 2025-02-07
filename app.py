import streamlit as st
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from io import BytesIO

st.title("Buscador de Contactos Profesionales por País")

st.write("""
Esta aplicación utiliza la API de Serper para buscar información de contacto (correos electrónicos) 
de profesionales en un país específico.

Para utilizarla, introduce tu clave API de Serper.
""")

# El usuario introduce su API Key
api_key = st.text_input("Introduce tu API Key de Serper", type="password")
profesion = st.text_input("Ingresa la profesión o industria", "Ingenieros de software")
pais = st.text_input("Ingresa el país", "España")
count = st.slider("Número de resultados", 100, 1000, 100, step=100)

email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extraer_emails(texto):
    return list(set(re.findall(email_pattern, texto)))

def extraer_emails_desde_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return extraer_emails(soup.get_text())
    except requests.exceptions.RequestException:
        return []
    return []

if st.button("Buscar"):
    if not api_key:
        st.error("Por favor, introduce tu API Key de Serper.")
    elif not profesion or not pais:
        st.error("Por favor, introduce una profesión y un país.")
    else:
        with st.spinner("Buscando..."):
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            query = f"{profesion} en {pais} contacto email"
            data = {
                "q": query
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                results = response.json()
                contactos = []
                
                for item in results.get("organic", []):
                    emails = extraer_emails(item.get("snippet", ""))
                    if not emails:
                        emails = extraer_emails_desde_url(item.get("link", ""))
                    for email in emails:
                        contactos.append({
                            "Nombre": item.get("title", "Desconocido"),
                            "Email": email,
                            "Fuente": item.get("link", "#")
                        })
                
                if contactos:
                    df = pd.DataFrame(contactos)
                    st.success("Búsqueda completada con éxito!")
                    st.dataframe(df)
                    
                    # Exportar a CSV
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Descargar CSV",
                        data=csv_data,
                        file_name="contactos.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No se encontraron correos electrónicos en los resultados.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
