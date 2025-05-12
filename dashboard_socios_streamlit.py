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
departamentos = st.sidebar.multiselect("Departamento", df["Departamento (Envío)"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

filtro = df.copy()
if estados:
    filtro = filtro[filtro["Estado"].isin(estados)]
if rubros:
    filtro = filtro[filtro["Rubro"].isin(rubros)]
if departamentos:
    filtro = filtro[filtro["Departamento (Envío)"].isin(departamentos)]
if tipos:
    filtro = filtro[filtro["Tipo de socio"].isin(tipos)]

st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias comerciales.")

# Fidelizacion
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Distribución Geográfica")
st.plotly_chart(px.histogram(filtro, x="Departamento (Envío)", color="Tipo de socio", barmode="group"))

st.subheader("Antigüedad de los Socios")
st.plotly_chart(px.histogram(filtro, x="Antiguedad", nbins=20))

# Detalle de socios filtrados
st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_contacto = [col for col in filtro.columns if any(key in col.lower() for key in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    columnas_mostrar = list(dict.fromkeys([col for col in filtro.columns if "nombre" in col.lower() or "rubro" in col.lower() or "contacto" in col.lower() or "mail" in col.lower() or "email" in col.lower() or "tel" in col.lower()]))
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

# Mapeo institucional y oportunidades
st.header("Mapeo de Socios y Cooperación Institucional")
st.subheader("Mapa de Distribución por Departamento")
mapa_data = df["Departamento (Envío)"].value_counts().reset_index()
mapa_data.columns = ["Departamento", "Cantidad"]
st.plotly_chart(px.choropleth(mapa_data, locationmode="country names", locations="Departamento", color="Cantidad", title="Distribución de socios por departamento (simulado)", color_continuous_scale="Blues"))

st.subheader("Identificación de Oportunidades de Cooperación")
coop_df = df.groupby(["Departamento (Envío)", "Rubro"]).size().reset_index(name="Cantidad")
st.plotly_chart(px.treemap(coop_df, path=['Departamento (Envío)', 'Rubro'], values='Cantidad', title="Mapa de potenciales clústers y cooperaciones"))

# Inteligencia Institucional
st.header("Inteligencia Institucional")
creados_por_ano = df['Fecha de Creacion'].dropna()
if not creados_por_ano.empty:
    creados_por_ano = pd.to_datetime(creados_por_ano, errors='coerce').dt.year.value_counts().sort_index()
    st.subheader("Altas por Año")
    st.bar_chart(creados_por_ano)

st.subheader("Resumen por Departamento")
depa_data = df["Departamento (Envío)"].value_counts().reset_index()
depa_data.columns = ["Departamento", "Cantidad"]
st.dataframe(depa_data)

# Recomendaciones
st.header("Recomendaciones Estratégicas")
st.markdown("""
- **Fidelización**: Crear beneficios segmentados por rubro, como capacitaciones o convenios exclusivos.
- **Reactivación**: Contactar sectores con altas bajas como prioridad, usando encuestas para entender causas.
- **Difusión**: Email marketing personalizado según antigüedad y tipo de socio.
- **Cooperación**: Identificar regiones y rubros con alta concentración para alianzas estratégicas regionales.
- **Captación**: Fortalecer presencia institucional en zonas con baja concentración de socios.
""")

