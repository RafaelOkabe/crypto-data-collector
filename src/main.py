import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
from google.cloud import bigquery

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("COINCAP_API_KEY")
bq_project = os.getenv("BQ_PROJECT_ID")
bq_dataset = os.getenv("BQ_DATASET")
bq_table = os.getenv("BQ_TABLE")
# Define o caminho para o arquivo de credenciais do Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Define as criptomoedas que serão coletadas
ids = {"bitcoin", "ethereum", "solana", "dogecoin"}
url = "https://rest.coincap.io/v3/assets"
# Adiciona a chave da API ao cabeçalho da requisição
headers = {"Authorization": f"Bearer {api_key}"}

# Faz a requisição HTTP para a API da CoinCap
resp = requests.get(url, headers=headers)
data = resp.json()

# Converte o timestamp da API (em milissegundos) para o formato de data (UTC)
date_str = datetime.utcfromtimestamp(data["timestamp"] / 1000).date()

# Itera sobre os dados da API para extrair informações das criptomoedas desejadas
rows = [
    # Cria um dicionário para cada linha, convertendo o preço para o tipo Decimal
    {"id": item["id"], "priceUsd": Decimal(item['priceUsd']), "date": date_str}
    for item in data["data"]
    # Filtra apenas as criptomoedas que estão no nosso conjunto 'ids'
    if item["id"] in ids
]

# Converte a lista de dicionários em um DataFrame do Pandas para facilitar a manipulação
df = pd.DataFrame(rows)

# Garante que a coluna 'id' seja do tipo String, um formato compatível com o BigQuery
df['id'] = df['id'].astype(pd.StringDtype())

# Inicializa o client do BigQuery usando o projeto configurado
client = bigquery.Client(project=bq_project)
# Monta o identificador completo da tabela (projeto.dataset.tabela)
table_id = f"{bq_project}.{bq_dataset}.{bq_table}"

# Configura o job de carregamento, especificando que os novos dados devem ser adicionados
# ao final da tabela, sem apagar o conteúdo existente
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
)

# Carrega os dados do DataFrame para a tabela no BigQuery
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
# Aguarda o job de carregamento ser concluído
job.result()

print("Dados enviados ao BigQuery com sucesso!")