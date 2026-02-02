"""
Serviço de Funcionários
Responsável por operações CRUD de funcionários
"""
from typing import List, Tuple, Optional
from app.models.funcionario import Funcionario, StatusFuncionario
from app.database.connection import Database
from app.utils.validators import ValidadorCEP
from datetime import datetime


class ServicoFuncionario:
    """CRUD completo para funcionários"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def criar(self, funcionario: Funcionario) -> Tuple[bool, str]:
        """
        Cria novo funcionário
        
        Args:
            funcionario: Objeto Funcionario
            
        Returns:
            (sucesso, mensagem)
        """
        # Valida funcionário
        valido, erros = funcionario.validar()
        if not valido:
            return False, "\n".join(erros)
        
        # Verifica duplicidade de CPF
        existente = self.db.executar_um(
            "SELECT id FROM funcionarios WHERE cpf = ?",
            (funcionario.cpf,)
        )
        if existente:
            return False, "CPF já cadastrado no sistema"
        
        # Verifica duplicidade de email
        existente_email = self.db.executar_um(
            "SELECT id FROM funcionarios WHERE email = ?",
            (funcionario.email,)
        )
        if existente_email:
            return False, "Email já cadastrado no sistema"
        
        try:
            query = """
                INSERT INTO funcionarios (
                    nome, cpf, cargo, email, telefone, cep,
                    logradouro, numero, complemento, bairro, cidade, uf,
                    salario, data_admissao, status, observacoes, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                funcionario.nome,
                funcionario.cpf,
                funcionario.cargo,
                funcionario.email,
                funcionario.telefone,
                funcionario.cep,
                funcionario.logradouro,
                funcionario.numero,
                funcionario.complemento,
                funcionario.bairro,
                funcionario.cidade,
                funcionario.uf,
                funcionario.salario,
                funcionario.data_admissao.strftime("%Y-%m-%d"),
                funcionario.status.value,
                funcionario.observacoes,
                datetime.now()
            )
            
            funcionario_id = self.db.inserir(query, params)
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'funcionarios', 'INSERT', funcionario_id,
                dados_novos=funcionario.to_dict()
            )
            
            return True, f"Funcionário criado com sucesso (ID: {funcionario_id})"
        
        except Exception as e:
            return False, f"Erro ao criar funcionário: {str(e)}"
    
    def obter(self, funcionario_id: int) -> Optional[dict]:
        """Obtém funcionário por ID"""
        resultado = self.db.executar_um(
            "SELECT * FROM funcionarios WHERE id = ?",
            (funcionario_id,)
        )
        return dict(resultado) if resultado else None
    
    def obter_por_cpf(self, cpf: str) -> Optional[dict]:
        """Obtém funcionário por CPF"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        resultado = self.db.executar_um(
            "SELECT * FROM funcionarios WHERE cpf = ?",
            (cpf_limpo,)
        )
        return dict(resultado) if resultado else None
    
    def listar(
        self,
        status: Optional[str] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """
        Lista funcionários com filtros opcionais
        
        Args:
            status: Filtro por status (opcional)
            limite: Número máximo de resultados
            offset: Deslocamento para paginação
            
        Returns:
            Lista de funcionários
        """
        if status:
            query = """
                SELECT * FROM funcionarios
                WHERE status = ?
                ORDER BY data_cadastro DESC
                LIMIT ? OFFSET ?
            """
            resultados = self.db.executar(query, (status, limite, offset))
        else:
            query = """
                SELECT * FROM funcionarios
                ORDER BY data_cadastro DESC
                LIMIT ? OFFSET ?
            """
            resultados = self.db.executar(query, (limite, offset))
        
        return [dict(r) for r in resultados]
    
    def listar_ativos(self, limite: int = 100, offset: int = 0) -> List[dict]:
        """Lista apenas funcionários ativos"""
        return self.listar(status='ativo', limite=limite, offset=offset)
    
    def atualizar(self, funcionario_id: int, funcionario: Funcionario) -> Tuple[bool, str]:
        """
        Atualiza funcionário existente
        
        Args:
            funcionario_id: ID do funcionário
            funcionario: Dados atualizados
            
        Returns:
            (sucesso, mensagem)
        """
        # Busca funcionário antigo para auditoria
        funcionario_antigo = self.obter(funcionario_id)
        if not funcionario_antigo:
            return False, "Funcionário não encontrado"
        
        # Valida novo funcionário
        valido, erros = funcionario.validar()
        if not valido:
            return False, "\n".join(erros)
        
        # Verifica duplicidade de email (excluindo o funcionário atual)
        existente_email = self.db.executar_um(
            "SELECT id FROM funcionarios WHERE email = ? AND id != ?",
            (funcionario.email, funcionario_id)
        )
        if existente_email:
            return False, "Email já cadastrado por outro funcionário"
        
        try:
            query = """
                UPDATE funcionarios SET
                    nome = ?, cpf = ?, cargo = ?, email = ?, telefone = ?,
                    cep = ?, logradouro = ?, numero = ?, complemento = ?,
                    bairro = ?, cidade = ?, uf = ?, salario = ?,
                    data_admissao = ?, status = ?, observacoes = ?,
                    data_atualizacao = ?
                WHERE id = ?
            """
            
            params = (
                funcionario.nome,
                funcionario.cpf,
                funcionario.cargo,
                funcionario.email,
                funcionario.telefone,
                funcionario.cep,
                funcionario.logradouro,
                funcionario.numero,
                funcionario.complemento,
                funcionario.bairro,
                funcionario.cidade,
                funcionario.uf,
                funcionario.salario,
                funcionario.data_admissao.strftime("%Y-%m-%d"),
                funcionario.status.value,
                funcionario.observacoes,
                datetime.now(),
                funcionario_id
            )
            
            self.db.atualizar(query, params)
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'funcionarios', 'UPDATE', funcionario_id,
                dados_anteriores=funcionario_antigo,
                dados_novos=funcionario.to_dict()
            )
            
            return True, "Funcionário atualizado com sucesso"
        
        except Exception as e:
            return False, f"Erro ao atualizar funcionário: {str(e)}"
    
    def deletar(self, funcionario_id: int) -> Tuple[bool, str]:
        """
        Deleta funcionário (soft delete)
        Apenas marca como inativo
        
        Args:
            funcionario_id: ID do funcionário
            
        Returns:
            (sucesso, mensagem)
        """
        funcionario = self.obter(funcionario_id)
        if not funcionario:
            return False, "Funcionário não encontrado"
        
        try:
            # Marca como inativo em vez de deletar
            query = """
                UPDATE funcionarios
                SET status = ?, data_atualizacao = ?
                WHERE id = ?
            """
            
            self.db.atualizar(query, ('inativo', datetime.now(), funcionario_id))
            
            # Registra auditoria
            self.db.registrar_auditoria(
                'funcionarios', 'DELETE', funcionario_id,
                dados_anteriores=funcionario
            )
            
            return True, "Funcionário desativado com sucesso"
        
        except Exception as e:
            return False, f"Erro ao deletar funcionário: {str(e)}"
    
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
        """Retorna total de funcionários"""
        resultado = self.db.executar_um("SELECT COUNT(*) as total FROM funcionarios")
        return resultado['total'] if resultado else 0
    
    def contar_por_status(self, status: str) -> int:
        """Retorna total de funcionários por status"""
        resultado = self.db.executar_um(
            "SELECT COUNT(*) as total FROM funcionarios WHERE status = ?",
            (status,)
        )
        return resultado['total'] if resultado else 0
    
    def calcular_folha_mensal(self, mes: int, ano: int) -> float:
        """Calcula total da folha de pagamento mensal"""
        resultado = self.db.executar_um(
            """
            SELECT SUM(salario) as total
            FROM funcionarios
            WHERE status = 'ativo' AND
            strftime('%m', data_admissao) <= ? AND
            strftime('%Y', data_admissao) <= ?
            """,
            (str(mes).zfill(2), str(ano))
        )
        return resultado['total'] or 0 if resultado else 0

