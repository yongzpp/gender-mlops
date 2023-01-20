FROM prefecthq/prefect:2.7.7-python3.9

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app
COPY ingest_data.py ingest_data.py
COPY data data

#ENTRYPOINT ["python", "ingest_data.py"]