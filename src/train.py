from datetime import timedelta

import mlflow
import pandas as pd
from prefect import flow, task
from prefect.deployments import Deployment
from prefect.filesystems import GCS
from prefect.orion.schemas.schedules import CronSchedule, IntervalSchedule
from sklearn.model_selection import train_test_split

from config import cfg
from model import ModelService

gcs_block = GCS.load("gender-prefect-store")


@flow
def train_flow():
    '''
    Contains references to:
    What's in a Name? Gender Classification of Names with Character Based Machine Learning Models
    https://arxiv.org/pdf/2102.03692.pdf
    (Logistic Regression + N-Grams + Prefix + Suffix)
    '''
    data = pd.read_csv(cfg.data.path)
    df_train, df_val = train_test_split(data, test_size=0.33, random_state=1)

    X_train, X_val = df_train["name"], df_val["name"]
    y_train, y_val = df_train["gender"], df_val["gender"]

    model = ModelService()
    model.train(X_train, X_val, y_train, y_val)


if __name__ == '__main__':
    train_flow()

    # deployment = Deployment.build_from_flow(
    #     flow=train_flow,
    #     name="model_training",
    #     schedule=IntervalSchedule(interval=timedelta(minutes=3)),
    #     storage=gcs_block,
    #     work_queue_name="ml")
    # deployment.apply()
