"""
Modelo de Lançamento Financeiro com relacionamentos
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoLancamento(Enum):
    """Tipos de lançamento"""
    RECEITA = "Receita"
    DESPESA = "Despesa"


@dataclass
class Lancamento:
    """Modelo de lançamento financeiro"""

    data: str  # YYYY-MM-DD
    tipo: TipoLancamento
    categoria_id: int
    subcategoria_id: int
    valor: float
    descricao: str

    # Relacionamentos
    cliente_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    funcionario_id: Optional[int] = None

    # Dados adicionais
    banco: str = ""
    nota_fiscal: str = ""
    comprovante: str = ""
    observacao: str = ""

    # Auditoria
    id: Optional[int] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    def validar(self) -> tuple[bool, list]:
        """Valida lançamento e retorna (válido, erros)"""
        erros = []

        # Validação de data
        try:
            datetime.strptime(self.data, "%Y-%m-%d")
        except ValueError:
            erros.append("Data inválida. Use formato YYYY-MM-DD")

        # Validação de valor
        if self.valor <= 0:
            erros.append("Valor deve ser maior que zero")

        # Validação de tipo
        if self.tipo not in TipoLancamento:
            erros.append(f"Tipo inválido. Deve ser: Receita ou Despesa")

        # Validação de categoria e subcategoria
        if not isinstance(self.categoria_id, int) or self.categoria_id <= 0:
            erros.append("Categoria inválida")

        if not isinstance(self.subcategoria_id, int) or self.subcategoria_id <= 0:
            erros.append("Subcategoria inválida")

        # Validação de descrição
        if not self.descricao or len(self.descricao.strip()) == 0:
            erros.append("Descrição é obrigatória")

        if len(self.descricao) > 500:
            erros.append("Descrição não pode ter mais de 500 caracteres")

        # Validação de relacionamentos (depende do tipo)
        if self.tipo == TipoLancamento.RECEITA:
            if not self.cliente_id or self.cliente_id <= 0:
                erros.append("Para receitas, cliente é obrigatório")
            if not self.nota_fiscal or len(self.nota_fiscal.strip()) == 0:
                erros.append("Para receitas, nota fiscal é obrigatória")

        elif self.tipo == TipoLancamento.DESPESA:
            if not self.fornecedor_id or self.fornecedor_id <= 0:
                erros.append("Para despesas, fornecedor é obrigatório")

        return len(erros) == 0, erros

    def para_dict(self) -> dict:
        """Converte lançamento para dicionário"""
        return {
            "id": self.id,
            "data": self.data,
            "tipo": self.tipo.value,
            "categoria_id": self.categoria_id,
            "subcategoria_id": self.subcategoria_id,
            "valor": self.valor,
            "descricao": self.descricao,
            "cliente_id": self.cliente_id,
            "fornecedor_id": self.fornecedor_id,
            "funcionario_id": self.funcionario_id,
            "banco": self.banco,
            "nota_fiscal": self.nota_fiscal,
            "comprovante": self.comprovante,
            "observacao": self.observacao,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }

    @staticmethod
    def de_dict(dados: dict) -> 'Lancamento':
        """Cria lançamento a partir de dicionário"""
        tipo = TipoLancamento(dados['tipo']) if isinstance(dados['tipo'], str) else dados['tipo']
        
        return Lancamento(
            data=dados['data'],
            tipo=tipo,
            categoria_id=dados['categoria_id'],
            subcategoria_id=dados['subcategoria_id'],
            valor=dados['valor'],
            descricao=dados['descricao'],
            cliente_id=dados.get('cliente_id'),
            fornecedor_id=dados.get('fornecedor_id'),
            funcionario_id=dados.get('funcionario_id'),
            banco=dados.get('banco', ''),
            nota_fiscal=dados.get('nota_fiscal', ''),
            comprovante=dados.get('comprovante', ''),
            observacao=dados.get('observacao', ''),
            id=dados.get('id'),
            criado_em=dados.get('criado_em'),
            atualizado_em=dados.get('atualizado_em'),
        )

