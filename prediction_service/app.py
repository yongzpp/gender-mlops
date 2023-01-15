import logging
import os

import bentoml
import mlflow
import pandas as pd
import requests
from bentoml.io import JSON
from model import ModelService
from pydantic import BaseModel
# from flask import Flask, jsonify, request
from pymongo import MongoClient
from config import cfg

logging.basicConfig(level=logging.INFO)

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017")
mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")

EVIDENTLY_ADDRESS = os.getenv('EVIDENTLY_SERVICE', 'http://127.0.0.1:8085')

RUN_ID = cfg.test.run_id
model = ModelService(RUN_ID)
model_bento = model.model_bentoml
model_runner = model_bento.to_runner()
svc = bentoml.Service('gender-classifier', runners=[model_runner])


class GenderApplication(BaseModel):
    name: str
    gender: str
    numerical: int


@svc.api(input=JSON(pydantic_model=GenderApplication), output=JSON(), route="/predict")
async def predict_endpoint(app_data):
    app_data = app_data.dict()
    features = ModelService.prepare_features(pd.Series(app_data["name"]))

    pred = await model_runner.predict.async_run(features)
    result = {
        'name': app_data["name"],
        'gender': app_data["gender"],
        'model_version': RUN_ID,
        'prediction': pred[0],
    }
    logging.info("Prediction Done...")

    save_to_db(app_data, pred[0])
    logging.info("Saved to Database...")

    send_to_evidently_service(app_data, pred[0])
    logging.info("Sent to Dashboard...")
    return result


def save_to_db(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    #collection.insert_one(rec)


def send_to_evidently_service(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    requests.post(f"{EVIDENTLY_ADDRESS}/iterate/gender", json=[rec], timeout=100)

# app = Flask(__name__)

# @app.route('/predict', methods=['POST'])
# def predict_endpoint():
#     app_data = request.get_json()
#     features = ModelService.prepare_features(pd.Series(app_data["name"]))

#     model = ModelService(RUN_ID)
#     pred = model.predict(features)[0]
#     result = {'name': app_data["name"],
#               'gender': app_data["gender"],
#               'model_version': RUN_ID,
#               'prediction': pred}
#     logging.info("Prediction Done...")

#     save_to_db(name, pred)
#     logging.info("Saved to Database...")

#     send_to_evidently_service(name, pred)
#     logging.info("Sent to Dashboard...")
#     return jsonify(result)

# if __name__ == "__main__":
#     app.run(debug=True)