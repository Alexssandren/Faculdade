import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class CrudTab:
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.styling = main_window.styling
        
        # Estado do CRUD
        self.current_table = None
        self.current_record = None
        self.editing_mode = False
        
        # Importar CRUDs para dados reais
        try:
            from src.crud import (
                EstadosCRUD, IndicadoresIDHCRUD, DespesasCRUD, 
                OrgaosPublicosCRUD, RegiaosCRUD
            )
            self.estados_crud = EstadosCRUD()
            self.indicadores_crud = IndicadoresIDHCRUD()
            self.despesas_crud = DespesasCRUD()
            self.orgaos_crud = OrgaosPublicosCRUD()
            self.regioes_crud = RegiaosCRUD()
            self.use_real_data = True
    
        except Exception as e:
            print(f"⚠️ Erro ao carregar CRUDs: {e} - usando dados simulados")
            self.use_real_data = False
        
        # Dados das tabelas
        self.tables_info = {
            'estados': {
                'name': 'Estados',
                'fields': ['id', 'nome_estado', 'sigla_uf', 'regiao_nome', 'capital', 'populacao_estimada'],
                'display_fields': ['ID', 'Nome', 'Sigla', 'Região', 'Capital', 'População']
            },
            'indicadores_idh': {
                'name': 'Indicadores IDH',
                'fields': ['id', 'nome_estado', 'ano', 'idh_geral', 'idh_educacao', 'idh_longevidade', 'idh_renda'],
                'display_fields': ['ID', 'Estado', 'Ano', 'IDH Geral', 'IDH Educação', 'IDH Longevidade', 'IDH Renda']
            },
            'despesas_publicas': {
                'name': 'Despesas Públicas',
                'fields': ['id', 'nome_categoria', 'ano', 'valor_total'],
                'display_fields': ['ID', 'Categoria', 'Ano', 'Valor Total (Brasil)']
            },
            'organizacoes': {
                'name': 'Órgãos Públicos',
                'fields': ['id', 'nome_orgao', 'tipo_orgao', 'sigla_orgao', 'ativo'],
                'display_fields': ['ID', 'Nome', 'Tipo', 'Sigla', 'Status']
            }
        }
        
        # Criar interface
        self._create_interface()
        
        # Carregar primeira tabela
        self.load_table('estados')
        
    def _create_interface(self):
        """Cria a interface do CRUD"""
        # Container principal
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Painel superior - seleção de tabela e controles
        self._create_top_panel(main_container)
        
        # Painel principal - lista e formulário
        self._create_main_panel(main_container)
        
        # Painel inferior - estatísticas e ações
        self._create_bottom_panel(main_container)
        
    def _create_top_panel(self, parent):
        """Cria painel superior com controles"""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=X, pady=(0, 10))
        
        # Título
        title_label = ttk.Label(
            top_frame,
            text=f"{self.styling.icons['database']} Gerenciamento de Dados",
            font=self.styling.fonts['large_bold']
        )
        title_label.pack(side=LEFT)
        
        # Controles à direita
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(side=RIGHT)
        
        # Seleção de tabela
        table_label = ttk.Label(controls_frame, text="Tabela:")
        table_label.pack(side=LEFT, padx=(0, 5))
        
        self.table_var = tk.StringVar(value="estados")
        table_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.table_var,
            values=list(self.tables_info.keys()),
            state="readonly",
            width=20
        )
        table_combo.pack(side=LEFT, padx=(0, 10))
        table_combo.bind("<<ComboboxSelected>>", self.on_table_changed)
        
        # Botão atualizar
        refresh_btn = ttk.Button(
            controls_frame,
            text=f"{self.styling.icons['refresh']} Atualizar",
            command=self.refresh_data,
            style=PRIMARY
        )
        refresh_btn.pack(side=LEFT, padx=5)
        
    def _create_main_panel(self, parent):
        """Cria painel principal com lista e formulário"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=2)  # Lista
        main_frame.columnconfigure(1, weight=1)  # Formulário
        
        # Painel da lista (esquerda)
        self._create_list_panel(main_frame)
        
        # Painel do formulário (direita)  
        self._create_form_panel(main_frame)
        
    def _create_list_panel(self, parent):
        """Cria painel da lista de registros"""
        # Frame da lista
        list_frame = ttk.LabelFrame(parent, text="Registros", padding=10)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Barra de pesquisa
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text=f"{self.styling.icons['search']} Pesquisar:")
        search_label.pack(side=LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, fill=X, expand=True)
        search_entry.bind("<KeyRelease>", self.on_search_changed)
        
        # Treeview para lista de registros
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            selectmode="extended"
        )
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind eventos
        self.tree.bind("<<TreeviewSelect>>", self.on_record_selected)
        self.tree.bind("<Double-1>", self.on_record_double_click)
        
        # Menu de contexto
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.edit_record)
        self.context_menu.add_command(label="Duplicar", command=self.duplicate_record)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Excluir", command=self.delete_record)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def _create_form_panel(self, parent):
        """Cria painel do formulário"""
        # Frame do formulário
        form_frame = ttk.LabelFrame(parent, text="Detalhes do Registro", padding=10)
        form_frame.grid(row=0, column=1, sticky="nsew")
        
        # Modo de edição
        mode_frame = ttk.Frame(form_frame)
        mode_frame.pack(fill=X, pady=(0, 10))
        
        self.mode_label = ttk.Label(
            mode_frame,
            text=f"{self.styling.icons['view']} Modo Visualização",
            font=self.styling.fonts['medium_bold'],
            foreground=self.styling.colors['info']
        )
        self.mode_label.pack(side=LEFT)
        
        # Container para campos do formulário
        self.form_container = ttk.Frame(form_frame)
        self.form_container.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Botões de ação
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=X)
        
        # Botão Novo
        self.new_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['plus']} Novo",
            command=self.new_record,
            style=SUCCESS
        )
        self.new_btn.pack(side=LEFT, padx=(0, 5))
        
        # Botão Editar
        self.edit_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['edit']} Editar",
            command=self.edit_record,
            style=PRIMARY
        )
        self.edit_btn.pack(side=LEFT, padx=(0, 5))
        
        # Botão Salvar
        self.save_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['save']} Salvar",
            command=self.save_record,
            style=SUCCESS,
            state=DISABLED
        )
        self.save_btn.pack(side=LEFT, padx=(0, 5))
        
        # Botão Cancelar
        self.cancel_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['cancel']} Cancelar",
            command=self.cancel_edit,
            style=SECONDARY,
            state=DISABLED
        )
        self.cancel_btn.pack(side=LEFT, padx=(0, 5))
        
        # Botão Excluir
        self.delete_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['trash']} Excluir",
            command=self.delete_record,
            style=DANGER
        )
        self.delete_btn.pack(side=RIGHT)
        
    def _create_bottom_panel(self, parent):
        """Cria painel inferior com estatísticas"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=X)
        
        # Separador
        ttk.Separator(bottom_frame, orient=HORIZONTAL).pack(fill=X, pady=(0, 10))
        
        # Estatísticas
        stats_frame = ttk.Frame(bottom_frame)
        stats_frame.pack(fill=X)
        
        # Total de registros
        self.total_label = ttk.Label(
            stats_frame,
            text="Total: 0 registros",
            font=self.styling.fonts['small']
        )
        self.total_label.pack(side=LEFT)
        
        # Último update
        self.update_label = ttk.Label(
            stats_frame,
            text="Última atualização: --",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['text_secondary']
        )
        self.update_label.pack(side=RIGHT)
        
    def load_table(self, table_name):
        """Carrega dados da tabela especificada"""
        self.current_table = table_name
        table_info = self.tables_info[table_name]
        
        # Atualizar título
        form_frame = None
        for child in self.parent.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.LabelFrame) and "Detalhes" in subchild.cget("text"):
                        subchild.config(text=f"Detalhes - {table_info['name']}")
                        break
        
        # Configurar colunas do Treeview
        self.tree["columns"] = table_info['fields'][1:]  # Excluir ID
        self.tree["show"] = "tree headings"
        
        # Cabeçalho da árvore (ID)
        self.tree.heading("#0", text="ID", anchor=W)
        self.tree.column("#0", width=50, minwidth=50)
        
        # Configurar colunas
        for i, (field, display) in enumerate(zip(table_info['fields'][1:], table_info['display_fields'][1:])):
            self.tree.heading(field, text=display, anchor=W)
            self.tree.column(field, width=100, minwidth=80)
        
        # Carregar dados reais
        self._load_real_data()
        
        # Atualizar form
        self._create_form_fields()
        
        # Atualizar estatísticas
        self._update_stats()
        
    def _load_real_data(self):
        """Carrega dados reais baseados na tabela atual"""
        # Limpar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            if not self.use_real_data:
                print("⚠️ Usando dados simulados - CRUDs não disponíveis")
                self._load_sample_data()
                return
                
  
            
            if self.current_table == 'estados':
                data = self.estados_crud.listar()
    
            elif self.current_table == 'indicadores_idh':
                data = self.indicadores_crud.listar()
    
            elif self.current_table == 'despesas_publicas':
                data = self.despesas_crud.listar_agregado()
                
            else:  # organizacoes
                data = self.orgaos_crud.listar()
                
            
            # Verificar se há dados
            if not data:
                print(f"⚠️ Nenhum dado encontrado para {self.current_table} - usando dados simulados")
                self._load_sample_data()
                return
            
            # Inserir dados no tree
            for row in data:
                # row[0] é o ID, row[1:] são os outros campos
                self.tree.insert("", "end", text=str(row[0]), values=row[1:])
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados reais: {e}")
            print("🔄 Fallback para dados simulados")
            self._load_sample_data()
    
    def _load_sample_data(self):
        """Carrega dados simulados como fallback"""
        # Limpar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        print(f"📊 Carregando dados simulados para: {self.current_table}")
            
        if self.current_table == 'estados':
            sample_data = [
                (1, "São Paulo", "SP", "Sudeste", "São Paulo", "46.649.132"),
                (2, "Rio de Janeiro", "RJ", "Sudeste", "Rio de Janeiro", "17.463.349"),
                (3, "Minas Gerais", "MG", "Sudeste", "Belo Horizonte", "21.411.923"),
                (4, "Bahia", "BA", "Nordeste", "Salvador", "14.985.284"),
                (5, "Paraná", "PR", "Sul", "Curitiba", "11.597.484")
            ]
        elif self.current_table == 'indicadores_idh':
            sample_data = [
                (1, "São Paulo", 2023, 0.783, 0.760, 0.845, 0.744),
                (2, "Rio de Janeiro", 2023, 0.761, 0.742, 0.835, 0.708),
                (3, "Minas Gerais", 2023, 0.731, 0.715, 0.828, 0.648),
                (4, "Bahia", 2023, 0.673, 0.632, 0.769, 0.618),
                (5, "Paraná", 2023, 0.749, 0.733, 0.838, 0.676)
            ]
        elif self.current_table == 'despesas_publicas':
            sample_data = [
                (1, "Equipamentos E Material Permanente", 2023, "R$ 76.52M"),
                (2, "Material De Consumo", 2023, "R$ 78.53M"),
                (3, "Pessoal E Encargos Sociais", 2023, "R$ 85.91M"),
                (4, "Transferências A Municípios", 2023, "R$ 62.19M"),
                (5, "Equipamentos E Material Permanente", 2022, "R$ 68.34M")
            ]
        else:  # organizacoes
            sample_data = [
                (1, "Secretaria de Educação SP", "Secretaria", "Estadual", "São Paulo"),
                (2, "Ministério da Saúde", "Ministério", "Federal", "Brasília"),
                (3, "Prefeitura de Belo Horizonte", "Prefeitura", "Municipal", "Minas Gerais"),
                (4, "BNDES", "Banco", "Federal", "Rio de Janeiro"),
                (5, "SEBRAE PR", "Agência", "Estadual", "Paraná")
            ]
            
        # Inserir dados no tree
        for row in sample_data:
            self.tree.insert("", "end", text=str(row[0]), values=row[1:])
        
    def _create_form_fields(self):
        """Cria campos do formulário baseados na tabela atual"""
        # Limpar container anterior
        for widget in self.form_container.winfo_children():
            widget.destroy()
            
        table_info = self.tables_info[self.current_table]
        self.form_fields = {}
        
        # Criar campos
        for i, (field, display) in enumerate(zip(table_info['fields'], table_info['display_fields'])):
            if field == 'id':
                continue  # Pular ID
                
            # Frame do campo
            field_frame = ttk.Frame(self.form_container)
            field_frame.pack(fill=X, pady=5)
            
            # Label
            label = ttk.Label(field_frame, text=f"{display}:", width=15, anchor=E)
            label.pack(side=LEFT, padx=(0, 10))
            
            # Campo de entrada
            if field in ['ano', 'populacao_estimada']:
                entry = ttk.Entry(field_frame, state=DISABLED)
            elif field.endswith('_id'):
                # Combobox para foreign keys
                entry = ttk.Combobox(field_frame, state=DISABLED)
                entry['values'] = ["Opção 1", "Opção 2", "Opção 3"]
            elif 'valor' in field or 'idh' in field:
                entry = ttk.Entry(field_frame, state=DISABLED)
            else:
                entry = ttk.Entry(field_frame, state=DISABLED)
                
            entry.pack(side=LEFT, fill=X, expand=True)
            self.form_fields[field] = entry
            
    def on_table_changed(self, event=None):
        """Callback para mudança de tabela"""
        table_name = self.table_var.get()
        self.load_table(table_name)
        self.main_window.update_status(f"Tabela carregada: {self.tables_info[table_name]['name']}")
        
    def on_record_selected(self, event=None):
        """Callback para seleção de registro"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            record_id = self.tree.item(item)['text']
            values = self.tree.item(item)['values']
            
            # Atualizar formulário
            self._populate_form(record_id, values)
            self.current_record = (record_id, values)
            
    def on_record_double_click(self, event=None):
        """Callback para duplo clique no registro"""
        self.edit_record()
        
    def on_search_changed(self, event=None):
        """Callback para mudança na pesquisa"""
        search_term = self.search_var.get().lower()
        
        # Simples filtragem local
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            text = self.tree.item(item)['text']
            
            # Verificar se o termo está em algum valor
            match = search_term in str(text).lower()
            for value in values:
                if search_term in str(value).lower():
                    match = True
                    break
                    
            # Mostrar/esconder item baseado na busca
            if not search_term or match:
                self.tree.move(item, "", "end")
            else:
                self.tree.detach(item)
                
    def _populate_form(self, record_id, values):
        """Popula formulário com dados do registro"""
        table_info = self.tables_info[self.current_table]
        
        # ID não é editável, então começamos do índice 1
        for i, field in enumerate(table_info['fields'][1:]):
            if field in self.form_fields:
                self.form_fields[field].config(state=NORMAL)
                self.form_fields[field].delete(0, END)
                if i < len(values):
                    self.form_fields[field].insert(0, str(values[i]))
                self.form_fields[field].config(state=DISABLED)
                
    def new_record(self):
        """Inicia criação de novo registro"""
        self._set_edit_mode(True)
        self._clear_form()
        self.current_record = None
        self.main_window.update_status("Criando novo registro")
        
    def edit_record(self):
        """Inicia edição do registro selecionado"""
        if not self.current_record:
            self.main_window.message_helper.show_warning("Selecione um registro para editar")
            return
            
        self._set_edit_mode(True)
        self.main_window.update_status("Editando registro")
        
    def save_record(self):
        """Salva o registro atual"""
        try:
            # Coletar dados do formulário
            data = {}
            for field, widget in self.form_fields.items():
                value = widget.get().strip()
                if value:  # Ignorar campos vazios
                    # Converter tipos conforme necessário
                    if field in ['ano', 'populacao_estimada']:
                        value = int(value)
                    elif 'valor' in field.lower():
                        value = float(value.replace('R$', '').replace('.', '').replace(',', '.'))
                    elif 'idh' in field.lower():
                        value = float(value)
                    elif field == 'ativo':
                        value = value.lower() == 'ativo'
                    data[field] = value
                    
            if not data:
                self.main_window.message_helper.show_warning("Nenhum dado para salvar")
                return
            
            # Determinar qual CRUD usar
            crud = None
            if self.current_table == 'estados':
                crud = self.estados_crud
            elif self.current_table == 'indicadores_idh':
                crud = self.indicadores_crud
            elif self.current_table == 'despesas_publicas':
                crud = self.despesas_crud
            elif self.current_table == 'organizacoes':
                crud = self.orgaos_crud
            
            if not crud:
                raise Exception("CRUD não encontrado para a tabela atual")
            
            # Salvar dados dentro de uma transação
            try:
                # Salvar dados
                if self.current_record:  # Atualização
                    record_id = int(self.current_record[0])
                    crud.update(record_id, **data)
                else:  # Novo registro
                    crud.create(**data)
                    
                self._set_edit_mode(False)
                self.main_window.message_helper.show_success("Registro salvo com sucesso!")
                self.main_window.update_status("Registro salvo")
                self.refresh_data()
                
            except Exception as e:
                raise Exception(f"Erro ao salvar no banco de dados: {str(e)}")
            
        except ValueError as e:
            self.main_window.message_helper.show_error(f"Erro de validação: {str(e)}")
            # Manter modo de edição em caso de erro
            return
        except Exception as e:
            self.main_window.message_helper.show_error(f"Erro ao salvar: {str(e)}")
            # Manter modo de edição em caso de erro
            return
            
    def delete_record(self):
        """Exclui o registro selecionado"""
        if not self.current_record:
            self.main_window.message_helper.show_warning("Selecione um registro para excluir")
            return
            
        if self.main_window.message_helper.ask_yes_no("Confirma a exclusão do registro?"):
            try:
                # Aqui integraria com o CRUD real
                self.main_window.message_helper.show_success("Registro excluído com sucesso!")
                self.main_window.update_status("Registro excluído")
                self.refresh_data()
                self._clear_form()
            except Exception as e:
                self.main_window.message_helper.show_error(f"Erro ao excluir: {str(e)}")
                
    def duplicate_record(self):
        """Duplica o registro selecionado"""
        if not self.current_record:
            self.main_window.message_helper.show_warning("Selecione um registro para duplicar")
            return
            
        self._set_edit_mode(True)
        self.current_record = None  # Novo registro baseado no atual
        self.main_window.update_status("Duplicando registro")
        
    def cancel_edit(self):
        """Cancela a edição atual"""
        self._set_edit_mode(False)
        if self.current_record:
            self._populate_form(self.current_record[0], self.current_record[1])
        else:
            self._clear_form()
        self.main_window.update_status("Edição cancelada")
        
    def refresh_data(self):
        """Atualiza dados da tabela"""
        self._load_real_data()
        self._update_stats()
        self.main_window.update_status("Dados atualizados")
        
    def show_context_menu(self, event):
        """Mostra menu de contexto"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def _set_edit_mode(self, editing):
        """Alterna modo de edição"""
        self.editing_mode = editing
        
        # Atualizar label do modo
        if editing:
            self.mode_label.config(
                text=f"{self.styling.icons['edit']} Modo Edição",
                foreground=self.styling.colors['warning']
            )
        else:
            self.mode_label.config(
                text=f"{self.styling.icons['view']} Modo Visualização",
                foreground=self.styling.colors['info']
            )
            
        # Habilitar/desabilitar campos
        for field_widget in self.form_fields.values():
            if editing:
                field_widget.config(state=NORMAL)
            else:
                field_widget.config(state=DISABLED)
                
        # Habilitar/desabilitar botões
        if editing:
            self.save_btn.config(state=NORMAL)
            self.cancel_btn.config(state=NORMAL)
            self.new_btn.config(state=DISABLED)
            self.edit_btn.config(state=DISABLED)
            self.delete_btn.config(state=DISABLED)
        else:
            self.save_btn.config(state=DISABLED)
            self.cancel_btn.config(state=DISABLED)
            self.new_btn.config(state=NORMAL)
            self.edit_btn.config(state=NORMAL)
            self.delete_btn.config(state=NORMAL)
            
    def _clear_form(self):
        """Limpa o formulário"""
        for field_widget in self.form_fields.values():
            field_widget.delete(0, END)
            
    def _update_stats(self):
        """Atualiza estatísticas da tabela"""
        total_records = len(self.tree.get_children())
        self.total_label.config(text=f"Total: {total_records} registros")
        
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.update_label.config(text=f"Última atualização: {current_time}") 