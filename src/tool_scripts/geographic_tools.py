from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MarkerCluster
from shapely.geometry import Point

from constants import ADD_RAW_OG_DATA, CENS_TRACT_COL, LAT_COL, LON_COL, OUTPUT_DATA

# Ruta al ZIP que contiene tu Shapefile
zip_path = Path(f"{ADD_RAW_OG_DATA}/INE_SECCIONS_2025-SECC_CE_20250101.zip")

# geopandas puede leer directamente desde un zip usando esta sintaxis:
CENSUS_GDF = gpd.read_file(f"zip://{zip_path}!SECC_CE_20250101.shp")


def add_cusec_column(
    df: pd.DataFrame, lat_col: str = LAT_COL, lon_col: str = LON_COL
) -> pd.DataFrame:
    """
    Dado un DataFrame con columnas de latitud y longitud, devuelve el mismo DataFrame
    con la columna CUSEC asignada según la geometría del shapefile.

    Args:
        df (pd.DataFrame): Dataset original con columnas de lat y lon.
        lat_col (str): Nombre de la columna de latitud.
        lon_col (str): Nombre de la columna de longitud.
        shapefile_path (str): Ruta al shapefile de secciones censales.

    Returns:
        pd.DataFrame: DataFrame original con columna 'CUSEC' añadida.
    """

    # Crear geometría de puntos
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col], strict=False)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # WGS84

    # Asegurar que ambos GeoDataFrames estén en la misma proyección
    if CENSUS_GDF.crs is not None:
        gdf = gdf.to_crs(CENSUS_GDF.crs)

    # Hacer spatial join para asignar CUSEC
    merged = gpd.sjoin(
        gdf, CENSUS_GDF[["CUSEC", "geometry"]], how="left", predicate="within"
    )

    merged.rename(columns={"CUSEC": CENS_TRACT_COL}, inplace=True)

    # Devolver DataFrame con la columna CUSEC
    return pd.DataFrame(merged.drop(columns=["geometry", "index_right"]))


def crear_mapa(
    df,
    lat_col: str = LAT_COL,
    lon_col: str = LON_COL,
    output_dir=OUTPUT_DATA,
    name_html: str = "map.html",
):
    """
    Crea un mapa interactivo con Folium, agrega secciones censales (opcional) y guarda HTML.

    Parámetros:
    - df: pd.DataFrame con datos de puntos
    - lat_col: str, nombre de la columna de latitud
    - lon_col: str, nombre de la columna de longitud
    - output_dir: str, carpeta donde guardar los archivos
    - name_html: str, nombre del archivo HTML de salida
    """

    # Centro del mapa basado en la media de lat y lon
    map_center = [df[lat_col].mean(), df[lon_col].mean()]
    m = folium.Map(location=map_center, zoom_start=13)

    # Agregar secciones censales si se proporciona
    if CENSUS_GDF is not None:
        folium.GeoJson(
            CENSUS_GDF.to_crs("EPSG:4326"),
            name="Secciones Censales",
            style_function=lambda _: {
                "fillColor": "#ffff00",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.1,
            },
        ).add_to(m)

    # Agregar cluster de marcadores
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_text = "<br>".join([f"{col}: {row[col]}" for col in df.columns])
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.7,
            popup=popup_text,
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    m.save(f"{output_dir}/{name_html}")
