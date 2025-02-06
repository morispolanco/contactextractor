import requests
import pandas as pd
import streamlit as st

# Configurar la página de Streamlit
st.set_page_config(page_title="Buscador de Lugares", layout="wide")

# Título de la aplicación
st.title("📍 Buscador de Lugares")

# Instrucciones en la barra lateral
with st.sidebar:
    st.header("🛠️ Instrucciones")
    st.markdown("""
    1️⃣ **Obtén tu clave API de ValueSerp**  
    2️⃣ **Pega tu clave API en el cuadro de texto**  
    3️⃣ **Ingresa un término de búsqueda (por ejemplo, 'pizza')**  
    4️⃣ **Presiona el botón para buscar lugares**  
    """)

# Función para buscar lugares usando ValueSerp
def search_places(api_key, query, location=None):
    url = "https://api.valueserp.com/search"
    params = {
        "api_key": api_key,
        "search_type": "places",
        "q": query,
        "location": location,  # Parámetro opcional para especificar la ubicación
        "num": 10  # Número máximo de resultados
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if not results:
            st.warning("❌ No se encontraron lugares para la búsqueda ingresada.")
        return results
    else:
        st.error(f"❌ Error de la API: {response.status_code} - {response.text}")
        return []

# Interfaz principal
def main():
    # Campo para ingresar la clave API
    api_key = st.text_input("🔑 Ingresa tu clave API de ValueSerp:", type="password")
    
    # Campos para ingresar el término de búsqueda y la ubicación
    col1, col2 = st.columns(2)
    with col1:
        query = st.text_input("🔍 Ingresa el término de búsqueda (por ejemplo, 'pizza'):")
    with col2:
        location = st.text_input("📍 Ingresa la ubicación (opcional):", placeholder="Ejemplo: Nueva York, NY")
    
    # Botón para buscar lugares
    if st.button("Buscar Lugares"):
        if not api_key.strip():
            st.warning("⚠️ Por favor ingresa tu clave API.")
        elif not query.strip():
            st.warning("⚠️ Por favor ingresa un término de búsqueda.")
        else:
            try:
                places = search_places(api_key, query, location)
                if places:
                    # Convertir los resultados en un DataFrame
                    df = pd.DataFrame(places)
                    st.success(f"✅ Se encontraron {len(df)} lugares.")
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    main()
