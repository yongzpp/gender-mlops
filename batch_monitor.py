import csv
import json
import os
import pickle

import pandas as pd
import pyarrow.parquet as pq
from evidently import ColumnMapping
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import ClassificationPerformanceTab
from evidently.model_profile import Profile
from evidently.model_profile.sections import (
    ClassificationPerformanceProfileSection
)
from prefect import flow, task
from pymongo import MongoClient

from src.model import ModelService


@task
def upload_target(filename):
    client = MongoClient("mongodb://localhost:27017/")
    collection = client.get_database("prediction_service").get_collection("batch")
    data = pd.read_csv(filename)
    for index, row in data.iterrows():
        collection.insert_one(
            {
                "name": row["name"],
                "prediction": row["prediction"],
                "gender": row["gender"],
                "numerical": row["numerical"],
            }
        )
    client.close()


@task
def load_reference_data(filename):
    RUN_ID = '5bd26caf8a64400e89e3734bf8aa3200'
    model = ModelService(RUN_ID)
    reference_data = pd.read_csv(filename)
    # Create features
    features = ModelService.prepare_features(reference_data["name"])

    # add target column
    reference_data['prediction'] = model.predict(features)
    return reference_data


@task
def fetch_data():
    client = MongoClient("mongodb://localhost:27017/")
    data = client.get_database("prediction_service").get_collection("batch").find()
    df = pd.DataFrame(list(data))
    print(df.head())
    return df


@task
def run_evidently(ref_data, data):
    profile = Profile(sections=[ClassificationPerformanceProfileSection()])
    print(ref_data.head())
    print(ref_data.dtypes)
    print(data.head())
    print(data.dtypes)
    mapping = ColumnMapping(
        prediction="prediction",
        numerical_features=['numerical'],
        categorical_features=[],
        datetime_features=[],
        target="gender",
    )
    profile.calculate(ref_data, data, mapping)

    dashboard = Dashboard(tabs=[ClassificationPerformanceTab(verbose_level=0)])
    dashboard.calculate(ref_data, data, mapping)
    return json.loads(profile.json()), dashboard


@task
def save_report(result):
    client = MongoClient("mongodb://localhost:27017/")
    client.get_database("prediction_service").get_collection("report").insert_one(
        result[0]
    )


@task
def save_html_report(result):
    result[1].save("evidently_report_example.html")


@flow
def batch_analyze():
    upload_target("./results/target.csv")
    ref_data = load_reference_data("./datasets/gender/reference.csv")
    data = fetch_data()
    result = run_evidently(ref_data, data)
    save_report(result)
    save_html_report(result)


batch_analyze()
