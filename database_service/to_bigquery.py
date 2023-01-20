import pandas as pd
from pathlib import Path

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

def extract_from_gcs():
    gcs_path = "data/name_gender.csv"
    gcs_block = GcsBucket.load("gender-db-bucket")
    gcs_block.get_directory(from_path=gcs_path, local=f"../data/")
    return Path(f"../data/{gcs_path}")

def write_bq(df):
    gcp_credentials_block = GcpCredentials.load("gender-cred")
    df.to_gbq(destination_table="gender_data",
              project_id="gender-mlops",
              credentials=gcp_credentials_block.get_credentials_from_service_account(),
              chunksize=500_000,
              if_exists="append")

def gcs_to_gbq():
    path = extract_from_gcs()
    df = pd.read_csv(path)
    write_bq(df)