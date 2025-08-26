import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------
# Cargar datos
# ---------------------------
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
    if 'Fecha Creación Empresa' in df.columns:
        df['Antiguedad en Meses'] = (datetime.today().year - df['Fecha Creación Empresa'].dt.year) * 12 + (datetime.today().month - df['Fecha Creación Empresa'].dt.month)
    elif 'Fecha de Creación' in df.columns:
        df['Antiguedad en Meses'] = (datetime.today().year - df['Fecha de Creación'].dt.year) * 12 + (datetime.today().month - df['Fecha de Creación'].dt.month)
    else:
        df['Antiguedad en Meses'] = None
    
    # Antigüedad detallada (años y meses)
    if df['Antiguedad en Meses'].notna().any():
        df['Antiguedad Detallada'] = (df['Antiguedad en Meses'] // 12).astype(str) + ' años y ' + (df['Antiguedad en Meses'] % 12).astype(str) + ' meses'
    else:
        df['Antiguedad Detallada'] = None

    # Clasificación de la antigüedad en categorías
    bins = [0, 1, 5, float('inf')]
    labels = ['Nuevo', 'Medio', 'Veterano']
    df['Antiguedad Categoria'] = pd.cut(df['Antiguedad'], bins=bins, labels=labels, right=False)

    return df

df = cargar_datos()

# ---------------------------
# Filtros en la barra lateral
# ---------------------------
st.sidebar.header("Filtros")

estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
with st.sidebar.expander("Ver información sobre Estados de los Socios"):
    st.markdown("""
    **Estados de los Socios**:
    - **VIG**: Socio activo y vigente.
    - **SOLIC-BAJA**: En proceso de baja o ya inactivo.
    - **BAJ**: Baja. El socio ha completado el proceso de baja y ya no está asociado.
    - **HON**: Socio honorario. El socio disfruta de algunos beneficios sin ser un socio activo con todas las obligaciones.
    - **LIC**: Socio licenciado. El socio tiene licencia temporal para no participar activamente.
    - **CAMRUT**: Socio en cambio de rut. El socio está realizando cambios administrativos en su registro.
    - **EMSUS**: Socio en suspensión. El socio está suspendido temporalmente.
    - **CANJ**: Socio en canje de servicios. Participa en un intercambio de servicios, sin transacciones monetarias.
    """)

rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo"].dropna().unique())
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
    filtro = filtro[filtro["Tipo"].isin(tipos)]
if regiones:
    filtro = filtro[filtro["Región / Localidad"].isin(regiones)]

# ---------------------------
# Título principal
# ---------------------------
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

# ---------------------------
# Socios activos
# ---------------------------
socios_activos = filtro[filtro["Estado"] == "VIG"].shape[0]
st.markdown(f"🎉 ¡Tenemos **{socios_activos}** socios activos! 🎉")
st.markdown("Estos socios representan el motor de nuestra comunidad, ¡y estamos aquí para ayudarlos a crecer y prosperar!")

# ---------------------------
# Socios recientes (últimos 6 meses)
# ---------------------------
st.header("🚀 Socios Recientes (últimos 6 meses)")
hoy = pd.Timestamp.today()
seis_meses_atras = hoy - pd.DateOffset(months=6)

if 'Fecha Creación Empresa' in filtro.columns:
    recientes = filtro[filtro['Fecha Creación Empresa'] >= seis_meses_atras]
elif 'Fecha de Creación' in filtro.columns:
    recientes = filtro[filtro['Fecha de Creación'] >= seis_meses_atras]
else:
    recientes = pd.DataFrame()

if not recientes.empty:
    st.markdown(f"En los últimos 6 meses se incorporaron **{recientes.shape[0]}** nuevos socios.")
    columnas_mostrar = [col for col in recientes.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(recientes[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No se registran nuevos socios en los últimos 6 meses según los filtros aplicados.")

# ---------------------------
# Fidelización
# ---------------------------
st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro, x="Rubro", color="Tipo", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad Categoria' in filtro.columns:
    st.plotly_chart(px.histogram(filtro, x="Antiguedad Categoria", height=400))

# ---------------------------
# Detalle de socios filtrados
# ---------------------------
st.subheader("Detalle de Socios Filtrados")
if not filtro.empty:
    columnas_mostrar = [col for col in filtro.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

# ---------------------------
# Socios inactivos (opcional)
# ---------------------------
mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")
if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo", title="Rubros más afectados"))

# ---------------------------
# Totales por rubro
# ---------------------------
st.header("Cantidad de socios y rubros según filtros seleccionados")
rubro_counts = filtro["Rubro"].value_counts().reset_index()
rubro_counts.columns = ["Rubro", "Cantidad"]
st.dataframe(rubro_counts.head(10))

# ---------------------------
# Clústeres por Rubro y Región/Localidad
# ---------------------------
if 'Rubro' in df.columns and 'Región / Localidad' in df.columns:
    cluster_df = df[~df["Rubro"].isna() & ~df["Región / Localidad"].isna()].copy()
    cluster_df = cluster_df.groupby(["Rubro", "Región / Localidad"]).size().reset_index(name="Cantidad")
    cluster_df = cluster_df[cluster_df["Cantidad"] > 1]
    st.plotly_chart(px.treemap(cluster_df, path=['Rubro', 'Región / Localidad'], values='Cantidad', title="Clústeres Potenciales por Rubro y Región/Localidad"))
