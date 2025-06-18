import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QLineEdit, 
                               QPushButton, QStackedWidget, QFrame)
from PySide6.QtCore import Qt, QUrl, QEvent, QRect
from PySide6.QtGui import QPalette, QColor, QPainter, QPixmap, QTextCursor
from pathlib import Path

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

# Classe para o widget com imagem de fundo personalizada
class BackgroundImageWidget(QWidget):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self.setContentsMargins(15, 15, 15, 15) # Margens para o conteúdo do chat

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap.isNull():
            # Escalar o pixmap para caber no widget mantendo a proporção
            scaled_pixmap = self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Calcular posição para centralizar o pixmap
            x = (self.width() - scaled_pixmap.width()) / 2
            y = (self.height() - scaled_pixmap.height()) / 2
            
            painter.drawPixmap(int(x), int(y), scaled_pixmap)
        else:
            # Fallback se o pixmap não for válido (opcional, pode só não desenhar)
            painter.fillRect(self.rect(), QColor("#2a2a2a")) # Pinta com a cor de fundo

        super().paintEvent(event) # Chama o paintEvent da classe base se necessário


class GeminiStyleDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        print("🚀 [INIT] Iniciando GeminiStyleDashboard")
        
        self.setWindowTitle("Brasil em Dados")
        self.setGeometry(100, 100, 1400, 900) # Aumentado o tamanho padrão

        # Configuração do Projeto
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.graphs_path = self.project_root / "results" / "visualizations"

        self._apply_dark_theme()
        
        # --- Widgets Principais ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal que conterá APENAS a área de conteúdo central.
        # As sidebars serão widgets filhos flutuantes, não gerenciadas por este layout.
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Área de Conteúdo Central ---
        content_container = QFrame()
        content_container.setObjectName("ContentContainer")
        content_container.setStyleSheet("QFrame#ContentContainer { border: none; }")
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(content_container, 1)

        # Título
        self._setup_title(content_container_layout)

        # Stack para alternar entre Chat e Gráficos
        self.view_stack = QStackedWidget()
        content_container_layout.addWidget(self.view_stack, 1)
        
        # Visão 1: Chat Central
        print("💬 [INIT] Criando widget de chat principal")
        self.main_chat_view = self._create_chat_widget(is_main_view=True)
        print(f"💬 [INIT] Chat criado: {self.main_chat_view}")
        self.view_stack.addWidget(self.main_chat_view)
        print(f"📊 [INIT] View stack após adicionar chat tem {self.view_stack.count()} widgets")

        # Visão 2: Container de Gráficos
        print("📈 [INIT] Criando widget de gráficos")
        self.graph_carousel_view = GraphsContainerWidget()
        self.view_stack.addWidget(self.graph_carousel_view)
        print(f"📊 [INIT] View stack após adicionar gráficos tem {self.view_stack.count()} widgets")

        print("📺 [INIT] Definindo chat como widget atual")
        self.view_stack.setCurrentWidget(self.main_chat_view)
        print(f"📺 [INIT] Widget atual no stack: {self.view_stack.currentWidget()}")

        # --- Barra Lateral Esquerda ---
        print("⬅️  [INIT] Configurando sidebar esquerda")
        self._setup_left_sidebar()
        
        # Controle de estado do chat (modo principal ou sidebar)
        print("🎛️  [INIT] Inicializando controles de estado do chat")
        self.chat_in_sidebar_mode = False
        self.chat_animation = None
        print(f"🎛️  [INIT] Estado inicial - chat_in_sidebar_mode: {self.chat_in_sidebar_mode}")
        
        # Configurar chat para ser flutuante (pode ficar sobre outros widgets)
        self._setup_floating_chat()
        
        # Inicialização do LLM
        print("🤖 [INIT] Inicializando LLM handler")
        self._initialize_llm_handler()

        # Conectar apenas o chat principal
        print("🔌 [INIT] Conectando eventos do chat")
        self.main_chat_input.returnPressed.connect(self._send_message)
        print("✅ [INIT] Dashboard inicializado com sucesso")

    def resizeEvent(self, event):
        """Sobrescreve o evento de redimensionamento para posicionar as sidebars."""
        super().resizeEvent(event)
        # Posicionar a sidebar esquerda
        self.left_sidebar.move(0, 0)
        self.left_sidebar.setFixedHeight(self.central_widget.height())
        
        # Reposicionar o chat conforme o modo atual
        if self.chat_in_sidebar_mode:
            self._position_chat_sidebar()
        else:
            self._position_chat_main()

    def _setup_floating_chat(self):
        """Configura o chat para ser flutuante e fazer transições animadas."""
        print("🌟 [SETUP] Configurando chat flutuante")
        
        # Remover o chat do view_stack e torná-lo flutuante
        self.view_stack.removeWidget(self.main_chat_view)
        self.main_chat_view.setParent(self.central_widget)
        
        # Posição inicial (modo principal - centro)
        self._position_chat_main()
        
        # Configurar animações
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
        
        self.chat_position_animation = QPropertyAnimation(self.main_chat_view, b"geometry")
        self.chat_position_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.chat_position_animation.setDuration(300)
        
        print(f"✅ [SETUP] Chat flutuante configurado: {self.main_chat_view}")

    def _position_chat_main(self):
        """Posiciona o chat no modo principal (centro, grande)."""
        # Margem ao redor do chat
        margin = 20
        x = margin
        y = 60  # Espaço para o título
        width = self.central_widget.width() - (2 * margin)
        height = self.central_widget.height() - y - margin
        
        print(f"📍 [POSICIONAMENTO] Chat modo principal: x={x}, y={y}, w={width}, h={height}")
        self.main_chat_view.setGeometry(x, y, width, height)
        self.main_chat_view.show()

    def _position_chat_sidebar(self):
        """Posiciona o chat no modo sidebar (direita, compacto)."""
        if not self.chat_in_sidebar_mode:
            return
            
        # Dimensões da sidebar (igual à esquerda)
        sidebar_width = 400 if hasattr(self, 'sidebar_expanded') and self.sidebar_expanded else 50
        x = self.central_widget.width() - sidebar_width
        y = 0
        height = self.central_widget.height()
        
        print(f"📍 [POSICIONAMENTO] Chat modo sidebar: x={x}, y={y}, w={sidebar_width}, h={height}")
        self.main_chat_view.setGeometry(x, y, sidebar_width, height)
        self.main_chat_view.show()

    def _setup_left_sidebar(self):
        self.left_sidebar = CollapsibleSidebar(self.central_widget, expanded_width=200, direction=Qt.LeftEdge)
        self.left_sidebar.setObjectName("LeftSidebar")
        
        sidebar_layout = self.left_sidebar.get_inner_layout()

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



    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #424242;")
        return separator

    def _setup_title(self, layout):
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
        
        self.title_label = QLabel(styled_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)

    def _create_chat_widget(self, is_main_view: bool):
        if is_main_view:
            background_pixmap = QPixmap()
            image_path = SCRIPT_DIR / "assets" / "Mapa Brasil.png"
            if image_path.exists():
                background_pixmap.load(str(image_path.resolve()))
            chat_container = BackgroundImageWidget(background_pixmap)
        else:
            chat_container = QWidget() # Sem imagem de fundo na sidebar
        
        chat_container.setObjectName("ChatContainerWidget")
        chat_container.setStyleSheet("background-color: transparent; border-radius: 8px;")
        
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0) if not is_main_view else chat_layout.setContentsMargins(15, 15, 15, 15)
        
        history_display = QTextEdit()
        history_display.setReadOnly(True)
        history_display.setObjectName("ChatHistoryDisplay")
        history_display.setStyleSheet("background-color: rgba(43, 43, 43, 0.8); color: #dcdcdc; border: 1px solid #3c3c3c; border-radius: 4px;")
        
        input_line = QLineEdit()
        input_line.setPlaceholderText("Digite sua mensagem...")
        input_line.setObjectName("ChatInputLine")
        input_line.setStyleSheet("background-color: #222222; color: #dcdcdc; border: 1px solid #3c3c3c; border-radius: 8px; padding: 10px; font-size: 14px;")
        input_line.setFixedHeight(50)
        
        chat_layout.addWidget(history_display, 1)
        chat_layout.addWidget(input_line)

        # Armazenar referências aos widgets de chat
        if is_main_view:
            self.main_chat_history = history_display
            self.main_chat_input = input_line
            
        return chat_container

    def _initialize_llm_handler(self):
        self.llm_handler = None
        if LLMQueryHandler:
            try:
                self.llm_handler = LLMQueryHandler()
                print("LLMQueryHandler inicializado com sucesso.")
            except Exception as e:
                print(f"Erro ao inicializar LLMQueryHandler: {e}")
    


    def _transition_chat_to_sidebar(self):
        """Faz transição animada do chat do centro para o modo sidebar."""
        print("🔄 [TRANSIÇÃO] Iniciando transição chat -> sidebar")
        
        if self.chat_in_sidebar_mode:
            print("⚠️  [TRANSIÇÃO] Chat já está no modo sidebar, abortando")
            return
            
        print("🎬 [TRANSIÇÃO] Iniciando animação para modo sidebar")
        
        # Configurar geometria final (sidebar compacta)
        sidebar_width = 50  # Largura compacta inicial
        target_x = self.central_widget.width() - sidebar_width
        target_y = 0
        target_width = sidebar_width
        target_height = self.central_widget.height()
        
        # Geometria atual (modo principal)
        current_geometry = self.main_chat_view.geometry()
        target_geometry = QRect(target_x, target_y, target_width, target_height)
        
        print(f"🎯 [TRANSIÇÃO] Geometria atual: {current_geometry}")
        print(f"🎯 [TRANSIÇÃO] Geometria alvo: {target_geometry}")
        
        # Configurar e iniciar animação
        self.chat_position_animation.setStartValue(current_geometry)
        self.chat_position_animation.setEndValue(target_geometry)
        
        # Callback para quando a animação terminar
        from PySide6.QtCore import QRect
        self.chat_position_animation.finished.connect(self._on_sidebar_animation_finished)
        
        self.chat_position_animation.start()
        self.chat_in_sidebar_mode = True
        
        # Configurar hover para expandir/contrair (igual sidebar esquerda)
        self._setup_chat_hover_behavior()
        
        print("✅ [TRANSIÇÃO] Animação para sidebar iniciada")

    def _transition_chat_to_main(self):
        """Faz transição animada do chat do modo sidebar para o centro."""
        print("🔄 [TRANSIÇÃO] Iniciando transição sidebar -> chat principal")
        
        if not self.chat_in_sidebar_mode:
            print("⚠️  [TRANSIÇÃO] Chat não está no modo sidebar, abortando")
            return
            
        print("🎬 [TRANSIÇÃO] Iniciando animação para modo principal")
        
        # Remover comportamento de hover
        self._remove_chat_hover_behavior()
        
        # Configurar geometria final (modo principal)
        margin = 20
        target_x = margin
        target_y = 60  # Espaço para o título
        target_width = self.central_widget.width() - (2 * margin)
        target_height = self.central_widget.height() - target_y - margin
        
        # Geometria atual (sidebar)
        current_geometry = self.main_chat_view.geometry()
        target_geometry = QRect(target_x, target_y, target_width, target_height)
        
        print(f"🎯 [TRANSIÇÃO] Geometria atual: {current_geometry}")
        print(f"🎯 [TRANSIÇÃO] Geometria alvo: {target_geometry}")
        
        # Configurar e iniciar animação
        self.chat_position_animation.setStartValue(current_geometry)
        self.chat_position_animation.setEndValue(target_geometry)
        
        # Callback para quando a animação terminar
        self.chat_position_animation.finished.connect(self._on_main_animation_finished)
        
        self.chat_position_animation.start()
        
        print("✅ [TRANSIÇÃO] Animação para modo principal iniciada")

    def _on_sidebar_animation_finished(self):
        """Callback chamado quando a animação para sidebar termina."""
        print("🎬 [ANIMAÇÃO] Transição para sidebar concluída")
        self.chat_position_animation.finished.disconnect()

    def _on_main_animation_finished(self):
        """Callback chamado quando a animação para modo principal termina."""
        print("🎬 [ANIMAÇÃO] Transição para modo principal concluída")
        self.chat_in_sidebar_mode = False
        self.chat_position_animation.finished.disconnect()

    def _setup_chat_hover_behavior(self):
        """Configura comportamento de hover para expandir/contrair quando no modo sidebar."""
        print("🖱️  [HOVER] Configurando comportamento de hover no chat")
        
        # Instalar event filter para detectar mouse enter/leave
        self.main_chat_view.installEventFilter(self)
        self.sidebar_expanded = False

    def _remove_chat_hover_behavior(self):
        """Remove comportamento de hover do chat."""
        print("🖱️  [HOVER] Removendo comportamento de hover do chat")
        self.main_chat_view.removeEventFilter(self)
        if hasattr(self, 'sidebar_expanded'):
            delattr(self, 'sidebar_expanded')

    def eventFilter(self, obj, event):
        """Filtro de eventos para detectar hover no chat quando em modo sidebar."""
        if obj == self.main_chat_view and self.chat_in_sidebar_mode:
            from PySide6.QtCore import QEvent
            
            if event.type() == QEvent.Enter:
                print("🖱️  [HOVER] Mouse entrou no chat - expandindo")
                self._expand_chat_sidebar()
            elif event.type() == QEvent.Leave:
                print("🖱️  [HOVER] Mouse saiu do chat - contraindo")
                self._collapse_chat_sidebar()
                
        return super().eventFilter(obj, event)

    def _expand_chat_sidebar(self):
        """Expande o chat quando em modo sidebar (igual sidebar esquerda)."""
        if not self.chat_in_sidebar_mode or self.sidebar_expanded:
            return
            
        print("📏 [HOVER] Expandindo chat sidebar")
        expanded_width = 400
        x = self.central_widget.width() - expanded_width
        y = 0
        height = self.central_widget.height()
        
        target_geometry = QRect(x, y, expanded_width, height)
        current_geometry = self.main_chat_view.geometry()
        
        self.chat_position_animation.setStartValue(current_geometry)
        self.chat_position_animation.setEndValue(target_geometry)
        self.chat_position_animation.start()
        
        self.sidebar_expanded = True

    def _collapse_chat_sidebar(self):
        """Contrai o chat quando em modo sidebar (igual sidebar esquerda)."""
        if not self.chat_in_sidebar_mode or not self.sidebar_expanded:
            return
            
        print("📏 [HOVER] Contraindo chat sidebar")
        collapsed_width = 50
        x = self.central_widget.width() - collapsed_width
        y = 0
        height = self.central_widget.height()
        
        target_geometry = QRect(x, y, collapsed_width, height)
        current_geometry = self.main_chat_view.geometry()
        
        self.chat_position_animation.setStartValue(current_geometry)
        self.chat_position_animation.setEndValue(target_geometry)
        self.chat_position_animation.start()
        
        self.sidebar_expanded = False

    def show_main_chat_view(self):
        """Volta para a tela de chat principal."""
        print("🏠 [NAVEGAÇÃO] Botão 'Início' clicado - voltando para chat principal")
        print(f"🔍 [NAVEGAÇÃO] Estado atual - chat_in_sidebar_mode: {self.chat_in_sidebar_mode}")
        
        # Fazer transição do chat para modo principal
        self._transition_chat_to_main()
        
        # Mostrar uma view vazia no stack (chat agora é flutuante)
        # Criamos um placeholder se não existe
        if not hasattr(self, 'empty_view'):
            self.empty_view = QWidget()
            self.view_stack.addWidget(self.empty_view)
            
        print(f"📺 [NAVEGAÇÃO] Definindo view_stack para empty_view (chat é flutuante)")
        self.view_stack.setCurrentWidget(self.empty_view)
        print(f"📺 [NAVEGAÇÃO] View atual no stack: {self.view_stack.currentWidget()}")
    
    def show_graph_view(self, year: int | None):
        print(f"📊 [NAVEGAÇÃO] Botão de gráfico clicado para ano: {year if year else 'Geral'}")
        print(f"🔍 [NAVEGAÇÃO] Estado atual - chat_in_sidebar_mode: {self.chat_in_sidebar_mode}")
        
        # Usar o método correto do GraphsContainerWidget
        print("🔧 [NAVEGAÇÃO] Carregando gráficos no container")
        self.graph_carousel_view.load_graphs_for_year(year)

        # Mostrar a view de gráficos
        print(f"📺 [NAVEGAÇÃO] Definindo view_stack para graph_carousel_view")
        self.view_stack.setCurrentWidget(self.graph_carousel_view)
        print(f"📺 [NAVEGAÇÃO] View atual no stack: {self.view_stack.currentWidget()}")
        
        # Fazer transição do chat para modo sidebar
        print("🔄 [NAVEGAÇÃO] Iniciando transição para sidebar")
        self._transition_chat_to_sidebar()

    def _send_message(self):
        user_text = self.main_chat_input.text().strip()
        if not user_text:
            return
            
        self.main_chat_input.clear()

        # Atualizar o histórico de chat
        formatted_user_message = f'<p style="color: #8BE9FD;"><b>Você:</b> {user_text}</p>'
        self.main_chat_history.append(formatted_user_message)
        self.main_chat_history.ensureCursorVisible()

        if self.llm_handler:
            # Lógica de chamar o LLM e exibir resposta
            self.main_chat_history.append(f'<p style="color: #A9A9A9;"><i>Assistente está digitando...</i></p>')
            QApplication.processEvents() 

            text_response, filters = self.llm_handler.get_response(user_text)
            
            # Remover "digitando"
            cursor = self.main_chat_history.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            if "Assistente está digitando..." in cursor.selectedText():
                cursor.removeSelectedText()
                cursor.deletePreviousChar()
            
            formatted_assistant_message = f'<p style="color: #50FA7B;"><b>Assistente:</b> {text_response}</p>'
            self.main_chat_history.append(formatted_assistant_message)

            if filters:
                filter_message = f'<p style="color: #D3D3D3; font-size: small;"><i>Filtros identificados: {filters}</i></p>'
                self.main_chat_history.append(filter_message)
        else:
            # Lógica de LLM não disponível
            error_message = f'<p style="color: #FF6347;"><b>Assistente:</b> LLM não está disponível.</p>'
            self.main_chat_history.append(error_message)
        
        self.main_chat_history.ensureCursorVisible()

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

if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = GeminiStyleDashboard()
    window.show()
    app.exec() 