import os
import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import Literal
from .conversor import dbc2dbf, dbf2parquet

def dbc2parquet(caminho_dbc: str, destino_parquet: str, pasta_temp_dbf: str = './temp_dbf', pasta_temp_parquet: str = './temp_parquet', operacao: Literal['lote', 'unico'] = 'unico', tamanho_lote: int = 50000):
  """
  Processa um único ficheiro DBC do início ao fim como uma transação atomica.
  Retorna uma tupla (nome_base, sucesso, mensagem).
  """
  os.makedirs(pasta_temp_dbf, exist_ok=True)
  os.makedirs(pasta_temp_parquet, exist_ok=True)

  nome_base = os.path.basename(caminho_dbc)
  nome_sem_ext = Path(caminho_dbc).stem

  caminho_dbf_temp = os.path.join(pasta_temp_dbf, f"{nome_sem_ext}.dbf")
  caminho_parquet_temp = os.path.join(pasta_temp_parquet, f"{nome_sem_ext}.parquet")
  caminho_parquet_final = os.path.join(destino_parquet, f"{nome_sem_ext}.parquet")

  try:
    dbc2dbf(caminho_dbc, caminho_dbf_temp)

    if dbf2parquet(caminho_dbf_temp, caminho_parquet_temp, tamanho_lote=tamanho_lote):
      try:
        shutil.move(caminho_parquet_temp, caminho_parquet_final)
      except Exception as e:
        raise Exception(f'ERRO ao mover o arquivo {os.path.basename(caminho_parquet_temp)}: {e}') from e
      
      if operacao == 'lote':
        return (nome_base, True, f"Sucesso com o arquivo {caminho_parquet_final}.")
      elif operacao == 'unico':
        return True
      
    else:

      if operacao == 'lote':
        return (nome_base, False, f"Falha: Dados incompletos com o arquivo {caminho_dbf_temp}.")
      elif operacao == 'unico':
        return False

  except Exception as e:
    if operacao == 'lote':
      return (nome_base, False, f"Falha com o arquivo {caminho_dbf_temp}.")
    elif operacao == 'unico':
      return False
  finally:
    if os.path.exists(caminho_dbf_temp):
      os.remove(caminho_dbf_temp)
    if os.path.exists(caminho_parquet_temp):
      os.remove(caminho_parquet_temp)


def orquestrador(pasta_origem_dbc: str, pasta_destino_parquet: str, pasta_temp_dbf: str, pasta_temp_parquet: str, max_workers: int = 1, tamanho_lote: int = 50000):
  """
  Orquestra o processamento completo de uma pasta de ficheiros DBC,
  usando multithreading para processar cada ficheiro de forma atomica e paralela.
  """

  for pasta in [pasta_temp_dbf, pasta_temp_parquet]:
    if os.path.exists(pasta):
      shutil.rmtree(pasta)
    os.makedirs(pasta, exist_ok=True)
  
  arquivos_dbc = list( Path( pasta_origem_dbc ).glob( '*.[dD][bB][cC]' ) )
  if not arquivos_dbc:
    print("Nenhum ficheiro .dbc encontrado na pasta de origem.")
    return

  sucessos, falhas = 0, 0
  start_time_total = time.perf_counter()

  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    progress_bar = tqdm( total = len(arquivos_dbc), desc = "Processando Ficheiros" )
    operacao = 'lote'
    futuros = []
    for caminho_dbc in arquivos_dbc:
      futuro.append(
        executor.submit(dbc2parquet, str(caminho_dbc), pasta_destino_parquet, pasta_temp_dbf, pasta_temp_parquet, operacao, tamanho_lote)
      )
    try:
      for futuro in as_completed(futuros):
        nome_base, sucesso, mensagem = futuro.result()
        if sucesso:
          sucessos += 1
        else:
          print(f"'{nome_base}': {mensagem}")
          falhas += 1
        progress_bar.update(1)
      progress_bar.close()
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

  duration_total = time.perf_counter() - start_time_total
  print(f"Processamento concluído em {duration_total:.2f} segundos.")
  print(f"Sucessos: {sucessos}")
  print(f"Falhas: {falhas}")
