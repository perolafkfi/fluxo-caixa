"""
Teste de exportacao executiva do Excel - Fluxo de Caixa
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

# Adicionar o diretorio ao path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import Database
from app.services.relatorios import GeradorRelatorios
from app.services.export_excel_profissional import gerar_planilha_profissional


def testar_exportacao() -> bool:
    """Testa exportacao do relatorio executivo."""
    print("=" * 60)
    print("TESTE DE EXPORTACAO EXCEL - FLUXO DE CAIXA")
    print("=" * 60)

    try:
        # 1. Conectar ao banco de dados
        print("\n1) Conectando ao banco...")
        db = Database()
        print("   OK")

        # 2. Inicializar servicos
        print("\n2) Inicializando servicos...")
        gerador = GeradorRelatorios(db)
        print("   OK")

        # 3. Definir periodo
        data_fim = datetime.now().strftime("%Y-%m-%d")
        data_inicio = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        print(f"\n3) Periodo: {data_inicio} a {data_fim}")

        # 4. Coletar dados
        print("\n4) Coletando dados...")
        lancamentos = gerador.obter_lancamentos_por_periodo(data_inicio, data_fim)
        df = pd.DataFrame(lancamentos)

        # Resumo mensal
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
            df['ano_mes'] = df['data'].dt.to_period('M').astype(str)
            entradas = df[df['tipo'] == 'Receita'].groupby('ano_mes')['valor'].sum().rename('entradas')
            saidas = df[df['tipo'] == 'Despesa'].groupby('ano_mes')['valor'].sum().rename('saidas')
            resumo_mensal = pd.concat([entradas, saidas], axis=1).fillna(0).reset_index()
            resumo_mensal['saldo'] = resumo_mensal['entradas'] - resumo_mensal['saidas']
        else:
            resumo_mensal = pd.DataFrame(columns=['ano_mes', 'entradas', 'saidas', 'saldo'])

        # Resumo anual
        if not df.empty:
            df['ano'] = df['data'].dt.year
            entradas_a = df[df['tipo'] == 'Receita'].groupby('ano')['valor'].sum().rename('entradas')
            saidas_a = df[df['tipo'] == 'Despesa'].groupby('ano')['valor'].sum().rename('saidas')
            resumo_anual = pd.concat([entradas_a, saidas_a], axis=1).fillna(0).reset_index()
            resumo_anual['saldo'] = resumo_anual['entradas'] - resumo_anual['saidas']
        else:
            resumo_anual = pd.DataFrame(columns=['ano', 'entradas', 'saidas', 'saldo'])

        # 5. Exportar
        print("\n5) Exportando arquivo...")
        output_dir = PROJECT_ROOT / 'output'
        output_dir.mkdir(exist_ok=True)
        arquivo_saida = output_dir / f"Relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        gerar_planilha_profissional(lancamentos, resumo_mensal, resumo_anual, arquivo_saida)
        print(f"   OK: {arquivo_saida}")

        # 6. Validar arquivo
        print("\n6) Validando arquivo...")
        if arquivo_saida.exists():
            tamanho = arquivo_saida.stat().st_size
            print(f"   OK: tamanho {tamanho/1024:.2f} KB")
        else:
            print("   ERRO: arquivo nao encontrado")
            return False

        print("\nAbas esperadas:")
        print("  - Dados_Brutos")
        print("  - Resumo_Mensal")
        print("  - Resumo_Anual")
        print("  - Indicadores")
        print("  - Graficos")

        return True

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    sucesso = testar_exportacao()
    sys.exit(0 if sucesso else 1)
