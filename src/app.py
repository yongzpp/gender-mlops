import logging
import os

import mlflow
import pandas as pd
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

import bentoml
from bentoml.io import JSON
from pydantic import BaseModel

from model import ModelService

logging.basicConfig(level=logging.INFO)

RUN_ID = 'ec4f26291d42414ba2b8908d8be7a99d'

MLFLOW_TRACKING_URI = 'http://localhost:5000'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


EVIDENTLY_SERVICE_ADDRESS = os.getenv('EVIDENTLY_SERVICE', 'http://127.0.0.1:5000')
MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017")

mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")

app = Flask(__name__)

# class GenderApplication(BaseModel):
#     name: str
#     gender: str
#     numerical: int

# model_wrapper = ModelService(RUN_ID)
# bentoml.sklearn.save_model('gender-model', model_wrapper.sklearn_model,
#                             signatures={
#                                'predict': {
#                                    'batchable': True,
#                                    'batch_dim': 0
#                                }
#                            })
# model_ref = bentoml.sklearn.get('gender-model:latest')
# model_runner = model_ref.to_runner()
# svc = bentoml.Service('gender-classifier', runners=[model_runner])


# @svc.api(input=JSON(pydantic_model=GenderApplication), output=JSON(), route="/predict")
# async def predict_endpoint(application_data):
#     application_data = application_data.dict()
#     features = ModelService.prepare_features(pd.Series(application_data["name"]))
#     pred = await model_runner.predict.async_run(features)
#     result = {'name': application_data["name"], 'gender': application_data["gender"], 'model_version': RUN_ID, 'prediction': pred[0]}
#     logging.info("Prediction Done...")
#     #save_to_db(application_data, pred[0])
#     logging.info("Saved to Database...")
#     #send_to_evidently_service(application_data, pred[0])
#     logging.info("Sent to Dashboard...")
#     return result

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    name = request.get_json()
    features = ModelService.prepare_features(pd.Series(name["name"]))

    model = ModelService(RUN_ID)
    pred = model.predict(features)[0]
    result = {'name': name["name"], 'gender': pred, 'model_version': RUN_ID}
    logging.info("Prediction Done...")
    save_to_db(name, pred)
    logging.info("Saved to Database...")
    send_to_evidently_service(name, pred)
    logging.info("Sent to Dashboard...")
    return jsonify(result)


def save_to_db(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    collection.insert_one(rec)


def send_to_evidently_service(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    requests.post(
        f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/gender", json=[rec], timeout=1000
    )


def fetch_data():
    data_db = collection.find()
    return data_db


if __name__ == "__main__":
    app.run(debug=True)
