"""Constantes da aplicação"""

# Tipos de lançamento
TIPOS_VALIDOS = ["Receita", "Despesa"]

# Categorias
CATEGORIAS_RECEITA = ["Receita"]
SUBCATEGORIAS_RECEITA = ["Serviço", "Produto"]

CATEGORIAS_DESPESA = ["Variável", "Fixa", "Pessoal"]
SUBCATEGORIAS_VARIAVEL = ["Insumos", "Mão de obra", "Fornecimento"]
SUBCATEGORIAS_FIXA = ["Telefone", "Internet", "Contador", "Energia", "Água"]
SUBCATEGORIAS_PESSOAL = ["Escola", "Cartão de crédito", "Lazer"]

# Cores para categorias
CORES_CATEGORIAS = {
    'Receita': '#27ae60',      # Verde
    'Variável': '#e74c3c',     # Vermelho
    'Fixa': '#f39c12',         # Laranja
    'Pessoal': '#8e44ad'       # Roxo
}

# Formato de data
FORMATO_DATA = "%Y-%m-%d"
FORMATO_DATA_EXIBICAO = "%d/%m/%Y"

