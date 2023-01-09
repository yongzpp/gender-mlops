import mlflow
import pandas as pd
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

from model import ModelService

RUN_ID = 'ec4f26291d42414ba2b8908d8be7a99d'

MLFLOW_TRACKING_URI = 'http://localhost:5000'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


MONGODB_ADDRESS = "mongodb://127.0.0.1:27017"
EVIDENTLY_SERVICE_ADDRESS = 'http://127.0.0.1:8085'

app = Flask('gender-flask')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    name = request.get_json()
    features = ModelService.prepare_features(pd.Series(name["name"]))

    model = ModelService(RUN_ID)
    pred = model.predict(features)
    result = {'gender': pred, 'model_version': RUN_ID}
    # save_to_db(name, pred)
    # send_to_evidently_service(name, pred)
    return jsonify(result)


def save_to_db(record, prediction):
    mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
    collection = mongo_client.get_database("prediction_db").get_collection(
        "prediction_table"
    )

    rec = record.copy()
    rec['prediction'] = prediction
    print(rec)
    collection.insert_one(rec)


def send_to_evidently_service(record, prediction):
    rec = record.copy()
    rec['gender'] = prediction
    requests.post(
        f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/gender", json=[rec], timeout=1000
    )


def fetch_data():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    data = (
        client.get_database("prediction_db").get_collection("prediction_table").find()
    )
    dataframe = pd.DataFrame(list(data))
    return dataframe


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
