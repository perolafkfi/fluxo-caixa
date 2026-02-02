"""
Serviço de Lançamentos Financeiros
Gerencia CRUD e operações complexas com lançamentos
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.models.lancamento import Lancamento, TipoLancamento
from app.database.database import Database


class ServicoLancamento:
    """Gerencia operações com lançamentos financeiros"""

    def __init__(self, db: Database):
        self.db = db

    def criar(self, lancamento: Lancamento) -> Tuple[bool, str]:
        """Cria novo lançamento usando categoria_id com foreign key"""
        # Validação básica dos dados obrigatórios
        if not lancamento.data:
            return False, "Data é obrigatória"
        if not lancamento.tipo:
            return False, "Tipo é obrigatório"
        if lancamento.valor <= 0:
            return False, "Valor deve ser maior que zero"
        if not lancamento.descricao:
            return False, "Descrição é obrigatória"
        if not lancamento.categoria_id or lancamento.categoria_id <= 0:
            return False, "Categoria é obrigatória"
        if not lancamento.subcategoria_id or lancamento.subcategoria_id <= 0:
            return False, "Subcategoria é obrigatória"

        try:
            # Query usando categoria_id e subcategoria_id com foreign keys
            query = '''
                INSERT INTO lancamentos (
                    data, tipo, categoria_id, subcategoria_id, valor, descricao,
                    cliente_id, fornecedor_id, funcionario_id, banco, nota_fiscal,
                    comprovante, observacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            params = (
                lancamento.data,
                lancamento.tipo.value if hasattr(lancamento.tipo, 'value') else str(lancamento.tipo),
                lancamento.categoria_id,
                lancamento.subcategoria_id,
                lancamento.valor,
                lancamento.descricao,
                lancamento.cliente_id,
                lancamento.fornecedor_id,
                lancamento.funcionario_id,
                lancamento.banco or '',
                lancamento.nota_fiscal or '',
                lancamento.comprovante or '',
                lancamento.observacao or '',
            )

            lancamento_id = self.db.inserir(query, params)
            return True, f"Lançamento criado com sucesso (ID: {lancamento_id})"

        except Exception as e:
            return False, f"Erro ao criar lançamento: {str(e)}"

    def obter(self, id: int) -> Optional[Lancamento]:
        """Obtém lançamento por ID"""
        query = "SELECT * FROM lancamentos WHERE id = ?"
        resultado = self.db.obter_um(query, (id,))
        return self._converter_para_lancamento(resultado) if resultado else None

    def obter_todos(self) -> List[Lancamento]:
        """Obtém todos os lançamentos"""
        query = "SELECT * FROM lancamentos ORDER BY data DESC"
        resultados = self.db.obter_todos(query)
        return [self._converter_para_lancamento(row) for row in resultados]

    def obter_por_periodo(self, data_inicio: str, data_fim: str) -> List[Lancamento]:
        """Obtém lançamentos em período específico"""
        query = '''
            SELECT * FROM lancamentos 
            WHERE data BETWEEN ? AND ? 
            ORDER BY data DESC
        '''
        resultados = self.db.obter_todos(query, (data_inicio, data_fim))
        return [self._converter_para_lancamento(row) for row in resultados]

    def obter_por_tipo(self, tipo: TipoLancamento) -> List[Lancamento]:
        """Obtém lançamentos por tipo"""
        query = "SELECT * FROM lancamentos WHERE tipo = ? ORDER BY data DESC"
        resultados = self.db.obter_todos(query, (tipo.value,))
        return [self._converter_para_lancamento(row) for row in resultados]

    def obter_por_categoria(self, categoria_id: int) -> List[Lancamento]:
        """Obtém lançamentos por categoria"""
        query = "SELECT * FROM lancamentos WHERE categoria_id = ? ORDER BY data DESC"
        resultados = self.db.obter_todos(query, (categoria_id,))
        return [self._converter_para_lancamento(row) for row in resultados]

    def obter_por_cliente(self, cliente_id: int) -> List[Lancamento]:
        """Obtém receitas de um cliente"""
        query = '''
            SELECT * FROM lancamentos 
            WHERE cliente_id = ? AND tipo = ?
            ORDER BY data DESC
        '''
        resultados = self.db.obter_todos(query, (cliente_id, TipoLancamento.RECEITA.value))
        return [self._converter_para_lancamento(row) for row in resultados]

    def obter_por_fornecedor(self, fornecedor_id: int) -> List[Lancamento]:
        """Obtém despesas de um fornecedor"""
        query = '''
            SELECT * FROM lancamentos 
            WHERE fornecedor_id = ? AND tipo = ?
            ORDER BY data DESC
        '''
        resultados = self.db.obter_todos(query, (fornecedor_id, TipoLancamento.DESPESA.value))
        return [self._converter_para_lancamento(row) for row in resultados]

    def buscar(self, filtros: Dict = None) -> List[Lancamento]:
        """Busca lançamentos com múltiplos filtros"""
        query = "SELECT * FROM lancamentos WHERE 1=1"
        params = []

        if filtros:
            if filtros.get('data_inicio'):
                query += " AND data >= ?"
                params.append(filtros['data_inicio'])
            
            if filtros.get('data_fim'):
                query += " AND data <= ?"
                params.append(filtros['data_fim'])
            
            if filtros.get('tipo'):
                query += " AND tipo = ?"
                params.append(filtros['tipo'])
            
            if filtros.get('categoria_id'):
                query += " AND categoria_id = ?"
                params.append(filtros['categoria_id'])
            
            if filtros.get('cliente_id'):
                query += " AND cliente_id = ?"
                params.append(filtros['cliente_id'])
            
            if filtros.get('fornecedor_id'):
                query += " AND fornecedor_id = ?"
                params.append(filtros['fornecedor_id'])
            
            if filtros.get('descricao'):
                query += " AND descricao LIKE ?"
                params.append(f"%{filtros['descricao']}%")

        query += " ORDER BY data DESC"
        resultados = self.db.obter_todos(query, tuple(params))
        return [self._converter_para_lancamento(row) for row in resultados]

    def atualizar(self, id: int, lancamento: Lancamento) -> Tuple[bool, str]:
        """Atualiza lançamento existente"""
        valido, erros = lancamento.validar()
        if not valido:
            return False, "\n".join(erros)

        try:
            query = '''
                UPDATE lancamentos SET
                    data = ?, tipo = ?, categoria_id = ?, subcategoria_id = ?,
                    valor = ?, descricao = ?, cliente_id = ?, fornecedor_id = ?,
                    funcionario_id = ?, banco = ?, nota_fiscal = ?, comprovante = ?,
                    observacao = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            '''
            params = (
                lancamento.data,
                lancamento.tipo.value,
                lancamento.categoria_id,
                lancamento.subcategoria_id,
                lancamento.valor,
                lancamento.descricao,
                lancamento.cliente_id,
                lancamento.fornecedor_id,
                lancamento.funcionario_id,
                lancamento.banco,
                lancamento.nota_fiscal,
                lancamento.comprovante,
                lancamento.observacao,
                id,
            )
            self.db.atualizar(query, params)
            return True, f"Lançamento {id} atualizado com sucesso"
        except Exception as e:
            return False, f"Erro ao atualizar lançamento: {str(e)}"

    def deletar(self, id: int) -> Tuple[bool, str]:
        """Deleta lançamento"""
        try:
            query = "DELETE FROM lancamentos WHERE id = ?"
            self.db.deletar(query, (id,))
            return True, f"Lançamento {id} deletado com sucesso"
        except Exception as e:
            return False, f"Erro ao deletar lançamento: {str(e)}"

    # Operações de relatório e análise

    def calcular_total_receitas(self, filtros: Dict = None) -> float:
        """Calcula total de receitas"""
        query = '''
            SELECT COALESCE(SUM(valor), 0) as total
            FROM lancamentos
            WHERE tipo = ?
        '''
        params = [TipoLancamento.RECEITA.value]

        if filtros:
            if filtros.get('data_inicio'):
                query += " AND data >= ?"
                params.append(filtros['data_inicio'])
            if filtros.get('data_fim'):
                query += " AND data <= ?"
                params.append(filtros['data_fim'])
            if filtros.get('categoria_id'):
                query += " AND categoria_id = ?"
                params.append(filtros['categoria_id'])

        resultado = self.db.obter_um(query, tuple(params))
        return float(resultado['total']) if resultado else 0.0

    def calcular_total_despesas(self, filtros: Dict = None) -> float:
        """Calcula total de despesas"""
        query = '''
            SELECT COALESCE(SUM(valor), 0) as total
            FROM lancamentos
            WHERE tipo = ?
        '''
        params = [TipoLancamento.DESPESA.value]

        if filtros:
            if filtros.get('data_inicio'):
                query += " AND data >= ?"
                params.append(filtros['data_inicio'])
            if filtros.get('data_fim'):
                query += " AND data <= ?"
                params.append(filtros['data_fim'])
            if filtros.get('categoria_id'):
                query += " AND categoria_id = ?"
                params.append(filtros['categoria_id'])

        resultado = self.db.obter_um(query, tuple(params))
        return float(resultado['total']) if resultado else 0.0

    def calcular_saldo(self, filtros: Dict = None) -> float:
        """Calcula saldo (receitas - despesas)"""
        receitas = self.calcular_total_receitas(filtros)
        despesas = self.calcular_total_despesas(filtros)
        return receitas - despesas

    def obter_totais_por_categoria(self, tipo: TipoLancamento, filtros: Dict = None) -> Dict[str, float]:
        """Retorna totais agrupados por categoria"""
        query = '''
            SELECT 
                c.nome as categoria,
                COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            LEFT JOIN categorias c ON l.categoria_id = c.id
            WHERE l.tipo = ?
        '''
        params = [tipo.value]

        if filtros:
            if filtros.get('data_inicio'):
                query += " AND l.data >= ?"
                params.append(filtros['data_inicio'])
            if filtros.get('data_fim'):
                query += " AND l.data <= ?"
                params.append(filtros['data_fim'])

        query += " GROUP BY c.id ORDER BY total DESC"

        resultados = self.db.obter_todos(query, tuple(params))
        return {row['categoria']: float(row['total']) for row in resultados}

    def obter_totais_por_subcategoria(self, tipo: TipoLancamento, filtros: Dict = None) -> Dict[str, float]:
        """Retorna totais agrupados por subcategoria"""
        query = '''
            SELECT 
                s.nome as subcategoria,
                COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            LEFT JOIN subcategorias s ON l.subcategoria_id = s.id
            WHERE l.tipo = ?
        '''
        params = [tipo.value]

        if filtros:
            if filtros.get('data_inicio'):
                query += " AND l.data >= ?"
                params.append(filtros['data_inicio'])
            if filtros.get('data_fim'):
                query += " AND l.data <= ?"
                params.append(filtros['data_fim'])
            if filtros.get('categoria_id'):
                query += " AND l.categoria_id = ?"
                params.append(filtros['categoria_id'])

        query += " GROUP BY s.id ORDER BY total DESC"

        resultados = self.db.obter_todos(query, tuple(params))
        return {row['subcategoria']: float(row['total']) for row in resultados}

    def obter_movimentacao_diaria(self, data_inicio: str, data_fim: str) -> Dict[str, float]:
        """Retorna movimentação por dia"""
        query = '''
            SELECT 
                DATE(data) as data,
                COALESCE(SUM(CASE WHEN tipo = ? THEN valor ELSE 0 END), 0) as receitas,
                COALESCE(SUM(CASE WHEN tipo = ? THEN valor ELSE 0 END), 0) as despesas
            FROM lancamentos
            WHERE data BETWEEN ? AND ?
            GROUP BY DATE(data)
            ORDER BY data
        '''
        params = (TipoLancamento.RECEITA.value, TipoLancamento.DESPESA.value, data_inicio, data_fim)
        resultados = self.db.obter_todos(query, params)
        
        movimentacao = {}
        for row in resultados:
            saldo = row['receitas'] - row['despesas']
            movimentacao[row['data']] = {
                'receitas': float(row['receitas']),
                'despesas': float(row['despesas']),
                'saldo': saldo
            }
        return movimentacao

    def _converter_para_lancamento(self, row: Dict) -> Lancamento:
        """Converte linha do DB para objeto Lancamento"""
        if not row:
            return None

        return Lancamento(
            id=row['id'],
            data=row['data'],
            tipo=TipoLancamento(row['tipo']),
            categoria_id=row['categoria_id'],
            subcategoria_id=row['subcategoria_id'],
            valor=float(row['valor']),
            descricao=row['descricao'],
            cliente_id=row['cliente_id'],
            fornecedor_id=row['fornecedor_id'],
            funcionario_id=row['funcionario_id'],
            banco=row['banco'] or '',
            nota_fiscal=row['nota_fiscal'] or '',
            comprovante=row['comprovante'] or '',
            observacao=row['observacao'] or '',
            criado_em=row['criado_em'],
            atualizado_em=row['atualizado_em'],
        )

    def _obter_categorias_disponiveis(self) -> List[str]:
        """Retorna lista de categorias disponíveis"""
        # Categorias padrão do sistema
        return [
            'Receitas', 'Vendas', 'Serviços', 'Aluguéis',
            'Despesas', 'Insumos', 'Salários', 'Aluguel',
            'Contas', 'Impostos', 'Manutenção', 'Outros'
        ]

    def _mapear_categoria_id_para_nome(self, categoria_id: int) -> str:
        """Mapeia categoria_id para nome da categoria (compatibilidade)"""
        # Mapeamento simples para compatibilidade
        mapeamento = {
            1: 'Receitas',
            2: 'Vendas',
            3: 'Serviços',
            4: 'Despesas',
            5: 'Insumos',
            6: 'Salários'
        }
        return mapeamento.get(categoria_id, 'Outros')

