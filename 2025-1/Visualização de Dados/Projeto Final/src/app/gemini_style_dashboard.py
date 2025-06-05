import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPalette, QColor, QPainter, QPixmap
from pathlib import Path # Adicionado para manipulação de caminhos

# Adicionar o diretório 'src' ao sys.path para import do LLMHandler
# Isso assume que gemini_style_dashboard.py está em src/app/
# e llm_handler.py está em src/llm/
SCRIPT_DIR_LLM = Path(__file__).resolve().parent # src/app
SRC_DIR_LLM = SCRIPT_DIR_LLM.parent # src/
if str(SRC_DIR_LLM) not in sys.path:
    sys.path.insert(0, str(SRC_DIR_LLM))

try:
    from llm.llm_handler import LLMQueryHandler
except ImportError as e:
    print(f"Erro ao importar LLMQueryHandler: {e}. Verifique o sys.path e a estrutura do projeto.")
    LLMQueryHandler = None # Define como None para que o app possa rodar com um aviso

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
        self.setGeometry(100, 100, 1200, 800) # x, y, largura, altura

        self._apply_dark_theme()

        # Carregar a imagem de fundo uma vez
        self.background_pixmap = QPixmap()
        image_name = "Mapa Brasil.png"
        script_dir = Path(__file__).parent
        image_path = script_dir / "assets" / image_name
        if image_path.exists():
            if not self.background_pixmap.load(str(image_path.resolve())):
                print(f"Erro ao carregar a imagem de fundo: {image_path}")
        else:
            print(f"Arquivo de imagem de fundo não encontrado: {image_path}")

        # Inicializar LLM Handler
        self.llm_handler = None
        if LLMQueryHandler:
            try:
                self.llm_handler = LLMQueryHandler()
                print("LLMQueryHandler inicializado com sucesso.")
            except Exception as e_llm_init:
                print(f"Erro ao inicializar LLMQueryHandler: {e_llm_init}")
                # self.llm_handler permanece None
        else:
            print("LLMQueryHandler não pôde ser importado. Funcionalidade de chat com IA desabilitada.")

        # Widget central e layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Placeholders para os elementos do design ---

        # 1. Título Superior "Brasil em Dados" com cores
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
                color_index += 1 # Incrementa o índice de cor apenas para caracteres não espaciais
        
        self.title_label = QLabel(styled_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        self.main_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)

        # 2. Área de Chat Central agora usa BackgroundImageWidget
        self.chat_container_widget = BackgroundImageWidget(self.background_pixmap)
        self.chat_container_widget.setObjectName("ChatContainerWidget")
        # QSS para cor de fundo base (visível se a imagem não carregar ou tiver transparência) e bordas
        self.chat_container_widget.setStyleSheet("""
            QWidget#ChatContainerWidget {
                background-color: #2a2a2a; 
                border-radius: 8px;
            }
        """)
        # O layout agora é do BackgroundImageWidget
        chat_container_layout = QVBoxLayout(self.chat_container_widget)
        # As margens agora são definidas no construtor do BackgroundImageWidget

        self.chat_history_display = QTextEdit()
        self.chat_history_display.setReadOnly(True)
        self.chat_history_display.setObjectName("ChatHistoryDisplay")
        # Tornar o fundo do QTextEdit transparente para ver a imagem do container por baixo
        self.chat_history_display.setStyleSheet("QTextEdit#ChatHistoryDisplay { background-color: rgba(43, 43, 43, 0.8); color: #dcdcdc; border: 1px solid #3c3c3c; border-radius: 4px; }") # Levemente translúcido
        chat_container_layout.addWidget(self.chat_history_display, 1) # Histórico ocupa a maior parte

        self.chat_input_line = QLineEdit()
        self.chat_input_line.setPlaceholderText("Digite sua mensagem e pressione Enter...")
        self.chat_input_line.setObjectName("ChatInputLine")
        self.chat_input_line.setStyleSheet("QLineEdit#ChatInputLine { background-color: #222222; color: #dcdcdc; border: 1px solid #3c3c3c; border-radius: 8px; padding: 10px; font-size: 14px; }")
        self.chat_input_line.setFixedHeight(50) # Altura um pouco maior para a caixa de entrada
        chat_container_layout.addWidget(self.chat_input_line) # Entrada na parte inferior do container do chat

        self.main_layout.addWidget(self.chat_container_widget, 1) # O container do chat agora é o item expansível central

        # REMOVER a antiga configuração da barra inferior do chat
        # bottom_bar_layout = QHBoxLayout()
        # ... (código da barra inferior removido)
        # self.main_layout.addLayout(bottom_bar_layout)
        
        self.central_widget.setLayout(self.main_layout)

        # Conectar sinais (apenas para chat_input_line.returnPressed)
        # self.send_button.clicked.connect(self._send_message) # Botão removido
        self.chat_input_line.returnPressed.connect(self._send_message)

    def _send_message(self):
        user_text = self.chat_input_line.text().strip()
        if not user_text:
            return

        self.chat_history_display.append(f"<p style=\"color: #8BE9FD;\"><b>Você:</b> {user_text}</p>")
        self.chat_input_line.clear()
        self.chat_history_display.ensureCursorVisible()

        # Feedback visual e chamada ao LLM
        if self.llm_handler:
            # Adiciona mensagem de "digitando" e força atualização da UI
            self.chat_history_display.append(f"<p style=\"color: #A9A9A9;\"><i>Assistente está digitando...</i></p>")
            QApplication.processEvents() # Processa eventos pendentes para mostrar a mensagem

            text_response, filters = self.llm_handler.get_response(user_text)
            
            # Remove a mensagem de "digitando"
            # Esta é uma forma simples, pode ser melhorada para IDs de mensagem se o QTextEdit suportar
            current_html = self.chat_history_display.toHtml()
            # Encontra a última ocorrência da mensagem de digitando e a remove
            # Cuidado com tags HTML parciais se a mensagem for muito complexa
            last_occurrence = current_html.rfind(f"<p style=\"color: #A9A9A9;\"><i>Assistente está digitando...</i></p>")
            if last_occurrence != -1:
                 # Precisamos ter cuidado ao manipular HTML diretamente
                 # Vamos procurar a tag <p> de fechamento correspondente se houver
                 # Simplificando por agora: remove a linha inteira baseada no texto exato.
                 # Uma abordagem mais segura seria usar QTextCursor para selecionar e remover a última linha/bloco.
                cursor = self.chat_history_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                if "Assistente está digitando..." in cursor.selectedText():
                    cursor.removeSelectedText()
                    # Pode ser necessário remover um newline extra que fica
                    cursor.deletePreviousChar() 
                else: # Fallback menos preciso se a seleção de bloco falhar em pegar a msg
                    self.chat_history_display.setHtml(current_html[:last_occurrence])
            
            self.chat_history_display.append(f"<p style=\"color: #50FA7B;\"><b>Assistente:</b> {text_response}</p>")
            if filters:
                self.chat_history_display.append(f"<p style=\"color: #D3D3D3; font-size: small;\"><i>Filtros identificados: {filters}</i></p>")
        else:
            self.chat_history_display.append(f"<p style=\"color: #FF6347;\"><b>Assistente:</b> LLM não está disponível.</p>")
        
        self.chat_history_display.ensureCursorVisible()

    def _apply_dark_theme(self):
        app = QApplication.instance()
        if app is None:
            print("QApplication instance not found for applying theme.")
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
    # Este bloco é para teste direto do dashboard, se necessário.
    app = QApplication.instance() # Tenta obter a instância existente
    if not app: # Cria uma nova se não existir (para execução direta)
        app = QApplication(sys.argv)
    
    # Aplica o tema escuro ANTES de criar a janela, se for execução direta
    # É melhor que a QApplication em main.py cuide disso se importado.
    # A lógica em _apply_dark_theme já pega o app instance.

    window = GeminiStyleDashboard()
    window.show()
    # sys.exit(app.exec()) # Removido sys.exit para permitir que main.py gerencie o loop do app
    app.exec() # Apenas executa se estiver no __main__ 