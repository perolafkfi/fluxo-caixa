"""
Modelo de Categoria e Subcategoria do Fluxo de Caixa
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TipoCategoria(Enum):
    """Tipos de categorias disponíveis"""
    RECEITA = "Receita"
    DESPESA_VARIAVEL = "Despesa Variável"
    DESPESA_FIXA = "Despesa Fixa"
    DESPESA_PESSOAL = "Despesa Pessoal"

    @property
    def grupo(self) -> str:
        """Retorna grupo da categoria"""
        if self == TipoCategoria.RECEITA:
            return "Receita"
        return "Despesa"


@dataclass
class Categoria:
    """Modelo de categoria financeira"""
    
    nome: str
    tipo: TipoCategoria
    descricao: str = ""
    ativo: bool = True
    id: Optional[int] = None

    def para_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo.value,
            "descricao": self.descricao,
            "ativo": self.ativo
        }


@dataclass
class Subcategoria:
    """Modelo de subcategoria financeira"""
    
    nome: str
    categoria_id: int
    descricao: str = ""
    ativo: bool = True
    id: Optional[int] = None

    def para_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria_id": self.categoria_id,
            "descricao": self.descricao,
            "ativo": self.ativo
        }


# Categorias e Subcategorias padrão do sistema

CATEGORIAS_PADRAO = [
    {
        "nome": "Receita",
        "tipo": TipoCategoria.RECEITA,
        "descricao": "Entradas de dinheiro",
        "subcategorias": [
            {"nome": "Serviços", "descricao": "Receitas de serviços prestados"},
            {"nome": "Produtos", "descricao": "Vendas de produtos"},
            {"nome": "Investimentos", "descricao": "Retorno de investimentos"},
            {"nome": "Empréstimos", "descricao": "Empréstimos recebidos"},
            {"nome": "Outras", "descricao": "Outras receitas"},
        ]
    },
    {
        "nome": "Despesa Variável",
        "tipo": TipoCategoria.DESPESA_VARIAVEL,
        "descricao": "Despesas que variam conforme a operação",
        "subcategorias": [
            {"nome": "Insumos", "descricao": "Matéria-prima e insumos de produção"},
            {"nome": "Mão de Obra", "descricao": "Custos com colaboradores"},
            {"nome": "Fornecimentos", "descricao": "Materiais de consumo"},
            {"nome": "Transportes", "descricao": "Despesas com transporte e logística"},
            {"nome": "Outras", "descricao": "Outras despesas variáveis"},
        ]
    },
    {
        "nome": "Despesa Fixa",
        "tipo": TipoCategoria.DESPESA_FIXA,
        "descricao": "Despesas que se repetem regularmente",
        "subcategorias": [
            {"nome": "Energia", "descricao": "Conta de energia elétrica"},
            {"nome": "Água", "descricao": "Conta de água"},
            {"nome": "Internet", "descricao": "Internet e telefone"},
            {"nome": "Contador", "descricao": "Serviços contábeis"},
            {"nome": "Seguro", "descricao": "Seguros diversos"},
            {"nome": "Outras", "descricao": "Outras despesas fixas"},
        ]
    },
    {
        "nome": "Despesa Pessoal",
        "tipo": TipoCategoria.DESPESA_PESSOAL,
        "descricao": "Despesas pessoais do proprietário",
        "subcategorias": [
            {"nome": "Educação", "descricao": "Gastos com educação"},
            {"nome": "Saúde", "descricao": "Gastos com saúde"},
            {"nome": "Alimentação", "descricao": "Gastos com alimentação"},
            {"nome": "Lazer", "descricao": "Gastos com lazer"},
            {"nome": "Cartão de Crédito", "descricao": "Pagamento de cartão"},
            {"nome": "Outras", "descricao": "Outras despesas pessoais"},
        ]
    }
]

