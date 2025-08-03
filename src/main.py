import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
from google.cloud import bigquery

load_dotenv()
api_key = os.getenv("COINCAP_API_KEY")
bq_project = os.getenv("BQ_PROJECT_ID")
bq_dataset = os.getenv("BQ_DATASET")
bq_table = os.getenv("BQ_TABLE")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

ids = {"bitcoin", "ethereum", "solana", "dogecoin"}
url = "https://rest.coincap.io/v3/assets"
headers = {"Authorization": f"Bearer {api_key}"}
resp = requests.get(url, headers=headers)
data = resp.json()
date_str = datetime.utcfromtimestamp(data["timestamp"] / 1000).date()

rows = [
    {"id": item["id"], "priceUsd": Decimal(item['priceUsd']), "date": date_str}
    for item in data["data"]
    if item["id"] in ids
]

df = pd.DataFrame(rows)

df['id'] = df['id'].astype(pd.StringDtype())

client = bigquery.Client(project=bq_project)
table_id = f"{bq_project}.{bq_dataset}.{bq_table}"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
)

job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()

print("Dados enviados ao BigQuery com sucesso!")