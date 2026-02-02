"""
Serviço de Fornecedores - Sistema de Fluxo de Caixa
CRUD completo com validações
"""
from typing import List, Optional
from app.models.fornecedor import Fornecedor, TipoPessoa
from app.database.connection import Database


class ServicoFornecedor:
    """Serviço de fornecedores"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def criar_tabela(self) -> None:
        """Cria tabela de fornecedores se não existir"""
        sql = """
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
            )
        """
        self.db.executar(sql)

    def criar_indice_cpf_cnpj(self) -> None:
        """Cria índice para CPF/CNPJ para melhor performance"""
        sql = "CREATE INDEX IF NOT EXISTS idx_fornecedor_cpf_cnpj ON fornecedores(cpf_cnpj)"
        self.db.executar(sql)
    
    def criar(self, fornecedor: Fornecedor) -> int:
        """Cria novo fornecedor"""
        fornecedor.validar()
        
        # Verificar duplicata
        if self.obter_por_cpf_cnpj(fornecedor.cpf_cnpj):
            raise ValueError(f"Fornecedor com CPF/CNPJ {fornecedor.cpf_cnpj} já existe")
        
        sql = """
            INSERT INTO fornecedores (
                tipo, nome, cpf_cnpj, nome_fantasia, telefone, email,
                cep, endereco, numero, complemento, bairro, cidade,
                estado, observacoes, status, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            fornecedor.tipo.value,
            fornecedor.nome,
            fornecedor.cpf_cnpj,
            fornecedor.nome_fantasia,
            fornecedor.telefone,
            fornecedor.email,
            fornecedor.cep,
            fornecedor.endereco,
            fornecedor.numero,
            fornecedor.complemento,
            fornecedor.bairro,
            fornecedor.cidade,
            fornecedor.estado,
            fornecedor.observacoes,
            fornecedor.status,
            fornecedor.data_cadastro
        )
        
        return self.db.inserir(sql, params)
    
    def obter_por_id(self, fornecedor_id: int) -> Optional[Fornecedor]:
        """Obtém fornecedor por ID"""
        sql = "SELECT * FROM fornecedores WHERE id = ?"
        resultado = self.db.executar_um(sql, (fornecedor_id,))

        if resultado:
            return self._mapear_para_fornecedor(resultado)
        return None

    def obter_por_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Fornecedor]:
        """Obtém fornecedor por CPF/CNPJ"""
        sql = "SELECT * FROM fornecedores WHERE cpf_cnpj = ?"
        resultado = self.db.executar_um(sql, (cpf_cnpj,))

        if resultado:
            return self._mapear_para_fornecedor(resultado)
        return None
    
    def listar_todos(self, apenas_ativos: bool = True) -> List[Fornecedor]:
        """Lista todos os fornecedores"""
        if apenas_ativos:
            sql = "SELECT * FROM fornecedores WHERE status = 'ativo' ORDER BY nome"
        else:
            sql = "SELECT * FROM fornecedores ORDER BY nome"
        
        resultados = self.db.executar(sql)
        return [self._mapear_para_fornecedor(r) for r in resultados]
    
    def listar_por_tipo(self, tipo: TipoPessoa, apenas_ativos: bool = True) -> List[Fornecedor]:
        """Lista fornecedores por tipo"""
        if apenas_ativos:
            sql = "SELECT * FROM fornecedores WHERE tipo = ? AND status = 'ativo' ORDER BY nome"
        else:
            sql = "SELECT * FROM fornecedores WHERE tipo = ? ORDER BY nome"
        
        resultados = self.db.executar(sql, (tipo.value,))
        return [self._mapear_para_fornecedor(r) for r in resultados]
    
    def atualizar(self, fornecedor: Fornecedor) -> bool:
        """Atualiza fornecedor"""
        if not fornecedor.id:
            raise ValueError("Fornecedor deve ter ID para atualizar")
        
        fornecedor.validar()
        
        sql = """
            UPDATE fornecedores SET
                tipo = ?, nome = ?, cpf_cnpj = ?, nome_fantasia = ?,
                telefone = ?, email = ?, cep = ?, endereco = ?,
                numero = ?, complemento = ?, bairro = ?, cidade = ?,
                estado = ?, observacoes = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        params = (
            fornecedor.tipo.value,
            fornecedor.nome,
            fornecedor.cpf_cnpj,
            fornecedor.nome_fantasia,
            fornecedor.telefone,
            fornecedor.email,
            fornecedor.cep,
            fornecedor.endereco,
            fornecedor.numero,
            fornecedor.complemento,
            fornecedor.bairro,
            fornecedor.cidade,
            fornecedor.estado,
            fornecedor.observacoes,
            fornecedor.status,
            fornecedor.id
        )
        
        return self.db.atualizar(sql, params) > 0
    
    def deletar(self, fornecedor_id: int) -> bool:
        """Deleta fornecedor"""
        sql = "DELETE FROM fornecedores WHERE id = ?"
        return self.db.deletar(sql, (fornecedor_id,)) > 0
    
    def inativar(self, fornecedor_id: int) -> bool:
        """Inativa fornecedor"""
        sql = "UPDATE fornecedores SET status = 'inativo', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.atualizar(sql, (fornecedor_id,)) > 0
    
    def ativar(self, fornecedor_id: int) -> bool:
        """Ativa fornecedor"""
        sql = "UPDATE fornecedores SET status = 'ativo', updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        return self.db.atualizar(sql, (fornecedor_id,)) > 0
    
    def buscar_por_nome(self, nome: str) -> List[Fornecedor]:
        """Busca fornecedores por nome (busca parcial)"""
        sql = "SELECT * FROM fornecedores WHERE nome LIKE ? ORDER BY nome"
        resultados = self.db.executar(sql, (f"%{nome}%",))
        return [self._mapear_para_fornecedor(r) for r in resultados]
    
    def contar(self) -> int:
        """Conta total de fornecedores"""
        sql = "SELECT COUNT(*) as total FROM fornecedores"
        resultado = self.db.executar_um(sql)
        return resultado['total'] if resultado else 0

    def contar_ativos(self) -> int:
        """Conta fornecedores ativos"""
        sql = "SELECT COUNT(*) as total FROM fornecedores WHERE status = 'ativo'"
        resultado = self.db.executar_um(sql)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def _mapear_para_fornecedor(row) -> Fornecedor:
        """Mapeia linha do banco para objeto Fornecedor"""
        from datetime import datetime

        return Fornecedor(
            id=row['id'],
            tipo=TipoPessoa(row['tipo']),
            nome=row['nome'],
            cpf_cnpj=row['cpf_cnpj'],
            nome_fantasia=row['nome_fantasia'],
            telefone=row['telefone'],
            email=row['email'],
            cep=row['cep'],
            endereco=row['endereco'],
            numero=row['numero'],
            complemento=row['complemento'],
            bairro=row['bairro'],
            cidade=row['cidade'],
            estado=row['estado'],
            observacoes=row['observacoes'],
            status=row['status'],
            data_cadastro=datetime.fromisoformat(row['data_cadastro']) if isinstance(row['data_cadastro'], str) else row['data_cadastro']
        )

