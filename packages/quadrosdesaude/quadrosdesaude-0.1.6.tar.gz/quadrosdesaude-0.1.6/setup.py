from setuptools import setup, Extension
import sys

print("--- DEBUG: Iniciando build.py ---", file=sys.stderr)

try:
  ext_modules_list = [
    Extension(
      name="quadrosdesaude.datasus", 
      sources=[
        "src/quadrosdesaude/c_src/decompress.c",
        "src/quadrosdesaude/c_src/blast.c"
      ],
      language="c",
    )
  ]
  print(f"--- DEBUG: ext_modules definidos: {ext_modules_list} ---", file=sys.stderr)

  print("--- DEBUG: Chamando setup()... ---", file=sys.stderr)
  setup(ext_modules=ext_modules_list)
  print("--- DEBUG: setup() concluído (ou falhou silenciosamente se não vir mais nada) ---", file=sys.stderr)

except Exception as e:
  print(f"--- ERRO DENTRO DO build.py: {e} ---", file=sys.stderr)
  raise

print("--- DEBUG: Fim do build.py ---", file=sys.stderr)