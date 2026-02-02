#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migração - Fluxo de Caixa com Categorias
Migra dados do banco antigo para o novo schema
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/fluxo_caixa.db")

print("=" * 70)
print("MIGRAÇÃO - NOVO SCHEMA DE FLUXO DE CAIXA")
print("=" * 70)

try:
    if not DB_PATH.exists():
        print(f"\n✓ Banco não existe, será criado novo em {DB_PATH}")
    else:
        print(f"\n[1] Fazendo backup do banco...")
        import shutil
        backup_path = DB_PATH.parent / "fluxo_caixa.db.bak"
        shutil.copy(DB_PATH, backup_path)
        print(f"    ✓ Backup criado: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n[2] Criando tabelas de categorias...")
    
    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("    ✓ Tabela 'categorias' criada")
    
    # Tabela de Subcategorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE,
            UNIQUE(categoria_id, nome)
        )
    ''')
    print("    ✓ Tabela 'subcategorias' criada")
    
    print("\n[3] Migrando tabela 'lancamentos'...")
    
    # Verifica se tabela antiga existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lancamentos'")
    if cursor.fetchone():
        print("    ✓ Tabela 'lancamentos' encontrada")
        
        # Verifica schema atual
        cursor.execute("PRAGMA table_info(lancamentos)")
        colunas = [col[1] for col in cursor.fetchall()]
        print(f"    Colunas atuais: {', '.join(colunas[:7])}...")
        
        # Se não tiver categoria_id, adiciona as novas colunas
        if 'categoria_id' not in colunas:
            print("⚠ Adicionando novas colunas...")
            
            if 'categoria_id' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN categoria_id INTEGER")
            if 'subcategoria_id' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN subcategoria_id INTEGER")
            if 'fornecedor_id' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN fornecedor_id INTEGER")
            if 'funcionario_id' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN funcionario_id INTEGER")
            if 'comprovante' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN comprovante TEXT")
            if 'nota_fiscal' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN nota_fiscal TEXT")
            if 'banco' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN banco TEXT")
            if 'atualizado_em' not in colunas:
                cursor.execute("ALTER TABLE lancamentos ADD COLUMN atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            print("    ✓ Novas colunas adicionadas")
    else:
        print("    ℹ Tabela 'lancamentos' não existe, será criada nova")
        
        # Cria tabela nova
        cursor.execute('''
            CREATE TABLE lancamentos (
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
            )
        ''')
    
    print("\n[4] Inserindo categorias padrão...")
    
    categorias_padrao = [
        {
            "nome": "Receita",
            "tipo": "Receita",
            "descricao": "Entradas de dinheiro",
            "subcategorias": ["Serviços", "Produtos", "Investimentos", "Empréstimos", "Outras"]
        },
        {
            "nome": "Despesa Variável",
            "tipo": "Despesa Variável",
            "descricao": "Despesas que variam conforme a operação",
            "subcategorias": ["Insumos", "Mão de Obra", "Fornecimentos", "Transportes", "Outras"]
        },
        {
            "nome": "Despesa Fixa",
            "tipo": "Despesa Fixa",
            "descricao": "Despesas que se repetem regularmente",
            "subcategorias": ["Energia", "Água", "Internet", "Contador", "Seguro", "Outras"]
        },
        {
            "nome": "Despesa Pessoal",
            "tipo": "Despesa Pessoal",
            "descricao": "Despesas pessoais do proprietário",
            "subcategorias": ["Educação", "Saúde", "Alimentação", "Lazer", "Cartão de Crédito", "Outras"]
        }
    ]
    
    for cat_data in categorias_padrao:
        try:
            cursor.execute(
                "INSERT INTO categorias (nome, tipo, descricao) VALUES (?, ?, ?)",
                (cat_data["nome"], cat_data["tipo"], cat_data["descricao"])
            )
            cat_id = cursor.lastrowid
            print(f"    ✓ Categoria '{cat_data['nome']}' inserida")
            
            for subcat_nome in cat_data["subcategorias"]:
                cursor.execute(
                    "INSERT INTO subcategorias (nome, categoria_id, descricao) VALUES (?, ?, ?)",
                    (subcat_nome, cat_id, "")
                )
            print(f"      + {len(cat_data['subcategorias'])} subcategorias adicionadas")
        except sqlite3.IntegrityError:
            print(f"    ℹ Categoria '{cat_data['nome']}' já existe")
    
    print("\n[5] Criando índices...")
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_data ON lancamentos(data)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_tipo ON lancamentos(tipo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_categoria_id ON lancamentos(categoria_id)')
        if 'subcategoria_id' in colunas:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_subcategoria ON lancamentos(subcategoria_id)')
        if 'cliente_id' in colunas:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_cliente ON lancamentos(cliente_id)')
        if 'fornecedor_id' in colunas:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lancamentos_fornecedor ON lancamentos(fornecedor_id)')
    except Exception as e:
        print(f"    ⚠ Alguns índices não puderam ser criados: {e}")
    print("✓ Índices criados")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"Banco de dados: {DB_PATH}")
    print("=" * 70)

except Exception as e:
    print(f"\n✗ ERRO DURANTE A MIGRAÇÃO: {str(e)}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)
