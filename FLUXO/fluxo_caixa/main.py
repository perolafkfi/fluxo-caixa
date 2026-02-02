"""Ponto de entrada da aplicacao - Sistema de Fluxo de Caixa Profissional"""
import sys
from pathlib import Path

# Adicionar o diretorio raiz ao path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tkinter as tk
from tkinter import ttk, messagebox

try:
    import ttkbootstrap as ttb # pyright: ignore[reportMissingImports]
except ImportError:  # fallback when ttkbootstrap is not installed
    ttb = None

from app.config.settings import Settings
from app.database.database import Database
from app.services.categoria import ServicoCategoria
from app.services.cliente import ServicoCliente
from app.services.funcionario import ServicoFuncionario
from app.services.fornecedor import ServicoFornecedor
from app.services.lancamento import ServicoLancamento
from app.services.relatorios import GeradorRelatorios
from app.ui.views.clientes import TelaClientes
from app.ui.views.funcionarios import TelaFuncionarios
from app.ui.views.fornecedores import TelaFornecedores
from app.ui.views.lancamentos import TelaLancamentos
from app.ui.views.relatorios_ui import TelaRelatorios


class AplicacaoFluxoCaixa:
    """Aplicacao principal de Fluxo de Caixa Profissional."""

    def __init__(self, root):
        self.root = root

        # Inicializa banco de dados
        self.db = Database()

        # Inicializa servicos
        self.servico_categoria = ServicoCategoria(self.db)
        self.servico_cliente = ServicoCliente(self.db)
        self.servico_funcionario = ServicoFuncionario(self.db)
        self.servico_fornecedor = ServicoFornecedor(self.db)
        self.servico_fornecedor.criar_tabela()  # Garante que a tabela de fornecedores existe
        self.servico_lancamento = ServicoLancamento(self.db)
        self.gerador_relatorios = GeradorRelatorios(self.db)

        self.configurar_janela()
        self.criar_menu()
        self.criar_abas()

    def configurar_janela(self):
        """Configura janela principal."""
        self.root.title("Fluxo de Caixa Profissional - Sistema Integrado")
        self.root.geometry("1400x800")

        # Centraliza janela
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def criar_menu(self):
        """Cria menu da aplicacao."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Backup do Banco", command=self.fazer_backup)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.root.quit)

        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)

    def fazer_backup(self):
        """Realiza backup do banco de dados."""
        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_backup = Settings.DATA_DIR / "backups" / f"fluxo_caixa_{timestamp}.db"
            caminho_backup.parent.mkdir(parents=True, exist_ok=True)

            self.db.backup(caminho_backup)
            messagebox.showinfo("Sucesso", f"Backup realizado em:\n{caminho_backup}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {str(e)}")

    def mostrar_sobre(self):
        """Mostra janela sobre."""
        messagebox.showinfo(
            "Sobre",
            "SISTEMA DE FLUXO DE CAIXA PROFISSIONAL\n\n"
            "Versao 1.0\n"
            "(C) 2026 - Todos os direitos reservados\n\n"
            "Recursos:\n"
            "- Cadastro de Clientes\n"
            "- Cadastro de Funcionarios\n"
            "- Controle de Fluxo de Caixa\n"
            "- Relatorios Profissionais\n"
            "- Impressao Integrada\n"
            "- Busca de CEP Automatica",
        )

    def criar_abas(self):
        """Cria abas principais da aplicacao."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba de Clientes
        frame_clientes = ttk.Frame(self.notebook)
        self.notebook.add(frame_clientes, text="Clientes")
        self.tela_clientes = TelaClientes(self.root, self.servico_cliente)
        self.tela_clientes.criar_interface(frame_clientes)

        # Aba de Funcionarios
        frame_funcionarios = ttk.Frame(self.notebook)
        self.notebook.add(frame_funcionarios, text="Funcionarios")
        self.tela_funcionarios = TelaFuncionarios(self.root, self.servico_funcionario)
        self.tela_funcionarios.criar_interface(frame_funcionarios)

        # Aba de Fornecedores
        frame_fornecedores = ttk.Frame(self.notebook)
        self.notebook.add(frame_fornecedores, text="Fornecedores")
        self.tela_fornecedores = TelaFornecedores(self.root, self.servico_fornecedor)
        self.tela_fornecedores.criar_interface(frame_fornecedores)

        # Aba de Lancamentos
        frame_lancamentos = ttk.Frame(self.notebook)
        self.notebook.add(frame_lancamentos, text="Fluxo de Caixa")
        self.tela_lancamentos = TelaLancamentos(
            self.root,
            self.db,
            self.servico_lancamento,
            self.servico_categoria,
            self.servico_cliente,
            self.servico_fornecedor,
        )
        self.tela_lancamentos.criar_interface(frame_lancamentos)

        # Aba de Relatorios
        frame_relatorios = ttk.Frame(self.notebook)
        self.notebook.add(frame_relatorios, text="Relatorios")
        self.tela_relatorios = TelaRelatorios(self.root, self.gerador_relatorios)
        self.tela_relatorios.criar_interface(frame_relatorios)


def main():
    """Funcao principal."""
    try:
        if ttb is not None:
            root = ttb.Window(themename="litera")
        else:
            print("[AVISO] ttkbootstrap nao instalado. Usando Tkinter padrao.")
            root = tk.Tk()
            try:
                style = ttk.Style(root)
                if "clam" in style.theme_names():
                    style.theme_use("clam")
            except Exception:
                pass
        app = AplicacaoFluxoCaixa(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicacao: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
