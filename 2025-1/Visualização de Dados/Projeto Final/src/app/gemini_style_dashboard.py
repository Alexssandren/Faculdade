import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QLineEdit, 
                               QPushButton, QStackedWidget, QFrame)
from PySide6.QtCore import Qt, QUrl, QEvent
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
        self.main_chat_view = self._create_chat_widget(is_main_view=True)
        self.view_stack.addWidget(self.main_chat_view)

        # Visão 2: Container de Gráficos
        self.graph_carousel_view = GraphsContainerWidget()
        self.view_stack.addWidget(self.graph_carousel_view)

        self.view_stack.setCurrentWidget(self.main_chat_view)

        # --- Barras Laterais (Agora flutuantes) ---
        # Elas são criadas mas não são adicionadas a nenhum layout.
        # Serão posicionadas manualmente.
        self._setup_left_sidebar()
        self._setup_right_sidebar()
        
        # Inicialização do LLM
        self._initialize_llm_handler()

        # Conectar os widgets de chat ao handler
        self._connect_chat_widgets()

    def resizeEvent(self, event):
        """Sobrescreve o evento de redimensionamento para posicionar as sidebars."""
        super().resizeEvent(event)
        # Posicionar as sidebars manualmente sobre o central_widget
        self.left_sidebar.move(0, 0)
        self.left_sidebar.setFixedHeight(self.central_widget.height())
        
        self._reposition_right_sidebar()
        self.right_sidebar.setFixedHeight(self.central_widget.height())

    def _reposition_right_sidebar(self):
        """Move a sidebar direita para a posição correta, com base na sua largura atual."""
        x_pos = self.central_widget.width() - self.right_sidebar.width()
        self.right_sidebar.move(x_pos, 0)

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

    def _setup_right_sidebar(self):
        self.right_sidebar = CollapsibleSidebar(self.central_widget, expanded_width=400, direction=Qt.RightEdge)
        self.right_sidebar.setObjectName("RightSidebar")
        
        sidebar_layout = self.right_sidebar.get_inner_layout()

        # Adiciona Título
        title_label = QLabel("Assistente")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px; color: #e0e0e0;")
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self._create_separator())
        
        self.sidebar_chat_view = self._create_chat_widget(is_main_view=False)
        sidebar_layout.addWidget(self.sidebar_chat_view)

        self.right_sidebar.widthChanged.connect(self._reposition_right_sidebar)

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

        # Armazenar referências aos widgets de chat para poder conectar os sinais
        if is_main_view:
            self.main_chat_history = history_display
            self.main_chat_input = input_line
        else:
            self.sidebar_chat_history = history_display
            self.sidebar_chat_input = input_line
            
        return chat_container

    def _initialize_llm_handler(self):
        self.llm_handler = None
        if LLMQueryHandler:
            try:
                self.llm_handler = LLMQueryHandler()
                print("LLMQueryHandler inicializado com sucesso.")
            except Exception as e:
                print(f"Erro ao inicializar LLMQueryHandler: {e}")
    
    def _connect_chat_widgets(self):
        self.main_chat_input.returnPressed.connect(self._send_message)
        self.sidebar_chat_input.returnPressed.connect(self._send_message)

    def show_main_chat_view(self):
        """Volta para a tela de chat principal."""
        self.sidebar_chat_view.hide()
        self.view_stack.setCurrentWidget(self.main_chat_view)
    
    def show_graph_view(self, year: int | None):
        print(f"Carregando gráficos para o ano: {year if year else 'Geral'}")
        
        # Usar o método correto do GraphsContainerWidget
        self.graph_carousel_view.load_graphs_for_year(year)

        self.sidebar_chat_view.show()
        self.view_stack.setCurrentWidget(self.graph_carousel_view)

    def _send_message(self):
        # Descobrir qual input de texto enviou a mensagem
        sender_input = self.sender()
        if sender_input is self.main_chat_input:
            user_text = self.main_chat_input.text().strip()
            self.main_chat_input.clear()
        elif sender_input is self.sidebar_chat_input:
            user_text = self.sidebar_chat_input.text().strip()
            self.sidebar_chat_input.clear()
        else:
            return

        if not user_text:
            return

        # Atualizar ambos os históricos de chat
        formatted_user_message = f'<p style="color: #8BE9FD;"><b>Você:</b> {user_text}</p>'
        self.main_chat_history.append(formatted_user_message)
        self.sidebar_chat_history.append(formatted_user_message)
        self.main_chat_history.ensureCursorVisible()
        self.sidebar_chat_history.ensureCursorVisible()

        if self.llm_handler:
            # ... (Lógica de chamar o LLM e exibir resposta)
            # ... (A resposta do assistente também deve ser adicionada a ambos os históricos)
            self.main_chat_history.append(f'<p style="color: #A9A9A9;"><i>Assistente está digitando...</i></p>')
            self.sidebar_chat_history.append(f'<p style="color: #A9A9A9;"><i>Assistente está digitando...</i></p>')
            QApplication.processEvents() 

            text_response, filters = self.llm_handler.get_response(user_text)
            
            # Remover "digitando" de ambos
            for history_widget in [self.main_chat_history, self.sidebar_chat_history]:
                cursor = history_widget.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                if "Assistente está digitando..." in cursor.selectedText():
                    cursor.removeSelectedText()
                    cursor.deletePreviousChar()
            
            formatted_assistant_message = f'<p style="color: #50FA7B;"><b>Assistente:</b> {text_response}</p>'
            self.main_chat_history.append(formatted_assistant_message)
            self.sidebar_chat_history.append(formatted_assistant_message)

            if filters:
                filter_message = f'<p style="color: #D3D3D3; font-size: small;"><i>Filtros identificados: {filters}</i></p>'
                self.main_chat_history.append(filter_message)
                self.sidebar_chat_history.append(filter_message)
        else:
            # ... (Lógica de LLM não disponível)
             error_message = f'<p style="color: #FF6347;"><b>Assistente:</b> LLM não está disponível.</p>'
             self.main_chat_history.append(error_message)
             self.sidebar_chat_history.append(error_message)
        
        self.main_chat_history.ensureCursorVisible()
        self.sidebar_chat_history.ensureCursorVisible()

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