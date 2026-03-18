import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor Ganadero · Chubut",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root & Reset ── */
:root {
    --bg:         #0d1117;
    --bg2:        #161b22;
    --bg3:        #21262d;
    --border:     #30363d;
    --accent:     #3fb950;
    --accent2:    #58a6ff;
    --accent3:    #f78166;
    --text:       #e6edf3;
    --text-muted: #8b949e;
    --radius:     10px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* ── Background ── */
.stApp { background: var(--bg) !important; }
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

/* ── Sidebar widgets ── */
section[data-testid="stSidebar"] label { color: var(--text-muted) !important; font-size: 0.78rem !important; letter-spacing: .05em; text-transform: uppercase; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stNumberInput > div > div > input,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.4rem !important;
    transition: border-color .2s;
}
[data-testid="metric-container"]:hover { border-color: var(--accent) !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-size: 1.9rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: .8rem !important; }

/* ── DataFrames ── */
.stDataFrame { border-radius: var(--radius) !important; overflow: hidden; border: 1px solid var(--border) !important; }

/* ── Buttons ── */
.stDownloadButton > button, .stButton > button {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all .2s;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    padding: 3px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
    transition: all .2s;
}
.stTabs [aria-selected="true"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: .6rem;
    font-size: 1rem; font-weight: 600; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: .08em;
    margin: 1.5rem 0 .8rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: .5rem;
}

/* ── Alert / info boxes ── */
.stAlert { border-radius: var(--radius) !important; }

/* ── Chart containers ── */
.plot-container { border-radius: var(--radius) !important; overflow: hidden; }

/* ── Print styles ── */
@media print {
    section[data-testid="stSidebar"]        { display: none !important; }
    .stDownloadButton, .stButton            { display: none !important; }
    .stTabs [data-baseweb="tab-list"]       { display: none !important; }
    [data-testid="stToolbar"]               { display: none !important; }
    .stApp, body                            { background: white !important; color: black !important; }
    [data-testid="metric-container"]        { border: 1px solid #ccc !important; background: #f9f9f9 !important; }
    .js-plotly-plot .plotly                 { page-break-inside: avoid; }
    h1, h2, h3                              { color: black !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY TEMPLATE ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(22,27,34,1)",
    plot_bgcolor="rgba(22,27,34,1)",
    font=dict(family="DM Sans", color="#e6edf3", size=12),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
    legend=dict(bgcolor="rgba(22,27,34,0)", bordercolor="#30363d"),
    margin=dict(l=40, r=20, t=40, b=40),
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# ─── DATA LOADING ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('renspa_unificado.csv')
    df['periodo'] = pd.to_numeric(df['periodo'], errors='coerce').fillna(0).astype(int)
    cols_num = ['total ovinos', 'total bovinos', 'superficie', 'latitud', 'longitud']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['renspa']         = df['renspa'].astype(str).str.strip()
    df['cuit cuil']      = df['cuit cuil'].astype(str).str.replace('nan', 'S/D')
    df['establecimiento'] = df.get('establecimiento', pd.Series()).fillna(df.get('nombre_establecimiento', '')).fillna('S/D')
    df['departamento']   = df['departamento'].fillna('SIN DATO')
    if 'condicion' in df.columns:
        df['condicion'] = df['condicion'].fillna('S/D')
    if 'principal ingreso' in df.columns:
        df['principal ingreso'] = df['principal ingreso'].fillna('S/D')
    return df

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐑 Monitor Ganadero")
    st.markdown("<small style='color:#8b949e'>Provincia del Chubut · RENSPA</small>", unsafe_allow_html=True)
    st.markdown("---")

    try:
        df = load_data()
        LOADED = True
    except Exception as e:
        st.error(f"No se pudo cargar el CSV: {e}")
        LOADED = False
        st.stop()

    años_disponibles = sorted([a for a in df['periodo'].unique() if a > 0], reverse=True)
    año_sel = st.selectbox("📅 Año de análisis", años_disponibles)

    st.markdown("---")
    st.markdown("**Filtros de stock**")
    tipo_stock = st.selectbox("Tipo de ganado", ["Ovinos", "Bovinos"])
    col_stock  = 'total ovinos' if tipo_stock == "Ovinos" else 'total bovinos'
    min_animales = st.number_input(f"Mínimo de {tipo_stock}", min_value=0, value=100, step=50)

    st.markdown("---")
    st.markdown("**Filtros territoriales**")
    df_year = df[df['periodo'] == año_sel].copy()
    deptos_all = sorted(df_year['departamento'].unique())
    deptos = st.multiselect("Departamentos", options=deptos_all, default=deptos_all)

    # Informe primordial: umbral CUIT — sigue al tipo_stock seleccionado
    st.markdown("---")
    st.markdown("**Informe de productores**")
    umbral_cuit = st.number_input(f"Umbral {tipo_stock} para informe CUIT", min_value=0, value=1000, step=100)

    st.markdown("---")
    st.caption(f"Datos cargados: {len(df):,} registros · {df['periodo'].nunique()} periodos")

# ─── FILTERED DATA ────────────────────────────────────────────────────────────
mask         = (df_year[col_stock] >= min_animales) & (df_year['departamento'].isin(deptos))
df_filtered  = df_year[mask].copy()
df_cuit_inf  = df_year[(df_year[col_stock] >= umbral_cuit) & (df_year['departamento'].isin(deptos))].copy()

# ─── HEADER ──────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"# Monitor Ganadero · Ciclo {año_sel}")
    st.markdown(f"<small style='color:#8b949e'>Actualizado: {datetime.now().strftime('%d/%m/%Y')} · Filtro activo: ≥{min_animales} {tipo_stock}</small>", unsafe_allow_html=True)
with col_h2:
    # Botón de impresión
    st.markdown("""
    <button onclick="window.print()" style="
        width:100%; padding:.55rem 1rem; margin-top:1.5rem;
        background:#21262d; border:1px solid #30363d; border-radius:10px;
        color:#e6edf3; font-family:'DM Sans',sans-serif; font-size:.9rem;
        cursor:pointer; transition:all .2s;
    " onmouseover="this.style.borderColor='#3fb950'" onmouseout="this.style.borderColor='#30363d'">
        🖨️ Imprimir / Exportar PDF
    </button>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── KPI METRICS ─────────────────────────────────────────────────────────────
# Calcular deltas respecto al año anterior
años_sorted = sorted([a for a in df['periodo'].unique() if a > 0])
idx_actual  = años_sorted.index(año_sel) if año_sel in años_sorted else -1
año_ant     = años_sorted[idx_actual - 1] if idx_actual > 0 else None

def get_delta(col, año_ref, año_prev, deptos_filt, min_val=0):
    if año_prev is None:
        return None
    val_ref  = df[(df['periodo'] == año_ref) & (df['departamento'].isin(deptos_filt)) & (df[col] >= min_val)][col].sum()
    val_prev = df[(df['periodo'] == año_prev) & (df['departamento'].isin(deptos_filt)) & (df[col] >= min_val)][col].sum()
    if val_prev == 0:
        return None
    return f"{((val_ref - val_prev) / val_prev * 100):+.1f}%"

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Productores activos", f"{len(df_filtered):,}")
m2.metric(f"Total {tipo_stock}", f"{int(df_filtered[col_stock].sum()):,}".replace(",", "."),
          delta=get_delta(col_stock, año_sel, año_ant, deptos, min_animales))
m3.metric("Total Ovinos (universo)", f"{int(df_year['total ovinos'].sum()):,}".replace(",", "."),
          delta=get_delta('total ovinos', año_sel, año_ant, deptos_all))
m4.metric("Superficie total (Ha)", f"{int(df_filtered['superficie'].sum()):,}".replace(",", "."))
m5.metric(f"CUIT únicos (≥{umbral_cuit} ov.)", f"{df_cuit_inf['cuit cuil'].nunique():,}")

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa geolocalizado",
    "📋 Informe CUIT",
    "📈 Evolución histórica",
    "📊 Análisis por departamento",
    "🔍 Explorador de variables",
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 · MAPA
# ════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 1])
    with col_right:
        size_var  = st.selectbox("Tamaño del punto", ["superficie", "total ovinos", "total bovinos"])
        color_var = st.selectbox("Color del punto",  ["total ovinos", "total bovinos", "superficie"])
        mapa_style = st.selectbox("Estilo de mapa", ["carto-darkmatter", "carto-positron", "open-street-map"])

    df_mapa = df_filtered[(df_filtered['latitud'] != 0) & (df_filtered['longitud'] != 0)].copy()
    df_mapa['_size'] = df_mapa[size_var].clip(lower=1)

    with col_left:
        if not df_mapa.empty:
            fig_map = px.scatter_mapbox(
                df_mapa,
                lat="latitud", lon="longitud",
                color=color_var,
                size="_size",
                hover_name="establecimiento",
                hover_data={
                    "renspa": True,
                    "cuit cuil": True,
                    "total ovinos": True,
                    "total bovinos": True,
                    "superficie": True,
                    "departamento": True,
                    "_size": False,
                },
                color_continuous_scale="Viridis",
                size_max=18,
                zoom=5.5,
                mapbox_style=mapa_style,
                height=560,
                title=f"Establecimientos {año_sel} · color={color_var} · tamaño={size_var}",
            )
            fig_map.update_layout(
                paper_bgcolor="rgba(22,27,34,1)",
                font=dict(family="DM Sans", color="#e6edf3"),
                margin=dict(l=0, r=0, t=40, b=0),
                coloraxis_colorbar=dict(tickfont=dict(color="#8b949e")),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(f"Mostrando {len(df_mapa):,} establecimientos con coordenadas válidas")
        else:
            st.warning("Sin datos geográficos para los filtros seleccionados.")

# ════════════════════════════════════════════════════════════════════
# TAB 2 · INFORME CUIT (primordial)
# ════════════════════════════════════════════════════════════════════
with tab2:
    label_ganado = tipo_stock.lower()  # "ovinos" o "bovinos"
    st.markdown(f"### Productores {label_ganado} con ≥ {umbral_cuit:,} cabezas · Ciclo {año_sel}")
    st.markdown(f"*Universo de CUITs únicos — filtro: {tipo_stock} ≥ {umbral_cuit:,} · departamentos seleccionados*")

    cols_informe = ['cuit cuil', 'establecimiento', 'departamento', 'renspa',
                    'total ovinos', 'total bovinos', 'superficie']
    if 'condicion' in df_cuit_inf.columns:
        cols_informe.append('condicion')

    df_informe = (df_cuit_inf[cols_informe]
                  .sort_values(col_stock, ascending=False)   # ← ordena por el tipo elegido
                  .reset_index(drop=True))
    df_informe.index += 1

    # Resumen rápido
    r1, r2, r3 = st.columns(3)
    r1.metric("Establecimientos", f"{len(df_informe):,}")
    r2.metric("CUITs únicos", f"{df_informe['cuit cuil'].nunique():,}")
    r3.metric(f"{tipo_stock} acumulados",          # ← label dinámico
              f"{int(df_informe[col_stock].sum()):,}".replace(",","."))

    st.dataframe(df_informe, use_container_width=True, height=480)

    csv_inf = df_informe.to_csv(index=True).encode('utf-8')
    st.download_button(
        f"⬇️ Descargar informe CUIT (CSV)",
        csv_inf,
        f"informe_cuit_{umbral_cuit}{label_ganado[:2]}_{año_sel}.csv",
        "text/csv",
    )

    # Gráfico de concentración por departamento
    st.markdown("#### Distribución por departamento")
    dist_depto = (df_informe.groupby('departamento')
                  .agg(establecimientos=('renspa','count'), stock=(col_stock,'sum'))
                  .sort_values('stock', ascending=True).reset_index())

    fig_depto = go.Figure()
    fig_depto.add_trace(go.Bar(
        y=dist_depto['departamento'],
        x=dist_depto['stock'],
        orientation='h',
        name=tipo_stock,
        marker_color='#3fb950' if tipo_stock == "Ovinos" else '#58a6ff',
        text=dist_depto['stock'].apply(lambda x: f"{int(x):,}"),
        textposition='outside',
    ))
    # Barra escalada de establecimientos
    max_stock = dist_depto['stock'].max()
    max_est   = dist_depto['establecimientos'].max()
    if max_est > 0:
        fig_depto.add_trace(go.Bar(
            y=dist_depto['departamento'],
            x=dist_depto['establecimientos'] * (max_stock / max_est),
            orientation='h',
            name='Establecimientos (escalado)',
            marker_color='#d2a8ff',
            opacity=0.45,
        ))
    fig_depto.update_layout(
        **PLOTLY_LAYOUT,
        barmode='overlay',
        height=max(300, len(dist_depto) * 32),
        title=f"{tipo_stock} ≥{umbral_cuit:,} por departamento · {año_sel}",
        xaxis_title="Cabezas",
    )
    st.plotly_chart(fig_depto, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 · EVOLUCIÓN HISTÓRICA
# ════════════════════════════════════════════════════════════════════
with tab3:
    df_hist = df[df['periodo'] > 0].copy()

    # Evolución global
    evol_global = (df_hist.groupby('periodo')
                   .agg(ovinos=('total ovinos','sum'), bovinos=('total bovinos','sum'),
                        productores=('renspa','nunique'), superficie=('superficie','sum'))
                   .reset_index())

    # ── Gráfico 1: líneas stock ──
    fig_evol = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Stock Ovino Provincial", "Stock Bovino Provincial",
                        "Nro. Establecimientos (RENSPA)", "Superficie Total (Ha)"),
        vertical_spacing=0.14, horizontal_spacing=0.1,
    )
    colors = ['#3fb950', '#58a6ff', '#f78166', '#d2a8ff']

    for i, (col_e, name) in enumerate([('ovinos','Ovinos'),('bovinos','Bovinos'),
                                        ('productores','Establecimientos'),('superficie','Superficie')]):
        r, c = divmod(i, 2)
        fig_evol.add_trace(go.Scatter(
            x=evol_global['periodo'], y=evol_global[col_e],
            mode='lines+markers', name=name,
            line=dict(color=colors[i], width=2.5),
            marker=dict(size=7),
            fill='tozeroy', fillcolor=colors[i].replace('#','rgba(').rstrip(')') if False else f"rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:7],16)},0.08)",
        ), row=r+1, col=c+1)

    fig_evol.update_layout(
        **PLOTLY_LAYOUT,
        height=520,
        showlegend=False,
        title_text=f"Evolución histórica provincial · todos los periodos",
    )
    fig_evol.update_xaxes(type='category')
    st.plotly_chart(fig_evol, use_container_width=True)

    # ── Gráfico 2: evolución por departamento ──
    st.markdown("#### Stock ovino por departamento a lo largo del tiempo")
    top_deptos = (df_hist.groupby('departamento')['total ovinos'].sum()
                  .nlargest(10).index.tolist())
    df_evol_dep = (df_hist[df_hist['departamento'].isin(top_deptos)]
                   .groupby(['periodo','departamento'])['total ovinos']
                   .sum().reset_index())

    fig_dep = px.line(
        df_evol_dep, x='periodo', y='total ovinos',
        color='departamento', markers=True,
        title="Top 10 departamentos · evolución ovinos",
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig_dep.update_layout(**PLOTLY_LAYOUT, height=420)
    fig_dep.update_xaxes(type='category')
    st.plotly_chart(fig_dep, use_container_width=True)

    # ── Variación interanual ──
    st.markdown("#### Variación interanual (%)")
    evol_pct = evol_global.copy()
    evol_pct['Δ% ovinos']  = evol_pct['ovinos'].pct_change() * 100
    evol_pct['Δ% bovinos'] = evol_pct['bovinos'].pct_change() * 100
    evol_pct = evol_pct.dropna(subset=['Δ% ovinos'])

    fig_pct = go.Figure()
    fig_pct.add_trace(go.Bar(
        x=evol_pct['periodo'].astype(str), y=evol_pct['Δ% ovinos'],
        name='Δ% Ovinos',
        marker_color=['#3fb950' if v >= 0 else '#f78166' for v in evol_pct['Δ% ovinos']],
    ))
    fig_pct.add_trace(go.Bar(
        x=evol_pct['periodo'].astype(str), y=evol_pct['Δ% bovinos'],
        name='Δ% Bovinos',
        marker_color=['#58a6ff' if v >= 0 else '#d2a8ff' for v in evol_pct['Δ% bovinos']],
        opacity=0.7,
    ))
    fig_pct.update_layout(**PLOTLY_LAYOUT, barmode='group', height=340,
                          title="Variación interanual del stock (%)")
    st.plotly_chart(fig_pct, use_container_width=True)

    # Tabla resumen histórico
    with st.expander("📄 Tabla resumen histórico"):
        st.dataframe(evol_global.sort_values('periodo', ascending=False), use_container_width=True)
        csv_h = evol_global.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar histórico (CSV)", csv_h, "historico_provincial.csv", "text/csv")

# ════════════════════════════════════════════════════════════════════
# TAB 4 · ANÁLISIS POR DEPARTAMENTO
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"### Análisis departamental · {año_sel}")

    agg_dep = (df_year.groupby('departamento')
               .agg(
                   establecimientos=('renspa','count'),
                   ovinos=('total ovinos','sum'),
                   bovinos=('total bovinos','sum'),
                   superficie=('superficie','sum'),
                   cuits=('cuit cuil','nunique'),
               ).sort_values('ovinos', ascending=False).reset_index())

    # Treemap
    fig_tree = px.treemap(
        agg_dep, path=['departamento'], values='ovinos',
        color='bovinos', color_continuous_scale='Blues',
        title=f"Distribución ovinos por departamento · {año_sel}",
        hover_data=['establecimientos','superficie','cuits'],
    )
    fig_tree.update_layout(**PLOTLY_LAYOUT, height=440)
    st.plotly_chart(fig_tree, use_container_width=True)

    # Scatter superficie vs stock
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        fig_sc = px.scatter(
            agg_dep, x='superficie', y='ovinos',
            size='establecimientos', color='bovinos',
            hover_name='departamento',
            color_continuous_scale='Viridis',
            title="Superficie vs Stock Ovino",
            size_max=40,
        )
        fig_sc.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_sc2:
        fig_bar_dep = px.bar(
            agg_dep.head(15), x='departamento',
            y=['ovinos','bovinos'],
            barmode='group',
            title="Top 15 departamentos · stock",
            color_discrete_map={'ovinos':'#3fb950','bovinos':'#58a6ff'},
        )
        fig_bar_dep.update_layout(**PLOTLY_LAYOUT, height=380)
        fig_bar_dep.update_xaxes(tickangle=35)
        st.plotly_chart(fig_bar_dep, use_container_width=True)

    st.dataframe(agg_dep, use_container_width=True)
    csv_dep = agg_dep.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar tabla departamental (CSV)", csv_dep,
                       f"departamentos_{año_sel}.csv", "text/csv")

# ════════════════════════════════════════════════════════════════════
# TAB 5 · EXPLORADOR DE VARIABLES
# ════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### Explorador libre de variables")
    st.caption("Cruzá cualquier combinación de columnas para descubrir patrones.")

    num_cols  = [c for c in ['total ovinos','total bovinos','superficie'] if c in df_year.columns]
    cat_cols  = [c for c in ['departamento','condicion','principal ingreso','partido'] if c in df_year.columns]

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1: eje_x = st.selectbox("Eje X", num_cols + cat_cols, index=0)
    with col_e2: eje_y = st.selectbox("Eje Y", num_cols, index=1 if len(num_cols) > 1 else 0)
    with col_e3: color_e = st.selectbox("Color", cat_cols + num_cols, index=0)
    with col_e4: tipo_g = st.selectbox("Tipo gráfico", ["Scatter", "Box", "Violin", "Histograma", "Barra agrupada"])

    df_exp = df_filtered.copy()

    if tipo_g == "Scatter":
        fig_exp = px.scatter(df_exp, x=eje_x, y=eje_y, color=color_e,
                             hover_name='establecimiento', opacity=0.7,
                             trendline='ols' if eje_x in num_cols else None)
    elif tipo_g == "Box":
        fig_exp = px.box(df_exp, x=color_e if color_e in cat_cols else None,
                         y=eje_y, color=color_e if color_e in cat_cols else None)
    elif tipo_g == "Violin":
        fig_exp = px.violin(df_exp, x=color_e if color_e in cat_cols else None,
                            y=eje_y, color=color_e if color_e in cat_cols else None, box=True)
    elif tipo_g == "Histograma":
        fig_exp = px.histogram(df_exp, x=eje_x, color=color_e if color_e in cat_cols else None,
                               nbins=40, opacity=0.8)
    else:
        agg_exp = df_exp.groupby(color_e)[eje_y].sum().reset_index().sort_values(eje_y, ascending=False).head(20)
        fig_exp = px.bar(agg_exp, x=color_e, y=eje_y, color=eje_y,
                         color_continuous_scale='Viridis')

    fig_exp.update_layout(**PLOTLY_LAYOUT, height=460)
    st.plotly_chart(fig_exp, use_container_width=True)

    with st.expander("🔎 Ver datos filtrados"):
        st.dataframe(df_filtered, use_container_width=True, height=300)
        csv_all = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar datos filtrados (CSV)", csv_all,
                           f"datos_filtrados_{año_sel}.csv", "text/csv")
