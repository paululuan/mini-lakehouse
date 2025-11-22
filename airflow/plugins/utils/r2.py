import pandas as pd
import boto3
import os
import io
from datetime import datetime
from botocore.exceptions import ClientError

class R2Client:
    """
    Cliente para interagir com o Cloudflare R2 (Serviço compatível com S3) 
    para operações de upload e download de DataFrames.
    """
    
    def __init__(self, bucket_name: str, endpoint: str = None, 
                 access_key: str = None, secret_key: str = None):
        """
        Inicializa o cliente R2. Prioriza variáveis de ambiente se os argumentos 
        não forem fornecidos.
        """
        
        # 1. Obtém credenciais do ambiente ou dos argumentos
        endpoint = endpoint or os.environ.get("R2_ENDPOINT")
        access_key = access_key or os.environ.get("R2_ACCESS_KEY")
        secret_key = secret_key or os.environ.get("R2_SECRET_KEY")
        self.bucket_name = bucket_name or os.environ.get("R2_BUCKET")

        if not all([endpoint, access_key, secret_key]):
            raise EnvironmentError("Credenciais ou Endpoint do R2 incompletos. Verifique R2_ENDPOINT_URL, R2_ACCESS_KEY_ID e R2_SECRET_ACCESS_KEY no ambiente ou argumentos.")

        # 2. Configura a conexão S3/R2 usando boto3
        session = boto3.session.Session()
        self.s3_client = session.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            # 🚨 ADICIONE ESTA LINHA APENAS PARA TESTES 🚨
            verify=False
        )
        print(f"R2Client inicializado para o bucket: {self.bucket_name}")

    # ----------------------------------------
    # MÉTODO DE UPLOAD (Revisado para classe)
    # ----------------------------------------
    
    def upload_dataframe(self, df: pd.DataFrame, file_name: str, folder_path: str) -> str:
        """
        Converte um DataFrame do Pandas para CSV em memória e faz o upload para o R2.
        """
        
        # 1. Prepara o nome do arquivo e a chave
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name_clean = file_name.replace(' ', '_').replace('/', '_')
        r2_key = f"{folder_path}/{file_name_clean}_{timestamp}.csv"
        
        # 2. Converte o DataFrame para CSV em memória (IO)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # 3. Envia o arquivo para o R2
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=r2_key,
                Body=csv_buffer.getvalue().encode('utf-8'),
                ContentType='text/csv'
            )
            return r2_key
        except ClientError as e:
            raise Exception(f"Erro no upload para R2 (Key: {r2_key}): {e}")

    # ----------------------------------------
    # NOVO MÉTODO DE DOWNLOAD
    # ----------------------------------------

    def download_to_dataframe(self, key: str, file_format: str = 'csv', **kwargs) -> pd.DataFrame:
        """
        Baixa um arquivo do R2 e o carrega diretamente em um DataFrame do Pandas.
        Suporta arquivos CSV e Parquet.

        Args:
            key: O caminho (chave) do objeto no bucket R2 (ex: raw/meuarquivo.csv).
            file_format: O formato do arquivo ('csv' ou 'parquet').
            **kwargs: Argumentos adicionais passados para pd.read_csv ou pd.read_parquet.
            
        Returns:
            O DataFrame do Pandas.
        """
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            
            # Lê o conteúdo do arquivo em memória
            body = obj['Body'].read()
            
            if file_format.lower() == 'csv':
                # Usa io.BytesIO para ler o conteúdo binário como um arquivo
                return pd.read_csv(io.BytesIO(body), **kwargs)
            elif file_format.lower() == 'parquet':
                return pd.read_parquet(io.BytesIO(body), **kwargs)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_format}. Use 'csv' ou 'parquet'.")

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Arquivo não encontrado no R2: {key}")
            else:
                raise Exception(f"Erro no download do R2 (Key: {key}): {e}")