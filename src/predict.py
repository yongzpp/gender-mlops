import mlflow
import pandas as pd
from flask import Flask, jsonify, request
from mlflow.tracking import MlflowClient

from model import ModelService

# from pymongo import MongoClient


RUN_ID = 'ec4f26291d42414ba2b8908d8be7a99d'

MLFLOW_TRACKING_URI = 'http://localhost:5000'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


app = Flask('gender-flask')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    name = request.get_json()
    features = ModelService.prepare_features(pd.Series(name["name"]))

    model = ModelService(RUN_ID)
    pred = model.predict(features)
    result = {'gender': pred, 'model_version': RUN_ID}
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
