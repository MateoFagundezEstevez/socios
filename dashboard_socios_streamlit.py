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

# Título
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

# Explicación de tipos de socios
st.markdown("""
**Tipos de Socios**:
- **TS01**: Socios Activos (Empresas socias directas con todos los beneficios).
- **TS02**: Socios Adherentes (Participan parcialmente de servicios).
- **TS03**: Socios Institucionales (Vinculación con instituciones o entes públicos).
""")

# Fidelización
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad' in filtro.columns:
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
st.header("Cantidad de socios y rubros según filtros seleccionados")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# Inteligencia Comercial
st.header("Inteligencia Comercial")
if 'Fecha Creación Empresa' in df.columns and df['Fecha Creación Empresa'].dropna().empty and 'Fecha de Creación' in df.columns:
    creados_por_ano = pd.to_datetime(df['Fecha de Creación'], errors='coerce').dt.year.value_counts().sort_index()
else:
    creados_por_ano = pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce').dt.year.value_counts().sort_index()

if not creados_por_ano.empty:
    st.subheader("Altas por Año")
    st.bar_chart(creados_por_ano)

    for año in creados_por_ano.index:
        if año == datetime.today().year:
            st.markdown(f"**Recomendación de Servicios ({año})**:")
            st.markdown("- Campaña de bienvenida y orientación para nuevos socios.")
            st.markdown("- Sesiones de integración para acelerar su participación.")
        elif año < datetime.today().year - 1:
            st.markdown(f"**Recomendación de Servicios ({año})**:")
            st.markdown("- Actividades de networking para reactivar el interés.")
            st.markdown("- Evaluar satisfacción con los servicios actuales.")

# Resumen por rubro y tipo
st.subheader("Totales del mapeo de socios")
resumen = df.groupby(["Rubro", "Tipo de socio"]).size().reset_index(name="Cantidad")
st.dataframe(resumen.sort_values("Cantidad", ascending=False))
