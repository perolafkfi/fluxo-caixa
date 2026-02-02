"""
Serviço de Clientes
Responsável por operações CRUD de clientes
"""
from typing import List, Tuple, Optional
from app.models.cliente import Cliente, TipoPessoa, StatusCliente
from app.database.connection import Database
from app.utils.validators import ValidadorCEP
from datetime import datetime


class ServicoCliente:
    """CRUD completo para clientes"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def criar(self, cliente: Cliente) -> Tuple[bool, str]:
        """
        Cria novo cliente
        
        Args:
            cliente: Objeto Cliente
            
        Returns:
            (sucesso, mensagem)
        """
        # Valida cliente
        valido, erros = cliente.validar()
        if not valido:
            return False, "\n".join(erros)
        
        # Verifica duplicidade de documento
        existente = self.db.executar_um(
            "SELECT id FROM clientes WHERE documento = ?",
            (cliente.documento,)
        )
        if existente:
            return False, f"{cliente.tipo_pessoa.value.upper()} já cadastrado no sistema"
        
        # Verifica duplicidade de email
        existente_email = self.db.executar_um(
            "SELECT id FROM clientes WHERE email = ?",
            (cliente.email,)
        )
        if existente_email:
            return False, "Email já cadastrado no sistema"
        
        try:
            query = """
                INSERT INTO clientes (
                    nome, tipo_pessoa, documento, email, telefone, cep,
                    logradouro, numero, complemento, bairro, cidade, uf,
                    status, observacoes, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                cliente.nome,
                cliente.tipo_pessoa.value,
                cliente.documento,
                cliente.email,
                cliente.telefone,
                cliente.cep,
                cliente.logradouro,
                cliente.numero,
                cliente.complemento,
                cliente.bairro,
                cliente.cidade,
                cliente.uf,
                cliente.status.value,
                cliente.observacoes,
                datetime.now()
            )
            
            cliente_id = self.db.inserir(query, params)
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'clientes', 'INSERT', cliente_id,
                dados_novos=cliente.to_dict()
            )
            
            return True, f"Cliente criado com sucesso (ID: {cliente_id})"
        
        except Exception as e:
            return False, f"Erro ao criar cliente: {str(e)}"
    
    def obter(self, cliente_id: int) -> Optional[dict]:
        """Obtém cliente por ID"""
        resultado = self.db.executar_um(
            "SELECT * FROM clientes WHERE id = ?",
            (cliente_id,)
        )
        return dict(resultado) if resultado else None
    
    def obter_por_documento(self, documento: str) -> Optional[dict]:
        """Obtém cliente por CPF/CNPJ"""
        documento_limpo = ''.join(filter(str.isdigit, documento))
        resultado = self.db.executar_um(
            "SELECT * FROM clientes WHERE documento = ?",
            (documento_limpo,)
        )
        return dict(resultado) if resultado else None
    
    def listar(
        self, 
        status: Optional[str] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """
        Lista clientes com filtros opcionais
        
        Args:
            status: Filtro por status (opcional)
            limite: Número máximo de resultados
            offset: Deslocamento para paginação
            
        Returns:
            Lista de clientes
        """
        if status:
            query = """
                SELECT * FROM clientes 
                WHERE status = ?
                ORDER BY data_cadastro DESC
                LIMIT ? OFFSET ?
            """
            resultados = self.db.executar(query, (status, limite, offset))
        else:
            query = """
                SELECT * FROM clientes 
                ORDER BY data_cadastro DESC
                LIMIT ? OFFSET ?
            """
            resultados = self.db.executar(query, (limite, offset))
        
        return [dict(r) for r in resultados]
    
    def listar_ativos(self, limite: int = 100, offset: int = 0) -> List[dict]:
        """Lista apenas clientes ativos"""
        return self.listar(status='ativo', limite=limite, offset=offset)
    
    def atualizar(self, cliente_id: int, cliente: Cliente) -> Tuple[bool, str]:
        """
        Atualiza cliente existente
        
        Args:
            cliente_id: ID do cliente
            cliente: Dados atualizados
            
        Returns:
            (sucesso, mensagem)
        """
        # Busca cliente antigo para auditoria
        cliente_antigo = self.obter(cliente_id)
        if not cliente_antigo:
            return False, "Cliente não encontrado"
        
        # Valida novo cliente
        valido, erros = cliente.validar()
        if not valido:
            return False, "\n".join(erros)
        
        # Verifica duplicidade de email (excluindo o cliente atual)
        existente_email = self.db.executar_um(
            "SELECT id FROM clientes WHERE email = ? AND id != ?",
            (cliente.email, cliente_id)
        )
        if existente_email:
            return False, "Email já cadastrado por outro cliente"
        
        try:
            query = """
                UPDATE clientes SET
                    nome = ?, tipo_pessoa = ?, documento = ?, email = ?,
                    telefone = ?, cep = ?, logradouro = ?, numero = ?,
                    complemento = ?, bairro = ?, cidade = ?, uf = ?,
                    status = ?, observacoes = ?, data_atualizacao = ?
                WHERE id = ?
            """
            
            params = (
                cliente.nome,
                cliente.tipo_pessoa.value,
                cliente.documento,
                cliente.email,
                cliente.telefone,
                cliente.cep,
                cliente.logradouro,
                cliente.numero,
                cliente.complemento,
                cliente.bairro,
                cliente.cidade,
                cliente.uf,
                cliente.status.value,
                cliente.observacoes,
                datetime.now(),
                cliente_id
            )
            
            self.db.atualizar(query, params)
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'clientes', 'UPDATE', cliente_id,
                dados_anteriores=cliente_antigo,
                dados_novos=cliente.to_dict()
            )
            
            return True, "Cliente atualizado com sucesso"
        
        except Exception as e:
            return False, f"Erro ao atualizar cliente: {str(e)}"
    
    def deletar(self, cliente_id: int) -> Tuple[bool, str]:
        """
        Deleta cliente (soft delete)
        Apenas marca como inativo
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            (sucesso, mensagem)
        """
        cliente = self.obter(cliente_id)
        if not cliente:
            return False, "Cliente não encontrado"
        
        try:
            # Marca como inativo em vez de deletar
            query = """
                UPDATE clientes 
                SET status = ?, data_atualizacao = ?
                WHERE id = ?
            """
            
            self.db.atualizar(query, ('inativo', datetime.now(), cliente_id))
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'clientes', 'DELETE', cliente_id,
                dados_anteriores=cliente
            )
            
            return True, "Cliente desativado com sucesso"
        
        except Exception as e:
            return False, f"Erro ao deletar cliente: {str(e)}"
    
    def buscar_cep(self, cep: str) -> Tuple[bool, dict]:
        """
        Busca endereço por CEP
        
        Args:
            cep: String com CEP
            
        Returns:
            (sucesso, dicionário com endereço)
        """
        return ValidadorCEP.buscar_endereco(cep)
    
    def contar_total(self) -> int:
        """Retorna total de clientes"""
        resultado = self.db.executar_um("SELECT COUNT(*) as total FROM clientes")
        return resultado['total'] if resultado else 0
    
    def contar_por_status(self, status: str) -> int:
        """Retorna total de clientes por status"""
        resultado = self.db.executar_um(
            "SELECT COUNT(*) as total FROM clientes WHERE status = ?",
            (status,)
        )
        return resultado['total'] if resultado else 0

