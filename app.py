import requests
import pandas as pd
import streamlit as st

# Cargar API Key desde una variable de entorno o secretos de Streamlit
VALUE_SERP_API_KEY = st.secrets.get("VALUE_SERP_API_KEY")

# Configurar la página de Streamlit
st.set_page_config(page_title="Buscador de Lugares", layout="wide")

# Título de la aplicación
st.title("📍 Buscador de Lugares")

# Función para buscar lugares usando ValueSerp
def search_places(query):
    url = "https://api.valueserp.com/search"
    params = {
        "api_key": VALUE_SERP_API_KEY,
        "search_type": "places",
        "q": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        return results
    else:
        st.error(f"❌ Error al buscar lugares: {response.status_code}")
        return []

# Interfaz principal
def main():
    query = st.text_input("🔍 Ingresa el término de búsqueda (por ejemplo, 'pizza'):")
    if st.button("Buscar Lugares"):
        if not query.strip():
            st.warning("⚠️ Por favor ingrese un término de búsqueda.")
        else:
            try:
                places = search_places(query)
                if places:
                    # Convertir los resultados en un DataFrame
                    df = pd.DataFrame(places)
                    st.success(f"✅ Se encontraron {len(df)} lugares.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("❌ No se encontraron lugares para la búsqueda ingresada.")
            except Exception as e:
                st.error(f"⚠️ Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    main()
