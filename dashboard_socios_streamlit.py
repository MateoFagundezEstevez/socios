import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Cuentas (1).csv")
    df.columns = df.columns.str.strip().str.replace('"', '')
    # Verificamos si la columna "Fecha Creación Empresa" existe y la procesamos
    if 'Fecha Creación Empresa' in df.columns:
        df["Antiguedad"] = datetime.today().year - pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce').dt.year
    else:
        df["Antiguedad"] = None
    return df

df = cargar_datos()

# Filtros
st.sidebar.header("Filtros")
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

# Filtro por Región / Localidad (nuevo filtro)
if 'Región / Localidad' in df.columns:
    regiones = st.sidebar.multiselect("Región / Localidad", df["Región / Localidad"].dropna().unique())
else:
    regiones = []

# Filtrado de datos
filtro = df.copy()
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if tipos:
    filtro = filtro[filtro["Tipo de socio"].isin(tipos)]
if regiones:
    filtro = filtro[filtro["Región / Localidad"].isin(regiones)]

# Título de la página
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

# Fidelización
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

# Reactivación de Socios Inactivos
st.header("Reactivación de Socios Inactivos")
inactivos = df[df["Estado"] == "SOLIC-BAJA"]
st.write(f"Total de socios inactivos: {len(inactivos)}")
st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Totales
st.header("Difusión de Servicios y Beneficios")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# Inteligencia Comercial
st.header("Inteligencia Comercial")

# Usar la columna 'Fecha Creación Empresa'
if 'Fecha Creación Empresa' in df.columns:
    creados_por_ano = df['Fecha Creación Empresa'].dropna()
    if not creados_por_ano.empty:
        creados_por_ano = pd.to_datetime(creados_por_ano, errors='coerce').dt.year.value_counts().sort_index()
        st.subheader("Altas por Año")
        st.bar_chart(creados_por_ano)

        # Recomendación de Servicios desde la Cámara basada en Altas por Año
        años_creacion = creados_por_ano.index
        for año in años_creacion:
            if año == datetime.today().year:
                st.markdown(f"**Recomendación de Servicios (Año {año})**: ")
                st.markdown("- Realizar una campaña de bienvenida y orientación para los socios más recientes.")
                st.markdown("- Ofrecer sesiones de integración a nuevos socios para acelerar su participación.")
            elif año < datetime.today().year - 1:
                st.markdown(f"**Recomendación de Servicios (Año {año})**: ")
                st.markdown("- Fomentar la participación en eventos de networking para reactivar el interés de socios más antiguos.")
                st.markdown("- Evaluar la satisfacción con los servicios prestados a socios que llevan más tiempo.")

# Resumen por Rubro y Tipo
st.subheader("Resumen por Rubro y Tipo")
resumen = df.groupby(["Rubro", "Tipo de socio"]).size().reset_index(name="Cantidad")
st.dataframe(resumen.sort_values("Cantidad", ascending=False))

# Identificación de Oportunidades de Cooperación Institucional
st.header("Oportunidades de Cooperación Institucional")
st.subheader("Clústeres por Rubro y Región / Localidad")

# Clústeres por rubro y región/localidad
cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()
cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]
st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Región / Localidad"))

st.subheader("Detalle por Rubro y Región / Localidad Seleccionado")
if rubros and regiones:
    cluster_detalle = df[df["Rubro"].isin(rubros) & df["Región / Localidad"].isin(regiones)]
    columnas_detalle = [col for col in cluster_detalle.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(cluster_detalle[columnas_detalle].drop_duplicates().reset_index(drop=True))
