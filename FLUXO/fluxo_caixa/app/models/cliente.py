"""
Modelo de Cliente
Responsável por representar e validar dados de clientes
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class StatusCliente(Enum):
    """Status possíveis de um cliente"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"


class TipoPessoa(Enum):
    """Tipo de pessoa: Física (CPF) ou Jurídica (CNPJ)"""
    FISICA = "fisica"
    JURIDICA = "juridica"


@dataclass
class Cliente:
    """Modelo de Cliente com validações"""
    
    nome: str
    tipo_pessoa: TipoPessoa
    documento: str  # CPF ou CNPJ
    email: str
    telefone: str
    cep: str
    logradouro: str
    numero: str
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = ""
    status: StatusCliente = StatusCliente.ATIVO
    data_cadastro: datetime = field(default_factory=datetime.now)
    observacoes: str = ""
    id: Optional[int] = None
    
    def __post_init__(self):
        """Normaliza dados após inicialização"""
        self.nome = self.nome.strip()
        self.email = self.email.strip().lower()
        self.documento = self._normalizar_documento(self.documento)
        self.cep = self.cep.replace("-", "").replace(".", "").strip()
    
    def _normalizar_documento(self, doc: str) -> str:
        """Remove caracteres especiais do documento"""
        return ''.join(filter(str.isdigit, doc))
    
    def validar(self) -> tuple[bool, list[str]]:
        """
        Valida cliente e retorna (válido, lista_erros)
        
        Returns:
            tuple[bool, list[str]]: (é_válido, erros)
        """
        erros = []
        
        # Nome
        if not self.nome or len(self.nome) < 3:
            erros.append("Nome deve ter no mínimo 3 caracteres")
        
        # Email
        if "@" not in self.email or "." not in self.email:
            erros.append("Email inválido")
        
        # Telefone
        if len(self.documento) < 10:
            erros.append("Telefone deve ter no mínimo 10 dígitos")
        
        # Documento
        if not self._validar_documento():
            if self.tipo_pessoa == TipoPessoa.FISICA:
                erros.append("CPF inválido")
            else:
                erros.append("CNPJ inválido")
        
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
        
        return len(erros) == 0, erros
    
    def _validar_documento(self) -> bool:
        """Valida CPF ou CNPJ com algoritmo de dígito verificador"""
        if self.tipo_pessoa == TipoPessoa.FISICA:
            return self._validar_cpf(self.documento)
        else:
            return self._validar_cnpj(self.documento)
    
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
    
    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ utilizando dígitos verificadores"""
        if len(cnpj) != 14:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False
        
        # Primeiro dígito verificador
        soma = sum(int(cnpj[i]) * (5 - (i % 4)) for i in range(8))
        soma += sum(int(cnpj[i]) * (9 - (i % 4)) for i in range(8, 12))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1
        
        if int(cnpj[12]) != digito1:
            return False
        
        # Segundo dígito verificador
        soma = sum(int(cnpj[i]) * (6 - (i % 4)) for i in range(9))
        soma += sum(int(cnpj[i]) * (9 - (i % 4)) for i in range(9, 13))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2
        
        return int(cnpj[13]) == digito2
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo_pessoa': self.tipo_pessoa.value,
            'documento': self.documento,
            'email': self.email,
            'telefone': self.telefone,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
            'status': self.status.value,
            'data_cadastro': self.data_cadastro.isoformat(),
            'observacoes': self.observacoes,
        }

