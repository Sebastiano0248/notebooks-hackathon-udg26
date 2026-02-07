from tool_scripts.geographic_tools import lat_to_neighbourhood


def test_lat_to_neighbourhood():
    # Coordenadas de ejemplo (puedes cambiar estas por coordenadas reales de Girona)
    lat = 41.96831834614794
    lon = 2.81618835212095

    print("Testing lat_to_neighbourhood with coordinates:")
    print(f"Latitude: {lat}, Longitude: {lon}")

    lat_to_neighbourhood(lat, lon)


if __name__ == "__main__":
    test_lat_to_neighbourhood()
