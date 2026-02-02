"""
Modelo de Funcionário
Responsável por representar e validar dados de funcionários
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class StatusFuncionario(Enum):
    """Status possíveis de um funcionário"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    LICENCA = "licenca"
    DESLIGADO = "desligado"


@dataclass
class Funcionario:
    """Modelo de Funcionário com validações"""
    
    nome: str
    cpf: str
    cargo: str
    data_admissao: datetime
    salario: float
    email: str
    telefone: str
    cep: str
    logradouro: str
    numero: str
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = ""
    status: StatusFuncionario = StatusFuncionario.ATIVO
    data_cadastro: datetime = field(default_factory=datetime.now)
    observacoes: str = ""
    id: Optional[int] = None
    
    def __post_init__(self):
        """Normaliza dados após inicialização"""
        self.nome = self.nome.strip()
        self.email = self.email.strip().lower()
        self.cpf = self._normalizar_cpf(self.cpf)
        self.cep = self.cep.replace("-", "").replace(".", "").strip()
    
    def _normalizar_cpf(self, cpf: str) -> str:
        """Remove caracteres especiais do CPF"""
        return ''.join(filter(str.isdigit, cpf))
    
    def validar(self) -> tuple[bool, list[str]]:
        """
        Valida funcionário e retorna (válido, lista_erros)
        
        Returns:
            tuple[bool, list[str]]: (é_válido, erros)
        """
        erros = []
        
        # Nome
        if not self.nome or len(self.nome) < 3:
            erros.append("Nome deve ter no mínimo 3 caracteres")
        
        # CPF
        if not self._validar_cpf(self.cpf):
            erros.append("CPF inválido")
        
        # Email
        if "@" not in self.email or "." not in self.email:
            erros.append("Email inválido")
        
        # Telefone
        if len(self.telefone) < 10:
            erros.append("Telefone deve ter no mínimo 10 dígitos")
        
        # Cargo
        if not self.cargo or len(self.cargo) < 2:
            erros.append("Cargo inválido")
        
        # Salário
        if self.salario <= 0:
            erros.append("Salário deve ser maior que zero")
        
        # CEP
        if len(self.cep) != 8:
            erros.append("CEP deve ter 8 dígitos")
        
        # Endereço
        if not self.logradouro or len(self.logradouro) < 3:
            erros.append("Logradouro inválido")
        
        if not self.numero or len(self.numero) == 0:
            erros.append("Número é obrigatório")
        
        if not self.bairro or len(self.bairro) < 2:
            erros.append("Bairro inválido")
        
        if not self.cidade or len(self.cidade) < 2:
            erros.append("Cidade inválida")
        
        if len(self.uf) != 2:
            erros.append("UF deve ter 2 caracteres")
        
        # Data de admissão
        if self.data_admissao > datetime.now():
            erros.append("Data de admissão não pode ser no futuro")
        
        return len(erros) == 0, erros
    
    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        """Valida CPF utilizando dígitos verificadores"""
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1
        
        if int(cpf[9]) != digito1:
            return False
        
        # Segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2
        
        return int(cpf[10]) == digito2
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'cargo': self.cargo,
            'email': self.email,
            'telefone': self.telefone,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
            'salario': self.salario,
            'data_admissao': self.data_admissao.isoformat(),
            'status': self.status.value,
            'data_cadastro': self.data_cadastro.isoformat(),
            'observacoes': self.observacoes,
        }

