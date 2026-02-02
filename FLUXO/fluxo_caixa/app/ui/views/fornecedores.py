"""
Tela de Fornecedores
Interface idêntica aos cadastros de Clientes e Funcionários
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import requests

from app.models.fornecedor import Fornecedor, TipoPessoa
from app.services.fornecedor import ServicoFornecedor
from app.utils.validators import ValidadorDocumento


class TelaFornecedores:
    """Interface de gerenciamento de fornecedores"""
    
    def __init__(self, parent, servico_fornecedor: ServicoFornecedor):
        self.parent = parent
        self.servico = servico_fornecedor
        self.fornecedor_selecionado = None
        self.thread_cep = None
    
    def criar_interface(self, frame_principal):
        """Cria interface do cadastro de fornecedores"""
        frame_principal.grid_rowconfigure(1, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        
        # === Barra de Ferramentas ===
        self._criar_toolbar(frame_principal)
        
        # === Frame Principal com Grid ===
        frame_conteudo = ttk.Frame(frame_principal)
        frame_conteudo.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        frame_conteudo.grid_columnconfigure(0, weight=1)
        frame_conteudo.grid_rowconfigure(1, weight=1)
        
        # === Painel de Filtros ===
        self._criar_painel_filtros(frame_conteudo)
        
        # === Painel de Listagem ===
        self._criar_painel_listagem(frame_conteudo)
        
        # === Painel de Formulário ===
        self._criar_painel_formulario(frame_conteudo)
        
        # Carregar dados iniciais
        self.atualizar_lista()
    
    def _criar_toolbar(self, parent):
        """Cria toolbar com botões de ação"""
        frame_toolbar = ttk.Frame(parent)
        frame_toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Button(frame_toolbar, text="+ Novo", command=self.novo_fornecedor).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_toolbar, text="Editar", command=self.editar_fornecedor).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_toolbar, text="Excluir", command=self.excluir_fornecedor).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_toolbar, text="Inativar", command=self.inativar_fornecedor).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_toolbar, text="📊 Excel", command=self.exportar_excel).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_toolbar, text="Atualizar", command=self.atualizar_lista).pack(side=tk.LEFT, padx=2)
    
    def _criar_painel_filtros(self, parent):
        """Cria painel de filtros"""
        frame_filtros = ttk.LabelFrame(parent, text="Filtros", padding=5)
        frame_filtros.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        frame_filtros.grid_columnconfigure(1, weight=1)
        
        ttk.Label(frame_filtros, text="Buscar:").grid(row=0, column=0, sticky='w', padx=2)
        self.entry_busca = ttk.Entry(frame_filtros)
        self.entry_busca.grid(row=0, column=1, sticky='ew', padx=2)
        self.entry_busca.bind('<KeyRelease>', lambda e: self.filtrar_lista())
        
        ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=2, sticky='w', padx=2)
        self.combo_tipo_filtro = ttk.Combobox(frame_filtros, values=["Todos", "Pessoa Física", "Pessoa Jurídica"], state='readonly', width=20)
        self.combo_tipo_filtro.grid(row=0, column=3, sticky='w', padx=2)
        self.combo_tipo_filtro.set("Todos")
        self.combo_tipo_filtro.bind('<<ComboboxSelected>>', lambda e: self.filtrar_lista())
    
    def _criar_painel_listagem(self, parent):
        """Cria painel com listagem de fornecedores"""
        frame_lista = ttk.LabelFrame(parent, text="Fornecedores Cadastrados", padding=5)
        frame_lista.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        # Treeview
        colunas = ("ID", "Tipo", "Nome", "CPF/CNPJ", "Telefone", "Email", "Status")
        self.tree_fornecedores = ttk.Treeview(frame_lista, columns=colunas, height=12, show='headings')
        
        # Configurar colunas
        self.tree_fornecedores.column("ID", width=30, anchor=tk.CENTER)
        self.tree_fornecedores.column("Tipo", width=100, anchor=tk.CENTER)
        self.tree_fornecedores.column("Nome", width=200, anchor=tk.W)
        self.tree_fornecedores.column("CPF/CNPJ", width=120, anchor=tk.CENTER)
        self.tree_fornecedores.column("Telefone", width=120, anchor=tk.CENTER)
        self.tree_fornecedores.column("Email", width=180, anchor=tk.W)
        self.tree_fornecedores.column("Status", width=80, anchor=tk.CENTER)
        
        # Headers
        for col in colunas:
            self.tree_fornecedores.heading(col, text=col)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_fornecedores.yview)
        scrollbar_x = ttk.Scrollbar(frame_lista, orient=tk.HORIZONTAL, command=self.tree_fornecedores.xview)
        self.tree_fornecedores.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        # Layout
        self.tree_fornecedores.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Eventos
        self.tree_fornecedores.bind('<<TreeviewSelect>>', self._on_selecionar_fornecedor)
    
    def _criar_painel_formulario(self, parent):
        """Cria painel de formulário"""
        frame_form = ttk.LabelFrame(parent, text="Dados do Fornecedor", padding=10)
        frame_form.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        frame_form.grid_columnconfigure((1, 3), weight=1)
        
        # Tipo de Pessoa
        ttk.Label(frame_form, text="Tipo:").grid(row=0, column=0, sticky='w', pady=2)
        self.combo_tipo = ttk.Combobox(frame_form, values=["Pessoa Física", "Pessoa Jurídica"], state='readonly', width=20)
        self.combo_tipo.grid(row=0, column=1, sticky='ew', pady=2, padx=5)
        self.combo_tipo.bind('<<ComboboxSelected>>', self._on_tipo_mudado)
        
        # Nome
        ttk.Label(frame_form, text="Nome Completo:").grid(row=0, column=2, sticky='w', pady=2)
        self.entry_nome = ttk.Entry(frame_form, width=40)
        self.entry_nome.grid(row=0, column=3, sticky='ew', pady=2, padx=5)
        
        # CPF/CNPJ
        ttk.Label(frame_form, text="CPF/CNPJ:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_cpf_cnpj = ttk.Entry(frame_form, width=20)
        self.entry_cpf_cnpj.grid(row=1, column=1, sticky='w', pady=2, padx=5)
        
        # Nome Fantasia (PJ)
        ttk.Label(frame_form, text="Nome Fantasia:").grid(row=1, column=2, sticky='w', pady=2)
        self.entry_nome_fantasia = ttk.Entry(frame_form, width=40)
        self.entry_nome_fantasia.grid(row=1, column=3, sticky='ew', pady=2, padx=5)
        
        # CEP
        ttk.Label(frame_form, text="CEP:").grid(row=2, column=0, sticky='w', pady=2)
        frame_cep = ttk.Frame(frame_form)
        frame_cep.grid(row=2, column=1, sticky='ew', pady=2, padx=5)
        frame_cep.grid_columnconfigure(0, weight=1)
        
        self.entry_cep = ttk.Entry(frame_cep, width=15)
        self.entry_cep.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(frame_cep, text="Buscar", width=8, command=self.buscar_cep).pack(side=tk.LEFT, padx=2)
        
        # Endereço
        ttk.Label(frame_form, text="Endereço:").grid(row=2, column=2, sticky='w', pady=2)
        self.entry_endereco = ttk.Entry(frame_form, width=40)
        self.entry_endereco.grid(row=2, column=3, sticky='ew', pady=2, padx=5)
        
        # Número e Complemento
        ttk.Label(frame_form, text="Número:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_numero = ttk.Entry(frame_form, width=10)
        self.entry_numero.grid(row=3, column=1, sticky='w', pady=2, padx=5)
        
        ttk.Label(frame_form, text="Complemento:").grid(row=3, column=2, sticky='w', pady=2)
        self.entry_complemento = ttk.Entry(frame_form, width=40)
        self.entry_complemento.grid(row=3, column=3, sticky='ew', pady=2, padx=5)
        
        # Bairro, Cidade, Estado
        ttk.Label(frame_form, text="Bairro:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_bairro = ttk.Entry(frame_form, width=20)
        self.entry_bairro.grid(row=4, column=1, sticky='ew', pady=2, padx=5)
        
        ttk.Label(frame_form, text="Cidade:").grid(row=4, column=2, sticky='w', pady=2)
        self.entry_cidade = ttk.Entry(frame_form, width=20)
        self.entry_cidade.grid(row=4, column=3, sticky='ew', pady=2, padx=5)
        
        ttk.Label(frame_form, text="Estado:").grid(row=5, column=0, sticky='w', pady=2)
        self.entry_estado = ttk.Entry(frame_form, width=10)
        self.entry_estado.grid(row=5, column=1, sticky='w', pady=2, padx=5)
        
        # Telefone e Email
        ttk.Label(frame_form, text="Telefone:").grid(row=5, column=2, sticky='w', pady=2)
        self.entry_telefone = ttk.Entry(frame_form, width=20)
        self.entry_telefone.grid(row=5, column=3, sticky='w', pady=2, padx=5)
        
        ttk.Label(frame_form, text="Email:").grid(row=6, column=0, sticky='w', pady=2)
        self.entry_email = ttk.Entry(frame_form, width=40)
        self.entry_email.grid(row=6, column=1, columnspan=3, sticky='ew', pady=2, padx=5)
        
        # Observações
        ttk.Label(frame_form, text="Observações:").grid(row=7, column=0, sticky='nw', pady=2)
        self.text_observacoes = tk.Text(frame_form, height=3, width=100)
        self.text_observacoes.grid(row=7, column=1, columnspan=3, sticky='ew', pady=2, padx=5)
        
        # Status
        ttk.Label(frame_form, text="Status:").grid(row=8, column=0, sticky='w', pady=2)
        self.combo_status = ttk.Combobox(frame_form, values=["ativo", "inativo"], state='readonly', width=20)
        self.combo_status.grid(row=8, column=1, sticky='w', pady=2, padx=5)
        self.combo_status.set("ativo")
        
        # Botões
        frame_botoes = ttk.Frame(frame_form)
        frame_botoes.grid(row=9, column=0, columnspan=4, sticky='ew', pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar_formulario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_edicao).pack(side=tk.LEFT, padx=5)
    
    def _on_tipo_mudado(self, event=None):
        """Executa quando o tipo de pessoa muda"""
        tipo = self.combo_tipo.get()
        if tipo == "Pessoa Jurídica":
            self.entry_nome_fantasia.config(state=tk.NORMAL)
        else:
            self.entry_nome_fantasia.config(state=tk.DISABLED)
            self.entry_nome_fantasia.delete(0, tk.END)
    
    def _on_selecionar_fornecedor(self, event=None):
        """Executa quando um fornecedor é selecionado"""
        selecionado = self.tree_fornecedores.selection()
        if not selecionado:
            return
        
        item = selecionado[0]
        valores = self.tree_fornecedores.item(item, 'values')
        fornecedor_id = int(valores[0])
        
        self.fornecedor_selecionado = self.servico.obter_por_id(fornecedor_id)
        if self.fornecedor_selecionado:
            self._preencher_formulario(self.fornecedor_selecionado)
    
    def _preencher_formulario(self, fornecedor: Fornecedor):
        """Preenche formulário com dados do fornecedor"""
        self.combo_tipo.set("Pessoa Jurídica" if fornecedor.tipo == TipoPessoa.JURIDICA else "Pessoa Física")
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, fornecedor.nome)
        self.entry_cpf_cnpj.delete(0, tk.END)
        self.entry_cpf_cnpj.insert(0, fornecedor.cpf_cnpj)
        self.entry_nome_fantasia.delete(0, tk.END)
        if fornecedor.nome_fantasia:
            self.entry_nome_fantasia.insert(0, fornecedor.nome_fantasia)
        self.entry_cep.delete(0, tk.END)
        if fornecedor.cep:
            self.entry_cep.insert(0, fornecedor.cep)
        self.entry_endereco.delete(0, tk.END)
        if fornecedor.endereco:
            self.entry_endereco.insert(0, fornecedor.endereco)
        self.entry_numero.delete(0, tk.END)
        if fornecedor.numero:
            self.entry_numero.insert(0, fornecedor.numero)
        self.entry_complemento.delete(0, tk.END)
        if fornecedor.complemento:
            self.entry_complemento.insert(0, fornecedor.complemento)
        self.entry_bairro.delete(0, tk.END)
        if fornecedor.bairro:
            self.entry_bairro.insert(0, fornecedor.bairro)
        self.entry_cidade.delete(0, tk.END)
        if fornecedor.cidade:
            self.entry_cidade.insert(0, fornecedor.cidade)
        self.entry_estado.delete(0, tk.END)
        if fornecedor.estado:
            self.entry_estado.insert(0, fornecedor.estado)
        self.entry_telefone.delete(0, tk.END)
        self.entry_telefone.insert(0, fornecedor.telefone)
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, fornecedor.email)
        self.text_observacoes.delete(1.0, tk.END)
        if fornecedor.observacoes:
            self.text_observacoes.insert(1.0, fornecedor.observacoes)
        self.combo_status.set(fornecedor.status)
    
    def buscar_cep(self):
        """Busca endereço via API a partir do CEP"""
        cep = self.entry_cep.get().replace("-", "")
        if not cep or len(cep) != 8:
            messagebox.showwarning("Aviso", "CEP inválido")
            return
        
        def _buscar():
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                if response.status_code == 200:
                    dados = response.json()
                    if "erro" not in dados:
                        self.entry_endereco.delete(0, tk.END)
                        self.entry_endereco.insert(0, dados.get("logradouro", ""))
                        self.entry_bairro.delete(0, tk.END)
                        self.entry_bairro.insert(0, dados.get("bairro", ""))
                        self.entry_cidade.delete(0, tk.END)
                        self.entry_cidade.insert(0, dados.get("localidade", ""))
                        self.entry_estado.delete(0, tk.END)
                        self.entry_estado.insert(0, dados.get("uf", ""))
            except:
                messagebox.showerror("Erro", "Erro ao buscar CEP")
        
        self.thread_cep = threading.Thread(target=_buscar, daemon=True)
        self.thread_cep.start()
    
    def novo_fornecedor(self):
        """Cria novo fornecedor"""
        self.fornecedor_selecionado = None
        self.limpar_formulario()
        self.tree_fornecedores.selection_remove(self.tree_fornecedores.selection())
    
    def editar_fornecedor(self):
        """Edita fornecedor selecionado"""
        if not self.fornecedor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um fornecedor")
            return
    
    def excluir_fornecedor(self):
        """Exclui fornecedor selecionado"""
        if not self.fornecedor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um fornecedor")
            return
        
        if messagebox.askyesno("Confirmação", f"Excluir {self.fornecedor_selecionado.nome}?"):
            try:
                self.servico.deletar(self.fornecedor_selecionado.id)
                messagebox.showinfo("Sucesso", "Fornecedor excluído")
                self.atualizar_lista()
                self.limpar_formulario()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
    
    def inativar_fornecedor(self):
        """Inativa fornecedor selecionado"""
        if not self.fornecedor_selecionado:
            messagebox.showwarning("Aviso", "Selecione um fornecedor")
            return
        
        if messagebox.askyesno("Confirmação", f"Inativar {self.fornecedor_selecionado.nome}?"):
            try:
                self.servico.inativar(self.fornecedor_selecionado.id)
                messagebox.showinfo("Sucesso", "Fornecedor inativado")
                self.atualizar_lista()
                self.limpar_formulario()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao inativar: {str(e)}")
    
    def salvar_fornecedor(self):
        """Salva fornecedor"""
        try:
            # Validação básica da UI
            if not self.combo_tipo.get():
                messagebox.showwarning("Aviso", "Selecione o tipo de pessoa (Física ou Jurídica)")
                return

            tipo = TipoPessoa.JURIDICA if self.combo_tipo.get() == "Pessoa Jurídica" else TipoPessoa.FISICA

            fornecedor = Fornecedor(
                tipo=tipo,
                nome=self.entry_nome.get(),
                cpf_cnpj=self.entry_cpf_cnpj.get(),
                nome_fantasia=self.entry_nome_fantasia.get() if tipo == TipoPessoa.JURIDICA else None,
                telefone=self.entry_telefone.get(),
                email=self.entry_email.get(),
                cep=self.entry_cep.get(),
                endereco=self.entry_endereco.get(),
                numero=self.entry_numero.get(),
                complemento=self.entry_complemento.get(),
                bairro=self.entry_bairro.get(),
                cidade=self.entry_cidade.get(),
                estado=self.entry_estado.get(),
                observacoes=self.text_observacoes.get(1.0, tk.END),
                status=self.combo_status.get()
            )

            if self.fornecedor_selecionado:
                fornecedor.id = self.fornecedor_selecionado.id
                self.servico.atualizar(fornecedor)
                messagebox.showinfo("Sucesso", "Fornecedor atualizado")
            else:
                self.servico.criar(fornecedor)
                messagebox.showinfo("Sucesso", "Fornecedor criado")

            self.atualizar_lista()
            self.limpar_formulario()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def limpar_formulario(self):
        """Limpa formulário"""
        self.combo_tipo.set("")
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf_cnpj.delete(0, tk.END)
        self.entry_nome_fantasia.delete(0, tk.END)
        self.entry_cep.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.entry_numero.delete(0, tk.END)
        self.entry_complemento.delete(0, tk.END)
        self.entry_bairro.delete(0, tk.END)
        self.entry_cidade.delete(0, tk.END)
        self.entry_estado.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.text_observacoes.delete(1.0, tk.END)
        self.combo_status.set("ativo")
        self.fornecedor_selecionado = None
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.limpar_formulario()
        self.tree_fornecedores.selection_remove(self.tree_fornecedores.selection())
    
    def atualizar_lista(self):
        """Atualiza lista de fornecedores"""
        # Limpar treeview
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)
        
        fornecedores = self.servico.listar_todos(apenas_ativos=False)
        
        for f in fornecedores:
            self.tree_fornecedores.insert("", tk.END, values=(
                f.id,
                "PF" if f.tipo == TipoPessoa.FISICA else "PJ",
                f.nome,
                f.cpf_cnpj,
                f.telefone,
                f.email,
                f.status
            ))
    
    def filtrar_lista(self):
        """Filtra lista de fornecedores"""
        busca = self.entry_busca.get().lower()
        tipo_filtro = self.combo_tipo_filtro.get()
        
        # Limpar treeview
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)
        
        fornecedores = self.servico.listar_todos(apenas_ativos=False)
        
        for f in fornecedores:
            # Filtrar por tipo
            if tipo_filtro != "Todos":
                if tipo_filtro == "Pessoa Física" and f.tipo != TipoPessoa.FISICA:
                    continue
                if tipo_filtro == "Pessoa Jurídica" and f.tipo != TipoPessoa.JURIDICA:
                    continue
            
            # Filtrar por busca
            if busca and busca not in f.nome.lower() and busca not in f.cpf_cnpj:
                continue
            
            self.tree_fornecedores.insert("", tk.END, values=(
                f.id,
                "PF" if f.tipo == TipoPessoa.FISICA else "PJ",
                f.nome,
                f.cpf_cnpj,
                f.telefone,
                f.email,
                f.status
            ))

    def exportar_excel(self):
        """Exporta fornecedores para Excel"""
        from tkinter import filedialog
        from app.services.export_excel_profissional import gerar_planilha_fornecedores
        from pathlib import Path
        
        try:
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
                initialfile=f"Fornecedores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not arquivo:
                return
            
            fornecedores = self.servico.listar_todos(apenas_ativos=True)

            gerar_planilha_fornecedores(fornecedores, Path(arquivo))
            messagebox.showinfo("Sucesso", f"Fornecedores exportados com sucesso!\n\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

