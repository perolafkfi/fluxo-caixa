"""
Validadores reutilizaveis
Responsavel por validacoes de CPF, CNPJ, CEP, Email, etc.
"""
import re
from typing import Tuple
from datetime import datetime
import requests


def validar_data(data_str: str, formato: str = "%Y-%m-%d") -> bool:
    """Valida formato de data"""
    try:
        datetime.strptime(data_str, formato)
        return True
    except ValueError:
        return False


def validar_valor(valor: float) -> bool:
    """Valida se valor e positivo"""
    return valor > 0


def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class ValidadorDocumento:
    """Valida CPF e CNPJ com verificacao de digitos"""

    @staticmethod
    def validar_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida CPF

        Args:
            cpf: String com CPF (com ou sem formatacao)

        Returns:
            (valido, mensagem)
        """
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        if len(cpf_limpo) != 11:
            return False, "CPF deve ter 11 digitos"

        if cpf_limpo == cpf_limpo[0] * 11:
            return False, "CPF com digitos repetidos e invalido"

        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1

        if int(cpf_limpo[9]) != digito1:
            return False, "CPF com digito verificador invalido"

        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2

        if int(cpf_limpo[10]) != digito2:
            return False, "CPF com digito verificador invalido"

        return True, "CPF valido"

    @staticmethod
    def validar_cnpj(cnpj: str) -> Tuple[bool, str]:
        """
        Valida CNPJ

        Args:
            cnpj: String com CNPJ (com ou sem formatacao)

        Returns:
            (valido, mensagem)
        """
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

        if len(cnpj_limpo) != 14:
            return False, "CNPJ deve ter 14 digitos"

        if cnpj_limpo == cnpj_limpo[0] * 14:
            return False, "CNPJ com digitos repetidos e invalido"

        multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj_limpo[i]) * multiplicadores1[i] for i in range(12))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 >= 10 else digito1

        if int(cnpj_limpo[12]) != digito1:
            return False, "CNPJ com digito verificador invalido"

        multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]
        soma = sum(int(cnpj_limpo[i]) * multiplicadores2[i] for i in range(12))
        soma += int(cnpj_limpo[12]) * 2
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 >= 10 else digito2

        if int(cnpj_limpo[13]) != digito2:
            return False, "CNPJ com digito verificador invalido"

        return True, "CNPJ valido"


class ValidadorCEP:
    """Valida e busca endereco por CEP"""

    @staticmethod
    def validar_cep(cep: str) -> Tuple[bool, str]:
        """
        Valida formato de CEP

        Args:
            cep: String com CEP

        Returns:
            (valido, mensagem)
        """
        cep_limpo = ''.join(filter(str.isdigit, cep))

        if len(cep_limpo) != 8:
            return False, "CEP deve ter 8 digitos"

        return True, "CEP valido"

    @staticmethod
    def buscar_endereco(cep: str) -> Tuple[bool, dict]:
        """
        Busca endereco via API ViaCEP

        Args:
            cep: String com CEP

        Returns:
            (sucesso, dicionario com endereco ou erro)
        """
        cep_limpo = ''.join(filter(str.isdigit, cep))

        valido, msg = ValidadorCEP.validar_cep(cep_limpo)
        if not valido:
            return False, {'erro': msg}

        try:
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                dados = response.json()

                if 'erro' in dados:
                    return False, {'erro': 'CEP nao encontrado'}

                return True, {
                    'logradouro': dados.get('logradouro', ''),
                    'bairro': dados.get('bairro', ''),
                    'cidade': dados.get('localidade', ''),
                    'uf': dados.get('uf', ''),
                    'cep': cep_limpo
                }
            return False, {'erro': 'Erro ao consultar API de CEP'}

        except requests.exceptions.RequestException:
            return False, {'erro': 'Erro de conexao ao buscar CEP'}
        except Exception as e:
            return False, {'erro': f'Erro: {str(e)}'}


class ValidadorEmail:
    """Valida email"""

    @staticmethod
    def validar(email: str) -> Tuple[bool, str]:
        """
        Valida email

        Args:
            email: String com email

        Returns:
            (valido, mensagem)
        """
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(padrao, email.strip()):
            return True, "Email valido"
        return False, "Email invalido"


class ValidadorTelefone:
    """Valida telefone brasileiro"""

    @staticmethod
    def validar(telefone: str) -> Tuple[bool, str]:
        """
        Valida telefone

        Args:
            telefone: String com telefone

        Returns:
            (valido, mensagem)
        """
        tel_limpo = ''.join(filter(str.isdigit, telefone))

        if len(tel_limpo) < 10 or len(tel_limpo) > 11:
            return False, f"Telefone deve ter 10 ou 11 digitos (tem {len(tel_limpo)})"

        if not tel_limpo.startswith((
            '11', '12', '13', '14', '15', '16', '17', '18', '19',
            '21', '22', '24', '27', '28',
            '31', '32', '33', '34', '35', '37', '38',
            '41', '42', '43', '44', '45', '46',
            '47', '48', '49',
            '51', '53', '54', '55',
            '61', '62', '63', '64', '65',
            '66', '67', '68', '69',
            '71', '73', '74', '75', '77',
            '79',
            '81', '82', '83', '84', '85', '86', '87', '88', '89',
            '91', '92', '93', '94', '95', '96', '97', '98', '99'
        )):
            return False, "DDD (codigo de area) invalido"

        return True, "Telefone valido"


class ValidadorData:
    """Valida datas"""

    @staticmethod
    def validar_data(data: str, formato: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Valida data

        Args:
            data: String com data
            formato: Formato esperado (padrao: YYYY-MM-DD)

        Returns:
            (valido, mensagem)
        """
        try:
            datetime.strptime(data, formato)
            return True, "Data valida"
        except ValueError:
            return False, f"Formato de data invalido. Use: {formato}"

    @staticmethod
    def validar_data_nao_futura(data: str, formato: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Valida se data nao e futura

        Args:
            data: String com data
            formato: Formato esperado

        Returns:
            (valido, mensagem)
        """
        valida, msg = ValidadorData.validar_data(data, formato)
        if not valida:
            return False, msg

        data_obj = datetime.strptime(data, formato)
        if data_obj > datetime.now():
            return False, "Data nao pode ser no futuro"

        return True, "Data valida"


class ValidadorValor:
    """Valida valores numericos"""

    @staticmethod
    def validar_valor_positivo(valor: float) -> Tuple[bool, str]:
        """
        Valida se valor e positivo

        Args:
            valor: Valor numerico

        Returns:
            (valido, mensagem)
        """
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                return False, "Valor deve ser maior que zero"
            return True, "Valor valido"
        except (TypeError, ValueError):
            return False, "Valor deve ser numerico"

    @staticmethod
    def validar_valor_decimal(valor: float, casas: int = 2) -> Tuple[bool, str]:
        """
        Valida se valor tem no maximo X casas decimais

        Args:
            valor: Valor numerico
            casas: Numero maximo de casas decimais

        Returns:
            (valido, mensagem)
        """
        try:
            valor_float = float(valor)
            valor_str = f"{valor_float:.{casas}f}"
            if float(valor_str) != valor_float:
                return False, f"Valor pode ter no maximo {casas} casas decimais"
            return True, "Valor valido"
        except (TypeError, ValueError):
            return False, "Valor deve ser numerico"
