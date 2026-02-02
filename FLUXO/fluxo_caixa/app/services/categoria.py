"""
Serviço de Categorias e Subcategorias
Gerencia operações CRUD e relacionamentos
"""
from typing import List, Dict, Optional
from app.models.categoria import Categoria, Subcategoria, TipoCategoria, CATEGORIAS_PADRAO
from app.database.database import Database


class ServicoCategoria:
    """Gerencia operações com categorias"""

    def __init__(self, db: Database):
        self.db = db
        self._inicializar_categorias_padrao()

    def _inicializar_categorias_padrao(self):
        """Cria categorias padrão se não existirem"""
        try:
            # Verifica se já existe alguma categoria
            resultado = self.db.obter_um("SELECT COUNT(*) as total FROM categorias")
            if resultado and resultado['total'] > 0:
                return  # Já tem categorias
            
            # Insere categorias padrão
            for cat_data in CATEGORIAS_PADRAO:
                cat_id = self.criar_categoria(
                    nome=cat_data['nome'],
                    tipo=cat_data['tipo'],
                    descricao=cat_data['descricao']
                )
                
                # Insere subcategorias
                for subcat_data in cat_data['subcategorias']:
                    self.criar_subcategoria(
                        nome=subcat_data['nome'],
                        categoria_id=cat_id,
                        descricao=subcat_data['descricao']
                    )
        except Exception as e:
            print(f"Aviso ao inicializar categorias: {e}")

    def criar_categoria(self, nome: str, tipo: TipoCategoria, descricao: str = "") -> int:
        """Cria nova categoria"""
        query = '''
            INSERT INTO categorias (nome, tipo, descricao, ativo)
            VALUES (?, ?, ?, 1)
        '''
        params = (nome, tipo.value, descricao)
        return self.db.inserir(query, params)

    def obter_categoria(self, id: int) -> Optional[Categoria]:
        """Obtém categoria por ID"""
        query = "SELECT * FROM categorias WHERE id = ?"
        resultado = self.db.obter_um(query, (id,))
        if resultado:
            return Categoria(
                id=resultado['id'],
                nome=resultado['nome'],
                tipo=TipoCategoria(resultado['tipo']),
                descricao=resultado['descricao'],
                ativo=bool(resultado['ativo'])
            )
        return None

    def obter_todas_categorias(self, apenas_ativas: bool = True) -> List[Categoria]:
        """Obtém todas as categorias"""
        where = "WHERE ativo = 1" if apenas_ativas else ""
        query = f"SELECT * FROM categorias {where} ORDER BY nome"
        resultados = self.db.obter_todos(query)
        
        categorias = []
        for row in resultados:
            categorias.append(Categoria(
                id=row['id'],
                nome=row['nome'],
                tipo=TipoCategoria(row['tipo']),
                descricao=row['descricao'],
                ativo=bool(row['ativo'])
            ))
        return categorias

    def obter_categorias_por_tipo(self, tipo: TipoCategoria) -> List[Categoria]:
        """Obtém categorias filtradas por tipo"""
        query = "SELECT * FROM categorias WHERE tipo = ? AND ativo = 1 ORDER BY nome"
        resultados = self.db.obter_todos(query, (tipo.value,))
        
        categorias = []
        for row in resultados:
            categorias.append(Categoria(
                id=row['id'],
                nome=row['nome'],
                tipo=TipoCategoria(row['tipo']),
                descricao=row['descricao'],
                ativo=bool(row['ativo'])
            ))
        return categorias

    def atualizar_categoria(self, id: int, nome: str = None, descricao: str = None) -> bool:
        """Atualiza categoria"""
        updates = []
        params = []
        
        if nome:
            updates.append("nome = ?")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = ?")
            params.append(descricao)
        
        if not updates:
            return False
        
        params.append(id)
        query = f"UPDATE categorias SET {', '.join(updates)} WHERE id = ?"
        return self.db.atualizar(query, tuple(params)) > 0

    def deletar_categoria(self, id: int) -> bool:
        """Deleta categoria e subcategorias associadas"""
        query = "DELETE FROM categorias WHERE id = ?"
        return self.db.deletar(query, (id,)) > 0

    # Operações com Subcategorias

    def criar_subcategoria(self, nome: str, categoria_id: int, descricao: str = "") -> int:
        """Cria nova subcategoria"""
        query = '''
            INSERT INTO subcategorias (nome, categoria_id, descricao, ativo)
            VALUES (?, ?, ?, 1)
        '''
        params = (nome, categoria_id, descricao)
        return self.db.inserir(query, params)

    def obter_subcategoria(self, id: int) -> Optional[Subcategoria]:
        """Obtém subcategoria por ID"""
        query = "SELECT * FROM subcategorias WHERE id = ?"
        resultado = self.db.obter_um(query, (id,))
        if resultado:
            return Subcategoria(
                id=resultado['id'],
                nome=resultado['nome'],
                categoria_id=resultado['categoria_id'],
                descricao=resultado['descricao'],
                ativo=bool(resultado['ativo'])
            )
        return None

    def obter_subcategorias_da_categoria(self, categoria_id: int, apenas_ativas: bool = True) -> List[Subcategoria]:
        """Obtém subcategorias de uma categoria"""
        where = "AND ativo = 1" if apenas_ativas else ""
        query = f"SELECT * FROM subcategorias WHERE categoria_id = ? {where} ORDER BY nome"
        resultados = self.db.obter_todos(query, (categoria_id,))
        
        subcategorias = []
        for row in resultados:
            subcategorias.append(Subcategoria(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                descricao=row['descricao'],
                ativo=bool(row['ativo'])
            ))
        return subcategorias

    def obter_todas_subcategorias(self, apenas_ativas: bool = True) -> List[Subcategoria]:
        """Obtém todas as subcategorias"""
        where = "WHERE ativo = 1" if apenas_ativas else ""
        query = f"SELECT * FROM subcategorias {where} ORDER BY nome"
        resultados = self.db.obter_todos(query)
        
        subcategorias = []
        for row in resultados:
            subcategorias.append(Subcategoria(
                id=row['id'],
                nome=row['nome'],
                categoria_id=row['categoria_id'],
                descricao=row['descricao'],
                ativo=bool(row['ativo'])
            ))
        return subcategorias

    def atualizar_subcategoria(self, id: int, nome: str = None, descricao: str = None) -> bool:
        """Atualiza subcategoria"""
        updates = []
        params = []
        
        if nome:
            updates.append("nome = ?")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = ?")
            params.append(descricao)
        
        if not updates:
            return False
        
        params.append(id)
        query = f"UPDATE subcategorias SET {', '.join(updates)} WHERE id = ?"
        return self.db.atualizar(query, tuple(params)) > 0

    def deletar_subcategoria(self, id: int) -> bool:
        """Deleta subcategoria"""
        query = "DELETE FROM subcategorias WHERE id = ?"
        return self.db.deletar(query, (id,)) > 0

