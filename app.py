import streamlit as st
import requests
import re
from io import BytesIO
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Título de la aplicación
st.title("Buscador de Contactos por Profesión/Industria y País")
st.write("""
Esta aplicación utiliza la API de Serper.dev para buscar en Google profesiones o industrias, junto con países, 
y obtener información de contacto (emails) de las páginas web encontradas. 
Luego permite exportar los resultados a CSV o Excel.
""")
st.write("""
**Obtener API Key de Serper:**
1. Visitar [Serper](https://serper.dev/).
2. Registrarse o iniciar sesión.
3. Acceder a su cuenta y obtener la clave API.
""")

# Inputs del usuario
profesion = st.text_input("Ingrese la profesión o industria (ej: 'Abogados', 'Empresas de marketing'):")
pais = st.text_input("Ingrese el país (ej: 'España', 'México', 'Argentina'):")
api_key = st.text_input("Introduzca su API Key de Serper (Obligatorio)", type="password")

# Expresión regular mejorada para emails
email_pattern = r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

# Función para validar emails
def es_email_valido(email):
    if '@' not in email:
        return False
    parte_local, parte_dominio = email.split('@', 1)
    if '.' not in parte_dominio:
        return False
    # Descartar correos que tengan dígitos justo después de '@'
    if parte_dominio and parte_dominio[0].isdigit():
        return False
    return True

# Filtrar emails válidos
def filtrar_emails(emails):
    return [e for e in emails if not e.lower().endswith('.png') and es_email_valido(e)]

# Extraer emails de texto
def extraer_emails_texto(texto):
    found = re.findall(email_pattern, texto)
    found = list(set(found))
    return filtrar_emails(found)

# Extraer emails del HTML
def extraer_emails_html(url_sitio):
    emails_encontrados = []
    try:
        resp = requests.get(url_sitio, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Extraer texto visible
            texts = soup.stripped_strings
            for text in texts:
                found = re.findall(email_pattern, text)
                emails_encontrados.extend(found)
    except requests.exceptions.RequestException:
        pass
    return filtrar_emails(emails_encontrados)

# Verificar API Key
def verificar_api_key(api_key):
    test_url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(test_url, headers=headers, json={"q": "test", "location": "es-ES", "gl": "es", "hl": "es", "start": 0}, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

# Botón de búsqueda
if st.button("Buscar"):
    if not profesion or not pais or not api_key:
        st.error("Por favor ingrese la profesión/industria, el país y la API Key antes de continuar.")
    else:
        with st.spinner("Verificando la API Key..."):
            if not verificar_api_key(api_key):
                st.error("API Key inválida o no se pudo verificar. Por favor, revise su clave.")
            else:
                query = f"{profesion} en {pais} contacto email"
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                }
                contactos = []
                resultados_por_pagina = 10
                emails_encontrados_set = set()
                resultados_obtenidos = False
                paginas_resultados = []

                with st.spinner("Realizando búsqueda, por favor espere..."):
                    # Etapa 1: Obtener todos los resultados necesarios
                    start = 0
                    while True:
                        try:
                            response = requests.post(url, headers=headers, json={
                                "q": query,
                                "location": "es-ES",
                                "gl": "es",
                                "hl": "es",
                                "start": start
                            }, timeout=5)
                            response.raise_for_status()
                        except requests.exceptions.Timeout:
                            st.error("La solicitud a la API de Serper ha excedido el tiempo de espera.")
                            break
                        except requests.exceptions.HTTPError as http_err:
                            st.error(f"Error HTTP al conectar con la API de Serper: {http_err}")
                            break
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error al conectar con la API de Serper: {e}")
                            break

                        data = response.json()
                        if "organic" not in data or len(data["organic"]) == 0:
                            if not resultados_obtenidos:
                                st.info("No se encontraron resultados para la búsqueda realizada.")
                            break
                        resultados_obtenidos = True
                        paginas_resultados.extend(data["organic"])
                        start += resultados_por_pagina

                        # Si no hay más resultados, salir del bucle
                        if len(data["organic"]) < resultados_por_pagina:
                            break

                    # Etapa 2: Extraer emails primero de los snippets
                    progress_bar = st.progress(0)
                    for i, item in enumerate(paginas_resultados):
                        snippet = item.get("snippet", "")
                        title = item.get("title", "")
                        emails_snippet = extraer_emails_texto(snippet)
                        for email in emails_snippet:
                            if email not in emails_encontrados_set:
                                emails_encontrados_set.add(email)
                                contactos.append({
                                    "nombre": title,
                                    "email": email
                                })
                        progress = (i + 1) / len(paginas_resultados)
                        progress_bar.progress(min(progress, 1.0))

                    # Etapa 3: Si no alcanzamos el objetivo, extraer del HTML
                    if len(contactos) > 0:
                        with ThreadPoolExecutor(max_workers=10) as executor:
                            future_to_url = {executor.submit(extraer_emails_html, item.get("link", "")): item for item in paginas_resultados if item.get("link", "")}
                            for future in as_completed(future_to_url):
                                item = future_to_url[future]
                                title = item.get("title", "")
                                try:
                                    emails_html = future.result()
                                    for email in emails_html:
                                        if email not in emails_encontrados_set:
                                            emails_encontrados_set.add(email)
                                            contactos.append({
                                                "nombre": title,
                                                "email": email
                                            })
                                except Exception:
                                    continue

                st.success(f"Se han encontrado {len(contactos)} contactos.")
                if resultados_obtenidos and len(contactos) == 0:
                    st.info("No se encontraron correos electrónicos válidos en los resultados. Intente con otras palabras clave.")

                if len(contactos) > 0:
                    df = pd.DataFrame(contactos, columns=["nombre", "email"])

                    # Exportar a CSV (UTF-8)
                    csv_data = df.to_csv(index=False).encode("utf-8")

                    # Exportar a Excel (UTF-8)
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Contactos')
                    excel_data = excel_buffer.getvalue()

                    # Crear columnas para los botones de descarga
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Descargar CSV",
                            data=csv_data,
                            file_name="contactos.csv",
                            mime="text/csv"
                        )
                    with col2:
                        st.download_button(
                            label="Descargar Excel",
                            data=excel_data,
                            file_name="contactos.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
