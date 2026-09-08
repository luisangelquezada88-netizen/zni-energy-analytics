"""Tablero de control: generación eléctrica de las ZNI (tesis Quezada, 2024)."""
from pathlib import Path

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from branca.colormap import LinearColormap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from streamlit_folium import st_folium

DATA = Path(__file__).resolve().parents[1] / "data"

st.set_page_config(page_title="ZNI: tablero de control", layout="wide")
st.title("Generación eléctrica de las Zonas No Interconectadas con telemetría")


@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATA / "processed" / "servicio_electrico_limpio.csv")
    mapa = gpd.read_file(DATA / "geodata" / "MGN2024_DPTO_POLITICO" / "MGN_ADM_DPTO_POLITICO.shp")
    mapa = mapa.to_crs(3857)
    mapa["geometry"] = mapa.simplify(500)
    return df, mapa.to_crs(4326)


@st.cache_data
def clustering(df):
    mpio = df.groupby("municipio", observed=False).agg(
        energia_media=("energia_activa", "mean"),
        potencia_media=("potencia_maxima", "mean"),
        horas_media=("promedio_horas", "mean")).dropna()
    mpio = mpio[(mpio["energia_media"] > 0) & (mpio["horas_media"] > 0)]
    mpio = mpio[~mpio.index.isin(["san andrés", "san andres"])]
    base = mpio.copy()
    base[["energia_media", "potencia_media"]] = np.log10(base[["energia_media", "potencia_media"]])
    mpio["cluster"] = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(
        StandardScaler().fit_transform(base))
    orden = mpio.groupby("cluster")["horas_media"].mean().sort_values().index.tolist()
    mpio["riesgo"] = mpio["cluster"].map({orden[0]: "Crítico", orden[1]: "Medio", orden[2]: "Estable"})
    return mpio


@st.cache_data
def ranking_anual(_df, anio):
    ranking = _df[(_df["anio_servicio"] == anio) & (_df["promedio_horas"] > 0)]
    ranking = ranking.groupby("id_departamento")["promedio_horas"].mean().reset_index()
    ranking["id_departamento"] = ranking["id_departamento"].astype(str).str.zfill(2)
    return ranking


df, mapa = cargar_datos()
df_mpio = clustering(df)
depto_mpio = df.drop_duplicates("municipio").set_index("municipio")["departamento"]

# Filtros
st.sidebar.header("Filtros")
if "_click_depto" in st.session_state:
    st.session_state.deptos = st.session_state.pop("_click_depto")
anio = st.sidebar.selectbox("Año", sorted(df["anio_servicio"].unique()), index=len(df["anio_servicio"].unique()) - 1)
deptos = st.sidebar.multiselect("Departamentos", sorted(df["departamento"].unique()),
                                default=sorted(df["departamento"].unique()), key="deptos")
riesgos = st.sidebar.multiselect("Grupos de riesgo", ["Crítico", "Medio", "Estable"],
                                  default=["Crítico", "Medio", "Estable"])

sel = df[(df["anio_servicio"] == anio) & (df["departamento"].isin(deptos))]

# Fila 1: KPIs
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Horas promedio/día", f"{sel['promedio_horas'].mean():.1f}")
c2.metric("Localidades", f"{sel['localidad'].nunique():,}")
c3.metric("Municipios", f"{sel['municipio'].nunique():,}")
c4.metric("Departamentos", f"{sel['departamento'].nunique()}")
c5.metric("Diésel en matriz", "78,2 %")

# Fila 2: mapa + scatter
col_mapa, col_scatter = st.columns([3, 2])
with col_mapa:
    st.subheader(f"Mapa del servicio ({anio})")
    ranking = ranking_anual(df, anio)
    mapa_f = mapa[mapa["dpto_ccdgo"] != "88"].merge(ranking, left_on="dpto_ccdgo",
                                                   right_on="id_departamento", how="left")
    mapa_f["horas_label"] = mapa_f["promedio_horas"].map(
        lambda h: f"{h:.1f}" if pd.notna(h) else "Sin datos")
    m = folium.Map(location=[4.5, -73.5], zoom_start=5, tiles=None)
    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                     attr="Esri World Imagery", name="Satélite").add_to(m)
    escala = LinearColormap(colors=["red", "yellow", "green"],
                            vmin=mapa_f["promedio_horas"].min(),
                            vmax=mapa_f["promedio_horas"].max(), caption="Horas/día")

    def estilo(feature):
        h = feature["properties"].get("promedio_horas")
        if h is None or pd.isna(h):
            return {"fillColor": "#e0e0e0", "color": "white", "weight": 1, "fillOpacity": 0.6}
        return {"fillColor": escala(h), "color": "white", "weight": 1, "fillOpacity": 0.75}

    folium.GeoJson(mapa_f.__geo_interface__, style_function=estilo,
                   tooltip=folium.GeoJsonTooltip(fields=["dpto_cnmbr", "horas_label"],
                                                 aliases=["Departamento:", "Horas/día:"])).add_to(m)
    escala.add_to(m)
    click = st_folium(m, height=550, use_container_width=True, key="mapa")
    tocado = (click or {}).get("last_object_clicked")
    if tocado:
        marca = (round(tocado["lat"], 4), round(tocado["lng"], 4))
        if st.session_state.get("_click") != marca:
            st.session_state["_click"] = marca
            punto = gpd.GeoDataFrame(geometry=gpd.points_from_xy([tocado["lng"]], [tocado["lat"]]), crs=4326)
            hit = gpd.sjoin(punto, mapa_f[["dpto_ccdgo", "geometry"]], how="left", predicate="within")
            cod = hit["dpto_ccdgo"].iloc[0] if len(hit) and pd.notna(hit["dpto_ccdgo"].iloc[0]) else None
            if cod:
                nom = df.loc[df["id_departamento"].astype(str).str.zfill(2) == cod, "departamento"].iloc[0]
                st.session_state["_click_depto"] = sorted(df["departamento"].unique()) if st.session_state.deptos == [nom] else [nom]
                st.rerun()

with col_scatter:
    st.subheader("Perfiles de riesgo eléctrico (K-means clustering)")
    puntos = df_mpio[df_mpio["riesgo"].isin(riesgos) & df_mpio.index.map(depto_mpio).isin(deptos)].reset_index()
    fig_s = px.scatter(puntos, x="energia_media", y="horas_media", color="riesgo",
                       symbol="riesgo", hover_name="municipio", log_x=True,
                       color_discrete_map={"Crítico": "#d62728", "Medio": "#ff7f0e",
                                           "Estable": "#2ca02c"},
                       category_orders={"riesgo": ["Crítico", "Medio", "Estable"]},
                       labels={"energia_media": "Energía media (log)", "horas_media": "Horas medias"},
                       title="Grupos de municipios por energía y horas")
    st.plotly_chart(fig_s, use_container_width=True)

# Fila 3: línea de tiempo + treemap
col_linea, col_tree = st.columns(2)
with col_linea:
    st.subheader("Horas promedio por año")
    serie = df[df["departamento"].isin(deptos)].groupby("anio_servicio")["promedio_horas"].mean().reset_index()
    fig_l = px.line(serie, x="anio_servicio", y="promedio_horas", markers=True,
                    labels={"anio_servicio": "Año", "promedio_horas": "Horas promedio/día"})
    y0, y1 = serie["promedio_horas"].min(), serie["promedio_horas"].max()
    fig_l.update_yaxes(range=[y0 - 1, y1 + 1])
    st.plotly_chart(fig_l, use_container_width=True)

with col_tree:
    st.subheader("Matriz eléctrica (kW)")
    matriz = pd.DataFrame({
        "grupo": ["Diésel", "FNCER", "FNCER", "FNCER", "FNCER", "FNCER"],
        "tecnologia": ["Diésel", "Solar individual", "Solar concentrado",
                       "Pequeñas hidro", "Biomasa", "Residuos sólidos"],
        "kw": [262056, 54701, 8381, 4613, 4520, 1000]})
    fig_t = px.treemap(matriz, path=["grupo", "tecnologia"], values="kw")
    fig_t.update_traces(texttemplate="%{label}<br>%{percentRoot:.1%}")
    st.plotly_chart(fig_t, use_container_width=True)

# Fila 4: municipios + descarga
st.subheader("Municipios")
tabla = df_mpio[df_mpio["riesgo"].isin(riesgos)].copy()
tabla = tabla[tabla.index.map(depto_mpio).isin(deptos)]
tabla.insert(0, "departamento", tabla.index.map(depto_mpio))
st.dataframe(tabla.drop(columns="cluster").sort_values("horas_media").round(2), use_container_width=True)
st.download_button("Descargar datos filtrados (CSV)", sel.to_csv(index=False),
                   file_name="zni_filtrado.csv")

st.caption("Fuente: IPSE (2026). Estado de la prestación del servicio de energía en Zonas No  Interconectadas. Datos Abiertos Colombia. https://www.datos.gov.co/Minas-y-Energ-a/Estado-de-la-prestaci-n-del-servicio-de-energ-a-en/3ebi-d83g/about_data")
