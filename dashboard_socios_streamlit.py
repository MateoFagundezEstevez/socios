import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Cuentas (1).csv")
    df.columns = df.columns.str.strip().str.replace('"', '')

    # Procesar fechas y calcular antigüedad
    if 'Fecha Creación Empresa' in df.columns:
        df['Fecha Creación Empresa'] = pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce')
        df['Antiguedad'] = datetime.today().year - df['Fecha Creación Empresa'].dt.year
    else:
        df['Fecha Creación Empresa'] = pd.NaT
        df['Antiguedad'] = None

    # Calcular antigüedad en meses
    df['Antiguedad en Meses'] = (
        (datetime.today().year - df['Fecha Creación Empresa'].dt.year) * 12 +
        (datetime.today().month - df['Fecha Creación Empresa'].dt.month)
    )

    # Antigüedad detallada (años y meses)
    df['Antiguedad Detallada'] = (
        (df['Antiguedad en Meses'] // 12).astype(str) + ' años y ' +
        (df['Antiguedad en Meses'] % 12).astype(str) + ' meses'
    )

    # Clasificación de la antigüedad en categorías
    bins = [0, 1, 5, float('inf')]
    labels = ['Nuevo', 'Medio', 'Veterano']
    df['Antiguedad Categoria'] = pd.cut(df['Antiguedad'], bins=bins, labels=labels, right=False)

    return df

df = cargar_datos()

# =========================
# Filtros en la barra lateral
# =========================
st.sidebar.header("Filtros")

filtro = df.copy()

# --- Filtro de Estado ---
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])

with st.sidebar.expander("Ver información sobre Estados de los Socios"):
    st.markdown("""
    **Estados de los Socios**:
    - **VIG**: Socio activo y vigente.
    - **SOLIC-BAJA**: En proceso de baja o ya inactivo.
    - **BAJ**: Baja definitiva.
    - **HON**: Socio honorario.
    - **LIC**: Socio licenciado temporalmente.
    - **CAMRUT**: Socio en cambio de RUT.
    - **EMSUS**: Socio suspendido temporalmente.
    - **CANJ**: Socio en canje de servicios.
    """)

# --- Filtro de Rubro ---
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())

# --- Filtro de Tipo ---
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo"].dropna().unique())

# --- Filtro por Región / Localidad ---
if 'Región / Localidad' in df.columns:
    regiones = st.sidebar.multiselect("Región / Localidad", df["Región / Localidad"].dropna().unique())
else:
    regiones = []

# --- Filtro por Fecha de Creación ---
if 'Fecha Creación Empresa' in df.columns:
    fechas_validas = df['Fecha Creación Empresa'].dropna()
    if not fechas_validas.empty:
        min_fecha = fechas_validas.min().date()
        max_fecha = fechas_validas.max().date()
    else:
        # Si no hay fechas válidas, usar hoy como rango
        min_fecha = max_fecha = datetime.today().date()

    rango_fechas = st.sidebar.date_input(
        "Fecha de Creación (rango)",
        value=(min_fecha, max_fecha),
        min_value=min_fecha,
        max_value=max_fecha
    )

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        inicio, fin = rango_fechas
        filtro = filtro[
            (filtro['Fecha Creación Empresa'] >= pd.to_datetime(inicio)) &
            (filtro['Fecha Creación Empresa'] <= pd.to_datetime(fin))
        ]

# --- Aplicar filtros adicionales ---
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if tipos:
    filtro = filtro[filtro["Tipo"].isin(tipos)]
if regiones:
    filtro = filtro[filtro["Región / Localidad"].isin(regiones)]

# --- Checkbox para prospectos ---
prospecto_filter = st.sidebar.checkbox("Ver Prospectos", value=False)
if prospecto_filter:
    filtro = filtro[filtro["Tipo"].str.contains("Prospecto", case=False, na=False)]

# =========================
# Visualización principal
# =========================
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

socios_activos = filtro[filtro["Estado"] == "VIG"].shape[0]
st.markdown(f"🎉 ¡Tenemos **{socios_activos}** socios activos! 🎉")

st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad Categoria' in filtro.columns:
    st.plotly_chart(px.histogram(filtro, x="Antiguedad Categoria", height=400))

st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_mostrar = [col for col in filtro.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")
if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo", title="Rubros más afectados"))

st.header("Cantidad de socios y rubros según filtros seleccionados")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()
cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]

st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Rubro y Región/Localidad"))
