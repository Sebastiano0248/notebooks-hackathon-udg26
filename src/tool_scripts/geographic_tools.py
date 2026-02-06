import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MarkerCluster
from shapely.geometry import Point

from constants import ADD_RAW_OG_DATA, CENS_TRACT_COL, LAT_COL, LON_COL, OUTPUT_DATA

# Cargar shapefile de secciones censales
CENSUS_GDF = gpd.read_file(f"{ADD_RAW_OG_DATA}/seccionado_2025/SECC_CE_20250101.shp")


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
            style_function=lambda x: {
                "fillColor": "#ffff00",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.1,
            },
        ).add_to(m)

    # Agregar cluster de marcadores
    m = folium.Map(location=[df.lat.mean(), df.lon.mean()], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.7,
            popup=f"Precio: {row.price}€<br>Área: {row.area}m²",
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    m.save(f"{output_dir}/{name_html}")
