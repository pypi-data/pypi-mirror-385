import os
import glob
import shutil

def formatar_tamanho(num_bytes: int):
  """
  Converte um tamanho em bytes para um formato legível (KB, MB, GB, etc.).
  """
  if num_bytes is None:
    return "0 Bytes"

  power = 1024
  n = 0
  power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}

  while num_bytes >= power and n < len(power_labels):
    num_bytes /= power
    n += 1

  return f"{num_bytes:.2f} {power_labels[n]}B"

def medir_tamanho_pasta(caminho_pasta: str):
  """
  Calcula o tamanho total de uma pasta e de todas as suas subpastas.
  """
  print(f"🔎 Calculando o tamanho da pasta: {caminho_pasta}...")
  tamanho_total_bytes = 0
  for dirpath, dirnames, filenames in os.walk(caminho_pasta):
    for f in filenames:
      caminho_arquivo = os.path.join(dirpath, f)
      try:
        tamanho_total_bytes += os.path.getsize(caminho_arquivo)
      except OSError:
        print(f"Não foi possível acessar o arquivo: {caminho_arquivo}")
        pass
  tamanho_formatado = formatar_tamanho(tamanho_total_bytes)
  print(f'Tamanho da pasta é {tamanho_formatado}')
  return tamanho_formatado


def limpador_(caminho_pasta: str):
  confirmacao = input(f"Digite 'sim' para confirmar e continuar a exclusão de tudo que está na pasta {caminho_pasta}: ")
  if confirmacao.lower() == 'sim':
    if os.path.exists(caminho_pasta):
      print(f"\nIniciando a limpeza da pasta '{caminho_pasta}'...")
      itens_para_apagar = glob.glob(os.path.join(caminho_pasta, '*'))
      if not itens_para_apagar:
        print("A pasta já está vazia. Nenhuma ação necessária.")
      else:
        for item_path in itens_para_apagar:
          try:
            if os.path.isfile(item_path):
              os.remove(item_path)
              print(f"  - Arquivo apagado: {os.path.basename(item_path)}")
            elif os.path.isdir(item_path):
              shutil.rmtree(item_path)
              print(f"  - Pasta apagada: {os.path.basename(item_path)}")
          except Exception as e:
            print(f"  - ERRO ao apagar {item_path}: {e}")
        print("\n✅ Limpeza concluída com sucesso!")
    else:
      print(f"\nERRO: A pasta '{caminho_pasta}' não foi encontrada. Verifique o caminho.")
  else:
    print("\nOperação cancelada pelo usuário.")