"""Remove dados de exemplo das telas (clientes, funcionarios, fornecedores, lancamentos)."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import Database


def limpar_dados():
    db = Database()
    tabelas = [
        "lancamentos",
        "clientes",
        "funcionarios",
        "fornecedores",
        "saldo_diario",
        "auditoria",
    ]

    total = 0
    for tabela in tabelas:
        try:
            deletados = db.deletar(f"DELETE FROM {tabela}")
            total += deletados
            print(f"[OK] {tabela}: {deletados} registro(s) removido(s)")
        except Exception as e:
            print(f"[ERRO] {tabela}: {e}")

    print(f"[OK] Limpeza concluida. Total removido: {total}")


if __name__ == "__main__":
    limpar_dados()
