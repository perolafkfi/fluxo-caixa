"""
Schema Unificado do Banco de Dados - Sistema de Fluxo de Caixa
Define a estrutura completa e padronizada de todas as tabelas
"""

CRIAR_TABELAS_SQL = """
-- ============================================
-- SCHEMA UNIFICADO - SISTEMA DE FLUXO DE CAIXA
-- ============================================

-- ============================================
-- TABELA: CATEGORIAS
-- ============================================
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABELA: SUBCATEGORIAS
-- ============================================
CREATE TABLE IF NOT EXISTS subcategorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE,
    UNIQUE(categoria_id, nome)
);

-- ============================================
-- TABELA: CLIENTES
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo_pessoa TEXT NOT NULL CHECK(tipo_pessoa IN ('fisica', 'juridica')),
    documento TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    cep TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ativo' CHECK(status IN ('ativo', 'inativo', 'suspenso')),
    observacoes TEXT,
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_documento ON clientes(documento);
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);
CREATE INDEX IF NOT EXISTS idx_clientes_status ON clientes(status);
CREATE INDEX IF NOT EXISTS idx_clientes_data_cadastro ON clientes(data_cadastro);

-- ============================================
-- TABELA: FUNCIONÁRIOS
-- ============================================
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    cargo TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    cep TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    salario REAL NOT NULL,
    data_admissao DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'ativo' CHECK(status IN ('ativo', 'inativo')),
    observacoes TEXT,
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_funcionarios_cpf ON funcionarios(cpf);
CREATE INDEX IF NOT EXISTS idx_funcionarios_email ON funcionarios(email);
CREATE INDEX IF NOT EXISTS idx_funcionarios_status ON funcionarios(status);

-- ============================================
-- TABELA: FORNECEDORES
-- ============================================
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    nome TEXT NOT NULL UNIQUE,
    cpf_cnpj TEXT NOT NULL UNIQUE,
    nome_fantasia TEXT,
    telefone TEXT NOT NULL,
    email TEXT NOT NULL,
    cep TEXT,
    endereco TEXT,
    numero TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    estado TEXT,
    observacoes TEXT,
    status TEXT DEFAULT 'ativo',
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tipo CHECK (tipo IN ('fisica', 'juridica'))
);

-- Índices para performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_fornecedor_cpf_cnpj ON fornecedores(cpf_cnpj);
CREATE INDEX IF NOT EXISTS idx_fornecedor_tipo ON fornecedores(tipo);
CREATE INDEX IF NOT EXISTS idx_fornecedor_status ON fornecedores(status);

-- ============================================
-- TABELA: LANÇAMENTOS
-- ============================================
CREATE TABLE IF NOT EXISTS lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    tipo TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    subcategoria_id INTEGER NOT NULL,
    valor REAL NOT NULL,
    descricao TEXT NOT NULL,
    cliente_id INTEGER,
    fornecedor_id INTEGER,
    funcionario_id INTEGER,
    banco TEXT,
    nota_fiscal TEXT,
    comprovante TEXT,
    observacao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_lancamentos_data ON lancamentos(data);
CREATE INDEX IF NOT EXISTS idx_lancamentos_tipo ON lancamentos(tipo);
CREATE INDEX IF NOT EXISTS idx_lancamentos_categoria ON lancamentos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_cliente ON lancamentos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_fornecedor ON lancamentos(fornecedor_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_funcionario ON lancamentos(funcionario_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_data_categoria ON lancamentos(data, categoria_id);

-- ============================================
-- TABELA: RESUMO DE SALDO DIÁRIO (Cache)
-- ============================================
CREATE TABLE IF NOT EXISTS saldo_diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL UNIQUE,
    saldo_entrada REAL NOT NULL DEFAULT 0,
    saldo_saida REAL NOT NULL DEFAULT 0,
    saldo_liquido REAL NOT NULL DEFAULT 0,
    data_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índice para acesso rápido
CREATE INDEX IF NOT EXISTS idx_saldo_diario_data ON saldo_diario(data);

-- ============================================
-- TABELA: AUDITORIA
-- ============================================
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabela TEXT NOT NULL,
    operacao TEXT NOT NULL CHECK(operacao IN ('INSERT', 'UPDATE', 'DELETE')),
    registro_id INTEGER NOT NULL,
    dados_anteriores TEXT,
    dados_novos TEXT,
    usuario TEXT,
    data_operacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índice para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_auditoria_tabela ON auditoria(tabela);
CREATE INDEX IF NOT EXISTS idx_auditoria_data ON auditoria(data_operacao);
"""

# Dados de exemplo para testes
DADOS_EXEMPLO = {
    'categorias': [
        {'nome': 'Receitas', 'tipo': 'receita', 'descricao': 'Receitas gerais'},
        {'nome': 'Vendas', 'tipo': 'receita', 'descricao': 'Vendas de produtos/serviços'},
        {'nome': 'Despesas', 'tipo': 'despesa', 'descricao': 'Despesas gerais'},
        {'nome': 'Salários', 'tipo': 'despesa', 'descricao': 'Pagamentos de salários'},
    ],
    'subcategorias': [
        {'categoria_id': 1, 'nome': 'Vendas Diretas', 'descricao': 'Vendas diretas ao cliente'},
        {'categoria_id': 1, 'nome': 'Comissões', 'descricao': 'Comissões recebidas'},
        {'categoria_id': 2, 'nome': 'Produtos', 'descricao': 'Vendas de produtos'},
        {'categoria_id': 2, 'nome': 'Serviços', 'descricao': 'Prestação de serviços'},
        {'categoria_id': 3, 'nome': 'Aluguel', 'descricao': 'Pagamento de aluguel'},
        {'categoria_id': 3, 'nome': 'Contas', 'descricao': 'Contas básicas'},
        {'categoria_id': 4, 'nome': 'Funcionários', 'descricao': 'Salários de funcionários'},
    ]
}

