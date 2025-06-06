import sys
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

class GraphCarouselWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GraphCarousel")
        
        self.graph_files = []
        self.current_index = -1

        # Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 1. Painel de Navegação Superior
        nav_panel = QWidget()
        nav_layout = QHBoxLayout(nav_panel)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_button = QPushButton("< Anterior")
        self.graph_title_label = QLabel("Selecione um ano para ver os gráficos")
        self.graph_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_button = QPushButton("Próximo >")

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.graph_title_label, 1)
        nav_layout.addWidget(self.next_button)
        main_layout.addWidget(nav_panel)

        # 2. Área de Exibição do Gráfico (StackedWidget)
        self.view_stack = QStackedWidget()
        main_layout.addWidget(self.view_stack, 1)

        # Conectar sinais
        self.prev_button.clicked.connect(self.show_previous_graph)
        self.next_button.clicked.connect(self.show_next_graph)
        
        self.update_nav_buttons()

    def set_graphs(self, graph_files: list[Path]):
        self.graph_files = graph_files
        
        # Limpar views antigos
        while self.view_stack.count() > 0:
            widget = self.view_stack.widget(0)
            self.view_stack.removeWidget(widget)
            widget.deleteLater()

        if not self.graph_files:
            # TODO: Adicionar um widget de placeholder/aviso
            self.current_index = -1
        else:
            for graph_path in self.graph_files:
                view = QWebEngineView()
                view.setUrl(QUrl.fromLocalFile(str(graph_path.resolve())))
                self.view_stack.addWidget(view)
            self.current_index = 0
            self.view_stack.setCurrentIndex(self.current_index)
        
        self.update_title()
        self.update_nav_buttons()

    def show_previous_graph(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.view_stack.setCurrentIndex(self.current_index)
            self.update_title()
            self.update_nav_buttons()

    def show_next_graph(self):
        if self.current_index < len(self.graph_files) - 1:
            self.current_index += 1
            self.view_stack.setCurrentIndex(self.current_index)
            self.update_title()
            self.update_nav_buttons()
            
    def update_title(self):
        if self.current_index != -1 and self.graph_files:
            # Formata o nome do arquivo para ser mais legível
            file_name = self.graph_files[self.current_index].stem
            title = file_name.replace("fase3_", "").replace("_", " ").title()
            self.graph_title_label.setText(f"{title} ({self.current_index + 1}/{len(self.graph_files)})")
        else:
            self.graph_title_label.setText("Nenhum gráfico para exibir")

    def update_nav_buttons(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.graph_files) - 1) 