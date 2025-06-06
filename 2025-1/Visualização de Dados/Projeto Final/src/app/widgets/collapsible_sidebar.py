from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, QEvent, Qt

class CollapsibleSidebar(QWidget):
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

        self.setFixedWidth(self.collapsed_width)
        self.setObjectName("CollapsibleSidebar")

        # Define o estilo da borda com base na direção da sidebar
        border_color = "#555555" # Um cinza um pouco mais claro
        if self.direction == Qt.Edge.RightEdge:
            border_style = f"border-left: 1px solid {border_color};"
        else:
            border_style = f"border-right: 1px solid {border_color};"

        self.setStyleSheet(f"""
            QWidget#CollapsibleSidebar {{
                background-color: #2c313a;
                {border_style}
            }}
        """)

        # Layout para o conteúdo da sidebar
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(5, 10, 5, 10)
        self.content_layout.setSpacing(10)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Widget interno para o conteúdo, que será mostrado/escondido
        self.content_widget = QWidget()
        self.content_layout.addWidget(self.content_widget)
        self.inner_layout = QVBoxLayout(self.content_widget)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        
        # Animação para expandir/recolher
        self.animation = QPropertyAnimation(self, b"current_width", self)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(self.animation_duration)

        self.content_widget.hide() # Conteúdo começa escondido

    def get_inner_layout(self):
        return self.inner_layout

    def enterEvent(self, event: QEvent):
        self.expand()
        event.accept()

    def leaveEvent(self, event: QEvent):
        self.collapse()
        event.accept()

    def expand(self):
        if self.width() != self.expanded_width:
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.expanded_width)
            self.animation.finished.connect(self.content_widget.show)
            self.animation.start()

    def collapse(self):
        if self.width() != self.collapsed_width:
            self.content_widget.hide()
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(self.collapsed_width)
            self.animation.finished.disconnect()
            self.animation.start()

    def set_current_width(self, width):
        self.setFixedWidth(width)

    def get_current_width(self):
        return self.width()

    current_width = Property(int, get_current_width, set_current_width) 