"""
Tela de Cadastro e Gerenciamento de Funcionários
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading

from app.models.funcionario import Funcionario, StatusFuncionario
from app.services.funcionario import ServicoFuncionario


class TelaFuncionarios:
    """Interface de cadastro de funcionários"""
    
    def __init__(self, parent, servico_funcionario: ServicoFuncionario):
        self.parent = parent
        self.servico = servico_funcionario
        self.funcionario_selecionado = None
        self.criando_novo = True
    
    def criar_interface(self, frame_principal):
        """Cria interface da tela"""
        self._criar_frame_lista(frame_principal)
        self._criar_frame_formulario(frame_principal)
        
        # Carrega dados apos criar interface
        self.atualizar_lista()
    
    def _criar_frame_lista(self, parent):
        """Cria frame com lista de funcionários"""
        frame_lista = ttk.LabelFrame(parent, text="Funcionários Cadastrados", padding=10)
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de ferramentas
        frame_toolbar = ttk.Frame(frame_lista)
        frame_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            frame_toolbar,
            text="✓ Novo",
            command=self.novo_funcionario
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_toolbar,
            text="✎ Editar",
            command=self.editar_funcionario_selecionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_toolbar,
            text="✗ Desativar",
            command=self.desativar_funcionario
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_toolbar,
            text="📊 Excel",
            command=self.exportar_excel
        ).pack(side=tk.LEFT, padx=2)
        
        # Entrada de busca
        frame_busca = ttk.Frame(frame_lista)
        frame_busca.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(frame_busca, text="Buscar:").pack(side=tk.LEFT, padx=2)
        self.var_busca = tk.StringVar()
        self.var_busca.trace('w', lambda *args: self.filtrar_funcionarios())
        
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca)
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Treeview para lista
        frame_tree = ttk.Frame(frame_lista)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_funcionarios = ttk.Treeview(
            frame_tree,
            columns=("ID", "Nome", "CPF", "Cargo", "Salário", "Status"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree_funcionarios.yview)
        
        # Configurar colunas
        self.tree_funcionarios.column("#0", width=0, stretch=tk.NO)
        self.tree_funcionarios.column("ID", width=40, anchor=tk.CENTER)
        self.tree_funcionarios.column("Nome", width=120, anchor=tk.W)
        self.tree_funcionarios.column("CPF", width=120, anchor=tk.CENTER)
        self.tree_funcionarios.column("Cargo", width=100, anchor=tk.W)
        self.tree_funcionarios.column("Salário", width=100, anchor=tk.E)
        self.tree_funcionarios.column("Status", width=80, anchor=tk.CENTER)
        
        # Cabeçalhos
        self.tree_funcionarios.heading("#0", text="")
        self.tree_funcionarios.heading("ID", text="ID")
        self.tree_funcionarios.heading("Nome", text="Nome")
        self.tree_funcionarios.heading("CPF", text="CPF")
        self.tree_funcionarios.heading("Cargo", text="Cargo")
        self.tree_funcionarios.heading("Salário", text="Salário")
        self.tree_funcionarios.heading("Status", text="Status")
        
        self.tree_funcionarios.bind('<<TreeviewSelect>>', self.on_funcionario_selecionado)
        self.tree_funcionarios.pack(fill=tk.BOTH, expand=True)
    
    def _criar_frame_formulario(self, parent):
        """Cria frame com formulário"""
        frame_form = ttk.LabelFrame(parent, text="Dados do Funcionário", padding=10)
        frame_form.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(frame_form)
        scrollbar = ttk.Scrollbar(frame_form, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Nome
        ttk.Label(scrollable_frame, text="Nome Completo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_nome = ttk.Entry(scrollable_frame, width=40)
        self.entry_nome.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # CPF
        ttk.Label(scrollable_frame, text="CPF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_cpf = ttk.Entry(scrollable_frame, width=40)
        self.entry_cpf.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Cargo
        ttk.Label(scrollable_frame, text="Cargo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_cargo = ttk.Entry(scrollable_frame, width=40)
        self.entry_cargo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Email
        ttk.Label(scrollable_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_email = ttk.Entry(scrollable_frame, width=40)
        self.entry_email.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Telefone
        ttk.Label(scrollable_frame, text="Telefone:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_telefone = ttk.Entry(scrollable_frame, width=40)
        self.entry_telefone.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Salário
        ttk.Label(scrollable_frame, text="Salário (R$):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.entry_salario = ttk.Entry(scrollable_frame, width=40)
        self.entry_salario.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Data de Admissão
        ttk.Label(scrollable_frame, text="Data Admissão (YYYY-MM-DD):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.entry_data_admissao = ttk.Entry(scrollable_frame, width=40)
        self.entry_data_admissao.grid(row=6, column=1, sticky=tk.EW, pady=5)
        self.entry_data_admissao.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # CEP com busca
        ttk.Label(scrollable_frame, text="CEP:").grid(row=7, column=0, sticky=tk.W, pady=5)
        frame_cep = ttk.Frame(scrollable_frame)
        frame_cep.grid(row=7, column=1, sticky=tk.EW, pady=5)
        self.entry_cep = ttk.Entry(frame_cep, width=15)
        self.entry_cep.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_cep, text="Buscar", command=self.buscar_endereco_cep, width=10).pack(side=tk.LEFT, padx=2)
        
        # Logradouro
        ttk.Label(scrollable_frame, text="Logradouro:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.entry_logradouro = ttk.Entry(scrollable_frame, width=40)
        self.entry_logradouro.grid(row=8, column=1, sticky=tk.EW, pady=5)
        
        # Número
        ttk.Label(scrollable_frame, text="Número:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.entry_numero = ttk.Entry(scrollable_frame, width=40)
        self.entry_numero.grid(row=9, column=1, sticky=tk.EW, pady=5)
        
        # Complemento
        ttk.Label(scrollable_frame, text="Complemento:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.entry_complemento = ttk.Entry(scrollable_frame, width=40)
        self.entry_complemento.grid(row=10, column=1, sticky=tk.EW, pady=5)
        
        # Bairro
        ttk.Label(scrollable_frame, text="Bairro:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.entry_bairro = ttk.Entry(scrollable_frame, width=40)
        self.entry_bairro.grid(row=11, column=1, sticky=tk.EW, pady=5)
        
        # Cidade
        ttk.Label(scrollable_frame, text="Cidade:").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.entry_cidade = ttk.Entry(scrollable_frame, width=40)
        self.entry_cidade.grid(row=12, column=1, sticky=tk.EW, pady=5)
        
        # UF
        ttk.Label(scrollable_frame, text="UF:").grid(row=13, column=0, sticky=tk.W, pady=5)
        self.entry_uf = ttk.Entry(scrollable_frame, width=5)
        self.entry_uf.grid(row=13, column=1, sticky=tk.W, pady=5)
        
        # Status
        ttk.Label(scrollable_frame, text="Status:").grid(row=14, column=0, sticky=tk.W, pady=5)
        self.var_status = tk.StringVar(value="ativo")
        combo_status = ttk.Combobox(
            scrollable_frame,
            textvariable=self.var_status,
            values=["ativo", "inativo", "licenca", "desligado"],
            width=37
        )
        combo_status.grid(row=14, column=1, sticky=tk.EW, pady=5)
        
        # Observações
        ttk.Label(scrollable_frame, text="Observações:").grid(row=15, column=0, sticky=tk.NW, pady=5)
        self.text_observacoes = scrolledtext.ScrolledText(scrollable_frame, width=40, height=5)
        self.text_observacoes.grid(row=15, column=1, sticky=tk.EW, pady=5)
        
        # Botões
        frame_botoes = ttk.Frame(scrollable_frame)
        frame_botoes.grid(row=16, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_funcionario, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar_formulario, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_edicao, width=15).pack(side=tk.LEFT, padx=2)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollable_frame.columnconfigure(1, weight=1)
    
    def buscar_endereco_cep(self):
        """Busca endereço por CEP"""
        cep = self.entry_cep.get().strip()
        if not cep:
            messagebox.showwarning("Aviso", "Digite um CEP")
            return
        
        thread = threading.Thread(target=self._buscar_cep_thread, args=(cep,))
        thread.start()
    
    def _buscar_cep_thread(self, cep: str):
        """Executa busca em thread"""
        sucesso, dados = self.servico.buscar_cep(cep)
        
        if sucesso:
            self.entry_logradouro.delete(0, tk.END)
            self.entry_logradouro.insert(0, dados.get('logradouro', ''))
            self.entry_bairro.delete(0, tk.END)
            self.entry_bairro.insert(0, dados.get('bairro', ''))
            self.entry_cidade.delete(0, tk.END)
            self.entry_cidade.insert(0, dados.get('cidade', ''))
            self.entry_uf.delete(0, tk.END)
            self.entry_uf.insert(0, dados.get('uf', ''))
        else:
            messagebox.showerror("Erro", dados.get('erro', 'Erro ao buscar CEP'))
    
    def novo_funcionario(self):
        """Novo funcionário"""
        self.criando_novo = True
        self.limpar_formulario()
    
    def editar_funcionario_selecionado(self):
        """Edita selecionado"""
        if not self.funcionario_selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário")
            return
        self.editar_funcionario(self.funcionario_selecionado)
    
    def editar_funcionario(self, funcionario_id: int):
        """Carrega para edição"""
        func = self.servico.obter(funcionario_id)
        if not func:
            messagebox.showerror("Erro", "Funcionário não encontrado")
            return
        
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, func['nome'])
        self.entry_cpf.delete(0, tk.END)
        self.entry_cpf.insert(0, func['cpf'])
        self.entry_cargo.delete(0, tk.END)
        self.entry_cargo.insert(0, func['cargo'])
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, func['email'])
        self.entry_telefone.delete(0, tk.END)
        self.entry_telefone.insert(0, func['telefone'])
        self.entry_salario.delete(0, tk.END)
        self.entry_salario.insert(0, f"{func['salario']:.2f}")
        self.entry_data_admissao.delete(0, tk.END)
        self.entry_data_admissao.insert(0, func['data_admissao'].split()[0])
        self.entry_cep.delete(0, tk.END)
        self.entry_cep.insert(0, func['cep'])
        self.entry_logradouro.delete(0, tk.END)
        self.entry_logradouro.insert(0, func['logradouro'])
        self.entry_numero.delete(0, tk.END)
        self.entry_numero.insert(0, func['numero'])
        self.entry_complemento.delete(0, tk.END)
        self.entry_complemento.insert(0, func['complemento'] or '')
        self.entry_bairro.delete(0, tk.END)
        self.entry_bairro.insert(0, func['bairro'])
        self.entry_cidade.delete(0, tk.END)
        self.entry_cidade.insert(0, func['cidade'])
        self.entry_uf.delete(0, tk.END)
        self.entry_uf.insert(0, func['uf'])
        self.var_status.set(func['status'])
        self.text_observacoes.delete(1.0, tk.END)
        self.text_observacoes.insert(1.0, func['observacoes'] or '')
        
        self.funcionario_selecionado = funcionario_id
        self.criando_novo = False
    
    def salvar_funcionario(self):
        """Salva funcionário"""
        try:
            data_adm = datetime.strptime(self.entry_data_admissao.get(), "%Y-%m-%d")
            salario = float(self.entry_salario.get())
            
            funcionario = Funcionario(
                nome=self.entry_nome.get(),
                cpf=self.entry_cpf.get(),
                cargo=self.entry_cargo.get(),
                email=self.entry_email.get(),
                telefone=self.entry_telefone.get(),
                salario=salario,
                data_admissao=data_adm,
                cep=self.entry_cep.get(),
                logradouro=self.entry_logradouro.get(),
                numero=self.entry_numero.get(),
                complemento=self.entry_complemento.get(),
                bairro=self.entry_bairro.get(),
                cidade=self.entry_cidade.get(),
                uf=self.entry_uf.get(),
                status=StatusFuncionario(self.var_status.get()),
                observacoes=self.text_observacoes.get(1.0, tk.END)
            )
        except ValueError as e:
            messagebox.showerror("Erro", f"Dados inválidos: {str(e)}")
            return
        
        if self.criando_novo or not self.funcionario_selecionado:
            sucesso, msg = self.servico.criar(funcionario)
        else:
            sucesso, msg = self.servico.atualizar(self.funcionario_selecionado, funcionario)
        
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_lista()
            self.limpar_formulario()
        else:
            messagebox.showerror("Erro", msg)
    
    def desativar_funcionario(self):
        """Desativa funcionário"""
        if not self.funcionario_selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário")
            return
        
        if messagebox.askyesno("Confirmar", "Desativar este funcionário?"):
            sucesso, msg = self.servico.deletar(self.funcionario_selecionado)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.atualizar_lista()
                self.limpar_formulario()
            else:
                messagebox.showerror("Erro", msg)
    
    def limpar_formulario(self):
        """Limpa formulário"""
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_cargo.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_salario.delete(0, tk.END)
        self.entry_data_admissao.delete(0, tk.END)
        self.entry_data_admissao.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_cep.delete(0, tk.END)
        self.entry_logradouro.delete(0, tk.END)
        self.entry_numero.delete(0, tk.END)
        self.entry_complemento.delete(0, tk.END)
        self.entry_bairro.delete(0, tk.END)
        self.entry_cidade.delete(0, tk.END)
        self.entry_uf.delete(0, tk.END)
        self.var_status.set("ativo")
        self.text_observacoes.delete(1.0, tk.END)
        self.funcionario_selecionado = None
        self.criando_novo = True
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.limpar_formulario()
        self.funcionario_selecionado = None
    
    def atualizar_lista(self):
        """Atualiza lista"""
        self.filtrar_funcionarios()
    
    def filtrar_funcionarios(self):
        """Filtra funcionários"""
        termo = self.var_busca.get().lower()
        funcionarios = self.servico.listar(limite=1000)
        
        for item in self.tree_funcionarios.get_children():
            self.tree_funcionarios.delete(item)
        
        for func in funcionarios:
            if termo == "" or \
               termo in func['nome'].lower() or \
               termo in func['cpf'] or \
               termo in func['cargo'].lower():
                
                self.tree_funcionarios.insert(
                    "",
                    tk.END,
                    values=(
                        func['id'],
                        func['nome'],
                        func['cpf'],
                        func['cargo'],
                        f"R$ {func['salario']:.2f}",
                        func['status']
                    )
                )
    
    def on_funcionario_selecionado(self, event):
        """Evento de seleção"""
        selecionado = self.tree_funcionarios.selection()
        if selecionado:
            item = self.tree_funcionarios.item(selecionado[0])
            func_id = item['values'][0]
            self.funcionario_selecionado = func_id
            self.editar_funcionario(func_id)

    def exportar_excel(self):
        """Exporta funcionários para Excel"""
        from tkinter import filedialog
        from app.services.export_excel_profissional import gerar_planilha_funcionarios
        from pathlib import Path
        
        try:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
                initialfile=f"Funcionarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not arquivo:
                return
            
            funcionarios = self.servico.listar_ativos()

            gerar_planilha_funcionarios(funcionarios, Path(arquivo))
            messagebox.showinfo("Sucesso", f"Funcionários exportados com sucesso!\n\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

