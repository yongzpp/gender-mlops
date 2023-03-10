import json
import sys

import requests
from deepdiff import DeepDiff

sys.path.append('./prediction_service')

from time import sleep

import pandas as pd

# from app import fetch_data
# from config import cfg
from model import ModelService

RUN_ID = '2a47f4923cc34c589b00773f75168747'

with open('./tests/event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


def test_predict():
    url = 'http://127.0.0.1:8080/predict'
    actual_response = requests.post(url, json=event, timeout=1000).json()
    print('actual response:')

    print(json.dumps(actual_response, indent=2))

    expected_response = {
        'name': 'Baby Bugs',
        'gender': "M",
        'model_version': 'ec4f26291d42414ba2b8908d8be7a99d',
    }

    # diff = DeepDiff(actual_response, expected_response, significant_digits=1)
    # print(f'diff={diff}')

    # assert 'type_changes' not in diff
    # assert 'values_changed' not in diff


# def test_mongo():
#     url = 'http://127.0.0.1:9696/predict'
#     actual_response = requests.post(url, json=event, timeout=1000).json()
#     print('actual response:')

#     prediction_df = fetch_data()
#     # collection.find()
#     assert "Baby Bugs" in list(prediction_df["name"])


def test_online_predict():
    data = pd.read_csv("./prediction_service/data/val_revised.csv")

    url = 'http://127.0.0.1:8080/predict'

    for index, row in data.iterrows():
        print(row)
        if index >= 29:
            break
        data = {
            'name': row["name"],
            'numerical': int(row["numerical"]),
            'gender': row["gender"],
        }
        resp = requests.post(url, json=data, timeout=1000).json()
        print(f"prediction: {resp['gender']}")
        sleep(1)


def test_batch_predict():
    model = ModelService(RUN_ID)
    model.batch_predict()


if __name__ == '__main__':
    # test_predict()
    # test_mongo()
    test_online_predict()
    #test_batch_predict()
