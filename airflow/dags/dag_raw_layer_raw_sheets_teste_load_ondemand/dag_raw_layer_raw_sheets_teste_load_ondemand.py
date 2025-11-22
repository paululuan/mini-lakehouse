from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread
import pandas as pd
import json
import os

config_path = os.path.join(os.path.dirname(__file__), 'prd.json')

with open(config_path, 'r') as keys:
    var = json.load(keys)  

dag_config = var["dag_variables"]

DAG_ID = dag_config['dag_id']
SCHEDULE_INTERVAL = dag_config["schedule_interval"]
RAW_PROJECT = dag_config["raw_project"]
BRONZE_PROJECT = dag_config["bronze_project"]
SILVER_PROJECT = dag_config["silver_project"]
GOLD_PROJECT = dag_config["gold_project"]
SERVICE_ACCOUNT_FILE = dag_config['service_account_file']
DEST_FOLDER = dag_config['dest_folder']
DRIVE_FOLDER_ID = dag_config['drive_folder_id']

def driver_file_list():
    # Conectar usando service account
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build('drive', 'v3', credentials=creds)
    
    # Listar arquivos da pasta
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get('files', [])

    if not arquivos:
        print("Nenhum arquivo encontrado na pasta.")
        return
    
    # Mostrar arquivos encontrados
    for arq in arquivos:
        print(f"ID: {arq['id']} - Nome: {arq['name']}")


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2025, 11, 21),
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=False,
) as dag:
    inicio = DummyOperator(task_id = 'Início')
    fim = DummyOperator(task_id = 'Fim')

    liste_arquivos = PythonOperator(
        task_id='liste_arquivos',
        python_callable=driver_file_list
    )

inicio >> liste_arquivos >> fim