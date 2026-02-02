#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para validar schema SQL"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.schema_unificado import CRIAR_TABELAS_SQL
import sqlite3

# Criar banco de dados temporário
test_db = Path('test_db.db')
if test_db.exists():
    test_db.unlink()

conn = sqlite3.connect(test_db)
cursor = conn.cursor()

# Tentar executar o schema
print("=" * 60)
print("VALIDANDO SCHEMA SQL")
print("=" * 60)
print("\nSQL a executar:")
print(CRIAR_TABELAS_SQL[:500])
print("...")

try:
    # Tentar executar como script
    cursor.executescript(CRIAR_TABELAS_SQL)
    conn.commit()
    print("\n✓ Schema executado com sucesso!")
    
    # Listar tabelas criadas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    print(f"\nTabelas criadas ({len(tabelas)}):")
    for t in tabelas:
        print(f"  - {t[0]}")
        
except Exception as e:
    print(f"\n✗ Erro: {e}")
    print(f"Tipo: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
finally:
    conn.close()
    test_db.unlink()
    print("\n✓ Teste finalizado")

