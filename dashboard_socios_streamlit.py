import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# Cargar datos
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Cuentas (1).csv")
    df.columns = df.columns.str.strip().str.replace('"', '')

    # Procesar fechas y calcular antigüedad
    if 'Fecha Creación Empresa' in df.columns:
        df['Fecha Creación Empresa'] = pd.to_datetime(df['Fecha Creación Empresa'], errors='coerce')
        df['Antiguedad'] = datetime.today().year - df['Fecha Creación Empresa'].dt.year
    else:
        df['Fecha Creación Empresa'] = pd.NaT
        df['Antiguedad'] = None

    # Categorías de antigüedad
    bins = [0, 1, 5, float('inf')]
    labels = ['Nuevo', 'Medio', 'Veterano']
    df['Antiguedad Categoria'] = pd.cut(df['Antiguedad'], bins=bins, labels=labels, right=False)

    return df

df = cargar_datos()

# =========================
# Barra lateral: filtros
# =========================
st.sidebar.header("Filtros")

# --- Filtro de Estado ---
estados = st.sidebar.multiselect("Estado", df["Estado"].dropna().unique(), default=["VIG"])
filtro_estado = df[df["Estado"].isin(estados)] if estados else df.copy()

# --- Filtro de Rubro ---
rubros = st.sidebar.multiselect("Rubro", df["Rubro"].dropna().unique())
filtro_rubro = filtro_estado[filtro_estado["Rubro"].isin(rubros)] if rubros else filtro_estado.copy()

# --- Filtro de Tipo ---
tipos = st.sidebar.multiselect("Tipo de socio", df["Tipo"].dropna().unique())
filtro_tipo = filtro_rubro[filtro_rubro["Tipo"].isin(tipos)] if tipos else filtro_rubro.copy()

# --- Filtro por Región / Localidad ---
if 'Región / Localidad' in df.columns:
    regiones = st.sidebar.multiselect("Región / Localidad", df["Región / Localidad"].dropna().unique())
    filtro_final = filtro_tipo[filtro_tipo["Región / Localidad"].isin(regiones)] if regiones else filtro_tipo.copy()
else:
    filtro_final = filtro_tipo.copy()

# --- Checkbox: Ver socios nuevos desde mayo 2025 ---
ver_socios_nuevos = st.sidebar.checkbox("Ver socios nuevos (desde mayo 2025)")
if ver_socios_nuevos:
    fecha_corte = pd.to_datetime("2025-05-01")
    filtro_final = filtro_final[filtro_final["Fecha Creación Empresa"] >= fecha_corte]

# =========================
# Visualización principal
# =========================
st.title("Análisis Integral de Socios - Cámara de Comercio")
st.markdown("Este dashboard permite visualizar información clave para decisiones sobre fidelización, reactivación y estrategias institucionales.")

socios_activos = filtro_final[filtro_final["Estado"] == "VIG"].shape[0]
st.markdown(f"🎉 ¡Tenemos **{socios_activos}** socios activos! 🎉")

st.header("Fidelización de Socios Activos")
st.subheader("Distribución por Rubro")
st.plotly_chart(px.histogram(filtro_final, x="Rubro", color="Tipo", barmode="group", height=400))

st.subheader("Antigüedad de los Socios")
if 'Antiguedad Categoria' in filtro_final.columns:
    st.plotly_chart(px.histogram(filtro_final, x="Antiguedad Categoria", height=400))

st.subheader("Detalle de Socios Filtrados")
if not filtro_final.empty:
    columnas_mostrar = [col for col in filtro_final.columns if any(k in col.lower() for k in ["nombre", "rubro", "mail", "email", "tel", "contacto"])]
    st.dataframe(filtro_final[columnas_mostrar].drop_duplicates().reset_index(drop=True))
else:
    st.write("No hay socios que coincidan con los filtros seleccionados.")

# Mostrar análisis de socios inactivos
mostrar_inactivos = st.sidebar.checkbox("Mostrar análisis de socios inactivos")
if mostrar_inactivos:
    st.header("Reactivación de Socios Inactivos")
    inactivos = df[df["Estado"] == "SOLIC-BAJA"]
    st.write(f"Total de socios inactivos: {len(inactivos)}")
    st.plotly_chart(px.histogram(inactivos, x="Rubro", color="Tipo", title="Rubros más afectados"))

