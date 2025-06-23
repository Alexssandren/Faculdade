import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QLineEdit, 
                               QPushButton, QFrame)
from PySide6.QtCore import Qt, QUrl, QEvent, Property, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QPalette, QColor, QPainter, QPixmap, QTextCursor
from pathlib import Path
from enum import Enum

# Adicionar o diretório 'src' ao sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from llm.llm_handler import LLMQueryHandler
    from app.widgets.collapsible_sidebar import CollapsibleSidebar
    from app.widgets.graphs_container import GraphsContainerWidget
except ImportError as e:
    print(f"Erro ao importar módulos: {e}. Verifique o sys.path e a estrutura do projeto.")
    LLMQueryHandler = None
    CollapsibleSidebar = None
    GraphsContainerWidget = None

class ChatLayoutMode(Enum):
    """Enum para definir os modos de layout do chat."""
    MAIN_VIEW = "main_view"      # 90% centralizado, sem funcionalidade de collapse
    SIDEBAR_VIEW = "sidebar_view" # Barra lateral direita com funcionalidade de collapse

# Classe para o widget com imagem de fundo personalizada
class BackgroundImageWidget(QWidget):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self._solid_background_mode = False
        self.setContentsMargins(15, 15, 15, 15)

    def set_background_mode(self, is_solid: bool):
        """Controla se o fundo do widget deve ser sólido ou transparente."""
        if self._solid_background_mode != is_solid:
            self._solid_background_mode = is_solid
            self.update() # Força uma nova pintura

    def paintEvent(self, event):
        painter = QPainter(self)

        # 1. Pinta o fundo manualmente para ter controle total da ordem.
        if self._solid_background_mode:
            painter.fillRect(self.rect(), QColor("#2b2b2b"))
        # Se não, o fundo fica transparente por padrão.

        # 2. Pinta a imagem do mapa por cima do fundo.
        if not self.pixmap.isNull():
            # Escalar o pixmap para caber no widget mantendo a proporção
            scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Calcular posição para centralizar o pixmap
            x = (self.width() - scaled_pixmap.width()) / 2
            y = (self.height() - scaled_pixmap.height()) / 2
            
            painter.drawPixmap(int(x), int(y), scaled_pixmap)

class GeminiStyleDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brasil em Dados")
        self.setGeometry(100, 100, 1400, 900) # Aumentado o tamanho padrão
        self.showMaximized()  # Forçar janela maximizada para garantir tamanho total

        # Configuração do Projeto
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.graphs_path = self.project_root / "results" / "visualizations"

        # Estado do modo de layout do chat
        self.chat_mode = ChatLayoutMode.MAIN_VIEW
        self.transition_animation = None  # Para armazenar a animação de transição
        
        # Timer para debouncing de redimensionamento
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_delayed_resize)
        self.resize_timer.setInterval(50)  # 50ms de delay para debouncing

        self._apply_dark_theme()
        
        # --- Widgets Principais ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal que conterá APENAS a área de conteúdo central.
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self._setup_main_title()

        # --- Área de Conteúdo Central ---
        content_container = QFrame()
        content_container.setObjectName("ContentContainer")
        content_container.setStyleSheet("QFrame#ContentContainer { border: none; }")
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(content_container, 1)

        # O contêiner de conteúdo agora abriga diretamente a visão de gráficos
        self.graphs_view = GraphsContainerWidget()
        content_container_layout.addWidget(self.graphs_view, 1)

        # --- Barras Laterais (Agora flutuantes) ---
        self._setup_left_sidebar()
        self._setup_right_sidebar()
        
        # Conecta o sinal de mudança de largura para reposicionar a barra
        self.right_sidebar.widthChanged.connect(self._reposition_right_sidebar)
        
        self.title_label.raise_() # Eleva o título para garantir que fique visível

        # Inicialização do LLM
        self._initialize_llm_handler()
        
        # CORREÇÃO: Garantir que o chat seja visível no estado inicial
        self.right_sidebar.show()
        self.chat_widget.show()
        
        # CORREÇÃO: Configurar primeiro, depois expandir
        # Define o estado inicial do dashboard (será configurado após a janela ser mostrada)
        self.show_main_chat_view()
        
        # Forçar expansão APÓS configuração correta
        self.right_sidebar.expand()
        


    
    def resizeEvent(self, event):
        """Sobrescreve o evento de redimensionamento para posicionar as sidebars com debouncing."""
        if event is not None:
            # Usar debouncing para evitar múltiplas operações durante redimensionamento contínuo
            self.resize_timer.start()
            return
            
        super().resizeEvent(event)
        
        # Verificar se a janela tem tamanho válido
        if self.central_widget.width() <= 0 or self.central_widget.height() <= 0:
            return
        
        # Posiciona o título principal para que seja independente
        self.title_label.setGeometry(0, 10, self.central_widget.width(), 50)
        self.title_label.raise_()

        # Posicionar a sidebar esquerda
        self.left_sidebar.move(0, 0)
        self.left_sidebar.setFixedHeight(self.central_widget.height())
        
        # CORREÇÃO: NÃO forçar altura total - usar valores fixos
        # self.right_sidebar.setFixedHeight(self.central_widget.height())  # REMOVIDO
        
        # Parar animação atual se estiver rodando durante redimensionamento
        if self.transition_animation and self.transition_animation.state() == QPropertyAnimation.State.Running:
            self.transition_animation.stop()
        
        if self.chat_mode == ChatLayoutMode.MAIN_VIEW:
            # CORREÇÃO: Usar valores fixos para o redimensionamento
            chat_x, chat_width = self._calculate_main_mode_geometry()
            chat_height = self._get_main_mode_height()
            # Atualizar também a largura expandida da sidebar
            self.right_sidebar.expanded_width = chat_width
            self.right_sidebar.setFixedWidth(chat_width)
            self.right_sidebar.setGeometry(chat_x, 70, chat_width, chat_height)
        else:  # SIDEBAR_VIEW
            # CORREÇÃO: Usar valores fixos para o modo sidebar
            sidebar_x, sidebar_width = self._calculate_sidebar_mode_geometry()
            sidebar_height = self._get_main_mode_height()
            self.right_sidebar.expanded_width = sidebar_width
            self.right_sidebar.setFixedWidth(sidebar_width)
            self.right_sidebar.setGeometry(sidebar_x, 70, sidebar_width, sidebar_height)

    def _reposition_right_sidebar(self):
        """Move a sidebar direita para a posição correta, com base na sua largura atual."""
        x_pos = self.central_widget.width() - self.right_sidebar.width()
        self.right_sidebar.move(x_pos, 0)
        # CORREÇÃO: NÃO forçar altura total - usar altura fixa
        # self.right_sidebar.setFixedHeight(self.central_widget.height())  # REMOVIDO

    def _calculate_main_mode_geometry(self):
        """Calcula geometria para modo principal com valores pré-definidos."""
        # CORREÇÃO: Usar valores fixos pré-definidos pelo usuário
        chat_width = 1382  # Largura fixa
        total_width = self.central_widget.width()
        chat_x = int((total_width - chat_width) / 2)  # Centralizar
        
        # Garantir que a posição não seja negativa
        chat_x = max(0, chat_x)
        
        
        return chat_x, chat_width

    def _get_main_mode_height(self):
        """Retorna altura fixa pré-definida para modo principal."""
        # CORREÇÃO: Usar valor fixo pré-definido pelo usuário
        fixed_height = 756  # Altura fixa
        
        
        return fixed_height

    def _calculate_sidebar_mode_geometry(self):
        """Calcula geometria para modo barra lateral com tamanho original."""
        # CORREÇÃO: Restaurar tamanho original da sidebar (400px)
        chat_width = self.sidebar_original_expanded_width  # 400px - tamanho original
        total_width = self.central_widget.width()
        
        # Para sidebar, posicionar na direita (manter comportamento atual de sidebar)
        sidebar_x = total_width - chat_width
        
        # Garantir que a posição não seja negativa
        sidebar_x = max(0, sidebar_x)
        
        
        return sidebar_x, chat_width

    def transition_to_main_mode(self):
        """Executa transição animada para modo principal (90% centralizado)."""
        if self.chat_mode == ChatLayoutMode.MAIN_VIEW:
            return  # Já está no modo correto
            
        self.chat_mode = ChatLayoutMode.MAIN_VIEW
        self._animate_chat_transition()

    def transition_to_sidebar_mode(self):
        """Executa transição animada para modo barra lateral."""
        if self.chat_mode == ChatLayoutMode.SIDEBAR_VIEW:
            return  # Já está no modo correto
            
        self.chat_mode = ChatLayoutMode.SIDEBAR_VIEW
        self._animate_chat_transition()

    def _animate_chat_transition(self):
        """Executa animação de transição entre os modos com valores fixos."""
        # Validar se a janela tem tamanho suficiente para animação
        if self.central_widget.width() <= 0 or self.central_widget.height() <= 0:
            return  # Silenciosamente ignorar se janela não tem tamanho válido
        
        # CORREÇÃO: Usar valores fixos para ambos os modos
        fixed_height = self._get_main_mode_height()
        
        # Determinar geometria alvo baseada no modo atual
        if self.chat_mode == ChatLayoutMode.MAIN_VIEW:
            target_x, target_width = self._calculate_main_mode_geometry()
            target_height = fixed_height
            # CORREÇÃO: Atualizar largura expandida da sidebar para o modo principal
            self.right_sidebar.expanded_width = target_width
            enable_hover = False
        else:  # SIDEBAR_VIEW
            target_x, target_width = self._calculate_sidebar_mode_geometry()
            target_height = fixed_height  # Mesma altura fixa
            # CORREÇÃO: Restaurar largura expandida para o modo sidebar
            self.right_sidebar.expanded_width = target_width
            enable_hover = True
        
        # Verificar se a geometria alvo é válida
        if target_width <= 0 or target_x < 0:
            return  # Silenciosamente ignorar geometria inválida
        
        # CORREÇÃO: Atualizar setFixedWidth antes da animação
        self.right_sidebar.setFixedWidth(target_width)
        
        # Verificar se já está na posição correta (otimização)
        current_rect = self.right_sidebar.geometry()
        if current_rect.x() == target_x and current_rect.width() == target_width:
            # Apenas ajustar hover se necessário
            self.right_sidebar.setHoverEnabled(enable_hover)
            return
        
        # Parar animação anterior se estiver rodando
        if self.transition_animation and self.transition_animation.state() == QPropertyAnimation.State.Running:
            self.transition_animation.stop()
            self.transition_animation.deleteLater()
        
        # Criar nova animação
        self.transition_animation = QPropertyAnimation(self.right_sidebar, b"geometry")
        self.transition_animation.setDuration(300)  # Mesmo tempo da sidebar existente
        self.transition_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Mesmo easing da sidebar existente
        
        # Configurar estados inicial e final
        start_rect = self.right_sidebar.geometry()
        # CORREÇÃO: Usar altura fixa para ambos os modos
        end_rect = QRect(target_x, 70, target_width, target_height)
        
        self.transition_animation.setStartValue(start_rect)
        self.transition_animation.setEndValue(end_rect)
        
        # Conectar finalização da animação para ajustar funcionalidade de hover
        self.transition_animation.finished.connect(lambda: self.right_sidebar.setHoverEnabled(enable_hover))
        
        # Iniciar animação
        self.transition_animation.start()

    def _setup_left_sidebar(self):
        self.left_sidebar = CollapsibleSidebar(self.central_widget, collapsed_width=25, expanded_width=200, direction=Qt.LeftEdge)
        self.left_sidebar.setObjectName("LeftSidebar")
        
        sidebar_layout = self.left_sidebar.get_inner_layout()

        # Adiciona margem superior para não sobrepor o título principal
        sidebar_layout.setContentsMargins(3, 10, 3, 10)  # Margens laterais menores para centralizar

        # Adiciona ícone de três riscos (hamburger menu)
        hamburger_icon = QLabel("☰")  # Mudando para ícone mais visível
        hamburger_icon.setObjectName("HamburgerIcon")  # Identificador único
        hamburger_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hamburger_icon.setStyleSheet("""
            font-size: 12px; 
            font-weight: bold; 
            color: #ffffff; 
            background-color: rgba(255, 255, 255, 0.1);
            padding: 2px;
            border-radius: 2px;
            margin: 0px;
        """)
        hamburger_icon.setToolTip("Menu de Navegação")
        hamburger_icon.setFixedSize(18, 18)  # Tamanho ajustado para caber na sidebar de 25px
        sidebar_layout.addWidget(hamburger_icon, 0, Qt.AlignmentFlag.AlignCenter)

        # Adiciona Título
        title_label = QLabel("Gráficos")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px; color: #e0e0e0;")
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self._create_separator())
        
        # Botão para voltar ao Chat principal
        home_button = QPushButton("🏠 Início")
        home_button.clicked.connect(self.show_main_chat_view)
        sidebar_layout.addWidget(home_button)
        sidebar_layout.addWidget(self._create_separator())

        subtitle_label = QLabel("Gráficos por Ano")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(subtitle_label)

        for year in range(2023, 2018, -1): # Ordem decrescente
            year_button = QPushButton(str(year))
            year_button.clicked.connect(lambda checked=False, y=year: self.show_graph_view(y))
            sidebar_layout.addWidget(year_button)
        
        sidebar_layout.addWidget(self._create_separator())
        
        general_button = QPushButton("Visão Geral")
        general_button.clicked.connect(lambda: self.show_graph_view(None))
        sidebar_layout.addWidget(general_button)

        sidebar_layout.addStretch()
        
        # Forçar atualização da visibilidade após todos os widgets serem adicionados
        self.left_sidebar.update_content_visibility()

    def _setup_right_sidebar(self):
        """Cria a barra lateral direita flutuante para o chat."""
        self.sidebar_original_expanded_width = 400
        
        # DEPURAÇÃO CORREÇÃO 1: Usar valores fixos desde o início
        initial_width = 1382  # CORRIGIDO: Usar largura fixa definida pelo usuário
        
        self.right_sidebar = CollapsibleSidebar(
            self.central_widget, 
            collapsed_width=25, 
            expanded_width=initial_width,  # CORRIGIDO: Usar valor fixo
            direction=Qt.RightEdge,
            enable_hover=False  # Inicialmente desabilitado para modo principal
        )
        
        # NÃO forçar largura inicial aqui - será ajustada em show_main_chat_view
        
        sidebar_layout = self.right_sidebar.get_inner_layout()

        # Margem normal - a geometria da sidebar já considera o espaço do título
        sidebar_layout.setContentsMargins(3, 10, 3, 10)  # Margens laterais menores para centralizar
        
        # Adiciona ícone de três riscos (hamburger menu) para sidebar direita
        hamburger_icon_right = QLabel("☰")
        hamburger_icon_right.setObjectName("HamburgerIconRight")  # Identificador único
        hamburger_icon_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hamburger_icon_right.setStyleSheet("""
            font-size: 12px; 
            font-weight: bold; 
            color: #ffffff; 
            background-color: rgba(255, 255, 255, 0.1);
            padding: 2px;
            border-radius: 2px;
            margin: 0px;
        """)
        hamburger_icon_right.setToolTip("Chat LLM")
        hamburger_icon_right.setFixedSize(18, 18)  # Tamanho ajustado para caber na sidebar de 25px
        sidebar_layout.addWidget(hamburger_icon_right, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Chat Widget
        self.chat_widget = self._create_chat_widget()
        sidebar_layout.addWidget(self.chat_widget, 1)  # stretch=1 para ocupar espaço disponível

        # CRÍTICO: Posicionar sidebar inicialmente fora da tela para evitar flash
        self.right_sidebar.setGeometry(-2000, 0, initial_width, self.central_widget.height())
        
        # Forçar atualização da visibilidade após todos os widgets serem adicionados
        self.right_sidebar.update_content_visibility()

    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #424242;")
        return separator
        
    def _setup_main_title(self):
        """Cria o título principal 'Brasil em Dados' como um widget flutuante."""
        title_text = "Brasil em Dados"
        colors = ["#009B3A", "#FFCC29", "#FFFFFF"] # Verde, Amarelo, Branco
        styled_title = ""
        color_index = 0
        for char in title_text:
            if char == ' ':
                styled_title += ' '
            else:
                color = colors[color_index % len(colors)]
                styled_title += f'<span style="color: {color};">{char}</span>'
                color_index += 1
        
        self.title_label = QLabel(styled_title, self.central_widget) # Parented to central widget
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; margin-bottom: 10px; background-color: transparent;"
        )

    def _create_chat_widget(self):
        """Cria o widget de chat único e reutilizável com layout vertical otimizado."""
        # O container principal do chat agora tem sempre a imagem de fundo
        chat_container = BackgroundImageWidget(QPixmap(str(self.project_root / "src/app/assets/Mapa Brasil.png")))
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(10)  # Espaçamento entre elementos

        # CORREÇÃO: Histórico da Conversa (área maior, fica em cima)
        history = QTextEdit()
        history.setReadOnly(True)
        history.setObjectName("ChatHistory")
        # Aumentar o stretch factor para dar mais espaço para a conversa
        chat_layout.addWidget(history, 6)  # Aumentado de 5 para 6 para mais espaço

        # CORREÇÃO: Layout para a entrada de texto (fica embaixo)
        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        input_container.setStyleSheet("""
            QFrame#InputContainer {
                background-color: rgba(53, 53, 53, 0.9);
                border: 1px solid #666;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(10)
        
        # CORREÇÃO: Caixa de Entrada de Texto com altura fixa
        input_box = QLineEdit()
        input_box.setPlaceholderText("Digite sua pergunta aqui...")
        input_box.setObjectName("ChatInput")
        input_box.setMinimumHeight(35)  # Altura mínima para melhor usabilidade
        input_box.setStyleSheet("""
            QLineEdit#ChatInput {
                background-color: rgba(35, 35, 35, 0.95);
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit#ChatInput:focus {
                border: 2px solid #42a5f5;
                background-color: rgba(35, 35, 35, 1.0);
            }
        """)
        input_box.returnPressed.connect(self._send_message)
        input_layout.addWidget(input_box, 1)

        # CORREÇÃO: Adicionar o container de input ao layout principal
        # Stretch factor 0 para que mantenha tamanho fixo
        chat_layout.addWidget(input_container, 0)

        # Armazena os widgets do chat como atributos do contêiner para fácil acesso
        chat_container.history = history
        chat_container.input_box = input_box
        
        return chat_container

    def _initialize_llm_handler(self):
        """Inicializa o handler do LLM."""
        if LLMQueryHandler:
            try:
                self.llm_handler = LLMQueryHandler()
                print("INFO: LLMQueryHandler inicializado com sucesso.")
            except Exception as e:
                print(f"ERRO: Erro ao inicializar LLMQueryHandler: {e}")
                self.llm_handler = None
        else:
            self.llm_handler = None
            print("AVISO: Classe LLMQueryHandler não foi encontrada/importada.")
    
    def _connect_chat_widgets(self):
        # Esta função não é mais necessária, a conexão é feita em _create_chat_widget
        pass

    def show_main_chat_view(self):
        """Mostra a visão principal do chat, escondendo a de gráficos."""
        
        # Configurar modo principal primeiro
        self.chat_mode = ChatLayoutMode.MAIN_VIEW
        
        # CORREÇÃO: Aguardar processamento de eventos para garantir dimensões corretas
        QApplication.processEvents()
        
        # CORREÇÃO: Usar valores fixos pré-definidos
        chat_x, chat_width = self._calculate_main_mode_geometry()
        chat_height = self._get_main_mode_height()
        
        
        # CORREÇÃO: Configurar sidebar com dimensões corretas
        self.right_sidebar.setHoverEnabled(False)  # Desabilitar hover no modo principal
        
        # Atualizar a largura expandida da sidebar para o modo principal
        self.right_sidebar.expanded_width = chat_width
        self.right_sidebar.setFixedWidth(chat_width)
        
        # CORREÇÃO: Usar animação para transição suave ao modo principal
        self._animate_chat_transition()
        
        # Configurar aparência
        self.chat_widget.set_background_mode(is_solid=False)
        
        # Mostrar/ocultar elementos
        self.graphs_view.hide()
        self.right_sidebar.show()
        self.chat_widget.show()  # Garantir que o chat widget seja mostrado explicitamente
        
        # CRÍTICO: Forçar expansão da sidebar para garantir visibilidade do chat
        self.right_sidebar.expand()
        
        # No modo principal, o ícone hamburger direito deve estar sempre oculto
        self.right_sidebar.update_content_visibility(force_hide_right_hamburger=True)
        
        # CORREÇÃO: Garantir ordem de camadas correta - sidebar esquerda sempre no topo
        self.right_sidebar.raise_() # Garante que a sidebar do chat esteja no topo
        self.left_sidebar.raise_()  # CORREÇÃO: Sidebar esquerda acima da conversa
        

    def show_graph_view(self, year: int | None):
        """Mostra a visão de gráficos para um ano específico."""
        
        # Configurar modo sidebar primeiro
        self.chat_mode = ChatLayoutMode.SIDEBAR_VIEW
        
        # CORREÇÃO: Usar valores fixos para modo sidebar também
        sidebar_x, sidebar_width = self._calculate_sidebar_mode_geometry()
        sidebar_height = self._get_main_mode_height()  # Mesma altura do modo principal
        
        # Atualizar dimensões da sidebar
        self.right_sidebar.expanded_width = sidebar_width
        self.right_sidebar.setFixedWidth(sidebar_width)
        
        # Configurar sidebar para modo barra lateral
        self.right_sidebar.setHoverEnabled(True)  # Habilitar hover no modo sidebar
        
        # CORREÇÃO: Posicionar com valores fixos
        self.right_sidebar.setGeometry(sidebar_x, 70, sidebar_width, sidebar_height)
        
        # Configurar aparência
        self.chat_widget.set_background_mode(is_solid=True)
        
        # Mostrar/ocultar elementos
        self.graphs_view.show()
        self.graphs_view.raise_()
        
        # Carrega os gráficos para o ano selecionado
        self.graphs_view.load_graphs_for_year(year)

        # CORREÇÃO: Colapsar automaticamente a sidebar no modo gráficos para dar mais espaço
        self.right_sidebar.collapse()
        
        # No modo sidebar, o ícone hamburger direito pode ser exibido normalmente
        self.right_sidebar.update_content_visibility(force_hide_right_hamburger=False)

        # CORREÇÃO: Garantir ordem de camadas correta
        self.right_sidebar.raise_() # Eleva a barra de chat por cima dos gráficos
        self.left_sidebar.raise_()  # CORREÇÃO: Sidebar esquerda sempre no topo
        

    def _append_message_to_history(self, sender: str, message: str, color: str):
        """Adiciona uma mensagem ao histórico do chat com formatação."""
        history = self.chat_widget.history
        
        # .append() é o método correto e mais robusto.
        # Ele garante que a mensagem seja adicionada em um novo parágrafo (bloco)
        # e renderiza o HTML dentro dele, evitando sobreposições.
        html_message = f"<b style='color: {color};'>{sender}:</b> {message}"
        history.append(html_message)
        
        # Rolar para o final
        history.verticalScrollBar().setValue(history.verticalScrollBar().maximum())

    def _send_message(self):
        input_box = self.chat_widget.input_box
        history = self.chat_widget.history
        
        user_message = input_box.text().strip()
        if not user_message:
            return

        self._append_message_to_history("Você", user_message, "#8be9fd")
        input_box.clear()
        
        QApplication.processEvents()

        if self.llm_handler:
            try:
                # Exibe uma mensagem de "pensando..."
                self._append_message_to_history("Assistente", "...", "#f1fa8c")
                QApplication.processEvents()

                # Obtém a resposta do LLM
                response = self.llm_handler.get_response(user_message)

                # Remove a mensagem "pensando..." de forma segura com undo()
                # Isso desfaz a última operação de append.
                history.undo()

                # Extrai apenas o texto se a resposta for uma tupla
                if isinstance(response, tuple) and len(response) > 0:
                    llm_text = response[0]
                else:
                    llm_text = str(response)

                self._append_message_to_history("Assistente", llm_text, "#50fa7b")

            except Exception as e:
                # Garante que a mensagem "..." seja removida mesmo em caso de erro
                history.undo()
                self._append_message_to_history("Erro", f"Não foi possível obter a resposta. {e}", "#ff5555")
        else:
            self._append_message_to_history("Assistente", "O handler do LLM não está inicializado.", "#ffb86c")

    def _apply_dark_theme(self):
        app = QApplication.instance()
        if app is None:
            return

        app.setStyle("Fusion")
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(40,40,40))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(40,40,40))
        app.setPalette(dark_palette)

        # O estilo do chat volta a ser global e semi-transparente
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTextEdit#ChatHistory {
                background-color: rgba(43, 43, 43, 0.85); /* Fundo semi-transparente */
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
        """)

    def _handle_delayed_resize(self):
        self.resizeEvent(None)

    def closeEvent(self, event):
        """Limpeza ao fechar a janela."""
        # Parar e limpar animação se estiver rodando
        if self.transition_animation and self.transition_animation.state() == QPropertyAnimation.State.Running:
            self.transition_animation.stop()
            self.transition_animation.deleteLater()
        
        # Parar timer de redimensionamento
        if self.resize_timer.isActive():
            self.resize_timer.stop()
        
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = GeminiStyleDashboard()
    window.show()
    app.exec() 