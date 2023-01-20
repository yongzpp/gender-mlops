import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine

from datetime import timedelta
from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect_sqlalchemy import SqlAlchemyConnector

from prefect_gcp.cloud_storage import GcsBucket

@task(log_prints=True, tags=["extract"], cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(path):
    #df_iter = pd.read_csv(path, iterator=True, chunksize=10000)
    #df = next(df_iter)
    df = pd.read_csv(path)
    return df

@task(log_prints=True)
def transform_data(data):
    # Do nothing
    return data

@task(log_prints=True)
def load_data(table_name, df):
    #engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # connection_block = SqlAlchemyConnector.load("postgres-connector")
    # with connection_block.get_connection(begin=False) as engine:
    #     df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    #     df.to_sql(name=table_name, con=engine, if_exists='append')

    gcp_cloud_storage_bucket_block = GcsBucket.load("gender-db-bucket")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path="./data/name_gender.csv",
                                                    to_path="data/name_gender.csv")

    # while True:
    #     try:
    #         t_start = time()
    #         df = next(df_iter)
    #         df.to_sql(name=table_name, con=engine, if_exists='append')
    #         t_end = time()
    #         print('inserted another chunk, took %.3f second' % (t_end - t_start))

    #     except StopIteration:
    #         print("Finished ingesting data into the postgres database")
    #         break

@flow(name="Ingest Data")
def main_flow():
    # parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    # parser.add_argument('--user', required=True, help='user name for postgres')
    # parser.add_argument('--password', required=True, help='password for postgres')
    # parser.add_argument('--host', required=True, help='host for postgres')
    # parser.add_argument('--port', required=True, help='port for postgres')
    # parser.add_argument('--db', required=True, help='database name for postgres')
    # parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    # parser.add_argument('--path', required=True, help='url of the csv file')

    # args = parser.parse_args()

    # Put in prefect-sqlalchemy connector
    # user = "root"
    # password = "root"
    # host = "localhost"
    # port = "5432"
    # db = "gender_data"
    table_name = "gender_table"
    path = "./data/name_gender.csv"

    df = extract_data(path)
    df = transform_data(df)
    load_data(table_name, df)


if __name__ == '__main__':
    main_flow()