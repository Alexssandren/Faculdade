"""
Funções Auxiliares para Interface Gráfica - Sistema DEC7588
Helpers para threading, validação, formatação e utilitários GUI
"""

import threading
import queue
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from typing import Callable, Any, Optional, Dict, List
import pandas as pd
from datetime import datetime
import os

class ThreadManager:
    """Gerenciador de threads para operações não-bloqueantes"""
    
    def __init__(self, callback_queue: Optional[queue.Queue] = None):
        self.callback_queue = callback_queue or queue.Queue()
        self.active_threads = []
        
    def run_thread(self, func: Callable, *args, callback: Optional[Callable] = None, **kwargs):
        """Executa função em thread separada"""
        def worker():
            try:
                result = func(*args, **kwargs)
                if callback:
                    callback(result)
            except Exception as e:
                if callback:
                    callback(None, str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        self.active_threads.append(thread)
        return thread
        
    def shutdown(self):
        """Encerra o gerenciador de threads"""
        # Aguarda threads ativas terminarem
        for thread in self.active_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

class MessageHelper:
    """Helper para mensagens e diálogos"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def show_info(self, message: str, title: str = "Informação"):
        """Mostra mensagem de informação"""
        messagebox.showinfo(title, message, parent=self.parent)
    
    def show_error(self, message: str, title: str = "Erro"):
        """Mostra mensagem de erro"""
        messagebox.showerror(title, message, parent=self.parent)
    
    def show_warning(self, message: str, title: str = "Aviso"):
        """Mostra mensagem de aviso"""
        messagebox.showwarning(title, message, parent=self.parent)
        
    def show_success(self, message: str, title: str = "Sucesso"):
        """Mostra mensagem de sucesso"""
        messagebox.showinfo(title, message, parent=self.parent)
    
    def ask_yes_no(self, message: str, title: str = "Confirmação") -> bool:
        """Pergunta sim/não ao usuário"""
        return messagebox.askyesno(title, message, parent=self.parent)
    
    def ask_ok_cancel(self, message: str, title: str = "Confirmação") -> bool:
        """Pergunta OK/Cancelar ao usuário"""
        return messagebox.askokcancel(title, message, parent=self.parent)

class FileHelper:
    """Helper para operações com arquivos"""
    
    @staticmethod
    def save_file_dialog(title: str = "Salvar arquivo", 
                        filetypes: List[tuple] = None,
                        defaultextension: str = ".txt") -> Optional[str]:
        """Abre diálogo para salvar arquivo"""
        if filetypes is None:
            filetypes = [
                ("Arquivos de texto", "*.txt"),
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
            ]
        
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=defaultextension
        )
    
    @staticmethod
    def open_file_dialog(title: str = "Abrir arquivo",
                        filetypes: List[tuple] = None) -> Optional[str]:
        """Abre diálogo para abrir arquivo"""
        if filetypes is None:
            filetypes = [
                ("Arquivos de texto", "*.txt"),
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
            ]
        
        return filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )

class DataFormatter:
    """Formatador de dados para exibição"""
    
    @staticmethod
    def format_currency(value: float, currency: str = "R$") -> str:
        """Formata valor como moeda"""
        try:
            return f"{currency} {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return f"{currency} 0,00"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Formata valor como porcentagem"""
        try:
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """Formata número com casas decimais"""
        try:
            return f"{value:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return "0,00"
    
    @staticmethod
    def format_date(date_obj, format_str: str = "%d/%m/%Y") -> str:
        """Formata data"""
        try:
            if isinstance(date_obj, str):
                # Tentar parser se for string
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
            return date_obj.strftime(format_str)
        except (ValueError, TypeError, AttributeError):
            return "Data inválida"
    
    @staticmethod
    def format_population(value: float) -> str:
        """Formata população com sufixos (M, Mil, etc)"""
        try:
            # Converter para float se for string
            if isinstance(value, str):
                value = float(value)
            
            # Definir escalas e sufixos
            if value >= 1_000_000:
                # Milhões
                formatted = value / 1_000_000
                suffix = "M"
            elif value >= 1_000:
                # Milhares
                formatted = value / 1_000
                suffix = "Mil"
            else:
                # Menor que mil
                return f"{value:.0f}"
            
            # Formatar com 2 casas decimais
            return f"{formatted:.2f}{suffix}"
            
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Trunca texto longo"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

class ValidationHelper:
    """Helper para validação de dados"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_number(value: str, allow_negative: bool = True) -> bool:
        """Valida se string é número válido"""
        try:
            num = float(value.replace(',', '.'))
            if not allow_negative and num < 0:
                return False
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_date(date_str: str, format_str: str = "%d/%m/%Y") -> bool:
        """Valida formato de data"""
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_required_fields(fields: Dict[str, Any]) -> List[str]:
        """Valida campos obrigatórios"""
        errors = []
        for field_name, value in fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Campo '{field_name}' é obrigatório")
        return errors

class TableHelper:
    """Helper para manipulação de tabelas (Treeview)"""
    
    @staticmethod
    def clear_table(tree: ttk.Treeview):
        """Limpa todos os itens da tabela"""
        for item in tree.get_children():
            tree.delete(item)
    
    @staticmethod
    def insert_dataframe(tree: ttk.Treeview, df: pd.DataFrame, max_rows: int = 1000):
        """Insere DataFrame na tabela"""
        TableHelper.clear_table(tree)
        
        # Configurar colunas se necessário
        if tree['columns'] != list(df.columns):
            tree['columns'] = list(df.columns)
            tree['show'] = 'tree headings'
            
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')
        
        # Inserir dados (limitado por max_rows)
        for idx, row in df.head(max_rows).iterrows():
            values = []
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    values.append("")
                elif isinstance(value, float):
                    values.append(DataFormatter.format_number(value))
                else:
                    values.append(str(value))
            
            tree.insert('', 'end', values=values)
    
    @staticmethod
    def get_selected_row_data(tree: ttk.Treeview) -> Optional[Dict]:
        """Retorna dados da linha selecionada"""
        selection = tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        values = tree.item(item, 'values')
        columns = tree['columns']
        
        if len(values) != len(columns):
            return None
        
        return dict(zip(columns, values))

class ProgressHelper:
    """Helper para barras de progresso"""
    
    def __init__(self, progress_var: tk.DoubleVar, 
                 status_var: tk.StringVar = None):
        self.progress_var = progress_var
        self.status_var = status_var
        self.current_step = 0
        self.total_steps = 0
    
    def start_progress(self, total_steps: int, initial_message: str = "Iniciando..."):
        """Inicia progresso"""
        self.total_steps = total_steps
        self.current_step = 0
        self.progress_var.set(0)
        if self.status_var:
            self.status_var.set(initial_message)
    
    def update_progress(self, message: str = None):
        """Atualiza progresso"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        self.progress_var.set(progress)
        
        if self.status_var and message:
            self.status_var.set(f"{message} ({self.current_step}/{self.total_steps})")
    
    def finish_progress(self, message: str = "Concluído!"):
        """Finaliza progresso"""
        self.progress_var.set(100)
        if self.status_var:
            self.status_var.set(message)

class ExportHelper:
    """Helper para exportação de dados"""
    
    @staticmethod
    def export_dataframe_to_csv(df: pd.DataFrame, 
                               filename: str = None,
                               show_dialog: bool = True) -> bool:
        """Exporta DataFrame para CSV"""
        try:
            if show_dialog or not filename:
                filename = FileHelper.save_file_dialog(
                    title="Exportar para CSV",
                    filetypes=[("Arquivos CSV", "*.csv")],
                    defaultextension=".csv"
                )
                
                if not filename:
                    return False
            
            df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
            MessageHelper.show_info(
                "Exportação Concluída",
                f"Dados exportados com sucesso para:\n{filename}"
            )
            return True
            
        except Exception as e:
            MessageHelper.show_error(
                "Erro na Exportação",
                f"Erro ao exportar dados:\n{str(e)}"
            )
            return False
    
    @staticmethod
    def export_text_to_file(text: str, 
                           filename: str = None,
                           show_dialog: bool = True) -> bool:
        """Exporta texto para arquivo"""
        try:
            if show_dialog or not filename:
                filename = FileHelper.save_file_dialog(
                    title="Salvar arquivo de texto",
                    filetypes=[("Arquivos de texto", "*.txt")],
                    defaultextension=".txt"
                )
                
                if not filename:
                    return False
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            
            MessageHelper.show_info(
                "Arquivo Salvo",
                f"Arquivo salvo com sucesso:\n{filename}"
            )
            return True
            
        except Exception as e:
            MessageHelper.show_error(
                "Erro ao Salvar",
                f"Erro ao salvar arquivo:\n{str(e)}"
            )
            return False

def center_window_on_parent(window, parent):
    """Centraliza janela em relação ao parent"""
    window.transient(parent)
    window.grab_set()
    
    # Aguardar que a janela seja desenhada
    window.update_idletasks()
    
    # Calcular posição central
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    
    x = parent_x + (parent_width // 2) - (window_width // 2)
    y = parent_y + (parent_height // 2) - (window_height // 2)
    
    window.geometry(f"+{x}+{y}") 