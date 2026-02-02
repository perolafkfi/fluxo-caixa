"""
Relatorios - consultas e agregacoes para UI e exportacao.
Mantem um unico ponto de acesso aos dados de relatorio.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.database.database import Database


class GeradorRelatorios:
    """Gera dados agregados de relatorios a partir do banco."""

    def __init__(self, db: Database):
        self.db = db
        self.data_geracao = datetime.now()

    def _montar_where(self, filtros: Optional[Dict]) -> Tuple[str, List]:
        where = " WHERE 1=1"
        params: List = []

        if not filtros:
            return where, params

        data_inicio = filtros.get("data_inicio")
        data_fim = filtros.get("data_fim")
        tipo = filtros.get("tipo")

        if data_inicio:
            where += " AND l.data >= ?"
            params.append(data_inicio)
        if data_fim:
            where += " AND l.data <= ?"
            params.append(data_fim)
        if tipo:
            where += " AND l.tipo = ?"
            params.append(tipo)

        return where, params

    def _normalizar_categoria_despesa(self, nome: str) -> str:
        if not nome:
            return "Outras"
        nome_lower = nome.lower()
        if "vari" in nome_lower:
            return "Variável"
        if "fixa" in nome_lower:
            return "Fixa"
        if "pessoal" in nome_lower:
            return "Pessoal"
        return nome

    def obter_lancamentos_filtrados(self, filtros: Optional[Dict] = None) -> List[Dict]:
        where, params = self._montar_where(filtros)

        query = f"""
            SELECT
                l.id,
                l.data,
                l.tipo,
                c.nome AS categoria,
                s.nome AS subcategoria,
                l.descricao,
                l.valor,
                l.banco,
                l.nota_fiscal,
                l.observacao,
                cl.nome AS cliente_nome,
                f.nome AS fornecedor_nome
            FROM lancamentos l
            LEFT JOIN categorias c ON l.categoria_id = c.id
            LEFT JOIN subcategorias s ON l.subcategoria_id = s.id
            LEFT JOIN clientes cl ON l.cliente_id = cl.id
            LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
            {where}
            ORDER BY l.data DESC
        """

        resultados = self.db.obter_todos(query, tuple(params))
        for row in resultados:
            categoria = row.get("categoria") or ""
            if row.get("tipo") == "Despesa":
                categoria = self._normalizar_categoria_despesa(categoria)
            row["categoria"] = categoria
            row["subcategoria"] = row.get("subcategoria") or ""
            row["empresa"] = row.get("cliente_nome") or row.get("fornecedor_nome") or ""
            row["banco"] = row.get("banco") or ""
            row["nota_fiscal"] = row.get("nota_fiscal") or ""
            row["observacao"] = row.get("observacao") or ""
        return resultados

    def obter_lancamentos_por_periodo(self, data_inicio: str, data_fim: str) -> List[Dict]:
        filtros = {}
        if data_inicio:
            filtros["data_inicio"] = data_inicio
        if data_fim:
            filtros["data_fim"] = data_fim
        return self.obter_lancamentos_filtrados(filtros)

    def obter_lancamentos(self, filtros: Optional[Dict] = None) -> List[Dict]:
        return self.obter_lancamentos_filtrados(filtros)

    def _calcular_total_por_tipo(self, tipo: str, filtros: Optional[Dict] = None) -> float:
        query = "SELECT COALESCE(SUM(valor), 0) as total FROM lancamentos WHERE tipo = ?"
        params: List = [tipo]

        if filtros:
            if filtros.get("data_inicio"):
                query += " AND data >= ?"
                params.append(filtros["data_inicio"])
            if filtros.get("data_fim"):
                query += " AND data <= ?"
                params.append(filtros["data_fim"])
            if filtros.get("categoria_id"):
                query += " AND categoria_id = ?"
                params.append(filtros["categoria_id"])

        resultado = self.db.obter_um(query, tuple(params))
        return float(resultado["total"]) if resultado else 0.0

    def calcular_total_receitas(self, filtros: Optional[Dict] = None) -> float:
        return self._calcular_total_por_tipo("Receita", filtros)

    def calcular_total_despesas(self, filtros: Optional[Dict] = None) -> float:
        return self._calcular_total_por_tipo("Despesa", filtros)

    def calcular_saldo(self, filtros: Optional[Dict] = None) -> float:
        return self.calcular_total_receitas(filtros) - self.calcular_total_despesas(filtros)

    def totais_por_categoria(self, filtros: Optional[Dict] = None) -> Dict[str, float]:
        where, params = self._montar_where(filtros)
        query = f"""
            SELECT c.nome AS categoria, COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            LEFT JOIN categorias c ON l.categoria_id = c.id
            {where}
            GROUP BY c.id
            ORDER BY total DESC
        """
        resultados = self.db.obter_todos(query, tuple(params))
        totais: Dict[str, float] = {}
        for row in resultados:
            nome = row.get("categoria") or "Sem categoria"
            chave = self._normalizar_categoria_despesa(nome) if "despesa" in nome.lower() else nome
            totais[chave] = totais.get(chave, 0.0) + float(row["total"])
        return totais

    def totais_por_subcategoria(self, filtros: Optional[Dict] = None) -> Dict[str, float]:
        where, params = self._montar_where(filtros)
        query = f"""
            SELECT s.nome AS subcategoria, COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            LEFT JOIN subcategorias s ON l.subcategoria_id = s.id
            {where}
            GROUP BY s.id
            ORDER BY total DESC
        """
        resultados = self.db.obter_todos(query, tuple(params))
        return {row.get("subcategoria") or "Sem subcategoria": float(row["total"]) for row in resultados}

    def totais_por_tipo(self, filtros: Optional[Dict] = None) -> Dict[str, float]:
        where, params = self._montar_where(filtros)
        query = f"""
            SELECT l.tipo AS tipo, COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            {where}
            GROUP BY l.tipo
        """
        resultados = self.db.obter_todos(query, tuple(params))
        return {row["tipo"]: float(row["total"]) for row in resultados}

    def despesas_por_tipo_categoria(self, filtros: Optional[Dict] = None) -> Dict[str, float]:
        filtros = dict(filtros or {})
        filtros["tipo"] = "Despesa"
        where, params = self._montar_where(filtros)
        query = f"""
            SELECT c.nome AS categoria, COALESCE(SUM(l.valor), 0) as total
            FROM lancamentos l
            LEFT JOIN categorias c ON l.categoria_id = c.id
            {where}
            GROUP BY c.id
        """
        resultados = self.db.obter_todos(query, tuple(params))
        totais: Dict[str, float] = {}
        for row in resultados:
            chave = self._normalizar_categoria_despesa(row.get("categoria") or "")
            totais[chave] = totais.get(chave, 0.0) + float(row["total"])
        return totais

    def gerar_resumo(self, filtros: Optional[Dict] = None) -> Dict:
        receitas = self.calcular_total_receitas(filtros)
        despesas = self.calcular_total_despesas(filtros)
        saldo = receitas - despesas

        return {
            "total_receitas": receitas,
            "total_despesas": despesas,
            "saldo": saldo,
            "por_categoria": self.totais_por_categoria(filtros),
            "por_tipo": self.totais_por_tipo(filtros),
            "despesas_por_tipo_categoria": self.despesas_por_tipo_categoria(filtros),
        }

    def obter_dados_grafico_barras(
        self, filtros: Optional[Dict] = None, usar_subcategoria: bool = False
    ) -> Tuple[List[str], List[float]]:
        totais = (
            self.totais_por_subcategoria(filtros)
            if usar_subcategoria
            else self.totais_por_categoria(filtros)
        )
        categorias = list(totais.keys())
        valores = list(totais.values())
        return categorias, valores

    def gerar_relatorio_geral(self, data_inicio: str, data_fim: str) -> str:
        filtros = {"data_inicio": data_inicio, "data_fim": data_fim}
        resumo = self.gerar_resumo(filtros)
        linhas = [
            "RELATORIO GERAL DE FLUXO DE CAIXA",
            f"Periodo: {data_inicio} a {data_fim}",
            f"Total Receitas: R$ {resumo['total_receitas']:.2f}",
            f"Total Despesas: R$ {resumo['total_despesas']:.2f}",
            f"Saldo: R$ {resumo['saldo']:.2f}",
        ]
        return "\n".join(linhas)

