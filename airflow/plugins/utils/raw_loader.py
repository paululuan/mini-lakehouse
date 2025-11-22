import pandas as pd
import os
from utils.r2 import R2Client 
from utils.google_drive import sheets_to_dataframe 

def execute_raw_load_from_sheet(
    bucket_name: str,
    search_name: str,
    r2_folder_path: str,
    drive_folder_id: str,
    service_account_file: str
) -> str:
    """
    Função genérica para orquestrar a carga de um Google Sheet para a camada RAW do R2.

    Args:
        search_name: Nome do arquivo a ser procurado no Google Drive.
        r2_folder_path: A subpasta de destino no bucket R2 (ex: "raw/vendas").
        drive_folder_id: ID da pasta do Google Drive onde buscar.
        service_account_file: Caminho do JSON da conta de serviço.
        
    Returns:
        A chave (key) do R2 do arquivo carregado via XCom.
    """
    
    # ----------------------------------------------------
    # 1. Leitura do Google Drive
    print(f"Iniciando busca pelo arquivo: '{search_name}'")
    
    df = sheets_to_dataframe(
        search_name=search_name,
        drive_folder_id=drive_folder_id,
        service_account_file=service_account_file
    )
    
    if df is None or df.empty:
        raise Exception("❌ Falha ao criar o DataFrame ou DataFrame vazio. Abortando a carga.")
    
    print(f"DataFrame lido com sucesso: {len(df)} linhas.")

    # ----------------------------------------------------
    # 2. Upload para o Cloudflare R2 (Camada RAW)
    
    # Inicializa o cliente R2 (lê as credenciais do ambiente automaticamente)
    r2_client = R2Client(bucket_name=bucket_name)
    
    # Faz o upload
    r2_key = r2_client.upload_dataframe(
        df=df,
        file_name=search_name, # Usa o nome de busca como nome base do arquivo
        folder_path=r2_folder_path 
    )
    
    print(f"✅ Carga RAW concluída. Chave R2: {r2_key}")
    
    return r2_key