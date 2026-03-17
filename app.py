import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Monitor Productivo Chubut", layout="wide")

@st.cache_data
def load_data():
    # Carga el archivo desde el mismo directorio donde está la app
    # Asegurate de subir 'renspa_unificado.csv' a tu GitHub
    df = pd.read_csv('renspa_unificado.csv')
    
    # Aseguramos que las columnas clave sean tratadas como strings para los filtros
    df['renspa'] = df['renspa'].astype(str)
    df['cuit cuil'] = df['cuit cuil'].astype(str)
    
    return df

try:
    df = load_data()
    
    st.title("📊 Panel de Control: RENSPA y Stock Ovino")
    st.markdown("Datos unificados de encuesta y georreferenciación (Archivo Local).")

    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header("Filtros de Búsqueda")

    # 1. Filtro por RENSPA (Buscador de texto)
    search_renspa = st.sidebar.text_input("Buscar por RENSPA")

    # 2. Filtro por CUIT/CUIL (Buscador de texto)
    search_cuit = st.sidebar.text_input("Buscar por CUIT/CUIL")

    # 3. Filtro por Rango de Ovinos (Slider)
    # Usamos float por si hay decimales, luego convertimos a int para el slider
    min_o, max_o = int(df['total ovinos'].min()), int(df['total ovinos'].max())
    rango_ovinos = st.sidebar.slider("Rango de Stock Ovino", min_o, max_o, (min_o, max_o))

    # 4. Filtro por Departamento
    deptos_disponibles = sorted(df['departamento'].unique().tolist())
    depto_sel = st.sidebar.multiselect("Filtrar por Departamento", options=deptos_disponibles, default=deptos_disponibles)

    # --- APLICACIÓN DE FILTROS ---
    mask = (
        df['renspa'].str.contains(search_renspa, case=False, na=False) &
        df['cuit cuil'].str.contains(search_cuit, na=False) &
        df['total ovinos'].between(rango_ovinos[0], rango_ovinos[1]) &
        df['departamento'].isin(depto_sel)
    )
    df_filtered = df[mask]

    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Establecimientos", f"{len(df_filtered)}")
    col2.metric("Total Ovinos", f"{int(df_filtered['total ovinos'].sum()):,}".replace(",", "."))
    col3.metric("Total Bovinos", f"{int(df_filtered['total bovinos'].sum()):,}".replace(",", "."))
    col4.metric("Superficie (Ha)", f"{int(df_filtered['superficie'].sum()):,}".replace(",", "."))

    # --- TABLA DE DATOS ---
    st.subheader("Detalle de Establecimientos")
    st.dataframe(df_filtered, use_container_width=True)

    # --- MAPA ---
    st.subheader("Geolocalización")
    if not df_filtered.empty and 'latitud' in df_filtered.columns:
        # Streamlit necesita columnas llamadas 'lat' y 'lon' o 'latitud' y 'longitud'
        map_df = df_filtered[['latitud', 'longitud']].dropna()
        st.map(map_df)
    else:
        st.info("No hay datos geográficos disponibles para los filtros seleccionados.")

except FileNotFoundError:
    st.error("No se encontró el archivo 'renspa_unificado.csv'. Asegurate de subirlo a tu repositorio de GitHub.")
except Exception as e:
    st.error(f"Ocurrió un error inesperado: {e}")
