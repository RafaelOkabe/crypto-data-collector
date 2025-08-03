# Crypto Data Collector

## Visão Geral do Projeto

Este projeto é uma aplicação em Python projetada para coletar dados de criptomoedas de uma API de Criptomoedas, processá-los e armazená-los no BigQuery do GCP. Os dados coletados são então utilizados para a criação de um dashboard analítico no Looker Studio.

### Estrutura e Arquitetura do Pipeline

A arquitetura do projeto segue um pipeline de dados simples, com as seguintes etapas:

1.  **Coleta de Dados:** O script Python se conecta à **CoinCap API** para extrair informações sobre criptomoedas específicas.
2.  **Processamento:** Os dados brutos da API são transformados em um formato estruturado usando a biblioteca `pandas`. Tipos de dados são ajustados para garantir a consistência e a integridade.
3.  **Armazenamento (Data Warehouse):** Os dados processados são carregados em um **dataset** no **Google BigQuery**, um serviço de data warehouse na nuvem.
4.  **Análise e Visualização:** As tabelas no BigQuery servem como fonte de dados para um dashboard analítico no **Google Looker Studio**.

### Diagrama do Banco de Dados (BigQuery)

O esquema do banco de dados é simples e eficiente para o propósito deste projeto. A tabela principal armazena os dados descritivos das criptomoedas e outra tabela contém histórico de cotação em dólar.

![Esquema de tabelas no BigQuery](assets/DiagramCrypto.jpg)

* `id`: Identificador da criptomoeda (ex: 'bitcoin', 'ethereum').
* `priceUsd`: Preço da criptomoeda em dólares americanos. O tipo `NUMERIC` garante alta precisão.
* `date`: Data da coleta dos dados.

---

## Como Configurar e Executar

### Pré-requisitos

* Python 3.8+
* Conta no Google Cloud Platform (GCP) com um projeto ativo.
* Credenciais da API da CoinCap.

### 1. Configuração do Ambiente

1.  Clone este repositório:
    `git clone <URL_DO_SEU_REPOSITORIO>`
    `cd <nome_do_repositorio>`

2.  Instale as dependências do Python:
    `pip install -r requirements.txt`

3.  Crie um arquivo `.env` na raiz do projeto com suas credenciais e configurações:

    ```bash
    COINCAP_API_KEY="sua_chave_da_api"
    BQ_PROJECT_ID="seu_id_do_projeto_gcp"
    BQ_DATASET="nome_do_seu_dataset_no_bigquery"
    BQ_TABLE="nome_da_sua_tabela"
    GOOGLE_APPLICATION_CREDENTIALS="caminho/para/seu/arquivo/credentials.json"
    ```

    > **Nota:** Certifique-se de que o arquivo de credenciais (`credentials.json`) tem permissão para acessar e gravar no BigQuery.

### 2. Execução do Programa

Basta executar o script principal:
`python main.py`

O programa irá coletar os dados da API e carregá-los na tabela do BigQuery especificada.

### 3. Dashboard no Looker Studio

1.  Acesse o **Google Looker Studio**.
2.  Crie uma nova fonte de dados e selecione o conector do **BigQuery**.
3.  Selecione seu projeto, dataset e a tabela `crypto_data`.
4.  Crie um dashboard visualizando a evolução dos preços das criptomoedas ao longo do tempo.

---

## Contato

* **Seu Nome** - [Seu Perfil do GitHub](https://github.com/seu-usuario)