"""
Tela de Lançamentos (Fluxo de Caixa)
Interface para registrar receitas e despesas com sistema de categorias
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.models.lancamento import Lancamento, TipoLancamento
from app.services.lancamento import ServicoLancamento
from app.services.categoria import ServicoCategoria
from app.services.cliente import ServicoCliente
from app.services.fornecedor import ServicoFornecedor


class TelaLancamentos:
    """Interface de lançamentos financeiros com categorias"""
    
    def __init__(self, parent, db, servico_lancamento: ServicoLancamento, 
                 servico_categoria: ServicoCategoria, servico_cliente: ServicoCliente,
                 servico_fornecedor: ServicoFornecedor):
        self.parent = parent
        self.db = db
        self.servico_lancamento = servico_lancamento
        self.servico_categoria = servico_categoria
        self.servico_cliente = servico_cliente
        self.servico_fornecedor = servico_fornecedor
        self.lancamento_selecionado = None
        self.categorias_cache = {}
        
    def criar_interface(self, frame_principal):
        """Cria a interface de lançamentos"""
        # Frame esquerdo - Lista
        frame_esquerdo = ttk.Frame(frame_principal)
        frame_esquerdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._criar_lista(frame_esquerdo)
        
        # Frame direito - Formulário
        frame_direito = ttk.Frame(frame_principal)
        frame_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._criar_formulario(frame_direito)
        
        # Carrega dados
        self.atualizar_lista()
    
    def _criar_lista(self, parent):
        """Cria painel com lista de lançamentos"""
        frame = ttk.LabelFrame(parent, text="Lançamentos Registrados", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de ferramentas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="✓ Novo", command=self.novo_lancamento).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✎ Editar", command=self.editar_selecionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✗ Deletar", command=self.deletar_lancamento).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Atualizar", command=self.atualizar_lista).pack(side=tk.LEFT, padx=2)

        # Busca
        frame_busca = ttk.Frame(frame)
        frame_busca.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(frame_busca, text="Buscar:").pack(side=tk.LEFT, padx=2)
        self.var_busca = tk.StringVar()
        self.var_busca.trace('w', lambda *args: self.filtrar_lancamentos())
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca)
        entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Treeview
        frame_tree = ttk.Frame(frame)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            frame_tree,
            columns=("ID", "Data", "Tipo", "Categoria", "Descrição", "Valor"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configurar colunas
        self.tree.column("#0", width=0)
        self.tree.column("ID", width=40, anchor=tk.CENTER)
        self.tree.column("Data", width=80, anchor=tk.CENTER)
        self.tree.column("Tipo", width=70, anchor=tk.CENTER)
        self.tree.column("Categoria", width=100, anchor=tk.W)
        self.tree.column("Descrição", width=150, anchor=tk.W)
        self.tree.column("Valor", width=100, anchor=tk.E)
        
        self.tree.heading("#0", text="")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Valor", text="Valor")
        
        self.tree.bind('<<TreeviewSelect>>', self._on_selecionado)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Resumo
        frame_resumo = ttk.LabelFrame(frame, text="Resumo Financeiro", padding=5)
        frame_resumo.pack(fill=tk.X, pady=(5, 0))
        
        self.label_resumo = ttk.Label(frame_resumo, text="Carregando...", font=("Arial", 10, "bold"))
        self.label_resumo.pack()
    
    def _criar_formulario(self, parent):
        """Cria formulário de entrada organizado em blocos lógicos"""
        frame = ttk.LabelFrame(parent, text="Novo Lançamento", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Canvas com scroll
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # === Bloco 1: Tipo/Data ===
        bloco_tipo_data = ttk.LabelFrame(scrollable, text="Tipo e Data", padding=10)
        bloco_tipo_data.pack(fill=tk.X, pady=(0, 10))

        # Tipo de Lançamento
        ttk.Label(bloco_tipo_data, text="Tipo:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.var_tipo = tk.StringVar(value="Receita")
        frame_tipo = ttk.Frame(bloco_tipo_data)
        frame_tipo.grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Radiobutton(frame_tipo, text="Receita", variable=self.var_tipo, value="Receita",
                       command=self._atualizar_categorias).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_tipo, text="Despesa", variable=self.var_tipo, value="Despesa",
                       command=self._atualizar_categorias).pack(side=tk.LEFT, padx=5)

        # Data
        ttk.Label(bloco_tipo_data, text="Data (YYYY-MM-DD):", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_data = ttk.Entry(bloco_tipo_data)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=1, column=1, sticky=tk.EW, pady=2)
        bloco_tipo_data.columnconfigure(1, weight=1)

        # === Bloco 2: Classificação ===
        bloco_classificacao = ttk.LabelFrame(scrollable, text="Classificação", padding=10)
        bloco_classificacao.pack(fill=tk.X, pady=(0, 10))

        # Categoria
        ttk.Label(bloco_classificacao, text="Categoria:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.var_categoria = tk.StringVar()
        self.combo_categoria = ttk.Combobox(bloco_classificacao, textvariable=self.var_categoria, state="readonly")
        self.combo_categoria.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._atualizar_subcategorias())

        # Subcategoria
        ttk.Label(bloco_classificacao, text="Subcategoria:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.var_subcategoria = tk.StringVar()
        self.combo_subcategoria = ttk.Combobox(bloco_classificacao, textvariable=self.var_subcategoria, state="readonly")
        self.combo_subcategoria.grid(row=1, column=1, sticky=tk.EW, pady=2)
        bloco_classificacao.columnconfigure(1, weight=1)

        # === Bloco 3: Valor/Origem ===
        bloco_valor_origem = ttk.LabelFrame(scrollable, text="Valor e Origem", padding=10)
        bloco_valor_origem.pack(fill=tk.X, pady=(0, 10))

        # Valor
        ttk.Label(bloco_valor_origem, text="Valor (R$):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_valor = ttk.Entry(bloco_valor_origem)
        self.entry_valor.grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Cliente/Fornecedor
        ttk.Label(bloco_valor_origem, text="Cliente/Fornecedor:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.var_entidade = tk.StringVar()
        self.combo_entidade = ttk.Combobox(bloco_valor_origem, textvariable=self.var_entidade, state="readonly")
        self.combo_entidade.grid(row=1, column=1, sticky=tk.EW, pady=2)
        bloco_valor_origem.columnconfigure(1, weight=1)

        # === Bloco 4: Complementares ===
        bloco_complementares = ttk.LabelFrame(scrollable, text="Informações Complementares", padding=10)
        bloco_complementares.pack(fill=tk.X, pady=(0, 10))

        # Descrição
        ttk.Label(bloco_complementares, text="Descrição:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_descricao = ttk.Entry(bloco_complementares)
        self.entry_descricao.grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Nota Fiscal
        ttk.Label(bloco_complementares, text="Nota Fiscal:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_nf = ttk.Entry(bloco_complementares)
        self.entry_nf.grid(row=1, column=1, sticky=tk.EW, pady=2)

        # Banco
        ttk.Label(bloco_complementares, text="Banco:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_banco = ttk.Entry(bloco_complementares)
        self.entry_banco.grid(row=2, column=1, sticky=tk.EW, pady=2)

        # Observação
        ttk.Label(bloco_complementares, text="Observação:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.NW, pady=2)
        self.text_obs = tk.Text(bloco_complementares, height=3, width=30)
        self.text_obs.grid(row=3, column=1, sticky=tk.EW, pady=2)
        bloco_complementares.columnconfigure(1, weight=1)

        # === Bloco 5: Ação ===
        bloco_acao = ttk.LabelFrame(scrollable, text="Ação", padding=10)
        bloco_acao.pack(fill=tk.X, pady=(0, 10))

        # Botão Adicionar Lançamento
        self.btn_adicionar = ttk.Button(bloco_acao, text="Adicionar Lançamento", command=self.adicionar_lancamento,
                                       style="Accent.TButton")
        self.btn_adicionar.pack(fill=tk.X, pady=5)

        canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Carrega categorias
        self._atualizar_categorias()
        self._carrega_entidades()
    
    def _atualizar_categorias(self):
        """Atualiza lista de categorias baseado no tipo selecionado"""
        tipo = self.var_tipo.get()
        categorias = self.servico_categoria.obter_todas_categorias()
        
        if tipo == "Receita":
            categorias = [c for c in categorias if c.tipo.value == "Receita"]
        else:
            categorias = [c for c in categorias if c.tipo.value != "Receita"]
        
        nomes = [c.nome for c in categorias]
        self.combo_categoria['values'] = nomes
        self.categorias_cache = {c.nome: c.id for c in categorias}
        
        if nomes:
            self.combo_categoria.current(0)
            self._atualizar_subcategorias()
    
    def _atualizar_subcategorias(self):
        """Atualiza lista de subcategorias baseado na categoria selecionada"""
        cat_nome = self.var_categoria.get()
        if not cat_nome or cat_nome not in self.categorias_cache:
            return
        
        cat_id = self.categorias_cache[cat_nome]
        subcategorias = self.servico_categoria.obter_subcategorias_da_categoria(cat_id)
        nomes = [s.nome for s in subcategorias]
        
        self.combo_subcategoria['values'] = nomes
        if nomes:
            self.combo_subcategoria.current(0)
    
    def _carrega_entidades(self):
        """Carrega clientes e fornecedores"""
        clientes = self.servico_cliente.listar_ativos()
        fornecedores = self.servico_fornecedor.listar_todos(apenas_ativos=True)
        
        nomes = [f"Cliente: {c['nome']}" for c in clientes] + [f"Fornecedor: {f.nome}" for f in fornecedores]
        self.combo_entidade['values'] = nomes
    
    def salvar_lancamento(self):
        """Salva novo lançamento ou edita existente"""
        try:
            # Validações
            if not self.var_categoria.get():
                messagebox.showerror("Erro", "Selecione uma categoria")
                return
            
            if not self.var_subcategoria.get():
                messagebox.showerror("Erro", "Selecione uma subcategoria")
                return
            
            if not self.entry_descricao.get():
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return
            
            try:
                valor = float(self.entry_valor.get().replace(",", "."))
                if valor <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erro", "Valor inválido")
                return
            
            # Obtém IDs
            tipo = TipoLancamento(self.var_tipo.get())
            cat_nome = self.var_categoria.get()
            subcat_nome = self.var_subcategoria.get()
            
            categoria_id = self.categorias_cache[cat_nome]
            
            # Encontra ID da subcategoria
            subcategorias = self.servico_categoria.obter_subcategorias_da_categoria(categoria_id)
            subcategoria_id = next(s.id for s in subcategorias if s.nome == subcat_nome)
            
            # Processa entidade (cliente/fornecedor)
            cliente_id = None
            fornecedor_id = None
            entidade = self.var_entidade.get()
            
            if entidade.startswith("Cliente:"):
                nome = entidade.replace("Cliente: ", "")
                clientes = self.servico_cliente.listar_ativos()
                for cliente in clientes:
                    if cliente['nome'] == nome:
                        cliente_id = cliente['id']
                        break
            elif entidade.startswith("Fornecedor:"):
                nome = entidade.replace("Fornecedor: ", "")
                fornecedores = self.servico_fornecedor.listar_todos(apenas_ativos=True)
                for fornecedor in fornecedores:
                    if fornecedor.nome == nome:
                        fornecedor_id = fornecedor.id
                        break
            
            # Cria lançamento
            lancamento = Lancamento(
                data=self.entry_data.get(),
                tipo=tipo,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                valor=valor,
                descricao=self.entry_descricao.get(),
                cliente_id=cliente_id,
                fornecedor_id=fornecedor_id,
                nota_fiscal=self.entry_nf.get(),
                banco=self.entry_banco.get(),
                observacao=self.text_obs.get("1.0", tk.END),
                id=self.lancamento_selecionado.id if self.lancamento_selecionado else None
            )
            
            # Salva
            if self.lancamento_selecionado:
                sucesso, msg = self.servico_lancamento.atualizar(self.lancamento_selecionado.id, lancamento)
                if sucesso:
                    messagebox.showinfo("Sucesso", msg)
                    self._limpar_formulario()
                    self.lancamento_selecionado = None
                    self.atualizar_lista()
                else:
                    messagebox.showerror("Erro", msg)
            else:
                sucesso, retorno = self.servico_lancamento.criar(lancamento)
                if sucesso:
                    # criar retorna o id do lançamento
                    lanc_id = retorno if isinstance(retorno, int) else None
                    msg = f"Lançamento {lanc_id} criado com sucesso" if lanc_id else "Lançamento criado com sucesso"
                    messagebox.showinfo("Sucesso", msg)
                    self._limpar_formulario()
                    self.lancamento_selecionado = None
                    self.atualizar_lista()
                else:
                    messagebox.showerror("Erro", retorno)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def _on_selecionado(self, event):
        """Evento ao selecionar lançamento"""
        selecionado = self.tree.selection()
        if not selecionado:
            return
        
        item = selecionado[0]
        valores = self.tree.item(item, 'values')
        lancamento_id = int(valores[0])
        
        lancamento = self.servico_lancamento.obter(lancamento_id)
        if lancamento:
            self.lancamento_selecionado = lancamento
            self._carregar_no_formulario(lancamento)
    
    def _carregar_no_formulario(self, lancamento: Lancamento):
        """Carrega dados do lançamento no formulário"""
        self.var_tipo.set(lancamento.tipo.value)
        self._atualizar_categorias()
        
        categoria = self.servico_categoria.obter_categoria(lancamento.categoria_id)
        if categoria:
            self.var_categoria.set(categoria.nome)
            self._atualizar_subcategorias()
        
        subcategoria = self.servico_categoria.obter_subcategoria(lancamento.subcategoria_id)
        if subcategoria:
            self.var_subcategoria.set(subcategoria.nome)
        
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, lancamento.data)
        
        self.entry_descricao.delete(0, tk.END)
        self.entry_descricao.insert(0, lancamento.descricao)
        
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, f"{lancamento.valor:,.2f}")
        
        self.entry_nf.delete(0, tk.END)
        self.entry_nf.insert(0, lancamento.nota_fiscal or "")
        
        self.entry_banco.delete(0, tk.END)
        self.entry_banco.insert(0, lancamento.banco or "")
        
        self.text_obs.delete("1.0", tk.END)
        self.text_obs.insert("1.0", lancamento.observacao or "")
    
    def _limpar_formulario(self):
        """Limpa dados do formulário"""
        self.var_tipo.set("Receita")
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_descricao.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.entry_nf.delete(0, tk.END)
        self.entry_banco.delete(0, tk.END)
        self.text_obs.delete("1.0", tk.END)
        self.lancamento_selecionado = None
        self._atualizar_categorias()

    def adicionar_na_tabela(self):
        """Adiciona o lançamento atual na tabela (persiste e insere linha no Treeview sem limpar o formulário)."""
        try:
            # Reutiliza validações da função salvar_lancamento
            if not self.var_categoria.get():
                messagebox.showerror("Erro", "Selecione uma categoria")
                return

            if not self.var_subcategoria.get():
                messagebox.showerror("Erro", "Selecione uma subcategoria")
                return

            if not self.entry_descricao.get():
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            try:
                valor = float(self.entry_valor.get().replace(",", "."))
                if valor <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erro", "Valor inválido")
                return

            tipo = TipoLancamento(self.var_tipo.get())
            cat_nome = self.var_categoria.get()
            subcat_nome = self.var_subcategoria.get()
            categoria_id = self.categorias_cache[cat_nome]
            subcategorias = self.servico_categoria.obter_subcategorias_da_categoria(categoria_id)
            subcategoria_id = next(s.id for s in subcategorias if s.nome == subcat_nome)

            cliente_id = None
            fornecedor_id = None
            entidade = self.var_entidade.get()
            if entidade.startswith("Cliente:"):
                nome = entidade.replace("Cliente: ", "")
                clientes = self.servico_cliente.listar_ativos()
                for cliente in clientes:
                    if cliente['nome'] == nome:
                        cliente_id = cliente['id']
                        break
            elif entidade.startswith("Fornecedor:"):
                nome = entidade.replace("Fornecedor: ", "")
                fornecedores = self.servico_fornecedor.listar_todos(apenas_ativos=True)
                for fornecedor in fornecedores:
                    if fornecedor.nome == nome:
                        fornecedor_id = fornecedor.id
                        break

            lancamento = Lancamento(
                data=self.entry_data.get(),
                tipo=tipo,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                valor=valor,
                descricao=self.entry_descricao.get(),
                cliente_id=cliente_id,
                fornecedor_id=fornecedor_id,
                nota_fiscal=self.entry_nf.get(),
                banco=self.entry_banco.get(),
                observacao=self.text_obs.get("1.0", tk.END)
            )

            sucesso, retorno = self.servico_lancamento.criar(lancamento)
            if sucesso:
                lanc_id = retorno if isinstance(retorno, int) else None
                # Inserir linha na tree
                categoria = self.servico_categoria.obter_categoria(categoria_id)
                cat_nome_display = categoria.nome if categoria else 'N/A'
                self.tree.insert('', 0, values=(
                    lanc_id or '',
                    lancamento.data,
                    lancamento.tipo.value,
                    cat_nome_display,
                    lancamento.descricao[:50],
                    f"R$ {lancamento.valor:,.2f}"
                ), tags=("Receita" if lancamento.tipo == TipoLancamento.RECEITA else "Despesa",))
                messagebox.showinfo("Sucesso", f"Lançamento {lanc_id or ''} adicionado na tabela")
            else:
                messagebox.showerror("Erro", retorno)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar na tabela: {e}")

    def adicionar_temporario(self):
        """Adiciona o lançamento atual na tabela temporariamente (sem salvar no banco de dados)"""
        try:
            # Validações
            if not self.var_categoria.get():
                messagebox.showerror("Erro", "Selecione uma categoria")
                return

            if not self.var_subcategoria.get():
                messagebox.showerror("Erro", "Selecione uma subcategoria")
                return

            if not self.entry_descricao.get():
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            try:
                valor = float(self.entry_valor.get().replace(",", "."))
                if valor <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erro", "Valor inválido")
                return

            # Obtém dados para exibição
            tipo = self.var_tipo.get()
            cat_nome = self.var_categoria.get()
            subcat_nome = self.var_subcategoria.get()
            data = self.entry_data.get()
            descricao = self.entry_descricao.get()
            valor_formatado = f"R$ {valor:,.2f}"

            # Insere na tree sem salvar no DB
            self.tree.insert('', 0, values=(
                'Temp',  # ID temporário
                data,
                tipo,
                cat_nome,
                descricao[:50],
                valor_formatado
            ), tags=("Receita" if tipo == "Receita" else "Despesa",))

            messagebox.showinfo("Sucesso", "Lançamento adicionado temporariamente à tabela")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar temporariamente: {e}")

    def novo_lancamento(self):
        """Novo lançamento"""
        self._limpar_formulario()
    
    def editar_selecionado(self):
        """Edita lançamento selecionado"""
        if not self.lancamento_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lançamento para editar")
    
    def deletar_lancamento(self):
        """Deleta lançamento selecionado"""
        if not self.lancamento_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lançamento para deletar")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente deletar este lançamento?"):
            sucesso, msg = self.servico_lancamento.deletar(self.lancamento_selecionado.id)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self._limpar_formulario()
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", msg)
    
    def adicionar_lancamento(self):
        """Adiciona novo lançamento com validação completa"""
        try:
            # Validações obrigatórias
            if not self.var_tipo.get():
                messagebox.showerror("Erro", "Selecione o tipo de lançamento")
                return

            if not self.entry_data.get():
                messagebox.showerror("Erro", "Data é obrigatória")
                return

            if not self.entry_valor.get():
                messagebox.showerror("Erro", "Valor é obrigatório")
                return

            if not self.var_categoria.get():
                messagebox.showerror("Erro", "Selecione uma categoria")
                return

            # Validação de valor
            try:
                valor = float(self.entry_valor.get().replace(",", "."))
                if valor <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erro", "Valor inválido")
                return

            # Obtém IDs
            tipo = TipoLancamento(self.var_tipo.get())
            cat_nome = self.var_categoria.get()
            subcat_nome = self.var_subcategoria.get()

            categoria_id = self.categorias_cache[cat_nome]

            # Encontra ID da subcategoria
            subcategorias = self.servico_categoria.obter_subcategorias_da_categoria(categoria_id)
            subcategoria_id = next(s.id for s in subcategorias if s.nome == subcat_nome)

            # Processa entidade (cliente/fornecedor)
            cliente_id = None
            fornecedor_id = None
            entidade = self.var_entidade.get()

            if entidade.startswith("Cliente:"):
                nome = entidade.replace("Cliente: ", "")
                clientes = self.servico_cliente.listar_ativos()
                for cliente in clientes:
                    if cliente['nome'] == nome:
                        cliente_id = cliente['id']
                        break
            elif entidade.startswith("Fornecedor:"):
                nome = entidade.replace("Fornecedor: ", "")
                fornecedores = self.servico_fornecedor.listar_todos(apenas_ativos=True)
                for fornecedor in fornecedores:
                    if fornecedor.nome == nome:
                        fornecedor_id = fornecedor.id
                        break

            # Cria lançamento
            lancamento = Lancamento(
                data=self.entry_data.get(),
                tipo=tipo,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                valor=valor,
                descricao=self.entry_descricao.get(),
                cliente_id=cliente_id,
                fornecedor_id=fornecedor_id,
                nota_fiscal=self.entry_nf.get(),
                banco=self.entry_banco.get(),
                observacao=self.text_obs.get("1.0", tk.END)
            )

            # Salva no banco
            sucesso, retorno = self.servico_lancamento.criar(lancamento)
            if sucesso:
                lanc_id = retorno if isinstance(retorno, int) else None
                messagebox.showinfo("Sucesso", f"Lançamento adicionado com sucesso!")

                # Limpa formulário
                self._limpar_formulario()

                # Atualiza lista
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", retorno)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar lançamento: {str(e)}")

    def atualizar_lista(self):
        """Atualiza lista de lançamentos"""
        # Limpa tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Carrega lançamentos
        lancamentos = self.servico_lancamento.obter_todos()
        termo = ""
        if hasattr(self, "var_busca"):
            termo = self.var_busca.get().strip().lower()

        for lance in lancamentos:
            categoria = self.servico_categoria.obter_categoria(lance.categoria_id)
            cat_nome = categoria.nome if categoria else "N/A"

            if termo:
                descricao = (lance.descricao or "")
                valor_txt = f"{lance.valor:,.2f}"
                linha = f"{lance.id} {lance.data} {lance.tipo.value} {cat_nome} {descricao} {valor_txt}"
                if termo not in linha.lower():
                    continue

            self.tree.insert('', 0, values=(
                lance.id,
                lance.data,
                lance.tipo.value,
                cat_nome,
                lance.descricao[:50],
                f"R$ {lance.valor:,.2f}"
            ), tags=("Receita" if lance.tipo == TipoLancamento.RECEITA else "Despesa",))

        # Atualiza resumo
        receitas = self.servico_lancamento.calcular_total_receitas()
        despesas = self.servico_lancamento.calcular_total_despesas()
        saldo = receitas - despesas

        resumo = f"Receitas: R$ {receitas:,.2f} | Despesas: R$ {despesas:,.2f} | Saldo: R$ {saldo:,.2f}"
        self.label_resumo.config(text=resumo)



    def filtrar_lancamentos(self):
        """Filtra lan?amentos conforme texto de busca"""
        self.atualizar_lista()

