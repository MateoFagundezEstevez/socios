import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Cuentas (1).csv")
    df.columns = df.columns.str.strip().str.replace('"', '')
    df['Fecha Creación Empresa'] = pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce')
    df['Año Alta'] = df['Fecha Creación Empresa'].dt.year
    return df

df = cargar_datos()

# Filtros en la barra lateral
st.sidebar.header("Filtros")

# Filtro de estado
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])

# Expansor para los estados de los socios
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
    - **CANJ**: Socio en canje de servicios (trueque o acuerdo no monetario).
    """)

# Filtro de rubros
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())

# Filtro de tipo de socio
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

# Conteo de socios activos (divertido)
socios_activos = filtro[filtro["Estado"] == "VIG"].shape[0]
st.markdown(f"🎉 ¡Tenemos **{socios_activos}** socios activos! 🎉")
st.markdown("Estos socios representan el motor de nuestra comunidad, ¡y estamos aquí para ayudarlos a crecer y prosperar!")

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
if 'Antiguedad Categoria' in filtro.columns:
    st.plotly_chart(px.histogram(filtro, x="Antiguedad Categoria", height=400))

# Detalle de socios filtrados
st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_mostrar = [col for col in filtro.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

# Mostrar análisis de inactivos solo si el usuario lo solicita
mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")

if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo de socio", title="Rubros más afectados"))

# Totales
st.header("Cantidad de socios y rubros según filtros seleccionados")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# **Clúster Fijo (Sin desplegar)**
st.header("Clústeres Potenciales")
cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()
cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")
cluster_df = cluster_df[cluster_df["Cantidad"] > 1]

# Gráfico de Treemap fijo para visualizar los clústeres potenciales
st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Rubro y Región/Localidad"))

# **Altas por Año (Desplegables)**
st.header("Altas por Año")
años_disponibles = df['Año Alta'].dropna().unique()
años_disponibles = sorted(años_disponibles)

# Filtro de Año
años_seleccionados = st.sidebar.multiselect("Seleccionar Año(s)", años_disponibles, default=años_disponibles)

# Contar las altas por año
conteo_altas = df['Año Alta'].value_counts().sort_index()

# Mostrar gráfico de barras con las altas por año
if años_seleccionados:
    st.subheader("Altas por Año Seleccionado(s)")
    st.bar_chart(conteo_altas[años_seleccionados])
else:
    st.subheader("Altas por Año")
    st.bar_chart(conteo_altas)

# Mostrar empresas creadas por año seleccionado
if años_seleccionados:
    st.header(f"Empresas creadas en {', '.join(map(str, años_seleccionados))}")
    empresas_por_año = df[df['Año Alta'].isin(años_seleccionados)]
    empresas_mostradas = empresas_por_año[['Nombre Empresa', 'Fecha Creación Empresa', 'Rubro', 'Estado', 'Tipo de socio']]

    # Mostrar tabla de empresas
    st.write(empresas_mostradas)
else:
    st.write("Seleccione un año para ver las empresas creadas en ese año.")
