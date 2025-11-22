from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import json
import os 

config_path = os.path.join(os.path.dirname(__file__), 'prd.json')

with open(config_path, 'r') as keys:
    var = json.load(keys)  

dag_config = var["dag_exemplo_load_ondemand"]

SCHEDULE_INTERVAL = dag_config["schedule_interval"]
RAW_PROJECT = dag_config["raw_project"]
BRONZE_PROJECT = dag_config["bronze_project"]
SILVER_PROJECT = dag_config["silver_project"]
GOLD_PROJECT = dag_config["gold_project"]

def dizer_ola():
    print('Olá, Airflow está funcionando!')

with DAG(
    dag_id='dag_exemplo_load_ondemand',
    start_date=datetime(2025, 11, 21),
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=False,
) as dag:
    inicio = DummyOperator(task_id = 'Início')
    fim = DummyOperator(task_id = 'Fim')

    tarefa_ola = PythonOperator(
        task_id='dizer_ola',
        python_callable=dizer_ola
    )

inicio >> tarefa_ola >> fim