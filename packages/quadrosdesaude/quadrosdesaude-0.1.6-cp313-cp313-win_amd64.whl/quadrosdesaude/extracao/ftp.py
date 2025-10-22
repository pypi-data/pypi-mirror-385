import os
import shutil
from ftplib import FTP, error_perm
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class FTPDownloader:
  """
  Uma classe para baixar arquivos do servidor FTP do Datasus.
  """
  def __init__(self, ftp_host="ftp.datasus.gov.br"):
    self.ftp_host = ftp_host

  def lista_arquivos(self, caminho_ftp: str, extensao: str = '.dbc', prefixo: str = None, usuario: str = None, senha: str = None):
    """
    Lista os arquivos em um diretório do servidor FTP.

    Args:
      caminho_ftp (str): O caminho do diretório no servidor FTP.
      extensao (str, optional): A extensão dos arquivos a serem listados. Defaults to '.dbc'.
      prefixo (str, optional): O prefixo dos arquivos a serem listados. Defaults to None.
      usuario (str, optional): Usuário para login ftp.
      senha (str, optional): Senha para login ftp.
    Returns:
      list: Uma lista de nomes de arquivos.
    """
    try:
      with FTP(self.ftp_host) as ftp:
        
        if usuario:
          ftp.login(user=usuario, passwd=senha)
        else:
          ftp.login()
        ftp.cwd(caminho_ftp)
        arquivos_e_pastas = ftp.nlst()

        if not prefixo and not extensao:
          return arquivos_e_pastas

        if extensao:
          files = [item for item in arquivos_e_pastas if item.upper().endswith(extensao.upper())]
        if prefixo:
          files = [item for item in files if item.upper().startswith(prefixo.upper())]
        
        if not files:
          print("Nenhum arquivo encontrado que corresponda aos filtros.")
          return []
        
        return files
      
    except error_perm as e:
      print(f"❌ Erro ao acessar o caminho: {e}. Verifique se o caminho está correto.")
      return []
    except Exception as e:
      print(f"❌ Ocorreu um erro inesperado: {e}")
      return []

  def download_arquivo(self, caminho_ftp: str, nome_arquivo: str, pasta_destino: str, pasta_temp: str = './temp_download', usuario: str = None, senha: str = None, flag_pasta: bool = False):
    """
    Baixa um único arquivo do servidor FTP.
    Args:
      caminho_ftp (str): O caminho do diretório no servidor FTP.
      arquivo (str): O nome do arquivo a ser baixado.
      pasta_destino (str): A pasta de destino para salvar o arquivo.
      pasta_temp (str): A pasta temporária para o download. Default é "./temp_download". 
    """
    os.makedirs(pasta_destino, exist_ok=True)
    os.makedirs(pasta_temp, exist_ok=True)

    caminho_destino = os.path.join(pasta_destino, nome_arquivo)
    caminho_temp = os.path.join(pasta_temp, nome_arquivo)

    if os.path.exists(caminho_destino):
      return f"Arquivo já baixado: {nome_arquivo}"

    try:
      with FTP(self.ftp_host) as ftp:
        if usuario:
          ftp.login(user=usuario, passwd=senha)
        else:
          ftp.login()
        ftp.cwd(caminho_ftp)

        if not flag_pasta:
          total_size = ftp.size(nome_arquivo)
          with open(caminho_temp, 'wb') as f_local, tqdm(
            total = total_size,
            unit = 'B', unit_scale = True, unit_divisor = 1024, desc = nome_arquivo
          ) as pbar:
            def callback(data):
              f_local.write(data)
              pbar.update(len(data))
            ftp.retrbinary(f"RETR {nome_arquivo}", callback)
        
        else:
          with open(caminho_temp, 'wb') as f_local:
            def callback(data):
              f_local.write(data)
            ftp.retrbinary(f"RETR {nome_arquivo}", callback)
      try:
        shutil.move(caminho_temp, caminho_destino)
      except Exception as e:
        raise Exception(f'ERRO ao mover o arquivo {os.path.basename(caminho_temp)}: {e}') from e
      return f"BAIXADO: {nome_arquivo}"

    except error_perm as e:
      print(f"❌ Erro de permissão ou arquivo não encontrado: {e}")
    except Exception as e:
      print(f"❌ Ocorreu um erro inesperado durante o download: {e}")
      if os.path.exists(caminho_temp):
        os.remove(caminho_temp)
    finally:
      if os.path.exists(caminho_temp):
        os.remove(caminho_temp)


  def download_pasta(self, caminho_ftp: str, pasta_destino: str, pasta_temp: str = './temp_download', extensao: str = '.dbc', prefix: str = None, max_workers: int = 1):
    """
    Baixa todos os arquivos de um diretório FTP de forma concorrente.

    Args:
      caminho_ftp (str): O caminho do diretório no servidor FTP.
      pasta_destino (str): A pasta de destino para salvar os arquivos.
      extensao (str, optional): A extensão dos arquivos a serem baixados. Default '.dbc'.
      prefixo (str, optional): O prefixo dos arquivos a serem baixados. Default None.
      max_workers (int, optional): O número máximo de downloads simultâneos. Default 1.
    """
    print("--- Iniciando o processo de download em lote ---")

    files_to_download = self.lista_arquivos(caminho_ftp, extensao, prefix)

    if not files_to_download:
      print("Nenhum arquivo encontrado. Verifique o caminho ou as permissões.")
      return

    total_arquivos = len(files_to_download)
    print(f"Encontrados {total_arquivos} arquivos. Começando downloads com {max_workers} conexões simultâneas.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
      futuros = []
      for nome_arquivo in files_to_download:
        futuros.append(
          executor.submit(self.download_file, caminho_ftp, nome_arquivo, pasta_destino, pasta_temp, flag_pasta = True)
        )

      with tqdm(total = total_arquivos, desc = "Progresso Geral", position = 0) as pbar:
        try:
          for future in as_completed(futuros):
            result = future.result()
            # print(result)
            pbar.update(1)
        except KeyboardInterrupt:
          print(f"\n\n🛑 INTERRUPÇÃO DETECTADA PELO USUÁRIO.")
          print("Encerrando o executor e cancelando tarefas pendentes... Por favor, aguarde.")
          executor.shutdown(wait=False, cancel_futures=True)
          return
        except Exception as e:
          print(f"\n\nERRO CRÍTICO: Interrompendo processamento...")
          print(f"Detalhes: {e}")
          executor.shutdown(wait=False, cancel_futures=True)
          return
    print("\n--- Processo de download concluído! ---")
    # if os.path.exists(pasta_temp):
    #   shutil.rmtree(pasta_temp)
