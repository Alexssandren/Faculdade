import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchFrame(ttk.Frame):
    def __init__(self, parent, search_callback: Callable[[str], None]):
        super().__init__(parent, padding="10")
        self.search_callback = search_callback
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface de busca"""
        self.pack(fill=tk.X)
        
        # Label
        ttk.Label(self, text="Buscar escola:").pack(side=tk.LEFT, padx=5)
        
        # Campo de busca
        self.entrada = ttk.Entry(self)
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entrada.bind('<Return>', self._on_search)
        
        # Botão de busca
        ttk.Button(self, text="Buscar", command=self._on_search).pack(side=tk.LEFT, padx=5)
        
    def _on_search(self, event=None):
        """Callback de busca"""
        termo = self.entrada.get()
        if self.search_callback:
            self.search_callback(termo)
            
    def get_search_term(self) -> str:
        """Retorna o termo de busca atual"""
        return self.entrada.get()

class ResultsTable(ttk.Frame):
    def __init__(self, parent, colunas: List[str]):
        super().__init__(parent, padding="10")
        self.colunas = colunas
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface da tabela"""
        self.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(self, columns=self.colunas, show='headings')
        
        # Configura colunas
        for col in self.colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
    def clear(self):
        """Limpa todos os resultados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def update_results(self, results: List[Tuple]):
        """Atualiza os resultados da tabela"""
        self.clear()
        for result in results:
            self.tree.insert('', tk.END, values=result)

class PaginationFrame(ttk.Frame):
    def __init__(self, parent, page_callback: Callable[[int], None], items_per_page: int = 50):
        super().__init__(parent, padding="10")
        self.page_callback = page_callback
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_items = 0
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface de paginação"""
        self.pack(fill=tk.X)
        
        # Frame para centralizar os controles
        control_frame = ttk.Frame(self)
        control_frame.pack(expand=True)
        
        # Botões de navegação
        self.btn_prev = ttk.Button(control_frame, text="Anterior", command=self._prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
        
        self.lbl_info = ttk.Label(control_frame, text="", width=20)
        self.lbl_info.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = ttk.Button(control_frame, text="Próxima", command=self._next_page)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self._update_buttons()
        
    def _prev_page(self):
        """Vai para a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_buttons()
            if self.page_callback:
                self.page_callback(self.current_page)
    
    def _next_page(self):
        """Vai para a próxima página"""
        total_pages = self._get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_buttons()
            if self.page_callback:
                self.page_callback(self.current_page)
    
    def _get_total_pages(self) -> int:
        """Calcula o número total de páginas"""
        if self.total_items == 0:
            return 1
        return (self.total_items + self.items_per_page - 1) // self.items_per_page
    
    def _update_buttons(self):
        """Atualiza o estado dos botões e informações"""
        total_pages = self._get_total_pages()
        
        # Atualiza texto informativo
        self.lbl_info.config(text=f"Página {self.current_page} de {total_pages}")
        
        # Atualiza estado dos botões
        self.btn_prev["state"] = "normal" if self.current_page > 1 else "disabled"
        self.btn_next["state"] = "normal" if self.current_page < total_pages else "disabled"
        
        # Força atualização do widget
        self.update_idletasks()
    
    def update_total_items(self, total: int):
        """Atualiza o total de itens e reseta a página atual"""
        self.total_items = total
        self.current_page = 1
        self._update_buttons()
        
    def get_offset(self) -> int:
        """Retorna o offset atual para consultas no banco"""
        return (self.current_page - 1) * self.items_per_page
        
    def reset(self):
        """Reseta a paginação para o estado inicial"""
        self.current_page = 1
        self.total_items = 0
        self._update_buttons()

class LoadingIndicator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_running = False
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface do indicador de carregamento"""
        # Label
        self.label = ttk.Label(self, text="Carregando...")
        self.label.pack(pady=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        
    def start(self):
        """Inicia a animação"""
        if not self.is_running:
            self.is_running = True
            self.pack(fill=tk.BOTH, expand=True)
            try:
                self.progress.start(10)
            except Exception as e:
                logger.error(f"Erro ao iniciar indicador de carregamento: {e}")
        
    def stop(self):
        """Para a animação e esconde o indicador"""
        if self.is_running:
            self.is_running = False
            try:
                self.progress.stop()
                self.pack_forget()
            except Exception as e:
                logger.error(f"Erro ao parar indicador de carregamento: {e}")
                # Tenta remover o widget mesmo se houver erro ao parar a animação
                try:
                    self.pack_forget()
                except:
                    pass 