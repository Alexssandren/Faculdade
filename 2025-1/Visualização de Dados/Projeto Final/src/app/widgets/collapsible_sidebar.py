from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, QEvent, Qt, Signal
from PySide6.QtGui import QPalette, QColor

class CollapsibleSidebar(QWidget):
    widthChanged = Signal(int) # Sinal para notificar mudança de largura

    def __init__(
        self,
        parent=None,
        collapsed_width: int = 20,
        expanded_width: int = 250,
        animation_duration: int = 300,
        direction: Qt.Edge = Qt.LeftEdge
    ):
        super().__init__(parent)
        
        self.collapsed_width = collapsed_width
        self.expanded_width = expanded_width
        self.animation_duration = animation_duration
        self.direction = direction
        self.hover_enabled = True # Flag para controlar o comportamento de hover

        self.setAutoFillBackground(True) # Garante que o widget desenhe seu fundo.
        self.setFixedWidth(self.collapsed_width)
        self.setObjectName("CollapsibleSidebar")

        # Define a cor de fundo via paleta (mais robusto) e a borda via stylesheet.
        background_color_str = "#3a3a3a"  # Cinza escuro
        border_color_str = "#555555"      # Cinza mais claro

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(background_color_str))
        self.setPalette(pal)

        if self.direction == Qt.Edge.RightEdge:
            border_style = f"border-left: 1px solid {border_color_str};"
        else:
            border_style = f"border-right: 1px solid {border_color_str};"

        # Stylesheet agora foca apenas na borda.
        self.setStyleSheet(f"""
            QWidget#CollapsibleSidebar {{
                {border_style}
            }}
        """)

        # Layout para o conteúdo da sidebar. O conteúdo será adicionado diretamente a ele.
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(5, 10, 5, 10)
        self.content_layout.setSpacing(10)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Animação para expandir/recolher
        self.animation = QPropertyAnimation(self, b"current_width", self)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(self.animation_duration)

    def get_inner_layout(self):
        # Retorna o layout principal para que outros widgets possam adicionar conteúdo.
        return self.content_layout

    def setHoverEnabled(self, enabled: bool):
        """Ativa ou desativa o comportamento de expandir/recolher com o mouse."""
        self.hover_enabled = enabled

    def enterEvent(self, event: QEvent):
        """Expande a barra lateral ao passar o mouse, se ativado."""
        if self.hover_enabled:
            self.expand()
        event.accept()

    def leaveEvent(self, event: QEvent):
        """Recolhe a barra lateral ao remover o mouse, se ativado."""
        if self.hover_enabled:
            self.collapse()
        event.accept()

    def expand(self):
        if self.width() != self.expanded_width:
            self.raise_() # Eleva o widget para o topo da pilha de widgets
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()

    def collapse(self):
        if self.width() != self.collapsed_width:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()

    def set_current_width(self, width):
        self.setFixedWidth(width)
        self.widthChanged.emit(width) # Emite o sinal com a nova largura

    def get_current_width(self):
        return self.width()

    current_width = Property(int, get_current_width, set_current_width) 