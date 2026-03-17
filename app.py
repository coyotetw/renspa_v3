import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor Productivo Chubut", layout="wide")

@st.cache_data
def load_data():
    # 1. Cargar el archivo
    df = pd.read_csv('renspa_unificado.csv')
    
    # 2. LIMPIEZA CRÍTICA: Convertir columnas numéricas y manejar errores
    # Esto reemplaza cualquier texto o celda vacía por 0 para que no falle el slider
    cols_numericas = ['total ovinos', 'total bovinos', 'superficie']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 3. Asegurar que las columnas de búsqueda sean texto
    df['renspa'] = df['renspa'].astype(str).replace('nan', '')
    df['cuit cuil'] = df['cuit cuil'].astype(str).replace('nan', '')
    df['departamento'] = df['departamento'].fillna('SIN DATO').astype(str)
    
    return df

try:
    df = load_data()
    
    st.title("📊 Panel de Control: RENSPA y Stock Ovino")

    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header("Filtros de Búsqueda")

    search_renspa = st.sidebar.text_input("Buscar por RENSPA")
    search_cuit = st.sidebar.text_input("Buscar por CUIT/CUIL")

    # Filtro de Ovinos con valores convertidos a int para evitar el error de comparación
    min_o = int(df['total ovinos'].min())
    max_o = int(df['total ovinos'].max())
    
    # El slider ahora siempre recibirá enteros, evitando el error de '<' entre float/str
    rango_ovinos = st.sidebar.slider("Rango de Stock Ovino", min_o, max_o, (min_o, max_o))

    deptos_disponibles = sorted(df['departamento'].unique().tolist())
    depto_sel = st.sidebar.multiselect("Filtrar por Departamento", options=deptos_disponibles, default=deptos_disponibles)

    # --- APLICACIÓN DE FILTROS ---
    mask = (
        df['renspa'].str.contains(search_renspa, case=False, na=False) &
        df['cuit cuil'].str.contains(search_cuit, na=False) &
        (df['total ovinos'] >= rango_ovinos[0]) & 
        (df['total ovinos'] <= rango_ovinos[1]) &
        df['departamento'].isin(depto_sel)
    )
    df_filtered = df[mask]

    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Establecimientos", f"{len(df_filtered)}")
    c2.metric("Total Ovinos", f"{int(df_filtered['total ovinos'].sum()):,}".replace(",", "."))
    c3.metric("Total Bovinos", f"{int(df_filtered['total bovinos'].sum()):,}".replace(",", "."))
    c4.metric("Superficie (
