import json
import sys

import pandas as pd

sys.path.append('./src')

from model import ModelService

with open('./tests/event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


def test_prepare_features():

    actual_features = ModelService.prepare_features(pd.Series(event["name"]))

    expected_features = "_babybugs_"

    assert actual_features[0] == expected_features


class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():
    model_mock = ModelMock(10.0)
    model = ModelService(model=model_mock)

    features = {"name": "_babybugs_"}

    actual_prediction = model.predict(features)
    expected_prediction = 10.0

    assert actual_prediction == expected_prediction


if __name__ == '__main__':
    test_prepare_features()
    test_predict()
