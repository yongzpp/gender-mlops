import logging
import os

import mlflow
import pandas as pd
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

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
