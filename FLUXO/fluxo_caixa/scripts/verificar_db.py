#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar banco de dados"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import Database

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()

print("=" * 60)
print("VERIFICACAO DO BANCO DE DADOS")
print("=" * 60)
print(f"\nTabelas criadas: {len(tabelas)}")
for t in tabelas:
    print(f"  [OK] {t[0]}")
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"    Registros: {count}")

print("\n" + "=" * 60)
print("[OK] Banco de dados verificado com sucesso!")
print("=" * 60)

conn.close()

