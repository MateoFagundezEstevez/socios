# Dashboard interactivo en Streamlit para analizar socios
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Cuentas (1).csv")
    df.columns = df.columns.str.strip().str.replace('"', '')
    fecha_col = next((col for col in df.columns if "creacion" in col.lower()), None)
    if fecha_col:
        df["Antiguedad"] = datetime.today().year - pd.to_datetime(df[fecha_col], errors='coerce').dt.year
    else:
        df["Antiguedad"] = None
    return df

df = cargar_datos()

# Filtros
st.sidebar.header("Filtros")
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

filtro = df.copy()
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if tipos:
    filtro = filtro[filtro["Tipo de socio"].isin(tipos)]

st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

# Fidelizacion
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
st.plotly_chart(px.histogram(filtro, x="Antiguedad", nbins=20))

# Detalle de socios filtrados
st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_mostrar = [col for col in filtro.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

# Reactivacion
st.header("Reactivación de Socios Inactivos")
inactivos = df[df["Estado"] == "SOLIC-BAJA"]
st.write(f"Total de socios inactivos: {len(inactivos)}")
st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Difusion
st.header("Difusión de Servicios y Beneficios")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# Inteligencia Institucional
st.header("Inteligencia Institucional")
creados_por_ano = df['Fecha de Creacion'].dropna()
if not creados_por_ano.empty:
    creados_por_ano = pd.to_datetime(creados_por_ano, errors='coerce').dt.year.value_counts().sort_index()
    st.subheader("Altas por Año")
    st.bar_chart(creados_por_ano)

st.subheader("Resumen por Rubro y Tipo")
resumen = df.groupby(["Rubro", "Tipo de socio"]).size().reset_index(name="Cantidad")
st.dataframe(resumen.sort_values("Cantidad", ascending=False))

# Identificación de Oportunidades de Cooperación
st.header("Oportunidades de Cooperación Institucional")
st.subheader("Clústeres por Rubro")
cluster_df = df[~df["Rubro"].isna()].copy()
cluster_df = cluster_df.groupby("Rubro").size().reset_index(name="Cantidad")
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]
st.plotly_chart(px.treemap(cluster_df, path=['Rubro'], values='Cantidad', title="Clústeres Potenciales"))

st.subheader("Detalle por Rubro Seleccionado")
if rubros:
    cluster_detalle = df[df["Rubro"].isin(rubros)]
    columnas_detalle = [col for col in cluster_detalle.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(cluster_detalle[columnas_detalle].drop_duplicates().reset_index(drop=True))
