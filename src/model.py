import sys
from datetime import timedelta

import mlflow
import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.context import get_run_context
from prefect.deployments import Deployment
from prefect.filesystems import GCS
from prefect.orion.schemas.schedules import CronSchedule, IntervalSchedule
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline

from config import cfg

TRACKING_SERVER_HOST = "0.0.0.0"
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
# gcs_block = GCS.load("gender-prefect-store")


class ModelService:
    def __init__(self, run_id=None, model=None):
        self.run_id = run_id
        self.model = self.load_model(self.run_id) if self.run_id else model

    @staticmethod
    def prepare_features(name):
        def removeSpecialCharacter(s):
            t = "_"
            for i in s:
                if i.isalpha():
                    t += i.lower()
            t += "_"
            return t

        return name.apply(removeSpecialCharacter)

    def compute_metrics(self, pred, labels):
        accuracy = accuracy_score(y_true=labels, y_pred=pred)
        return {"accuracy": accuracy}

    def train(self, X_train, X_val, y_train, y_val, C=1.0, solver='lbfgs'):
        mlflow.set_experiment("gender-experiment")

        with mlflow.start_run():
            mlflow.set_tag("Developer", "Zi Ping")

            X_train = self.prepare_features(X_train)
            X_val = self.prepare_features(X_val)

            params = {"C": C, "solver": solver}
            mlflow.log_params(params)

            pipeline = make_pipeline(
                TfidfVectorizer(
                    analyzer='char',
                    ngram_range=(cfg.train.ngram[0], cfg.train.ngram[1]),
                ),
                LogisticRegression(**params),
            )
            pipeline.fit(X_train, y_train)

            y_pred = pipeline.predict(X_val)
            mlflow.log_metric(
                "accuracy", self.compute_metrics(y_pred, list(y_val))["accuracy"]
            )
            mlflow.sklearn.log_model(pipeline, artifact_path="model")

    def load_model(self, run_id):
        logged_model = f'gs://gender-bucket/4/{run_id}/artifacts/model'
        model = mlflow.pyfunc.load_model(logged_model)
        return model

    def save_results(self, df, y_pred, run_id, output_file):
        df_result = pd.DataFrame()
        df_result['name'] = df['name']
        df_result['prediction'] = y_pred
        df_result['model_version'] = run_id
        df_result['gender'] = df["gender"]
        df_result['numerical'] = df["numerical"]
        # df_result.to_parquet("./results/predictions.parquet", index=False)
        df_result.to_csv(output_file, index=False)

    def apply_model(self, input_file, run_id, output_file):
        # logger = get_run_logger()

        # logger.info(f'Reading the data from {input_file}...')
        data = pd.read_csv(input_file)
        features = ModelService.prepare_features(data['name'])
        # logger.info(f'Loading the model with RUN_ID={run_id}...')

        # logger.info('Applying the model...')
        y_pred = self.predict(features)

        # logger.info(f'Saving the result to {output_file}...')
        self.save_results(data, y_pred, run_id, output_file)
        return output_file

    def batch_predict(self):
        # ctx = get_run_context()
        # run_date = ctx.flow_run.expected_start_time

        input_file, output_file = (
            cfg.data.test_path,
            # f"../results/predictions_{run_date}.csv",
            f"./results/target.csv",
        )

        self.apply_model(
            input_file=input_file, run_id=self.run_id, output_file=output_file
        )

    def predict(self, features):
        pred = self.model.predict(features)
        return pred
