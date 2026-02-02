"""
Database - Gerencia conexão e operações com SQLite
Schema completo com categorias, subcategorias e relacionamentos
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config.settings import Settings

DATABASE_PATH = Path(Settings.get_database_path())


class Database:
    """Gerencia conexão e operações com SQLite"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DATABASE_PATH
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        """Cria tabelas usando schema unificado"""
        from app.database.schema_unificado import CRIAR_TABELAS_SQL

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Executa o schema unificado completo
            cursor.executescript(CRIAR_TABELAS_SQL)
            conn.commit()
            print(f"[OK] Base de dados inicializada com schema unificado em: {self.db_path}")
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao inicializar banco de dados: {e}")
        finally:
            conn.close()

    def get_connection(self):
        """Retorna conexão com banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def executar_script(self, script: str) -> None:
        """Executa script SQL completo (multiplas instrucoes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executescript(script)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao executar script: {e}")
        finally:
            conn.close()

    def registrar_auditoria(
        self,
        tabela: str,
        operacao: str,
        registro_id: Optional[int] = None,
        dados_anteriores: Optional[Dict] = None,
        dados_novos: Optional[Dict] = None,
        usuario: Optional[str] = None,
    ) -> None:
        """Registra operacao de auditoria"""
        query = """
            INSERT INTO auditoria (tabela, operacao, registro_id, dados_anteriores, dados_novos, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            tabela,
            operacao,
            registro_id,
            json.dumps(dados_anteriores, ensure_ascii=False) if dados_anteriores else None,
            json.dumps(dados_novos, ensure_ascii=False) if dados_novos else None,
            usuario,
        )
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao registrar auditoria: {e}")
        finally:
            conn.close()

    def backup(self, caminho_destino) -> Path:
        """Cria backup do banco de dados"""
        destino = Path(caminho_destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as origem:
            with sqlite3.connect(destino) as alvo:
                origem.backup(alvo)
        return destino

    def limpar_tudo(self) -> None:
        """Limpa apenas os lancamentos (compatibilidade)"""
        self.deletar("DELETE FROM lancamentos")

    def executar(self, query: str, params: tuple = ()) -> Any:
        """Executa query e retorna resultado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            return result
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao executar query: {e}")
        finally:
            conn.close()

    def obter_um(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Executa query e retorna um resultado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
        except sqlite3.Error as e:
            raise Exception(f"Erro ao obter dados: {e}")
        finally:
            conn.close()

    def executar_um(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Compatibilidade: retorna um Ãºnico registro"""
        return self.obter_um(query, params)

    def obter_todos(self, query: str, params: tuple = ()) -> List[Dict]:
        """Executa query e retorna todos os resultados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            raise Exception(f"Erro ao obter dados: {e}")
        finally:
            conn.close()

    def inserir(self, query: str, params: tuple = ()) -> int:
        """Insere dados e retorna o ID da linha"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao inserir: {e}")
        finally:
            conn.close()

    def atualizar(self, query: str, params: tuple = ()) -> int:
        """Atualiza dados e retorna número de linhas afetadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar: {e}")
        finally:
            conn.close()

    def deletar(self, query: str, params: tuple = ()) -> int:
        """Deleta dados e retorna número de linhas afetadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erro ao deletar: {e}")
        finally:
            conn.close()

