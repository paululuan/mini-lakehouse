import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, Any

def sheets_to_dataframe(
    search_name: str,
    drive_folder_id: str,
    service_account_file: str,
    worksheet_index: int = 0,
    **kwargs: Any
) -> Optional[pd.DataFrame]:
    """
    Acessa uma pasta do Google Drive, procura um Google Sheet pelo nome 
    e retorna seu conteúdo como um Pandas DataFrame.

    Args:
        search_name: O nome ou parte do nome do arquivo Google Sheet a ser procurado.
        drive_folder_id: O ID da pasta do Google Drive onde a busca será realizada.
        service_account_file: O caminho para o arquivo JSON da conta de serviço.
        worksheet_index: O índice da aba (worksheet) a ser lida (padrão é a primeira, 0).
        **kwargs: Argumentos adicionais (como encoding, dtype) para pd.DataFrame().

    Returns:
        Um Pandas DataFrame com os dados da planilha ou None se o arquivo não for encontrado.
    """
    
    # 1. Configurar a Conexão com a Drive API (para buscar o arquivo ID)
    try:
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        drive_service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Erro ao inicializar a Drive API: {e}")
        return None

    # 2. Buscar o arquivo pelo nome e ID da pasta
    # A consulta filtra por: 
    # - Arquivos dentro da pasta específica
    # - Nome do arquivo que contém a string de busca (search_name)
    # - Tipo de arquivo ser Google Sheet
    query = (
        f"'{drive_folder_id}' in parents and "
        f"name contains '{search_name}' and "
        f"mimeType='application/vnd.google-apps.spreadsheet'"
    )
    
    try:
        results = drive_service.files().list(
            q=query, 
            fields="files(id, name)"
        ).execute()
        
        arquivos = results.get('files', [])
        
        if not arquivos:
            print(f"Nenhum arquivo Google Sheet encontrado com '*{search_name}*' na pasta.")
            return None
        
        # Assume que o primeiro resultado é o arquivo desejado (pode ser ajustado)
        sheet_info: Dict[str, str] = arquivos[0] 
        sheet_id = sheet_info['id']
        print(f"Arquivo encontrado: ID={sheet_id}, Nome={sheet_info['name']}")

    except HttpError as e:
        print(f"Erro na busca da Drive API: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado durante a busca: {e}")
        return None


    # 3. Configurar a Conexão com a Sheets API (gspread) e Ler o Conteúdo
    try:
        # gspread usa o mesmo arquivo de Service Account
        gc = gspread.service_account(filename=service_account_file)
        
        # Abre o Google Sheet pelo ID
        sh = gc.open_by_key(sheet_id)
        
        # Obtém a aba (worksheet)
        worksheet = sh.get_worksheet(worksheet_index)
        
        # Obtém todos os dados como lista de listas
        data = worksheet.get_all_values()
        
        if not data:
            print(f"A aba {worksheet_index} está vazia.")
            return None
            
        # 4. Converte para DataFrame
        # A primeira linha é usada como cabeçalho
        df = pd.DataFrame(data[1:], columns=data[0], **kwargs)
        
        print(f"DataFrame criado com sucesso ({len(df)} linhas).")
        return df

    except gspread.exceptions.WorksheetNotFound:
        print(f"Aba (worksheet) de índice {worksheet_index} não encontrada.")
        return None
    except Exception as e:
        print(f"Erro ao ler a planilha e criar o DataFrame: {e}")
        return None