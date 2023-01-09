import json
import sys

import requests
from deepdiff import DeepDiff

sys.path.append('./src')

from predict import fetch_data

with open('./tests/event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


def test_predict():
    url = 'http://34.87.56.146:9696/predict'
    actual_response = requests.post(url, json=event, timeout=10).json()
    print('actual response:')

    print(json.dumps(actual_response, indent=2))

    expected_response = {
        'gender': "M",
        'model_version': 'ec4f26291d42414ba2b8908d8be7a99d',
    }

    diff = DeepDiff(actual_response, expected_response, significant_digits=1)
    print(f'diff={diff}')

    assert 'type_changes' not in diff
    assert 'values_changed' not in diff


def test_mongo():
    url = 'http://34.87.56.146:9696/predict'
    actual_response = requests.post(url, json=event, timeout=10).json()
    print('actual response:')

    prediction_df = fetch_data()
    print(prediction_df)

    assert "Baby Bugs" in list(prediction_df["name"])


if __name__ == '__main__':
    test_predict()
    test_mongo()
