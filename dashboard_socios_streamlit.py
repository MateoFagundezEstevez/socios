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
        df['Año Alta'] = df['Fecha Creación Empresa'].dt.year


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

# Cargar datos
df = cargar_datos()

# Filtros en la barra lateral
st.sidebar.header("Filtros")

estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])

with st.sidebar.expander("Ver información sobre Estados de los Socios"):
    st.markdown("""
    **Estados de los Socios**:
    - **VIG**: Socio activo y vigente.
    - **SOLIC-BAJA**: En proceso de baja o ya inactivo.
    - **PROSP**: Prospecto, aún no es socio formal.
    - **HON**: Socio honorario.
    - **LIC**: Socio con licencia temporal (por ejemplo, suspendido).
    - **CAMRUT**: Socio con cambio de RUT (posible reingreso o reorganización).
    - **EMSUS**: Enviada solicitud de suspensión.
    - **CANJ**: Socio en canje de servicios.
    """)

rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo de socio"].dropna().unique())

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

# Título y bienvenida
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

# Conteo de socios activos
socios_activos = filtro[filtro["Estado"] == "VIG"].shape[0]
st.markdown(f"🎉 ¡Tenemos **{socios_activos}** socios activos! 🎉")

# Explicación tipos de socios
st.markdown("""
**Tipos de Socios**:
- **TS01**: Socios Activos
- **TS02**: Socios Adherentes
- **TS03**: Socios Institucionales
- **TS04**: Otro tipo de socio o categoría especial
""")

# Fidelización
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo de socio", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad Categoria' in filtro.columns:
    st.plotly_chart(px.histogram(filtro, x="Antiguedad Categoria", height=400))

# Detalle de socios filtrados
st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_mostrar = [col for col in filtro.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

# Reactivación de inactivos
mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")
if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Altas por año
mostrar_altas = st.sidebar.checkbox("Mostrar altas por año")
if mostrar_altas:
    st.header("Altas por Año (2023–2026)")

    # Asegurarse de que la columna está en formato datetime
    df['Fecha Creación Empresa'] = pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce')

    # Extraer el año
    df['Año Alta'] = df['Fecha Creación Empresa'].dt.year

    # Filtrar años relevantes
    años_objetivo = [2023, 2024, 2025, 2026]
    altas_filtradas = df[df['Año Alta'].isin(años_objetivo)]

    # Contar por año
    conteo_altas = altas_filtradas['Año Alta'].value_counts().sort_index()

    if not conteo_altas.empty:
        st.bar_chart(conteo_altas)
    else:
        st.info("No hay altas registradas para los años seleccionados.")

# Totales
st.header("Cantidad de socios y rubros según filtros seleccionados")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# Clústeres
cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()
cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]
st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Rubro y Región/Localidad"))
