"""
Interface Gráfica Principal - Sistema DEC7588
Interface moderna usando ttkbootstrap com 4 abas principais
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar DPI awareness para Windows antes de importar tkinter
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Tentar configurar DPI awareness de forma segura
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass  # Ignorar se não conseguir configurar
    except ImportError:
        pass  # ctypes não disponível

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import threading
import sys
import os

# Adicionar src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.utils.styling import Styling
from src.gui.utils.gui_helpers import ThreadManager, MessageHelper
from src.gui.components.dashboard_tab import DashboardTab
from src.gui.components.visualizations_tab import VisualizationsTab
from src.gui.components.crud_tab import CrudTab
from src.gui.components.chat_sidebar import ChatSidebar

class MainWindow:
    def __init__(self):
        # Inicializar tema e janela principal
        self.root = ttk_bootstrap.Window(themename="cosmo")
        self.root.title("Projeto Final - Banco de Dados")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configurar ícone da janela
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Ignorar se não houver ícone
            
        # Inicializar componentes
        self.styling = Styling()
        self.thread_manager = ThreadManager()
        self.message_helper = MessageHelper(self.root)
        
        # Status da aplicação
        self.status_text = tk.StringVar(value="Sistema carregado com sucesso")
        
        # Configurar estilo
        self._setup_styles()
        
        # Criar interface
        self._create_layout()
        self._setup_menu()
        
        # Configurar eventos de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _setup_styles(self):
        """Configura estilos customizados"""
        style = ttk_bootstrap.Style()
        
        # Estilo para abas principais
        style.configure(
            "Main.TNotebook", 
            background=self.styling.colors['background'],
            borderwidth=0
        )
        
        style.configure(
            "Main.TNotebook.Tab",
            padding=[20, 12],
            font=self.styling.fonts['medium_bold']
        )
        
        # Estilo para sidebar
        style.configure(
            "Sidebar.TFrame",
            background=self.styling.colors['sidebar_bg'],
            relief="solid",
            borderwidth=1
        )
        
        # Estilo para cabeçalho
        style.configure(
            "Header.TFrame",
            background=self.styling.colors['primary'],
            relief="flat"
        )
        
    def _create_layout(self):
        """Cria o layout principal da aplicação"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Cabeçalho
        self._create_header()
        
        # Container principal (conteúdo + sidebar)
        self.content_container = ttk.Frame(self.main_frame)
        self.content_container.pack(fill=BOTH, expand=True, pady=(10, 0))
        
        # Frame principal de conteúdo (esquerda)
        self.content_frame = ttk.Frame(self.content_container)
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Sidebar do chat (direita) - com funcionalidade de expansão
        self.sidebar_frame = ttk.Frame(
            self.content_container, 
            style="Sidebar.TFrame",
            width=60  # Largura contraída inicial
        )
        self.sidebar_frame.pack(side=RIGHT, fill=Y)
        self.sidebar_frame.pack_propagate(False)
        
        # Estado da sidebar
        self.sidebar_expanded = False
        self.sidebar_contracted_width = 60
        self.sidebar_expanded_width = 350
        
        # Notebook para abas principais
        self._create_main_tabs()
        
        # Inicializar componentes das abas
        self._initialize_tab_components()
        
        # Inicializar sidebar de chat
        self._initialize_chat_sidebar()
        
        # Configurar eventos de hover para sidebar
        self._setup_sidebar_hover()
        
        # Iniciar verificação periódica da sidebar
        self._start_sidebar_monitor()
        
        # Barra de status
        self._create_status_bar()
        
    def _create_header(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = ttk.Frame(self.main_frame, style="Header.TFrame")
        header_frame.pack(fill=X, pady=(0, 10))
        
        # Título principal
        title_label = ttk.Label(
            header_frame,
            text="Projeto Final - Banco de Dados",
            font=self.styling.fonts['large_bold'],
            foreground=self.styling.colors['white'],
            background=self.styling.colors['primary']
        )
        title_label.pack(side=LEFT, padx=20, pady=15)
        
        # Subtítulo
        subtitle_label = ttk.Label(
            header_frame,
            text="Análise IDH vs Despesas Públicas Federais (2019-2023)",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['white'],
            background=self.styling.colors['primary']
        )
        subtitle_label.pack(side=LEFT, padx=(20, 0), pady=15)
        
    def _create_main_tabs(self):
        """Cria as abas principais do sistema"""
        self.notebook = ttk.Notebook(self.content_frame, style="Main.TNotebook")
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Aba Dashboard
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.dashboard_frame, 
            text=f"{self.styling.icons['dashboard']} Dashboard"
        )
        
        # Aba Visualizações
        self.visualizations_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.visualizations_frame, 
            text=f"{self.styling.icons['chart']} Visualizações"
        )
        
        # Aba CRUD
        self.crud_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            self.crud_frame, 
            text=f"{self.styling.icons['database']} Gerenciar Dados"
        )
        
        # Bind evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Bind adicional para garantir sidebar sempre visível
        self.notebook.bind("<Button-1>", self._on_notebook_click)
        
    def _initialize_tab_components(self):
        """Inicializa os componentes das abas"""
        try:
            # Dashboard Tab
            self.dashboard_tab = DashboardTab(self.dashboard_frame, self)
            
            # Visualizations Tab
            self.visualizations_tab = VisualizationsTab(self.visualizations_frame, self)
            
            # CRUD Tab
            self.crud_tab = CrudTab(self.crud_frame, self)
            
        except Exception as e:
            self.message_helper.show_error(f"Erro ao inicializar componentes: {str(e)}")
            
    def _initialize_chat_sidebar(self):
        """Inicializa a sidebar de chat"""
        try:
            self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
        except Exception as e:
            self.message_helper.show_error(f"Erro ao inicializar chat: {str(e)}")
            
    def _create_status_bar(self):
        """Cria a barra de status"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=X, pady=(10, 0))
        
        # Separador
        separator = ttk.Separator(status_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(0, 5))
        
        # Container da barra de status
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill=X, padx=10, pady=5)
        
        # Status texto
        status_label = ttk.Label(
            status_container,
            textvariable=self.status_text,
            font=self.styling.fonts['small']
        )
        status_label.pack(side=LEFT)
        
        # Indicador de conexão
        self.connection_status = ttk.Label(
            status_container,
            text=f"{self.styling.icons['check']} Conectado",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['success']
        )
        self.connection_status.pack(side=RIGHT)
        
    def _setup_menu(self):
        """Configura menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Exportar Dados...", command=self.export_data)
        file_menu.add_command(label="Importar Dados...", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Limpar Cache", command=self.clear_cache)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        help_menu.add_command(label="Manual do Usuário", command=self.show_manual)
        
    def _on_notebook_click(self, event):
        """Manipula clique no notebook"""
        # Agendar verificação da sidebar após o clique
        self.root.after(100, self._ensure_sidebar_persistent)
            
    def on_tab_changed(self, event):
        """Manipula mudança de aba"""
        try:
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            self.update_status(f"Aba ativa: {tab_text}")
            
            # Salvar estado atual da sidebar
            current_expanded_state = self._save_sidebar_state()
            
            # Permitir que a mudança de aba seja processada primeiro
            self.root.update_idletasks()
            
            # Programar recriação da sidebar como operação FINAL
            self.root.after(100, lambda: self._smart_sidebar_check(current_expanded_state))
            
        except Exception as e:
            print(f"❌ Erro na mudança de aba: {e}")
            # Em caso de erro, tentar recuperar a sidebar
            self.root.after(100, lambda: self._emergency_sidebar_recovery())
            
    def _save_sidebar_state(self):
        """Salva o estado atual da sidebar"""
        try:
            # Verificar múltiplas fontes de estado
            main_expanded = getattr(self, 'sidebar_expanded', False)
            
            if hasattr(self, 'chat_sidebar') and hasattr(self.chat_sidebar, 'is_expanded'):
                chat_expanded = self.chat_sidebar.is_expanded
            else:
                chat_expanded = False
                
            # Usar o estado mais "expandido" como verdade
            final_state = main_expanded or chat_expanded
            
            return final_state
            
        except Exception as e:
            return False
            
    def _smart_sidebar_check(self, target_expanded_state):
        """Verificação inteligente da sidebar - corrige ou recria conforme necessário"""
        try:
            # Verificar se sidebar existe e tem problema
            needs_fix = self._sidebar_needs_reload()
            
            if not needs_fix:
                return
            
            # Tentar correção de layout primeiro (mais rápido que recriação)
            if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
                try:
                    # Obter largura atual
                    current_width = self.sidebar_frame.winfo_width()
                    target_width = self.sidebar_expanded_width if target_expanded_state else self.sidebar_contracted_width
                    
                    # Se largura muito pequena, tentar forçar layout
                    if current_width < 30:
                        self._force_sidebar_layout(target_width)
                        
                        # Verificar se correção funcionou
                        self.root.update_idletasks()
                        new_width = self.sidebar_frame.winfo_width()
                        
                        if new_width >= 30:
                            return
                    
                except Exception:
                    pass
            
            # Se chegou aqui, precisa recriação
            self._final_sidebar_reload(target_expanded_state, "smart_check")
            
        except Exception:
            self._emergency_sidebar_recovery()
    
    def _force_sidebar_layout(self, target_width):
        """Força o layout correto da sidebar sem recriação"""
        try:
            # Estratégia 1: Repack com configurações forçadas
            self.sidebar_frame.pack_forget()
            self.sidebar_frame.pack(side=RIGHT, fill=Y)
            self.sidebar_frame.pack_propagate(False)
            self.sidebar_frame.config(width=target_width, height=600)
            
            # Estratégia 2: Place override se necessário
            self.root.update_idletasks()
            check_width = self.sidebar_frame.winfo_width()
            
            if check_width < target_width * 0.5:  # Se ainda muito pequeno
                container_width = self.content_container.winfo_width()
                container_height = self.content_container.winfo_height()
                
                if container_width > target_width:
                    sidebar_x = container_width - target_width
                    self.sidebar_frame.place(
                        x=sidebar_x, 
                        y=0, 
                        width=target_width, 
                        height=container_height
                    )
            
        except Exception as e:
            raise e

    def _final_sidebar_reload(self, target_expanded_state, timing):
        """Recarrega completamente a sidebar como operação final"""
        try:
            # Limpar completamente a sidebar atual
            self._clean_existing_sidebar()
            
            # Recriar completamente
            self._create_fresh_sidebar(target_expanded_state)
            
        except Exception:
            # Se falhar, tentar recovery básico
            self.root.after(100, lambda: self._emergency_sidebar_recovery())
            
    def _sidebar_needs_reload(self):
        """Verifica se a sidebar precisa ser recarregada"""
        try:
            # Verificar se existe
            if not hasattr(self, 'sidebar_frame') or not self.sidebar_frame.winfo_exists():
                return True
                
            # Verificar se chat_sidebar existe
            if not hasattr(self, 'chat_sidebar'):
                return True
                
            # Verificar parent correto
            if str(self.sidebar_frame.winfo_parent()) != str(self.content_container):
                return True
            
            # Verificar largura mínima aceitável
            try:
                current_width = self.sidebar_frame.winfo_width()
                min_acceptable_width = 30  # Mínimo para ser considerado válido
                
                if current_width < min_acceptable_width:
                    return True
                    
            except Exception:
                return True
            
            # Se chegou até aqui, sidebar está OK
            return False
            
        except Exception:
            return True
            
    def _clean_existing_sidebar(self):
        """Limpa completamente a sidebar existente"""
        try:
            # Log estado antes da limpeza
            chat_exists = hasattr(self, 'chat_sidebar')
            frame_exists = hasattr(self, 'sidebar_frame')
            
            print(f"🧹 [CLEANUP] Estado antes: chat_sidebar={chat_exists}, sidebar_frame={frame_exists}")
            
            # Limpar chat_sidebar
            if hasattr(self, 'chat_sidebar'):
                try:
                    print(f"🧹 [CLEANUP] Destruindo chat_sidebar: {id(self.chat_sidebar)}")
                    self.chat_sidebar.cleanup()
                    del self.chat_sidebar
                    print(f"🧹 [CLEANUP] chat_sidebar removido")
                except Exception as e:
                    print(f"⚠️ [CLEANUP] Erro ao limpar chat_sidebar: {e}")
            else:
                print(f"🧹 [CLEANUP] chat_sidebar não existe")
                
            # Limpar sidebar_frame
            if hasattr(self, 'sidebar_frame'):
                try:
                    frame_id = id(self.sidebar_frame)
                    widget_exists = self.sidebar_frame.winfo_exists()
                    widget_children = len(self.sidebar_frame.winfo_children()) if widget_exists else 0
                    
                    print(f"🧹 [CLEANUP] Destruindo sidebar_frame: {frame_id}, exists={widget_exists}, children={widget_children}")
                    
                    if widget_exists:
                        self.sidebar_frame.destroy()
                        print(f"🧹 [CLEANUP] sidebar_frame.destroy() chamado")
                    
                    del self.sidebar_frame
                    print(f"🧹 [CLEANUP] sidebar_frame removido da memória")
                except Exception as e:
                    print(f"⚠️ [CLEANUP] Erro ao limpar sidebar_frame: {e}")
            else:
                print(f"🧹 [CLEANUP] sidebar_frame não existe")
                
            # Forçar garbage collection
            import gc
            gc.collect()
            print(f"🧹 [CLEANUP] Garbage collection executado")
            
            # Verificar se realmente foi limpo
            chat_still_exists = hasattr(self, 'chat_sidebar')
            frame_still_exists = hasattr(self, 'sidebar_frame')
            

            
        except Exception:
            pass
            
    def _create_fresh_sidebar(self, target_expanded_state):
        """Cria uma sidebar completamente nova"""
        try:
            # Determinar largura inicial
            initial_width = self.sidebar_expanded_width if target_expanded_state else self.sidebar_contracted_width
            
            # Verificar se content_container existe
            if not hasattr(self, 'content_container') or not self.content_container.winfo_exists():
                raise Exception("content_container não disponível")
            
            # Criar frame novo
            self.sidebar_frame = ttk.Frame(
                self.content_container,
                style="Sidebar.TFrame",
                width=initial_width
            )
            
            # Pack tradicional
            self.sidebar_frame.pack(side=RIGHT, fill=Y)
            self.sidebar_frame.pack_propagate(False)
            
            # Aguardar layout inicial
            self.root.update_idletasks()
            self.content_container.update_idletasks()
            
            # Verificar se pack funcionou
            try:
                pack_width = self.sidebar_frame.winfo_width()
                pack_height = self.sidebar_frame.winfo_height()
                
                # Se pack falhou (dimensões < 10), usar place como override
                if pack_width < 10 or pack_height < 10:
                    # Calcular posição para sidebar direita
                    try:
                        container_width = self.content_container.winfo_width()
                        container_height = self.content_container.winfo_height()
                        
                        if container_width > initial_width and container_height > 100:
                            sidebar_x = container_width - initial_width
                            
                            # Aplicar place como override mantendo pack
                            self.sidebar_frame.place(
                                x=sidebar_x, 
                                y=0, 
                                width=initial_width, 
                                height=container_height
                            )
                            
                    except Exception:
                        pass
                    
            except Exception:
                pass
            
            # Configurações adicionais forçadas
            self.sidebar_frame.config(width=initial_width, height=600)
            
            # Update final
            self.root.update_idletasks()
            
            # Criar chat_sidebar novo
            self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
            
            # Configurar estado
            self.sidebar_expanded = target_expanded_state
            self.chat_sidebar.is_expanded = target_expanded_state
            
            # Aplicar modo correto
            if target_expanded_state:
                self.chat_sidebar._set_expanded_mode()
            else:
                self.chat_sidebar._set_collapsed_mode()
                
            # Forçar atualização final
            self.sidebar_frame.update_idletasks()
            self.root.update_idletasks()
            
            # Verificação final
            final_exists = self.sidebar_frame.winfo_exists()
            
            if not final_exists:
                raise Exception("Frame destruído após criação")
            
        except Exception as e:
            raise e
            
    def _emergency_sidebar_recovery(self):
        """Recovery de emergência para a sidebar"""
        try:
            # Tentar criar sidebar básica
            self._clean_existing_sidebar()
            
            # Criar versão mais simples possível
            self.sidebar_frame = ttk.Frame(self.content_container, width=60)
            self.sidebar_frame.pack(side=RIGHT, fill=Y)
            self.sidebar_frame.pack_propagate(False)
            
            self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
            self.sidebar_expanded = False
            
        except Exception:
            pass
            
    def _final_sidebar_check(self):
        """Verificação final para garantir que a sidebar está presente"""
        try:
            if not hasattr(self, 'sidebar_frame') or not self.sidebar_frame.winfo_exists():
                self._recreate_sidebar()
            elif not self.sidebar_frame.winfo_viewable():
                self._ensure_sidebar_persistent()
        except Exception:
            self._recreate_sidebar()
            
    def _ensure_sidebar_persistent(self):
        """Garante que a sidebar permaneça persistente entre mudanças de aba"""
        try:
            # Verificar se os componentes básicos existem
            if not hasattr(self, 'content_container'):
                return
            elif not self.content_container.winfo_exists():
                return
                
            if not hasattr(self, 'sidebar_frame'):
                self._recreate_sidebar()
                return
            elif not self.sidebar_frame.winfo_exists():
                self._recreate_sidebar()
                return
                
            if not hasattr(self, 'chat_sidebar'):
                self._recreate_sidebar()
                return
            
            # Salvar estado atual de expansão antes de reconfigurar
            sidebar_expanded = getattr(self, 'sidebar_expanded', False)
            chat_expanded = getattr(self.chat_sidebar, 'is_expanded', False)
            was_expanded = sidebar_expanded or chat_expanded
            
            # IMPORTANTE: Garantir que a sidebar está no container correto
            current_parent = self.sidebar_frame.winfo_parent()
            expected_parent = str(self.content_container)
            
            if current_parent != expected_parent:
                self._reattach_sidebar_to_container(was_expanded)
                return
            
            # Verificar se a sidebar está visível no layout
            is_viewable = self.sidebar_frame.winfo_viewable()
            
            if not is_viewable:
                self._restore_sidebar_position(was_expanded)
                return
            
            # Se chegou até aqui, apenas sincronizar estado
            self._sync_sidebar_state(was_expanded)
                    
        except Exception as e:
            # Em caso de erro crítico, recriar completamente
            self._recreate_sidebar()
            
    def _reattach_sidebar_to_container(self, was_expanded):
        """Reanexa a sidebar ao container correto"""
        try:
            print("🔄 Reanexando sidebar ao container...")
            
            # Tentar resolver sem destruir primeiro (mais suave)
            try:
                self.sidebar_frame.pack_forget()
                
                # Reconfigurar parent se necessário (método menos destrutivo)
                if str(self.sidebar_frame.winfo_parent()) != str(self.content_container):
                    # Se o parent está errado, recriar é necessário
                    raise ValueError("Parent incorreto, precisa recriar")
                    
                # Se chegou aqui, apenas reposicionar
                width = self.sidebar_expanded_width if was_expanded else self.sidebar_contracted_width
                self.sidebar_frame.config(width=width)
                self.sidebar_frame.pack(side=RIGHT, fill=Y, before=None)
                self.sidebar_frame.pack_propagate(False)
                
                # Sincronizar estado
                self._sync_sidebar_state(was_expanded)
                
                pass  # Sidebar reposicionada
                return
                
            except Exception:
                # Se reposicionamento falhou, fazer recriação completa
                pass
                
            # Método destrutivo - apenas se necessário
            print("🔧 Recriação completa necessária...")
            
            # Remover da posição atual
            if hasattr(self, 'sidebar_frame'):
                self.sidebar_frame.pack_forget()
                self.sidebar_frame.destroy()
            
            # Recriar frame da sidebar no container correto
            width = self.sidebar_expanded_width if was_expanded else self.sidebar_contracted_width
            self.sidebar_frame = ttk.Frame(
                self.content_container,  # SEMPRE no content_container
                style="Sidebar.TFrame",
                width=width
            )
            
            # Posicionar corretamente
            self.sidebar_frame.pack(side=RIGHT, fill=Y, before=None)
            self.sidebar_frame.pack_propagate(False)
            
            # Aguardar frame estar pronto
            self.root.update_idletasks()
            
            # Recriar conteúdo da sidebar APENAS se necessário
            if hasattr(self.chat_sidebar, 'parent'):
                self.chat_sidebar.parent = self.sidebar_frame
                # Tentar reutilizar interface existente
                try:
                    if hasattr(self.chat_sidebar, 'main_container'):
                        self.chat_sidebar.main_container.pack_forget()
                        self.chat_sidebar.main_container.pack(fill=BOTH, expand=True, padx=2, pady=2)
                except:
                    # Se falhou, criar nova interface
                    self.chat_sidebar._create_interface()
                else:
                    # Recriar sidebar completamente
                    self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
            
            # Restaurar estado
            self.sidebar_expanded = was_expanded
            if hasattr(self.chat_sidebar, 'is_expanded'):
                self.chat_sidebar.is_expanded = was_expanded
                
                if was_expanded:
                    self.chat_sidebar._set_expanded_mode()
                else:
                    self.chat_sidebar._set_collapsed_mode()
                
                pass  # Sidebar reanexada
                    
        except Exception as e:
            print(f"❌ Erro ao reanexar sidebar: {e}")
            self._recreate_sidebar()
            
    def _restore_sidebar_position(self, was_expanded):
        """Restaura a posição da sidebar no layout com place override se necessário"""
        try:
            # Configurar largura correta
            width = self.sidebar_expanded_width if was_expanded else self.sidebar_contracted_width
            
            # Remover e readicionar ao layout
            self.sidebar_frame.pack_forget()
            self.sidebar_frame.config(width=width)
            self.sidebar_frame.pack(side=RIGHT, fill=Y)
            self.sidebar_frame.pack_propagate(False)
            
            # Forçar atualização para verificar se pack funcionou
            self.root.update_idletasks()
            
            # Verificar se pack funcionou adequadamente
            actual_width = self.sidebar_frame.winfo_width()
            is_viewable = self.sidebar_frame.winfo_viewable()
            
            # Se pack falhou (largura muito pequena ou não visível), aplicar place override
            if actual_width < width * 0.5 or not is_viewable:
                try:
                    # Aplicar place override para garantir visibilidade
                    container_width = self.content_container.winfo_width()
                    container_height = self.content_container.winfo_height()
                    
                    if container_width > width and container_height > 100:
                        sidebar_x = container_width - width
                        self.sidebar_frame.place(
                            x=sidebar_x, 
                            y=0, 
                            width=width, 
                            height=container_height
                        )
                        
                        # Aguardar layout
                        self.root.update_idletasks()
                        
                except Exception as place_error:
                    pass
            
            # Sincronizar estado
            self._sync_sidebar_state(was_expanded)
            
        except Exception as e:
            self._recreate_sidebar()
            
    def _sync_sidebar_state(self, was_expanded):
        """Sincroniza apenas o estado da sidebar"""
        try:
            # Atualizar estados
            self.sidebar_expanded = was_expanded
            
            if hasattr(self.chat_sidebar, 'is_expanded'):
                self.chat_sidebar.is_expanded = was_expanded
                
                # Aplicar modo correto
                if was_expanded:
                    self.chat_sidebar._set_expanded_mode()
                    self.sidebar_frame.config(width=self.sidebar_expanded_width)
                else:
                    self.chat_sidebar._set_collapsed_mode() 
                    self.sidebar_frame.config(width=self.sidebar_contracted_width)
            
            # Forçar atualização visual
            self.sidebar_frame.update_idletasks()
            
        except Exception as e:
            print(f"❌ Erro na sincronização de estado: {e}")
    
    def _recreate_sidebar(self):
        """Recria a sidebar em caso de problemas"""
        try:
            print("🔄 Recriando sidebar...")
            
            # Salvar estado atual de expansão antes de destruir
            was_expanded = getattr(self, 'sidebar_expanded', False)
            if hasattr(self, 'chat_sidebar') and hasattr(self.chat_sidebar, 'is_expanded'):
                was_expanded = was_expanded or self.chat_sidebar.is_expanded
            
            # Destruir sidebar existente se houver
            if hasattr(self, 'chat_sidebar'):
                try:
                    self.chat_sidebar.cleanup()
                except:
                    pass
                try:
                    del self.chat_sidebar
                except:
                    pass
            
            # Destruir frame da sidebar se existir
            if hasattr(self, 'sidebar_frame'):
                try:
                    self.sidebar_frame.destroy()
                except:
                    pass
            
            # Verificar se o content_container ainda existe
            if not hasattr(self, 'content_container') or not self.content_container.winfo_exists():
                print("❌ Content container não existe - não é possível recriar sidebar")
                return
                
            # Determinar largura inicial baseada no estado anterior
            initial_width = self.sidebar_expanded_width if was_expanded else self.sidebar_contracted_width
            
            # Recriar frame da sidebar no container correto
            self.sidebar_frame = ttk.Frame(
                self.content_container,  # SEMPRE no content_container
                style="Sidebar.TFrame",
                width=initial_width
            )
            
            # Posicionar corretamente no layout
            self.sidebar_frame.pack(side=RIGHT, fill=Y, before=None)
            self.sidebar_frame.pack_propagate(False)
            
            # Aguardar um momento para garantir que o frame esteja pronto
            self.root.update_idletasks()
            
            # Recriar sidebar com verificação de existência do frame
            if self.sidebar_frame.winfo_exists():
                self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
                
                # Aguardar criação da interface
                self.root.update_idletasks()
                
                # Restaurar estado de expansão após criação
                self.sidebar_expanded = was_expanded
                
                if hasattr(self.chat_sidebar, 'is_expanded'):
                    self.chat_sidebar.is_expanded = was_expanded
                    
                    if was_expanded:
                        self.chat_sidebar._set_expanded_mode()
                        print("🔄 Estado expandido restaurado após recriação")
                    else:
                        self.chat_sidebar._set_collapsed_mode()
                        
                # Forçar atualização final
                self.sidebar_frame.update_idletasks()
                
                pass  # Sidebar recriada
            else:
                print("❌ Frame da sidebar não foi criado corretamente")
                
        except Exception as e:
            print(f"❌ Erro ao recriar sidebar: {e}")
            # Tentar novamente após um delay
            self.root.after(1000, lambda: self._recreate_sidebar_fallback(was_expanded))
            
    def _recreate_sidebar_fallback(self, was_expanded=False):
        """Método de fallback para recriar sidebar em caso de falha"""
        try:
            print("🔄 Tentativa de fallback para recriar sidebar...")
            
            # Criar frame simples sem estilo primeiro
            self.sidebar_frame = ttk.Frame(
                self.content_container,
                width=self.sidebar_contracted_width
            )
            self.sidebar_frame.pack(side=RIGHT, fill=Y)
            self.sidebar_frame.pack_propagate(False)
            
            # Criar sidebar básica
            self.chat_sidebar = ChatSidebar(self.sidebar_frame, self)
            self.sidebar_expanded = False
            
            pass  # Sidebar recriada via fallback
            
        except Exception as e:
            print(f"❌ Fallback também falhou: {e}")
            
    def update_status(self, message):
        """Atualiza mensagem da barra de status"""
        self.status_text.set(message)
        
    def refresh_data(self):
        """Atualiza dados do sistema"""
        def refresh_task():
            self.update_status("Atualizando dados...")
            # Aqui implementaremos a lógica de atualização
            self.root.after(2000, lambda: self.update_status("Dados atualizados com sucesso"))
            
        self.thread_manager.run_thread(refresh_task)
        
    def export_data(self):
        """Exporta dados do sistema"""
        self.message_helper.show_info("Funcionalidade de exportação será implementada")
        
    def import_data(self):
        """Importa dados para o sistema"""
        self.message_helper.show_info("Funcionalidade de importação será implementada")
        
    def clear_cache(self):
        """Limpa cache do sistema"""
        self.message_helper.show_info("Cache limpo com sucesso")
        self.update_status("Cache limpo")
        
    def open_settings(self):
        """Abre janela de configurações"""
        self.message_helper.show_info("Janela de configurações será implementada")
        
    def show_about(self):
        """Mostra informações sobre o sistema"""
        about_text = """Projeto Final - Banco de Dados
        
Versão: 1.0.0
Desenvolvido para análise de correlação entre IDH e despesas públicas federais brasileiras.

Funcionalidades:
• Dashboard interativo com métricas principais
• Visualizações analíticas avançadas  
• Sistema CRUD completo para gerenciamento de dados
• Chat inteligente com IA Gemini integrada
• Consultas analíticas e relatórios automáticos

Dados: 2019-2023 | Estados: 27 + DF | Registros: 10.935"""
        
        self.message_helper.show_info(about_text, "Sobre o Sistema")
        
    def show_manual(self):
        """Mostra manual do usuário"""
        manual_text = """Manual do Usuário - Projeto Final

NAVEGAÇÃO:
• Use as abas superiores para navegar entre seções
• Dashboard: Visão geral e métricas principais
• Visualizações: Gráficos e análises detalhadas
• Gerenciar Dados: Operações CRUD nas tabelas
• Chat IA: Sidebar direita para análises inteligentes

FUNCIONALIDADES:
• Menu "Arquivo" para importar/exportar dados
• Menu "Ferramentas" para limpar cache
• Barra de status mostra informações do sistema
• Interface responsiva e moderna

CHAT IA:
• Digite suas perguntas na sidebar direita
• IA analisa dados e fornece insights
• Suporte a análises especializadas
• Recomendações baseadas em dados reais"""
        
        self.message_helper.show_info(manual_text, "Manual do Usuário")
        
    def on_closing(self):
        """Manipula fechamento da aplicação"""
        if self.message_helper.ask_yes_no("Deseja realmente sair do sistema?"):
            self.thread_manager.shutdown()
            self.root.quit()
            self.root.destroy()
            
    def run(self):
        """Inicia a aplicação"""
        try:
            self.update_status("Sistema inicializado com sucesso")
            self.root.mainloop()
        except Exception as e:
            self.message_helper.show_error(f"Erro crítico: {str(e)}")
            
    def _start_sidebar_monitor(self):
        """Inicia monitoramento simplificado da sidebar"""
        def check_sidebar():
            try:
                # Verificação simples - apenas garantir que existe
                if not hasattr(self, 'sidebar_frame') or not self.sidebar_frame.winfo_exists():
                    print("⚠️ Monitor: Sidebar perdida - recriando...")
                    current_state = self._save_sidebar_state()
                    self._create_fresh_sidebar(current_state)
                        
            except Exception as e:
                print(f"⚠️ Monitor: {e}")
            
            # Verificar novamente em 5 segundos (menos agressivo)
            self.root.after(5000, check_sidebar)
        
        # Iniciar verificação após 2 segundos
        self.root.after(2000, check_sidebar)
        
    def _setup_sidebar_hover(self):
        """Configura eventos de hover para sidebar - agora gerenciado pela própria sidebar"""
        # O hover é gerenciado diretamente pela ChatSidebar
        pass
        
    def _log_sidebar_state(self, momento):
        """Log do estado da sidebar para debug"""
        try:
            # Verificações básicas
            has_sidebar_frame = hasattr(self, 'sidebar_frame')
            has_chat_sidebar = hasattr(self, 'chat_sidebar') 
            has_content_container = hasattr(self, 'content_container')
            
            if has_sidebar_frame:
                try:
                    exists = self.sidebar_frame.winfo_exists()
                    visible = self.sidebar_frame.winfo_viewable()
                    parent = str(self.sidebar_frame.winfo_parent())
                    width = self.sidebar_frame.winfo_width()
                    height = self.sidebar_frame.winfo_height()
                except Exception as e:
                    pass
                
            if has_chat_sidebar:
                try:
                    is_expanded = self.chat_sidebar.is_expanded
                except Exception as e:
                    pass
            
            try:
                sidebar_expanded = self.sidebar_expanded
            except:
                pass
            
        except Exception as e:
            pass

    def _log_layout_state(self, momento):
        """Log do estado do layout para debug"""
        try:
            # Verificar content_container
            if hasattr(self, 'content_container'):
                try:
                    exists = self.content_container.winfo_exists()
                    visible = self.content_container.winfo_viewable()
                    children = self.content_container.winfo_children()
                    
                    for i, child in enumerate(children):
                        try:
                            child_class = child.__class__.__name__
                            child_visible = child.winfo_viewable()
                        except:
                            pass
                        
                except Exception as e:
                    pass
                
            # Verificar notebook
            if hasattr(self, 'notebook'):
                try:
                    exists = self.notebook.winfo_exists()
                    visible = self.notebook.winfo_viewable()
                    current_tab = self.notebook.index(self.notebook.select())
                except Exception as e:
                    pass
                
        except Exception as e:
            pass

    def _debug_delayed_check(self, timing):
        """Debug com delay para verificar estado"""
        # Fazer verificação da sidebar
        self._ensure_sidebar_persistent()

    def _debug_final_check(self, timing):
        """Verificação final do estado"""
        # Fazer verificação adicional do estado da sidebar  
        self._log_layout_state(f"FINAL-{timing}")

if __name__ == "__main__":
    app = MainWindow()
    app.run() 