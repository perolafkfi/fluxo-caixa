"""
Modelo de Fornecedor - Sistema de Fluxo de Caixa
Estrutura idêntica a Cliente e Funcionário com suporte a PF e PJ
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import re


class TipoPessoa(Enum):
    """Tipo de pessoa do fornecedor"""
    FISICA = "fisica"
    JURIDICA = "juridica"


@dataclass
class Fornecedor:
    """Modelo de Fornecedor com validações"""
    
    tipo: TipoPessoa
    nome: str
    cpf_cnpj: str
    telefone: str
    email: str
    status: str = "ativo"
    nome_fantasia: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    observacoes: Optional[str] = None
    data_cadastro: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        self.validar()
    
    def validar(self) -> None:
        """Valida dados do fornecedor"""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome é obrigatório")
        
        if not self.email or not self._validar_email(self.email):
            raise ValueError("Email inválido")
        
        if not self.telefone or not self._validar_telefone(self.telefone):
            raise ValueError("Telefone inválido")
        
        if self.tipo == TipoPessoa.FISICA:
            if not self._validar_cpf(self.cpf_cnpj):
                raise ValueError("CPF inválido")
        elif self.tipo == TipoPessoa.JURIDICA:
            if not self._validar_cnpj(self.cpf_cnpj):
                raise ValueError("CNPJ inválido")
            if not self.nome_fantasia or not self.nome_fantasia.strip():
                raise ValueError("Nome fantasia é obrigatório para PJ")
        
        if self.status not in ["ativo", "inativo"]:
            raise ValueError("Status inválido (ativo/inativo)")
    
    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        """Valida CPF"""
        cpf_limpo = re.sub(r'\D', '', cpf)
        
        if len(cpf_limpo) != 11:
            return False
        
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
        
        # Validar dígitos verificadores
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return int(cpf_limpo[9]) == digito1 and int(cpf_limpo[10]) == digito2
    
    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ"""
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        
        if len(cnpj_limpo) != 14:
            return False
        
        if cnpj_limpo == cnpj_limpo[0] * 14:
            return False
        
        # Validar primeiro dígito
        multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj_limpo[i]) * multiplicadores1[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Validar segundo dígito
        multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]
        soma = sum(int(cnpj_limpo[i]) * multiplicadores2[i] for i in range(12))
        soma += digito1 * 2
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return int(cnpj_limpo[12]) == digito1 and int(cnpj_limpo[13]) == digito2
    
    @staticmethod
    def _validar_email(email: str) -> bool:
        """Valida email"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def _validar_telefone(telefone: str) -> bool:
        """Valida telefone"""
        telefone_limpo = re.sub(r'\D', '', telefone)
        return len(telefone_limpo) >= 10 and len(telefone_limpo) <= 11
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'nome': self.nome,
            'cpf_cnpj': self.cpf_cnpj,
            'nome_fantasia': self.nome_fantasia,
            'telefone': self.telefone,
            'email': self.email,
            'cep': self.cep,
            'endereco': self.endereco,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'observacoes': self.observacoes,
            'status': self.status,
            'data_cadastro': self.data_cadastro.isoformat(),
        }

