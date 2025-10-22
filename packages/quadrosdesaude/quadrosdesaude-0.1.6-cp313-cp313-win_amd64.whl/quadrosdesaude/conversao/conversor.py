# src/quadrosdesaude/conversion/converter.py

import os
import time
import itertools
import gc
import polars as pl
import pyarrow.parquet as pq
from dbfread import DBF
from quadrosdesaude import descomprimir_dbc
from .parser import StringFieldParser

def harmonizar_registos_em_fluxo(iterator_dbf, schema_mestre):
  """
  Harmoniza os registros de um iterador DBF com um esquema mestre e devolve um yeld harmonizado.
  """
  valor_vazio = ''
  for registo in iterator_dbf:
    registo_completo = {coluna: valor_vazio for coluna in schema_mestre}
    registo_completo.update(registo)
    yield registo

def dbc2dbf(caminho_dbc: str, caminho_dbf: str):
  """
  Descomprime um único arquivo .dbc para .dbf.
  """
  start_time = time.perf_counter()
  try:
    descomprimir_dbc(caminho_dbc, caminho_dbf)
    duration = time.perf_counter() - start_time
    return True
  except Exception as e:
    duration = time.perf_counter() - start_time
    return False


def dbf2parquet(caminho_dbf: str, destino_parquet: str = None, tamanho_lote: int = 200000):
  """
  Converte um ficheiro .dbf para .parquet em lotes.
  """
  if not destino_parquet:
    nome_base = os.path.basename(caminho_dbf)
    destino_parquet = f'{nome_base}.parquet'

  start_time = time.perf_counter()
  writer = None
  total_linhas_processadas = 0

  try:
    tabela_dbf = DBF(caminho_dbf, parserclass = StringFieldParser)
    schema_mestre = tabela_dbf.field_names
    total_linhas_cabecalho = len(tabela_dbf)

    gerador_harmonizado = harmonizar_registos_em_fluxo( iter( tabela_dbf ), schema_mestre )

    for lote_de_registros in iter( lambda: list( itertools.islice( gerador_harmonizado, tamanho_lote ) ), [] ):
      df_lote = pl.DataFrame( lote_de_registros, schema_overrides={col: pl.Utf8 for col in schema_mestre} )
      tabela_arrow = df_lote.to_arrow()
      if writer is None:
        writer = pq.ParquetWriter(destino_parquet, tabela_arrow.schema)
      writer.write_table(tabela_arrow)
      total_linhas_processadas += len(df_lote)
      del lote_de_registros, df_lote, tabela_arrow
      gc.collect()

    if writer:
      writer.close()

    # Verificação
    linhas_no_parquet = pq.ParquetFile(destino_parquet).metadata.num_rows
    duration = time.perf_counter() - start_time

    if total_linhas_cabecalho == linhas_no_parquet:
      return True
    else:
      print(f'Falha no dbf2parquet do arquivo {caminho_dbf}')
      return False
  except Exception as e:
    print(f'Falha crítica ao processar dbf2parquet do arquivo {caminho_dbf}')
    del lote_de_registros, df_lote, tabela_arrow
    gc.collect()
    if writer:
      writer.close()
    return False
