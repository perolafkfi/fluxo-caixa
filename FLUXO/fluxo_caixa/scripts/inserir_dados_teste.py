"""
Script para popular banco de dados com dados de teste
Útil para testar funcionalidades sem inserir manualmente
"""

from database import Database
from models import Lancamento


def inserir_dados_teste():
    """Insere dados de teste no banco"""
    db = Database()
    
    # Limpar dados anteriores
    db.limpar_tudo()

    dados_teste = [
        # RECEITAS
        {
            "data": "2026-01-05",
            "tipo": "Receita",
            "categoria": "Receita",
            "subcategoria": "Serviço",
            "valor": 3000.00,
            "banco": "Banco do Brasil",
            "nota_fiscal": "NF001",
            "empresa": "Cliente A",
            "observacao": "Serviço de desenvolvimento web"
        },
        {
            "data": "2026-01-10",
            "tipo": "Receita",
            "categoria": "Receita",
            "subcategoria": "Produto",
            "valor": 1500.00,
            "banco": "Itaú",
            "nota_fiscal": "NF002",
            "empresa": "Loja Online",
            "observacao": "Venda de produtos"
        },
        {
            "data": "2026-01-15",
            "tipo": "Receita",
            "categoria": "Receita",
            "subcategoria": "Serviço",
            "valor": 2500.00,
            "banco": "Caixa",
            "nota_fiscal": "NF003",
            "empresa": "Empresa XYZ",
            "observacao": "Consultoria empresarial"
        },

        # DESPESAS VARIÁVEIS
        {
            "data": "2026-01-03",
            "tipo": "Despesa",
            "categoria": "Variável",
            "subcategoria": "Insumos",
            "valor": 800.00,
            "banco": "Itaú",
            "nota_fiscal": "NF-FORN001",
            "empresa": "Fornecedor ABC",
            "observacao": "Compra de materiais"
        },
        {
            "data": "2026-01-08",
            "tipo": "Despesa",
            "categoria": "Variável",
            "subcategoria": "Mão de obra",
            "valor": 1200.00,
            "banco": "Banco do Brasil",
            "nota_fiscal": "NF-MOB001",
            "empresa": "Prestador de Serviço",
            "observacao": "Pagamento de freelancer"
        },
        {
            "data": "2026-01-12",
            "tipo": "Despesa",
            "categoria": "Variável",
            "subcategoria": "Fornecimento",
            "valor": 500.00,
            "banco": "Caixa",
            "nota_fiscal": "NF-FORN002",
            "empresa": "Fornecedor DEF",
            "observacao": "Serviços terceirizados"
        },

        # DESPESAS FIXAS
        {
            "data": "2026-01-01",
            "tipo": "Despesa",
            "categoria": "Fixa",
            "subcategoria": "Internet",
            "valor": 150.00,
            "banco": "Débito",
            "observacao": "Internet fibra óptica"
        },
        {
            "data": "2026-01-02",
            "tipo": "Despesa",
            "categoria": "Fixa",
            "subcategoria": "Telefone",
            "valor": 100.00,
            "banco": "Débito",
            "observacao": "Plano móvel mensal"
        },
        {
            "data": "2026-01-05",
            "tipo": "Despesa",
            "categoria": "Fixa",
            "subcategoria": "Energia",
            "valor": 220.00,
            "banco": "Débito",
            "observacao": "Conta de luz"
        },
        {
            "data": "2026-01-07",
            "tipo": "Despesa",
            "categoria": "Fixa",
            "subcategoria": "Água",
            "valor": 80.00,
            "banco": "Débito",
            "observacao": "Conta de água"
        },
        {
            "data": "2026-01-10",
            "tipo": "Despesa",
            "categoria": "Fixa",
            "subcategoria": "Contador",
            "valor": 300.00,
            "banco": "Transferência",
            "observacao": "Serviço contábil mensal"
        },

        # DESPESAS PESSOAIS
        {
            "data": "2026-01-06",
            "tipo": "Despesa",
            "categoria": "Pessoal",
            "subcategoria": "Escola",
            "valor": 500.00,
            "banco": "Débito",
            "observacao": "Mensalidade escolar"
        },
        {
            "data": "2026-01-11",
            "tipo": "Despesa",
            "categoria": "Pessoal",
            "subcategoria": "Cartão de crédito",
            "valor": 1200.00,
            "banco": "Transferência",
            "observacao": "Pagamento de fatura"
        },
        {
            "data": "2026-01-13",
            "tipo": "Despesa",
            "categoria": "Pessoal",
            "subcategoria": "Lazer",
            "valor": 250.00,
            "banco": "Cartão",
            "observacao": "Cinema e restaurante"
        },
    ]

    for dados in dados_teste:
        lancamento = Lancamento(
            data=dados["data"],
            tipo=dados["tipo"],
            categoria=dados["categoria"],
            subcategoria=dados["subcategoria"],
            valor=dados["valor"],
            banco=dados.get("banco", ""),
            nota_fiscal=dados.get("nota_fiscal", ""),
            empresa=dados.get("empresa", ""),
            observacao=dados.get("observacao", "")
        )

        valido, erros = lancamento.validar()
        if valido:
            db.inserir_lancamento(lancamento.para_dict())
            print(f"✅ {lancamento.tipo} - {lancamento.categoria} - R$ {lancamento.valor:.2f}")
        else:
            print(f"❌ Erro: {', '.join(erros)}")

    print("\n✅ Dados de teste inseridos com sucesso!")
    print("\nResumo:")
    print("- 3 Receitas")
    print("- 3 Despesas Variáveis")
    print("- 5 Despesas Fixas")
    print("- 3 Despesas Pessoais")
    print("Total: 14 lançamentos")


if __name__ == "__main__":
    print("🔄 Inserindo dados de teste no banco...")
    inserir_dados_teste()

