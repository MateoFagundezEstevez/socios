import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from datetime import datetime

# Cargar datos
@st.cache_resource
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

# Reactivación
st.header("Reactivación de Socios Inactivos")
inactivos = df[df["Estado"] == "SOLIC-BAJA"]
st.write(f"Total de socios inactivos: {len(inactivos)}")
st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Difusión
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

# Mapa de Uruguay
st.header("Mapa de Distribución de Socios en Uruguay")
# Cargar mapa de Uruguay con geopandas
uruguay_map = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
uruguay_map = uruguay_map[uruguay_map.name == "Uruguay"]

# Mostrar el mapa
st.plotly_chart(px.choropleth_mapbox(df, geojson=uruguay_map.geometry, locations=df.index, color="Rubro", hover_name="Rubro",
                                      title="Distribución Geográfica de Socios en Uruguay", color_continuous_scale="Viridis",
                                      mapbox_style="carto-positron", center={"lat": -33.0, "lon": -56.0}, zoom=5))

# Identificación de Oportunidades de Cooperación
st.header("Oportunidades de Cooperación Institucional")
st.subheader("Clústeres por Rubro")

if rubros:
    # Filtrar por rubro seleccionado
    cluster_detalle = df[df["Rubro"].isin(rubros)]
    columnas_detalle = ["Nombre", "Rubro", "Mail", "Email", "Tel", "Contacto"]
    st.dataframe(cluster_detalle[columnas_detalle].drop_duplicates().reset_index(drop=True))

# Recomendaciones
st.header("Recomendaciones Estratégicas")
st.markdown(""" 
- **Fidelización**: Crear beneficios segmentados por rubro, como capacitaciones o convenios exclusivos.
- **Reactivación**: Contactar sectores con altas bajas como prioridad, usando encuestas para entender causas.
- **Difusión**: Email marketing personalizado según antigüedad y tipo de socio.
- **Cooperación**: Identificar rubros con alta concentración para alianzas estratégicas sectoriales.
- **Captación**: Fortalecer presencia institucional en sectores con baja concentración de socios.
""")
