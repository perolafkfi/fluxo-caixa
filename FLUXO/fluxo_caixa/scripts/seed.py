"""Seed de dados de exemplo para preencher as telas do sistema."""
from __future__ import annotations

import sys
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Garantir imports do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.database import Database
from app.models.categoria import TipoCategoria
from app.models.lancamento import TipoLancamento
from app.services.categoria import ServicoCategoria


def _calcular_dv_cpf(numeros: List[int]) -> int:
    pesos = list(range(len(numeros) + 1, 1, -1))
    soma = sum(n * p for n, p in zip(numeros, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def _gerar_cpf(indice: int) -> str:
    base = f"{indice:09d}"
    if base == base[0] * 9:
        base = "123456789"
    nums = [int(d) for d in base]
    d1 = _calcular_dv_cpf(nums)
    nums.append(d1)
    d2 = _calcular_dv_cpf(nums)
    return base + str(d1) + str(d2)


def _calcular_dv_cnpj(numeros: List[int]) -> Tuple[int, int]:
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(n * p for n, p in zip(numeros, pesos1))
    resto1 = soma1 % 11
    d1 = 0 if resto1 < 2 else 11 - resto1
    numeros2 = numeros + [d1]
    soma2 = sum(n * p for n, p in zip(numeros2, pesos2))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else 11 - resto2
    return d1, d2


def _gerar_cnpj(indice: int) -> str:
    base = f"{indice:012d}"
    if base == base[0] * 12:
        base = "123456789012"
    nums = [int(d) for d in base]
    d1, d2 = _calcular_dv_cnpj(nums)
    return base + str(d1) + str(d2)


def _get_or_create_cliente(db: Database, data: Dict) -> Tuple[int, bool]:
    row = db.obter_um("SELECT id FROM clientes WHERE email = ?", (data["email"],))
    if not row:
        row = db.obter_um("SELECT id FROM clientes WHERE documento = ?", (data["documento"],))
    if row:
        query = """
            UPDATE clientes SET
                nome = ?, tipo_pessoa = ?, documento = ?, email = ?, telefone = ?,
                cep = ?, logradouro = ?, numero = ?, complemento = ?, bairro = ?,
                cidade = ?, uf = ?, status = ?, observacoes = ?
            WHERE id = ?
        """
        params = (
            data["nome"],
            data["tipo_pessoa"],
            data["documento"],
            data["email"],
            data["telefone"],
            data["cep"],
            data["logradouro"],
            data["numero"],
            data.get("complemento", ""),
            data["bairro"],
            data["cidade"],
            data["uf"],
            data.get("status", "ativo"),
            data.get("observacoes", ""),
            row["id"],
        )
        db.atualizar(query, params)
        return row["id"], False
    query = """
        INSERT INTO clientes (
            nome, tipo_pessoa, documento, email, telefone, cep, logradouro,
            numero, complemento, bairro, cidade, uf, status, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data["nome"],
        data["tipo_pessoa"],
        data["documento"],
        data["email"],
        data["telefone"],
        data["cep"],
        data["logradouro"],
        data["numero"],
        data.get("complemento", ""),
        data["bairro"],
        data["cidade"],
        data["uf"],
        data.get("status", "ativo"),
        data.get("observacoes", ""),
    )
    return db.inserir(query, params), True


def _get_or_create_funcionario(db: Database, data: Dict) -> Tuple[int, bool]:
    row = db.obter_um("SELECT id FROM funcionarios WHERE email = ?", (data["email"],))
    if not row:
        row = db.obter_um("SELECT id FROM funcionarios WHERE cpf = ?", (data["cpf"],))
    if row:
        query = """
            UPDATE funcionarios SET
                nome = ?, cpf = ?, cargo = ?, email = ?, telefone = ?, cep = ?,
                logradouro = ?, numero = ?, complemento = ?, bairro = ?, cidade = ?,
                uf = ?, salario = ?, data_admissao = ?, status = ?, observacoes = ?
            WHERE id = ?
        """
        params = (
            data["nome"],
            data["cpf"],
            data["cargo"],
            data["email"],
            data["telefone"],
            data["cep"],
            data["logradouro"],
            data["numero"],
            data.get("complemento", ""),
            data["bairro"],
            data["cidade"],
            data["uf"],
            data["salario"],
            data["data_admissao"],
            data.get("status", "ativo"),
            data.get("observacoes", ""),
            row["id"],
        )
        db.atualizar(query, params)
        return row["id"], False
    query = """
        INSERT INTO funcionarios (
            nome, cpf, cargo, email, telefone, cep, logradouro, numero,
            complemento, bairro, cidade, uf, salario, data_admissao,
            status, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data["nome"],
        data["cpf"],
        data["cargo"],
        data["email"],
        data["telefone"],
        data["cep"],
        data["logradouro"],
        data["numero"],
        data.get("complemento", ""),
        data["bairro"],
        data["cidade"],
        data["uf"],
        data["salario"],
        data["data_admissao"],
        data.get("status", "ativo"),
        data.get("observacoes", ""),
    )
    return db.inserir(query, params), True


def _get_or_create_fornecedor(db: Database, data: Dict) -> Tuple[int, bool]:
    row = db.obter_um("SELECT id FROM fornecedores WHERE nome = ?", (data["nome"],))
    if not row:
        row = db.obter_um("SELECT id FROM fornecedores WHERE cpf_cnpj = ?", (data["cpf_cnpj"],))
    if row:
        query = """
            UPDATE fornecedores SET
                tipo = ?, nome = ?, cpf_cnpj = ?, nome_fantasia = ?, telefone = ?,
                email = ?, cep = ?, endereco = ?, numero = ?, complemento = ?,
                bairro = ?, cidade = ?, estado = ?, observacoes = ?, status = ?
            WHERE id = ?
        """
        params = (
            data["tipo"],
            data["nome"],
            data["cpf_cnpj"],
            data.get("nome_fantasia"),
            data["telefone"],
            data["email"],
            data.get("cep"),
            data.get("endereco"),
            data.get("numero"),
            data.get("complemento"),
            data.get("bairro"),
            data.get("cidade"),
            data.get("estado"),
            data.get("observacoes", ""),
            data.get("status", "ativo"),
            row["id"],
        )
        db.atualizar(query, params)
        return row["id"], False
    query = """
        INSERT INTO fornecedores (
            tipo, nome, cpf_cnpj, nome_fantasia, telefone, email, cep,
            endereco, numero, complemento, bairro, cidade, estado,
            observacoes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data["tipo"],
        data["nome"],
        data["cpf_cnpj"],
        data.get("nome_fantasia"),
        data["telefone"],
        data["email"],
        data.get("cep"),
        data.get("endereco"),
        data.get("numero"),
        data.get("complemento"),
        data.get("bairro"),
        data.get("cidade"),
        data.get("estado"),
        data.get("observacoes", ""),
        data.get("status", "ativo"),
    )
    return db.inserir(query, params), True


def _get_categoria_id(db: Database, tipo: TipoCategoria) -> int | None:
    row = db.obter_um(
        "SELECT id FROM categorias WHERE tipo = ? ORDER BY id LIMIT 1",
        (tipo.value,),
    )
    return row["id"] if row else None


def _get_subcategoria_ids(db: Database, categoria_id: int) -> List[int]:
    rows = db.obter_todos(
        "SELECT id FROM subcategorias WHERE categoria_id = ? ORDER BY id",
        (categoria_id,),
    )
    return [r["id"] for r in rows]


def _pick(items: List[int], index: int) -> int:
    if not items:
        raise ValueError("Lista de subcategorias vazia")
    return items[index % len(items)]


def _lancamento_existe(db: Database, data: Dict) -> bool:
    row = db.obter_um(
        """
        SELECT id FROM lancamentos
        WHERE data = ? AND tipo = ? AND valor = ? AND descricao = ?
          AND COALESCE(cliente_id, 0) = ?
          AND COALESCE(fornecedor_id, 0) = ?
        LIMIT 1
        """,
        (
            data["data"],
            data["tipo"],
            data["valor"],
            data["descricao"],
            data.get("cliente_id") or 0,
            data.get("fornecedor_id") or 0,
        ),
    )
    return row is not None


def _inserir_lancamento(db: Database, data: Dict) -> bool:
    if _lancamento_existe(db, data):
        return False
    query = """
        INSERT INTO lancamentos (
            data, tipo, categoria_id, subcategoria_id, valor, descricao,
            cliente_id, fornecedor_id, funcionario_id, banco, nota_fiscal,
            comprovante, observacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data["data"],
        data["tipo"],
        data["categoria_id"],
        data["subcategoria_id"],
        data["valor"],
        data["descricao"],
        data.get("cliente_id"),
        data.get("fornecedor_id"),
        data.get("funcionario_id"),
        data.get("banco", ""),
        data.get("nota_fiscal", ""),
        data.get("comprovante", ""),
        data.get("observacao", ""),
    )
    db.inserir(query, params)
    return True


def seed():
    db = Database()
    ServicoCategoria(db)  # Garante categorias/subcategorias padrao

    # Mapear categorias e subcategorias por tipo
    cat_receita = _get_categoria_id(db, TipoCategoria.RECEITA)
    cat_variavel = _get_categoria_id(db, TipoCategoria.DESPESA_VARIAVEL)
    cat_fixa = _get_categoria_id(db, TipoCategoria.DESPESA_FIXA)
    cat_pessoal = _get_categoria_id(db, TipoCategoria.DESPESA_PESSOAL)

    if not all([cat_receita, cat_variavel, cat_fixa, cat_pessoal]):
        print("Nao foi possivel localizar categorias padrao. Execute o app uma vez e tente novamente.")
        return

    sub_receita = _get_subcategoria_ids(db, cat_receita)
    sub_variavel = _get_subcategoria_ids(db, cat_variavel)
    sub_fixa = _get_subcategoria_ids(db, cat_fixa)
    sub_pessoal = _get_subcategoria_ids(db, cat_pessoal)

    if not all([sub_receita, sub_variavel, sub_fixa, sub_pessoal]):
        print("Nao foi possivel localizar subcategorias. Verifique o cadastro de categorias.")
        return

    clientes_data = [
        {
            "nome": "Joao Silva",
            "tipo_pessoa": "fisica",
            "documento": "49193872020",
            "email": "joao.silva@email.com",
            "telefone": "11999990001",
            "cep": "01001000",
            "logradouro": "Rua Central",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "status": "ativo",
        },
        {
            "nome": "Maria Oliveira",
            "tipo_pessoa": "fisica",
            "documento": "94378876086",
            "email": "maria.oliveira@email.com",
            "telefone": "11999990002",
            "cep": "30140071",
            "logradouro": "Av Brasil",
            "numero": "200",
            "bairro": "Savassi",
            "cidade": "Belo Horizonte",
            "uf": "MG",
            "status": "ativo",
        },
        {
            "nome": "Carlos Souza",
            "tipo_pessoa": "fisica",
            "documento": "07176260249",
            "email": "carlos.souza@email.com",
            "telefone": "21999990003",
            "cep": "20040002",
            "logradouro": "Rua das Flores",
            "numero": "45",
            "bairro": "Centro",
            "cidade": "Rio de Janeiro",
            "uf": "RJ",
            "status": "inativo",
        },
        {
            "nome": "Ana Costa",
            "tipo_pessoa": "fisica",
            "documento": "65100569689",
            "email": "ana.costa@email.com",
            "telefone": "31999990004",
            "cep": "40140000",
            "logradouro": "Rua Azul",
            "numero": "300",
            "bairro": "Barra",
            "cidade": "Salvador",
            "uf": "BA",
            "status": "ativo",
        },
        {
            "nome": "Paulo Lima",
            "tipo_pessoa": "fisica",
            "documento": "19835964777",
            "email": "paulo.lima@email.com",
            "telefone": "31999990005",
            "cep": "80010000",
            "logradouro": "Rua Norte",
            "numero": "87",
            "bairro": "Centro",
            "cidade": "Curitiba",
            "uf": "PR",
            "status": "suspenso",
        },
        {
            "nome": "Empresa Alpha LTDA",
            "tipo_pessoa": "juridica",
            "documento": "78618559157823",
            "email": "financeiro@alpha.com.br",
            "telefone": "1133334444",
            "cep": "01310930",
            "logradouro": "Av Paulista",
            "numero": "1000",
            "bairro": "Bela Vista",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "status": "ativo",
        },
    ]

    random.seed(42)
    extra_clientes_pf = 80
    extra_clientes_pj = 20
    for i in range(1, extra_clientes_pf + 1):
        idx = 1000 + i
        clientes_data.append(
            {
                "nome": f"Cliente PF {i:03d}",
                "tipo_pessoa": "fisica",
                "documento": _gerar_cpf(100000000 + idx),
                "email": f"cliente{idx}@exemplo.com",
                "telefone": f"11{idx:09d}"[-11:],
                "cep": f"{idx % 100000000:08d}",
                "logradouro": f"Rua Exemplo {i}",
                "numero": str(100 + i),
                "bairro": f"Bairro {i % 10:02d}",
                "cidade": "Sao Paulo",
                "uf": "SP",
                "status": "ativo" if i % 7 else "inativo",
            }
        )
    for i in range(1, extra_clientes_pj + 1):
        idx = 2000 + i
        clientes_data.append(
            {
                "nome": f"Cliente PJ {i:03d} LTDA",
                "tipo_pessoa": "juridica",
                "documento": _gerar_cnpj(200000000000 + idx),
                "email": f"cliente.pj{idx}@exemplo.com",
                "telefone": f"11{idx:09d}"[-11:],
                "cep": f"{(idx + 12345) % 100000000:08d}",
                "logradouro": f"Avenida Comercial {i}",
                "numero": str(500 + i),
                "bairro": f"Centro {i % 5}",
                "cidade": "Sao Paulo",
                "uf": "SP",
                "status": "ativo",
            }
        )

    fornecedores_data = [
        {
            "tipo": "juridica",
            "nome": "Alfa Distribuidora",
            "nome_fantasia": "Alfa Distrib",
            "cpf_cnpj": "45596661393110",
            "telefone": "1133334444",
            "email": "contato@alfadistrib.com.br",
            "cep": "01310930",
            "endereco": "Av Paulista",
            "numero": "1500",
            "bairro": "Bela Vista",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "status": "ativo",
        },
        {
            "tipo": "fisica",
            "nome": "Marcos Vieira",
            "cpf_cnpj": "41167876806",
            "telefone": "11988887777",
            "email": "marcos.vieira@email.com",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "status": "ativo",
        },
        {
            "tipo": "juridica",
            "nome": "Papelaria Central",
            "nome_fantasia": "Papel Central",
            "cpf_cnpj": "09544276661861",
            "telefone": "1144443333",
            "email": "vendas@papelcentral.com.br",
            "cidade": "Campinas",
            "estado": "SP",
            "status": "inativo",
        },
        {
            "tipo": "juridica",
            "nome": "Luz e Energia LTDA",
            "nome_fantasia": "Luz e Energia",
            "cpf_cnpj": "01753420256092",
            "telefone": "1132221100",
            "email": "financeiro@luz.com.br",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "status": "ativo",
        },
        {
            "tipo": "fisica",
            "nome": "Ana Paula Santos",
            "cpf_cnpj": "19835964777",
            "telefone": "11999998888",
            "email": "anapaula@email.com",
            "cidade": "Santos",
            "estado": "SP",
            "status": "ativo",
        },
        {
            "tipo": "juridica",
            "nome": "Contabill Servicos",
            "nome_fantasia": "Contabill",
            "cpf_cnpj": "48252877669322",
            "telefone": "1132123434",
            "email": "suporte@contabill.com.br",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "status": "ativo",
        },
    ]

    extra_fornecedores_pf = 60
    extra_fornecedores_pj = 60
    for i in range(1, extra_fornecedores_pf + 1):
        idx = 3000 + i
        fornecedores_data.append(
            {
                "tipo": "fisica",
                "nome": f"Fornecedor PF {i:03d}",
                "cpf_cnpj": _gerar_cpf(300000000 + idx),
                "telefone": f"11{idx:09d}"[-11:],
                "email": f"fornecedor.pf{idx}@exemplo.com",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "status": "ativo" if i % 8 else "inativo",
            }
        )
    for i in range(1, extra_fornecedores_pj + 1):
        idx = 4000 + i
        fornecedores_data.append(
            {
                "tipo": "juridica",
                "nome": f"Fornecedor PJ {i:03d} LTDA",
                "nome_fantasia": f"Fornecedor PJ {i:03d}",
                "cpf_cnpj": _gerar_cnpj(400000000000 + idx),
                "telefone": f"11{idx:09d}"[-11:],
                "email": f"fornecedor.pj{idx}@exemplo.com",
                "cidade": "Sao Paulo",
                "estado": "SP",
                "status": "ativo",
            }
        )

    funcionarios_data = [
        {
            "nome": "Lucas Ferreira",
            "cpf": "44337310304",
            "cargo": "Vendedor",
            "email": "lucas.ferreira@email.com",
            "telefone": "11990001111",
            "cep": "01001000",
            "logradouro": "Rua Central",
            "numero": "101",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "salario": 2500.00,
            "data_admissao": "2025-03-10",
            "status": "ativo",
        },
        {
            "nome": "Paula Mendes",
            "cpf": "88251580765",
            "cargo": "Administrativo",
            "email": "paula.mendes@email.com",
            "telefone": "11990002222",
            "cep": "01002000",
            "logradouro": "Rua Azul",
            "numero": "220",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "salario": 3200.00,
            "data_admissao": "2024-11-15",
            "status": "ativo",
        },
        {
            "nome": "Renata Alves",
            "cpf": "89172259345",
            "cargo": "Financeiro",
            "email": "renata.alves@email.com",
            "telefone": "21990003333",
            "cep": "20040002",
            "logradouro": "Rua das Flores",
            "numero": "55",
            "bairro": "Centro",
            "cidade": "Rio de Janeiro",
            "uf": "RJ",
            "salario": 4200.00,
            "data_admissao": "2023-07-01",
            "status": "inativo",
        },
        {
            "nome": "Diego Rocha",
            "cpf": "96974306598",
            "cargo": "Estoquista",
            "email": "diego.rocha@email.com",
            "telefone": "31990004444",
            "cep": "30140071",
            "logradouro": "Av Brasil",
            "numero": "56",
            "bairro": "Savassi",
            "cidade": "Belo Horizonte",
            "uf": "MG",
            "salario": 2100.00,
            "data_admissao": "2022-02-20",
            "status": "ativo",
        },
        {
            "nome": "Juliana Prado",
            "cpf": "35663220089",
            "cargo": "Gerente",
            "email": "juliana.prado@email.com",
            "telefone": "31990005555",
            "cep": "80010000",
            "logradouro": "Rua Norte",
            "numero": "10",
            "bairro": "Centro",
            "cidade": "Curitiba",
            "uf": "PR",
            "salario": 6800.00,
            "data_admissao": "2021-05-03",
            "status": "ativo",
        },
        {
            "nome": "Bruno Ribeiro",
            "cpf": "59719082941",
            "cargo": "Motorista",
            "email": "bruno.ribeiro@email.com",
            "telefone": "31990006666",
            "cep": "40140000",
            "logradouro": "Rua Azul",
            "numero": "33",
            "bairro": "Barra",
            "cidade": "Salvador",
            "uf": "BA",
            "salario": 2800.00,
            "data_admissao": "2020-01-15",
            "status": "ativo",
        },
    ]

    cargos = ["Vendedor", "Analista", "Financeiro", "Operacional", "Gerente", "Assistente", "Supervisor"]
    extra_funcionarios = 60
    for i in range(1, extra_funcionarios + 1):
        idx = 5000 + i
        funcionarios_data.append(
            {
                "nome": f"Funcionario {i:03d}",
                "cpf": _gerar_cpf(500000000 + idx),
                "cargo": random.choice(cargos),
                "email": f"funcionario{idx}@exemplo.com",
                "telefone": f"11{idx:09d}"[-11:],
                "cep": f"{(idx + 22222) % 100000000:08d}",
                "logradouro": f"Rua Trabalho {i}",
                "numero": str(10 + i),
                "bairro": f"Bairro {i % 12:02d}",
                "cidade": "Sao Paulo",
                "uf": "SP",
                "salario": round(1800 + (i % 20) * 150 + random.random() * 100, 2),
                "data_admissao": (date.today() - timedelta(days=30 + i)).isoformat(),
                "status": "ativo" if i % 9 else "inativo",
            }
        )

    inserted = {"clientes": 0, "fornecedores": 0, "funcionarios": 0, "lancamentos": 0}
    clientes_ids: List[int] = []
    fornecedores_ids: List[int] = []
    funcionarios_ids: List[int] = []

    for c in clientes_data:
        cid, created = _get_or_create_cliente(db, c)
        clientes_ids.append(cid)
        inserted["clientes"] += 1 if created else 0

    for f in fornecedores_data:
        fid, created = _get_or_create_fornecedor(db, f)
        fornecedores_ids.append(fid)
        inserted["fornecedores"] += 1 if created else 0

    for f in funcionarios_data:
        fid, created = _get_or_create_funcionario(db, f)
        funcionarios_ids.append(fid)
        inserted["funcionarios"] += 1 if created else 0

    base = date.today()
    lancamentos = [
        {
            "data": (base - timedelta(days=1)).isoformat(),
            "tipo": TipoLancamento.RECEITA.value,
            "categoria_id": cat_receita,
            "subcategoria_id": _pick(sub_receita, 0),
            "valor": 8500.00,
            "descricao": "Venda de mercadorias",
            "cliente_id": clientes_ids[0],
            "nota_fiscal": "NF-2026-0001",
        },
        {
            "data": (base - timedelta(days=2)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_fixa,
            "subcategoria_id": _pick(sub_fixa, 1),
            "valor": 1120.00,
            "descricao": "Conta de energia",
            "fornecedor_id": fornecedores_ids[3],
        },
        {
            "data": (base - timedelta(days=3)).isoformat(),
            "tipo": TipoLancamento.RECEITA.value,
            "categoria_id": cat_receita,
            "subcategoria_id": _pick(sub_receita, 1),
            "valor": 2350.00,
            "descricao": "Servico de consultoria",
            "cliente_id": clientes_ids[1],
            "nota_fiscal": "NF-2026-0002",
        },
        {
            "data": (base - timedelta(days=4)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_fixa,
            "subcategoria_id": _pick(sub_fixa, 2),
            "valor": 280.00,
            "descricao": "Internet corporativa",
            "fornecedor_id": fornecedores_ids[2],
        },
        {
            "data": (base - timedelta(days=5)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_variavel,
            "subcategoria_id": _pick(sub_variavel, 0),
            "valor": 1900.00,
            "descricao": "Compra de insumos",
            "fornecedor_id": fornecedores_ids[0],
        },
        {
            "data": (base - timedelta(days=6)).isoformat(),
            "tipo": TipoLancamento.RECEITA.value,
            "categoria_id": cat_receita,
            "subcategoria_id": _pick(sub_receita, 2),
            "valor": 650.00,
            "descricao": "Rendimento de investimento",
            "cliente_id": clientes_ids[5],
            "nota_fiscal": "NF-2026-0003",
        },
        {
            "data": (base - timedelta(days=7)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_pessoal,
            "subcategoria_id": _pick(sub_pessoal, 0),
            "valor": 420.00,
            "descricao": "Plano de saude",
            "fornecedor_id": fornecedores_ids[5],
            "funcionario_id": funcionarios_ids[2],
        },
        {
            "data": (base - timedelta(days=8)).isoformat(),
            "tipo": TipoLancamento.RECEITA.value,
            "categoria_id": cat_receita,
            "subcategoria_id": _pick(sub_receita, 3),
            "valor": 1200.00,
            "descricao": "Recebimento de servicos",
            "cliente_id": clientes_ids[3],
            "nota_fiscal": "NF-2026-0004",
        },
        {
            "data": (base - timedelta(days=9)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_variavel,
            "subcategoria_id": _pick(sub_variavel, 2),
            "valor": 760.00,
            "descricao": "Materiais de consumo",
            "fornecedor_id": fornecedores_ids[1],
        },
        {
            "data": (base - timedelta(days=10)).isoformat(),
            "tipo": TipoLancamento.DESPESA.value,
            "categoria_id": cat_fixa,
            "subcategoria_id": _pick(sub_fixa, 0),
            "valor": 980.00,
            "descricao": "Servico de contador",
            "fornecedor_id": fornecedores_ids[5],
        },
    ]

    extra_lancamentos = 300
    categorias_despesa = [cat_variavel, cat_fixa, cat_pessoal]
    sub_map = {
        cat_receita: sub_receita,
        cat_variavel: sub_variavel,
        cat_fixa: sub_fixa,
        cat_pessoal: sub_pessoal,
    }

    for i in range(1, extra_lancamentos + 1):
        is_receita = i % 2 == 0
        if is_receita:
            categoria_id = cat_receita
            subcategoria_id = _pick(sub_map[categoria_id], i)
            cliente_id = random.choice(clientes_ids)
            fornecedor_id = None
            nota_fiscal = f"NF-{base.year}-{1000 + i:04d}"
            descricao = f"Receita adicional {i:04d}"
            tipo = TipoLancamento.RECEITA.value
        else:
            categoria_id = random.choice(categorias_despesa)
            subcategoria_id = _pick(sub_map[categoria_id], i)
            cliente_id = None
            fornecedor_id = random.choice(fornecedores_ids)
            nota_fiscal = ""
            descricao = f"Despesa adicional {i:04d}"
            tipo = TipoLancamento.DESPESA.value

        dias_atras = random.randint(1, 180)
        valor = round(random.uniform(50, 8000), 2)
        funcionario_id = random.choice(funcionarios_ids) if (not is_receita and i % 5 == 0) else None

        lancamentos.append(
            {
                "data": (base - timedelta(days=dias_atras)).isoformat(),
                "tipo": tipo,
                "categoria_id": categoria_id,
                "subcategoria_id": subcategoria_id,
                "valor": valor,
                "descricao": descricao,
                "cliente_id": cliente_id,
                "fornecedor_id": fornecedor_id,
                "funcionario_id": funcionario_id,
                "banco": "Banco 001" if is_receita else "",
                "nota_fiscal": nota_fiscal,
            }
        )

    for l in lancamentos:
        created = _inserir_lancamento(db, l)
        inserted["lancamentos"] += 1 if created else 0

    print("Seed concluido.")
    print(
        f"Clientes: {inserted['clientes']} | "
        f"Fornecedores: {inserted['fornecedores']} | "
        f"Funcionarios: {inserted['funcionarios']} | "
        f"Lancamentos: {inserted['lancamentos']}"
    )


if __name__ == "__main__":
    seed()
