from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import json
import os

# Importa a função de orquestração reutilizável da camada RAW
from utils.raw_loader import execute_raw_load_from_sheet 

# --- 1. Configuração e Variáveis Globais ---
# Assumindo que você manteve o arquivo de configuração prd.json no mesmo diretório
config_path = os.path.join(os.path.dirname(__file__), 'prd.json')

try:
    with open(config_path, 'r') as keys:
        var = json.load(keys)  
except FileNotFoundError:
    raise FileNotFoundError(f"Arquivo de configuração '{config_path}' não encontrado.")

dag_config = var["dag_variables"]

# Variáveis do JSON (Configurações não sensíveis)
DAG_ID = dag_config.get('dag_id', 'dag_sheets_to_r2_pipeline')
SCHEDULE_INTERVAL = dag_config.get("schedule_interval", None)
SERVICE_ACCOUNT_FILE = dag_config['service_account_file']
DRIVE_FOLDER_ID = dag_config['drive_folder_id']
R2_BUCKET = os.environ.get("R2_BUCKET")
R2_FOLDER_PATH = dag_config['r2_folder_path']

# Verifica se variáveis críticas estão presentes
if not all([SERVICE_ACCOUNT_FILE, DRIVE_FOLDER_ID]):
    raise ValueError("SERVICE_ACCOUNT_FILE ou DRIVE_FOLDER_ID estão ausentes no prd.json.")

# --- 2. Funções Wrapper Específicas da DAG ---
# Criamos funções simples que chamam a lógica principal (execute_raw_load_from_sheet) 
# com os parâmetros específicos de cada fonte/destino.

def carregar_dados_teste(**kwargs):
    """ Orquestra a carga do Google Sheet 'teste' para R2. """
    return execute_raw_load_from_sheet(
        bucket_name=R2_BUCKET,
        search_name='teste',        
        r2_folder_path=R2_FOLDER_PATH,          
        drive_folder_id=DRIVE_FOLDER_ID,
        service_account_file=SERVICE_ACCOUNT_FILE
    )

# --- 3. Definição da DAG ---

with DAG(
    dag_id=DAG_ID,
    # Sugestão: Use uma data de início que já passou
    start_date=datetime(2024, 1, 1), 
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=False,
    tags=['raw', 'drive', 'r2', 'sheets'],
    default_args={
        'owner': 'airflow',
        'retries': 1,
    }
) as dag:
    
    inicio = DummyOperator(task_id = 'início')
    
    # --- Etapa 1: Carregamento RAW (Paralelo) ---

    # 1. Carrega o relatório de teste
    load_teste_raw = PythonOperator(
        task_id='load_teste_raw',
        python_callable=carregar_dados_teste
    )
    
    fim = DummyOperator(task_id = 'fim')


    # --- 4. Definição da Ordem de Execução (Fluxo) ---
    
    # O início leva às duas cargas RAW (execução paralela)
    inicio >> load_teste_raw >> fim