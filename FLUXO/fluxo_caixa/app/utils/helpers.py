"""Funções auxiliares"""
from datetime import datetime
from typing import Optional


def obter_data_atual(formato: str = "%Y-%m-%d") -> str:
    """Retorna data atual formatada"""
    return datetime.now().strftime(formato)


def formatar_data_para_exibicao(data_str: str) -> str:
    """Converte data de YYYY-MM-DD para DD/MM/YYYY"""
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except ValueError:
        return data_str


def formatar_moeda_brasileira(valor: float) -> str:
    """Formata valor como moeda brasileira (R$ 1.234,56)"""
    # Formata com vírgula para milhares e ponto para decimais primeiro
    valor_str = f"{valor:,.2f}"
    # Converte para formato brasileiro: ponto vira vírgula e vírgula vira ponto temporariamente
    valor_str = valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_str}"

