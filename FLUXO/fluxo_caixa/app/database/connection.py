from app.database.database import Database
from app.database.schema_unificado import CRIAR_TABELAS_SQL


def init_db(db_path=None):
    db = Database(db_path=db_path)
    db.executar_script(CRIAR_TABELAS_SQL)
    return db

    

