import json

import numpy as np
import pandas as pd
import xgboost as xgb


def predict_rent_smart(area, rooms, census_tract):
    """
    Predicts rent using the High-Accuracy Model.
    Auto-fills Lat/Lon/Elevator based on the Census Tract.
    """
    # 1. Load Model & Stats
    model = xgb.Booster()
    model.load_model("../data/model_results/girona_rent_model_v3_hybrid.json")

    with open("../data/model_results/girona_rent_model_v3_hybrid_stats.json") as f:
        lookup = json.load(f)

    # 2. Look up missing info
    tract_key = str(census_tract)

    if tract_key in lookup:
        stats = lookup[tract_key]
        est_lat = stats["lat_grid"]
        est_lon = stats["lon_grid"]
        est_floors = stats["floors"]
        est_elevator = stats["elevator"]
    else:
        # Fallback for unknown tracts (City Center Averages)
        print(f"Warning: Unknown Tract {tract_key}. Using defaults.")
        est_lat = 41.980
        est_lon = 2.820
        est_floors = 3
        est_elevator = 1

    # 3. Build Input DataFrame (Exact same features as training)
    input_df = pd.DataFrame(
        [
            {
                "area": area,
                "rooms": rooms,
                "floors": est_floors,
                "elevator": est_elevator,
                "census_tract": int(census_tract),
                "lat_grid": est_lat,
                "lon_grid": est_lon,
            }
        ]
    )

    # 4. Re-create Feature Engineering
    input_df["m2_per_room"] = input_df["area"] / input_df["rooms"]
    input_df["vertical_score"] = input_df["floors"] * input_df["elevator"]
    input_df["is_large"] = (input_df["area"] > 120).astype(int)
    input_df["area_lat"] = input_df["area"] * input_df["lat_grid"]
    input_df["area_lon"] = input_df["area"] * input_df["lon_grid"]

    # Cast Category
    input_df["census_tract"] = input_df["census_tract"].astype("category")

    # 5. Predict
    # Feature order must match training
    features = [
        "area",
        "rooms",
        "floors",
        "elevator",
        "census_tract",
        "lat_grid",
        "lon_grid",
        "m2_per_room",
        "vertical_score",
        "is_large",
        "area_lat",
        "area_lon",
    ]

    dinput = xgb.DMatrix(input_df[features], enable_categorical=True)

    log_pred = model.predict(dinput)[0]
    raw_pred = np.expm1(log_pred)

    # 6. Apply Safety Net
    final_pred = raw_pred * 1.10 if raw_pred > 1800 else raw_pred

    return final_pred


# --- TEST IT ---
# Try predicting that €2700 flat (Row 2082) using only basic info
# (Assuming you know its area/rooms/tract from your CSV)
price = predict_rent_smart(area=60, rooms=1, census_tract=1707904001)
print(f"Estimated Rent: €{price:.2f}")
