import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
from google.cloud import bigquery
from config import BQ_PROJECT_ID, BQ_DATASET, BQ_TABLE, ids

try:
    # Carrega as variáveis de ambiente
    load_dotenv()
    api_key = os.getenv("COINCAP_API_KEY")
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

    # Validação: Verifica se a resposta da API contém os campos esperados
    if not data or "data" not in data or "timestamp" not in data:
        print("Erro: Não houve retorno válido da API CoinCap.")
        exit(1)

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

    # Validação: verifica se há valores ausentes nas colunas obrigatórias
    missing = df[df[["id", "priceUsd", "date"]].isnull().any(axis=1)]
    if not missing.empty:
        print("Aviso: Existem linhas com campos obrigatórios ausentes:")
        print(missing)
        print("Erro: Nenhum dado válido para inserir no BigQuery.")
        exit(1)

    # Inicializa o client do BigQuery usando o projeto configurado
    client = bigquery.Client(project=BQ_PROJECT_ID)
    # Monta o identificador completo da tabela (projeto.dataset.tabela)
    table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

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
except Exception as e:
    print(f"Erro inesperado: {e}")
    exit(1)