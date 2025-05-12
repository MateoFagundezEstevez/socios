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
    df["Fecha de Creacion"] = pd.to_datetime(df["Fecha de Creacion"], errors='coerce')
    df["Antiguedad"] = datetime.today().year - df["Fecha de Creacion"].dt.year
    return df

df = cargar_datos()

# Filtros
st.sidebar.header("Filtros")
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
departamentos = st.sidebar.multiselect("Departamento", df["Departamento (Env\u00edo)"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

filtro = df.copy()
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if departamentos:
    filtro = filtro[filtro["Departamento (Env\u00edo)"].isin(departamentos)]
if tipos:
    filtro = filtro[filtro["Tipo de socio"].isin(tipos)]

st.title("An\u00e1lisis Integral de Socios - C\u00e1mara de Comercio")
st.markdown("Este dashboard permite visualizar informaci\u00f3n clave para decisiones sobre fidelizaci\u00f3n, reactivaci\u00f3n y estrategias comerciales.")

# Fidelizacion
st.header("Fidelizaci\u00f3n de Socios Activos")
st.subheader("Distribuci\u00f3n por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Distribuci\u00f3n Geogr\u00e1fica")
st.plotly_chart(px.histogram(filtro, x="Departamento (Env\u00edo)", color="Tipo de socio", barmode="group"))

st.subheader("Antig\u00fcedad de los Socios")
st.plotly_chart(px.histogram(filtro, x="Antiguedad", nbins=20))

# Reactivacion
st.header("Reactivaci\u00f3n de Socios Inactivos")
inactivos = df[df["Estado"] == "SOLIC-BAJA"]
st.write(f"Total de socios inactivos: {len(inactivos)}")
st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros m\u00e1s afectados"))

# Difusion
st.header("Difusi\u00f3n de Servicios y Beneficios")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# Comercializacion y Eventos
st.header("Comercializaci\u00f3n y Eventos")
st.markdown("Se sugiere priorizar eventos en departamentos con alta concentraci\u00f3n de socios, y adaptar los temas seg\u00fan el rubro.")
st.plotly_chart(px.sunburst(filtro, path=['Departamento (Env\u00edo)', 'Rubro'], values=None))

# Inteligencia Institucional
st.header("Inteligencia Institucional")
creados_por_ano = df['Fecha de Creacion'].dt.year.value_counts().sort_index()
st.subheader("Altas por A\u00f1o")
st.bar_chart(creados_por_ano)

st.subheader("Resumen por Departamento")
depa_data = df["Departamento (Env\u00edo)"].value_counts().reset_index()
depa_data.columns = ["Departamento", "Cantidad"]
st.dataframe(depa_data)

# Recomendaciones
st.header("Recomendaciones Estrat\u00e9gicas")
st.markdown("""
- **Fidelizaci\u00f3n**: Crear beneficios segmentados por rubro, como capacitaciones o convenios exclusivos.
- **Reactivaci\u00f3n**: Contactar sectores con altas bajas como prioridad, usando encuestas para entender causas.
- **Difusi\u00f3n**: Email marketing personalizado seg\u00fan antig\u00fcedad y tipo de socio.
- **Eventos**: Ofrecer eventos regionales en departamentos con alto volumen y por subgrupo de actividad.
- **Captaci\u00f3n**: Fortalecer presencia institucional en zonas con baja concentraci\u00f3n de socios.
""")
