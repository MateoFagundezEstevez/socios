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
    
    if df['Fecha Creación Empresa'].dropna().empty and 'Fecha de Creación' in df.columns:
        df['Fecha de Creación'] = pd.to_datetime(df['Fecha de Creación'], errors='coerce')
        df['Antiguedad'] = datetime.today().year - df['Fecha de Creación'].dt.year
    else:
        df['Antiguedad'] = datetime.today().year - df['Fecha Creación Empresa'].dt.year

    # Calcular antigüedad en meses
    df['Antiguedad en Meses'] = (datetime.today().year - df['Fecha Creación Empresa'].dt.year) * 12 + (datetime.today().month - df['Fecha Creación Empresa'].dt.month)
    
    # Antigüedad detallada (años y meses)
    df['Antiguedad Detallada'] = (df['Antiguedad en Meses'] // 12).astype(str) + ' años y ' + (df['Antiguedad en Meses'] % 12).astype(str) + ' meses'

    # Clasificación de la antigüedad en categorías
    bins = [0, 1, 5, float('inf')]
    labels = ['Nuevo', 'Medio', 'Veterano']
    df['Antiguedad Categoria'] = pd.cut(df['Antiguedad'], bins=bins, labels=labels, right=False)

    return df

df = cargar_datos()

# Filtros en la barra lateral
st.sidebar.header("Filtros")

estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

# Filtro por Región / Localidad
if 'Región / Localidad' in df.columns:
    regiones = st.sidebar.multiselect("Región / Localidad", df["Región / Localidad"].dropna().unique())
else:
    regiones = []

# Aplicar filtros
filtro = df.copy()
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if tipos:
    filtro = filtro[filtro["Tipo de socio"].isin(tipos)]
if regiones:
    filtro = filtro[filtro["Región / Localidad"].isin(regiones)]

# Depuración: Verificar columnas disponibles después de los filtros
st.write("Columnas disponibles en el DataFrame filtrado:")
st.write(filtro.columns)

# Detalle de empresas filtradas
st.header("Empresas Filtradas según los Filtros Aplicados")
if not filtro.empty:
    # Verificar si las columnas clave existen antes de intentar acceder
    columnas_requeridas = ['Nombre Empresa', 'Fecha Creación Empresa', 'Rubro', 'Estado', 'Tipo de socio']
    columnas_faltantes = [col for col in columnas_requeridas if col not in filtro.columns]
    
    if columnas_faltantes:
        st.write(f"Las siguientes columnas faltan: {columnas_faltantes}")
    else:
        empresas_mostradas = filtro[columnas_requeridas]
        st.write(empresas_mostradas)
else:
    st.write("No hay empresas que coincidan con los filtros seleccionados.")

# Fidelización
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad Categoria' in filtro.columns:
    st.plotly_chart(px.histogram(filtro, x="Antiguedad Categoria", height=400))

# Mostrar análisis de inactivos solo si el usuario lo solicita
mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")

if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Clústeres por Rubro y Región/Localidad
cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()

# Agrupamos por Rubro y Región/Localidad y contamos la cantidad de socios
cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")

# Filtramos los clústeres que tienen más de 1 socio
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]

# Gráfico de treemap para visualizar los clústeres potenciales
st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Rubro y Región/Localidad"))
