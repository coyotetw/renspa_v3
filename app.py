import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestión Ganadera Chubut", layout="wide")

@st.cache_data
def load_data():
    # Carga del archivo unificado
    df = pd.read_csv('renspa_unificado.csv')
    
    # 1. Limpieza de Periodo (Año) - Fundamental para evitar duplicados
    df['periodo'] = pd.to_numeric(df['periodo'], errors='coerce').fillna(0).astype(int)
    
    # 2. Limpieza de Columnas Numéricas
    cols_num = ['total ovinos', 'total bovinos', 'superficie', 'latitud', 'longitud']
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 3. Limpieza de Texto
    df['renspa'] = df['renspa'].astype(str).str.strip()
    df['cuit cuil'] = df['cuit cuil'].astype(str).str.replace('nan', 'S/D')
    df['establecimiento'] = df['establecimiento'].fillna(df['nombre_establecimiento']).fillna('S/D')
    df['departamento'] = df['departamento'].fillna('SIN DATO')
    
    return df

try:
    df = load_data()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Configuración de Visualización")
    
    # FILTRO CRÍTICO: Año (Periodo)
    años_disponibles = sorted([a for a in df['periodo'].unique() if a > 0], reverse=True)
    año_sel = st.sidebar.selectbox("Seleccionar Año de Análisis", años_disponibles)
    
    # Filtrado inicial por año para evitar duplicados en el resto de la app
    df_year = df[df['periodo'] == año_sel].copy()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros de Mapa y Tabla")
    
    # Filtro por cantidad de animales (tu pedido de productores > XX)
    tipo_stock = st.sidebar.selectbox("Filtrar Mapa/Tabla por:", ["Ovinos", "Bovinos"])
    col_stock = 'total ovinos' if tipo_stock == "Ovinos" else 'total bovinos'
    
    min_animales = st.sidebar.number_input(f"Productores con más de X {tipo_stock}:", min_value=0, value=100)
    
    # Filtro por Departamento
    deptos = st.sidebar.multiselect("Departamentos", options=sorted(df_year['departamento'].unique()), default=df_year['departamento'].unique())

    # Aplicar filtros al DF del año seleccionado
    mask = (df_year[col_stock] >= min_animales) & (df_year['departamento'].isin(deptos))
    df_filtered = df_year[mask]

    # --- CUERPO PRINCIPAL ---
    st.title(f"📊 Monitor Ganadero - Ciclo {año_sel}")
    
    # Métricas Principales
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Productores", f"{len(df_filtered)}")
    m2.metric(f"Total {tipo_stock}", f"{int(df_filtered[col_stock].sum()):,}".replace(",", "."))
    m3.metric("Superficie Total (Ha)", f"{int(df_filtered['superficie'].sum()):,}".replace(",", "."))
    m4.metric("Otros Ingresos", df_filtered['principal ingreso'].nunique())

    # --- MAPA GEOLOCALIZADO ---
    st.subheader(f"📍 Mapa de Establecimientos (> {min_animales} {tipo_stock})")
    if not df_filtered.empty:
        # Creamos una columna para el tamaño de los puntos en el mapa
        df_mapa = df_filtered[df_filtered['latitud'] != 0].copy()
        
        fig_mapa = px.scatter_mapbox(
            df_mapa, 
            lat="latitud", 
            lon="longitud", 
            color=col_stock,
            size="superficie",
            hover_name="establecimiento",
            hover_data=["renspa", "cuit cuil", "total ovinos", "total bovinos"],
            color_continuous_scale=px.colors.cyclical.IceFire, 
            size_max=15, 
            zoom=6,
            mapbox_style="carto-positron",
            height=600
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.warning("No hay datos geográficos para los filtros seleccionados.")

    # --- DOCUMENTO DE PRODUCTORES (TABLA EXPORTABLE) ---
    st.subheader("📋 Listado de Productores Seleccionados")
    # Seleccionamos solo las columnas que pediste
    columnas_ver = ['cuit cuil', 'establecimiento', 'departamento', 'renspa', 'total ovinos', 'total bovinos', 'superficie']
    st.dataframe(df_filtered[columnas_ver], use_container_width=True)
    
    # Botón de descarga
    csv = df_filtered[columnas_ver].to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Listado (CSV)", csv, f"productores_{año_sel}.csv", "text/csv")

    # --- ESTADÍSTICAS DE EVOLUCIÓN ---
    st.markdown("---")
    st.subheader("📈 Evolución Histórica (Año tras Año)")
    
    # Agrupamos el DF original (el que tiene todos los años)
    evolucion = df[df['periodo'] > 0].groupby('periodo')[['total ovinos', 'total bovinos']].sum().reset_index()
    
    if not evolucion.empty:
        fig_evol = px.line(evolucion, x='periodo', y=['total ovinos', 'total bovinos'], 
                           markers=True, title="Evolución del Stock Provincial")
        fig_evol.update_xaxes(type='category')
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("No hay suficientes datos históricos para mostrar la evolución.")

except Exception as e:
    st.error(f"Error en la aplicación: {e}")
