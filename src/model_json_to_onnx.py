import xgboost as xgb
from onnxmltools.convert import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType
from onnxmltools.utils import save_model

from constants import MODEL_PATH

model = xgb.Booster()
model.load_model(f"{MODEL_PATH}/girona_rent_model_v3_hybrid.json")

n_features = 12

initial_type = [("input", FloatTensorType([None, n_features]))]

onnx_model = convert_xgboost(model, initial_types=initial_type)
save_model(onnx_model, f"{MODEL_PATH}/model.onnx")
