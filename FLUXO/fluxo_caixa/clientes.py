"""
Tela de Cadastro e Gerenciamento de Clientes
Interface moderna com busca por CEP automática
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading

from app.models.cliente import Cliente, TipoPessoa, StatusCliente
from app.services.cliente import ServicoCliente
from app.utils.validators import ValidadorCEP, ValidadorDocumento


class TelaClientes:
    """Interface de cadastro de clientes"""
    
    def __init__(self, parent, servico_cliente: ServicoCliente):
        self.parent = parent
        self.servico = servico_cliente
        self.cliente_selecionado = None
        self.criando_novo = True
    
    def criar_interface(self, frame_principal):
        """Cria interface da tela"""
        # Frame esquerdo - Lista de clientes
        self._criar_frame_lista(frame_principal)
        
        # Frame direito - Formulário
        self._criar_frame_formulario(frame_principal)
        
        # Carrega dados após criar interface
        self.atualizar_lista()
    
    def _criar_frame_lista(self, parent):
        """Cria frame com lista de clientes"""
        frame_lista = ttk.LabelFrame(parent, text="Clientes Cadastrados", padding=10)
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de ferramentas
        frame_toolbar = ttk.Frame(frame_lista)
        frame_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            frame_toolbar,
            text="✓ Novo",
            command=self.novo_cliente
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_toolbar,
            text="✎ Editar",
            command=self.editar_cliente_selecionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_toolbar,
            text="✗ Desativar",
            command=self.desativar_cliente
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
        self.var_busca.trace('w', lambda *args: self.filtrar_clientes())
        
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca)
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Treeview para lista
        frame_tree = ttk.Frame(frame_lista)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_clientes = ttk.Treeview(
            frame_tree,
            columns=("ID", "Nome", "Documento", "Email", "Status"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree_clientes.yview)
        
        # Configurar colunas
        self.tree_clientes.column("#0", width=0, stretch=tk.NO)
        self.tree_clientes.column("ID", width=40, anchor=tk.CENTER)
        self.tree_clientes.column("Nome", width=150, anchor=tk.W)
        self.tree_clientes.column("Documento", width=120, anchor=tk.CENTER)
        self.tree_clientes.column("Email", width=150, anchor=tk.W)
        self.tree_clientes.column("Status", width=80, anchor=tk.CENTER)
        
        # Cabeçalhos
        self.tree_clientes.heading("#0", text="", anchor=tk.W)
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nome", text="Nome")
        self.tree_clientes.heading("Documento", text="Documento")
        self.tree_clientes.heading("Email", text="Email")
        self.tree_clientes.heading("Status", text="Status")
        
        # Bind para seleção
        self.tree_clientes.bind('<<TreeviewSelect>>', self.on_cliente_selecionado)
        
        self.tree_clientes.pack(fill=tk.BOTH, expand=True)
    
    def _criar_frame_formulario(self, parent):
        """Cria frame com formulário de entrada"""
        frame_form = ttk.LabelFrame(parent, text="Dados do Cliente", padding=10)
        frame_form.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scroll para formulário longo
        canvas = tk.Canvas(frame_form)
        scrollbar = ttk.Scrollbar(frame_form, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tipo de Pessoa
        ttk.Label(scrollable_frame, text="Tipo de Pessoa:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.var_tipo = tk.StringVar(value="fisica")
        frame_tipo = ttk.Frame(scrollable_frame)
        frame_tipo.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame_tipo, text="Física (CPF)", variable=self.var_tipo, value="fisica").pack(side=tk.LEFT)
        ttk.Radiobutton(frame_tipo, text="Jurídica (CNPJ)", variable=self.var_tipo, value="juridica").pack(side=tk.LEFT)
        
        # Nome
        ttk.Label(scrollable_frame, text="Nome Completo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_nome = ttk.Entry(scrollable_frame, width=40)
        self.entry_nome.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Documento
        ttk.Label(scrollable_frame, text="CPF/CNPJ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        frame_doc = ttk.Frame(scrollable_frame)
        frame_doc.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.entry_documento = ttk.Entry(frame_doc, width=25)
        self.entry_documento.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_doc, text="Validar", command=self.validar_documento, width=10).pack(side=tk.LEFT, padx=2)
        
        # Email
        ttk.Label(scrollable_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_email = ttk.Entry(scrollable_frame, width=40)
        self.entry_email.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Telefone
        ttk.Label(scrollable_frame, text="Telefone:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_telefone = ttk.Entry(scrollable_frame, width=40)
        self.entry_telefone.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # CEP com busca
        ttk.Label(scrollable_frame, text="CEP:").grid(row=5, column=0, sticky=tk.W, pady=5)
        frame_cep = ttk.Frame(scrollable_frame)
        frame_cep.grid(row=5, column=1, sticky=tk.EW, pady=5)
        self.entry_cep = ttk.Entry(frame_cep, width=15)
        self.entry_cep.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_cep, text="Buscar", command=self.buscar_endereco_cep, width=10).pack(side=tk.LEFT, padx=2)
        
        # Logradouro
        ttk.Label(scrollable_frame, text="Logradouro:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.entry_logradouro = ttk.Entry(scrollable_frame, width=40)
        self.entry_logradouro.grid(row=6, column=1, sticky=tk.EW, pady=5)
        
        # Número
        ttk.Label(scrollable_frame, text="Número:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.entry_numero = ttk.Entry(scrollable_frame, width=40)
        self.entry_numero.grid(row=7, column=1, sticky=tk.EW, pady=5)
        
        # Complemento
        ttk.Label(scrollable_frame, text="Complemento:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.entry_complemento = ttk.Entry(scrollable_frame, width=40)
        self.entry_complemento.grid(row=8, column=1, sticky=tk.EW, pady=5)
        
        # Bairro
        ttk.Label(scrollable_frame, text="Bairro:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.entry_bairro = ttk.Entry(scrollable_frame, width=40)
        self.entry_bairro.grid(row=9, column=1, sticky=tk.EW, pady=5)
        
        # Cidade
        ttk.Label(scrollable_frame, text="Cidade:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.entry_cidade = ttk.Entry(scrollable_frame, width=40)
        self.entry_cidade.grid(row=10, column=1, sticky=tk.EW, pady=5)
        
        # UF
        ttk.Label(scrollable_frame, text="UF:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.entry_uf = ttk.Entry(scrollable_frame, width=5)
        self.entry_uf.grid(row=11, column=1, sticky=tk.W, pady=5)
        
        # Status
        ttk.Label(scrollable_frame, text="Status:").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.var_status = tk.StringVar(value="ativo")
        combo_status = ttk.Combobox(
            scrollable_frame,
            textvariable=self.var_status,
            values=["ativo", "inativo", "suspenso"],
            width=37
        )
        combo_status.grid(row=12, column=1, sticky=tk.EW, pady=5)
        
        # Observações
        ttk.Label(scrollable_frame, text="Observações:").grid(row=13, column=0, sticky=tk.NW, pady=5)
        self.text_observacoes = scrolledtext.ScrolledText(scrollable_frame, width=40, height=5)
        self.text_observacoes.grid(row=13, column=1, sticky=tk.EW, pady=5)
        
        # Frame de botões
        frame_botoes = ttk.Frame(scrollable_frame)
        frame_botoes.grid(row=14, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_cliente, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar_formulario, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_edicao, width=15).pack(side=tk.LEFT, padx=2)
        
        # Pack para scrollbar funcionar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Permitir configuração de peso para expansão
        scrollable_frame.columnconfigure(1, weight=1)
    
    def buscar_endereco_cep(self):
        """Busca endereço via CEP em thread separada"""
        cep = self.entry_cep.get().strip()
        
        if not cep:
            messagebox.showwarning("Aviso", "Digite um CEP")
            return
        
        # Thread para não bloquear UI
        thread = threading.Thread(target=self._buscar_cep_thread, args=(cep,))
        thread.start()
    
    def _buscar_cep_thread(self, cep: str):
        """Executa busca de CEP em thread"""
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
            
            messagebox.showinfo("Sucesso", "Endereço preenchido automaticamente")
        else:
            messagebox.showerror("Erro", dados.get('erro', 'Erro ao buscar CEP'))
    
    def validar_documento(self):
        """Valida documento inserido"""
        documento = self.entry_documento.get().strip()
        tipo = self.var_tipo.get()
        
        if not documento:
            messagebox.showwarning("Aviso", "Digite um documento")
            return
        
        if tipo == "fisica":
            valido, msg = ValidadorDocumento.validar_cpf(documento)
        else:
            valido, msg = ValidadorDocumento.validar_cnpj(documento)
        
        if valido:
            messagebox.showinfo("Válido", msg)
        else:
            messagebox.showerror("Inválido", msg)
    
    def novo_cliente(self):
        """Novo cliente"""
        self.criando_novo = True
        self.limpar_formulario()
    
    def editar_cliente_selecionado(self):
        """Edita cliente selecionado"""
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
        
        self.editar_cliente(self.cliente_selecionado)
    
    def editar_cliente(self, cliente_id: int):
        """Carrega cliente para edição"""
        cliente = self.servico.obter(cliente_id)
        
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado")
            return
        
        # Preenche formulário
        self.var_tipo.set(cliente['tipo_pessoa'])
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, cliente['nome'])
        self.entry_documento.delete(0, tk.END)
        self.entry_documento.insert(0, cliente['documento'])
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, cliente['email'])
        self.entry_telefone.delete(0, tk.END)
        self.entry_telefone.insert(0, cliente['telefone'])
        self.entry_cep.delete(0, tk.END)
        self.entry_cep.insert(0, cliente['cep'])
        self.entry_logradouro.delete(0, tk.END)
        self.entry_logradouro.insert(0, cliente['logradouro'])
        self.entry_numero.delete(0, tk.END)
        self.entry_numero.insert(0, cliente['numero'])
        self.entry_complemento.delete(0, tk.END)
        self.entry_complemento.insert(0, cliente['complemento'] or '')
        self.entry_bairro.delete(0, tk.END)
        self.entry_bairro.insert(0, cliente['bairro'])
        self.entry_cidade.delete(0, tk.END)
        self.entry_cidade.insert(0, cliente['cidade'])
        self.entry_uf.delete(0, tk.END)
        self.entry_uf.insert(0, cliente['uf'])
        self.var_status.set(cliente['status'])
        self.text_observacoes.delete(1.0, tk.END)
        self.text_observacoes.insert(1.0, cliente['observacoes'] or '')
        
        self.cliente_selecionado = cliente_id
        self.criando_novo = False
    
    def salvar_cliente(self):
        """Salva cliente novo ou atualiza existente"""
        # Coleta dados
        try:
            cliente = Cliente(
                nome=self.entry_nome.get(),
                tipo_pessoa=TipoPessoa(self.var_tipo.get()),
                documento=self.entry_documento.get(),
                email=self.entry_email.get(),
                telefone=self.entry_telefone.get(),
                cep=self.entry_cep.get(),
                logradouro=self.entry_logradouro.get(),
                numero=self.entry_numero.get(),
                complemento=self.entry_complemento.get(),
                bairro=self.entry_bairro.get(),
                cidade=self.entry_cidade.get(),
                uf=self.entry_uf.get(),
                status=StatusCliente(self.var_status.get()),
                observacoes=self.text_observacoes.get(1.0, tk.END)
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler dados: {str(e)}")
            return
        
        if self.criando_novo or not self.cliente_selecionado:
            sucesso, msg = self.servico.criar(cliente)
        else:
            sucesso, msg = self.servico.atualizar(self.cliente_selecionado, cliente)
        
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_lista()
            self.limpar_formulario()
        else:
            messagebox.showerror("Erro", msg)
    
    def desativar_cliente(self):
        """Desativa cliente selecionado"""
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
        
        if messagebox.askyesno("Confirmar", "Desativar este cliente?"):
            sucesso, msg = self.servico.deletar(self.cliente_selecionado)
            
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.atualizar_lista()
                self.limpar_formulario()
            else:
                messagebox.showerror("Erro", msg)
    
    def limpar_formulario(self):
        """Limpa formulário"""
        self.var_tipo.set("fisica")
        self.entry_nome.delete(0, tk.END)
        self.entry_documento.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_cep.delete(0, tk.END)
        self.entry_logradouro.delete(0, tk.END)
        self.entry_numero.delete(0, tk.END)
        self.entry_complemento.delete(0, tk.END)
        self.entry_bairro.delete(0, tk.END)
        self.entry_cidade.delete(0, tk.END)
        self.entry_uf.delete(0, tk.END)
        self.var_status.set("ativo")
        self.text_observacoes.delete(1.0, tk.END)
        self.cliente_selecionado = None
        self.criando_novo = True
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.limpar_formulario()
        self.cliente_selecionado = None
    
    def atualizar_lista(self):
        """Atualiza lista de clientes"""
        self.filtrar_clientes()
    
    def filtrar_clientes(self):
        """Filtra clientes conforme texto de busca"""
        termo_busca = self.var_busca.get().lower()
        
        clientes = self.servico.listar(limite=1000)
        
        # Limpa tree
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        # Insere clientes filtrados
        for cliente in clientes:
            if termo_busca == "" or \
               termo_busca in cliente['nome'].lower() or \
               termo_busca in cliente['documento'] or \
               termo_busca in cliente['email'].lower():
                
                self.tree_clientes.insert(
                    "",
                    tk.END,
                    values=(
                        cliente['id'],
                        cliente['nome'],
                        cliente['documento'],
                        cliente['email'],
                        cliente['status']
                    )
                )
    
    def on_cliente_selecionado(self, event):
        """Evento de seleção de cliente"""
        selecionado = self.tree_clientes.selection()
        if selecionado:
            item = self.tree_clientes.item(selecionado[0])
            cliente_id = item['values'][0]
            self.cliente_selecionado = cliente_id
            self.editar_cliente(cliente_id)

    def exportar_excel(self):
        """Exporta clientes para Excel"""
        from tkinter import filedialog
        from app.services.export_excel_profissional import gerar_planilha_clientes
        from pathlib import Path
        
        try:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
                initialfile=f"Clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not arquivo:
                return
            
            # Obter dados
            clientes = self.servico.listar_ativos()

            # Gerar planilha executiva
            gerar_planilha_clientes(clientes, Path(arquivo))
            messagebox.showinfo("Sucesso", f"Clientes exportados com sucesso!\n\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

