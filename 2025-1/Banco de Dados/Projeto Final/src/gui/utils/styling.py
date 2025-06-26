"""
Sistema de Estilos e Temas - Interface DEC7588
Configurações visuais centralizadas para dashboard moderno
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class AppTheme:
    """Classe para gerenciar temas e estilos da aplicação"""
    
    # Cores principais do sistema
    COLORS = {
        'primary': '#1e3a8a',      # Azul escuro profissional
        'secondary': '#3b82f6',     # Azul médio
        'success': '#10b981',       # Verde sucesso
        'warning': '#f59e0b',       # Amarelo warning
        'danger': '#ef4444',        # Vermelho erro
        'info': '#06b6d4',          # Ciano informação
        'light': '#f8fafc',         # Cinza claro
        'dark': '#1e293b',          # Cinza escuro
        'muted': '#64748b',         # Cinza médio
        'white': '#ffffff',         # Branco
        'sidebar': '#f1f5f9',       # Cor sidebar
        'chat_bg': '#ffffff',       # Background chat
        'chat_user': '#e0f2fe',     # Cor mensagem usuário
        'chat_ai': '#f0f9ff'        # Cor mensagem IA
    }
    
    # Fontes do sistema
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'subtitle': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'mono': ('Consolas', 10),
        'chat': ('Segoe UI', 10),
        'button': ('Segoe UI', 10, 'bold')
    }
    
    # Dimensões padrão
    DIMENSIONS = {
        'window_width': 1400,
        'window_height': 900,
        'sidebar_width': 400,
        'min_width': 1200,
        'min_height': 700,
        'padding': 10,
        'margin': 5
    }
    
    @classmethod
    def get_theme_name(cls):
        """Retorna o nome do tema ttkbootstrap"""
        return 'cosmo'  # Tema moderno e profissional
    
    @classmethod
    def apply_widget_styles(cls, style: ttk.Style):
        """Aplica estilos personalizados aos widgets"""
        
        # Configurar notebook (abas)
        style.configure(
            'Custom.TNotebook',
            background=cls.COLORS['light'],
            borderwidth=1
        )
        
        style.configure(
            'Custom.TNotebook.Tab',
            padding=[20, 10],
            font=cls.FONTS['subtitle']
        )
        
        # Configurar frames
        style.configure(
            'Sidebar.TFrame',
            background=cls.COLORS['sidebar'],
            relief='raised',
            borderwidth=1
        )
        
        style.configure(
            'Chat.TFrame',
            background=cls.COLORS['chat_bg'],
            relief='flat'
        )
        
        # Configurar labels
        style.configure(
            'Title.TLabel',
            font=cls.FONTS['title'],
            foreground=cls.COLORS['primary'],
            background=cls.COLORS['white']
        )
        
        style.configure(
            'Subtitle.TLabel',
            font=cls.FONTS['subtitle'],
            foreground=cls.COLORS['dark']
        )
        
        # Configurar botões
        style.configure(
            'Primary.TButton',
            font=cls.FONTS['button']
        )
        
        style.configure(
            'Chat.TButton',
            font=cls.FONTS['chat']
        )
        
        # Configurar entry
        style.configure(
            'Chat.TEntry',
            font=cls.FONTS['chat'],
            fieldbackground=cls.COLORS['white']
        )

class IconManager:
    """Gerenciador de ícones e símbolos Unicode"""
    
    ICONS = {
        # Ícones principais
        'dashboard': '📊',
        'chart': '📈',
        'data': '🗄️',
        'ai': '🤖',
        'chat': '💬',
        'settings': '⚙️',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
        
        # Ícones de navegação
        'back': '🔙',
        'forward': '▶️',
        'refresh': '🔄',
        'search': '🔍',
        'filter': '🎯',
        'export': '📤',
        'import': '📥',
        
        # Ícones de ação
        'create': '➕',
        'edit': '✏️',
        'delete': '🗑️',
        'save': '💾',
        'cancel': '❌',
        'send': '📨',
        'clear': '🧹',
        
        # Ícones específicos
        'state': '🏛️',
        'region': '🗺️',
        'money': '💰',
        'education': '🎓',
        'health': '🏥',
        'infrastructure': '🏗️',
        'ranking': '🏆',
        'trend': '📈',
        'analysis': '🔬'
    }
    
    @classmethod
    def get(cls, name: str, default: str = '•') -> str:
        """Retorna ícone por nome"""
        return cls.ICONS.get(name, default)

def create_styled_window(title: str = "Sistema DEC7588") -> ttk.Window:
    """Cria janela principal com estilo aplicado"""
    
    # Criar janela com tema
    window = ttk.Window(
        title=title,
        themename=AppTheme.get_theme_name(),
        size=(AppTheme.DIMENSIONS['window_width'], 
              AppTheme.DIMENSIONS['window_height']),
        minsize=(AppTheme.DIMENSIONS['min_width'], 
                AppTheme.DIMENSIONS['min_height'])
    )
    
    # Centralizar janela
    window.place_window_center()
    
    # Aplicar estilos personalizados
    style = ttk.Style()
    AppTheme.apply_widget_styles(style)
    
    return window

class Styling:
    """Classe principal de estilos - compatibilidade com main_window"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1e3a8a',
            'secondary': '#3b82f6', 
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'background': '#ffffff',
            'sidebar_bg': '#f1f5f9',
            'white': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b'
        }
        
        self.fonts = {
            'large_bold': ('Segoe UI', 16, 'bold'),
            'medium_bold': ('Segoe UI', 12, 'bold'),
            'small_bold': ('Segoe UI', 10, 'bold'),
            'small': ('Segoe UI', 9),
            'extra_large_bold': ('Segoe UI', 20, 'bold')
        }
        
        self.icons = {
            'dashboard': '📊', 'chart': '📈', 'database': '🗄️', 'chat': '💬',
            'settings': '⚙️', 'refresh': '🔄', 'check': '✅', 'loading': '⏳',
            'search': '🔍', 'filter': '🎯', 'tools': '🛠️', 'download': '📥',
            'plus': '➕', 'edit': '✏️', 'save': '💾', 'cancel': '❌', 
            'trash': '🗑️', 'view': '👁️', 'send': '📨', 'lightbulb': '💡',
            'arrow_up': '↗️', 'arrow_down': '↘️', 'minus': '➖'
        }

def get_status_color(status: str) -> str:
    """Retorna cor baseada no status"""
    status_colors = {
        'success': AppTheme.COLORS['success'],
        'error': AppTheme.COLORS['danger'],
        'warning': AppTheme.COLORS['warning'],
        'info': AppTheme.COLORS['info'],
        'connected': AppTheme.COLORS['success'],
        'disconnected': AppTheme.COLORS['danger'],
        'processing': AppTheme.COLORS['warning']
    }
    
    return status_colors.get(status, AppTheme.COLORS['muted']) 