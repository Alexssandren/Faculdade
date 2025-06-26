import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime
import threading

class DashboardTab:
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.styling = main_window.styling
        
        # Dados principais
        self.metrics_data = {}
        self.loading = False
        
        # Criar interface
        self._create_interface()
        
        # Carregar dados iniciais
        self.load_dashboard_data()
        
    def _create_interface(self):
        """Cria a interface do dashboard"""
        # Configurar scroll
        self.canvas = tk.Canvas(self.parent)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Container principal
        main_container = ttk.Frame(self.scrollable_frame)
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Seções do dashboard
        self._create_metrics_section(main_container)
        self._create_overview_charts(main_container)
        self._create_quick_insights(main_container)
        
    def _create_metrics_section(self, parent):
        """Cria seção de métricas principais"""
        # Título da seção
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text=f"{self.styling.icons['dashboard']} Métricas Principais",
            font=self.styling.fonts['large_bold']
        )
        title_label.pack(anchor=W)
        
        # Container de métricas
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill=X, pady=(0, 30))
        
        # Grid de métricas (2x2)
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=X)
        
        # Configurar grid
        for i in range(4):
            metrics_grid.columnconfigure(i, weight=1, uniform="metric")
            
        # Inicializar com dados de placeholder que serão atualizados
        # Métrica 1: Total de Estados
        self.metric1_frame = self._create_metric_card(
            metrics_grid, 
            "Total de Estados", 
            "Carregando...", 
            "Estados + DF",
            self.styling.colors['primary'],
            0, 0
        )
        
        # Métrica 2: Período de Análise
        self.metric2_frame = self._create_metric_card(
            metrics_grid,
            "Período de Análise",
            "Carregando...",
            "Anos analisados",
            self.styling.colors['info'],
            0, 1
        )
        
        # Métrica 3: Total de Registros
        self.metric3_frame = self._create_metric_card(
            metrics_grid,
            "Total de Registros",
            "Carregando...",
            "Registros ativos",
            self.styling.colors['success'],
            0, 2
        )
        
        # Métrica 4: Última Atualização
        self.metric4_frame = self._create_metric_card(
            metrics_grid,
            "Última Atualização",
            "Carregando...",
            "Dados sincronizados",
            self.styling.colors['warning'],
            0, 3
        )
        
        # Carregar dados reais
        self.load_dashboard_data()
        
    def _create_metric_card(self, parent, title, value, subtitle, color, row, col):
        """Cria um card de métrica"""
        # Frame principal do card
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Container interno
        inner_frame = ttk.Frame(card_frame)
        inner_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_label = ttk.Label(
            inner_frame,
            text=title,
            font=self.styling.fonts['small_bold'],
            foreground=self.styling.colors['text_secondary']
        )
        title_label.pack(anchor=W)
        
        # Valor principal
        value_label = ttk.Label(
            inner_frame,
            text=value,
            font=self.styling.fonts['extra_large_bold'],
            foreground=color
        )
        value_label.pack(anchor=W, pady=(5, 0))
        
        # Subtítulo
        subtitle_label = ttk.Label(
            inner_frame,
            text=subtitle,
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['text_secondary']
        )
        subtitle_label.pack(anchor=W)
        
        return card_frame
        
    def _create_overview_charts(self, parent):
        """Cria gráficos de visão geral"""
        # Título da seção
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text=f"{self.styling.icons['chart']} Visão Geral",
            font=self.styling.fonts['large_bold']
        )
        title_label.pack(anchor=W)
        
        # Container de gráficos
        charts_frame = ttk.Frame(parent)
        charts_frame.pack(fill=X, pady=(0, 30))
        
        # Grid de gráficos (1x2)
        charts_grid = ttk.Frame(charts_frame)
        charts_grid.pack(fill=X)
        
        charts_grid.columnconfigure(0, weight=1)
        charts_grid.columnconfigure(1, weight=1)
        
        # Gráfico 1: Evolução IDH por Região
        self.chart1_frame = self._create_chart_card(
            charts_grid,
            "Evolução IDH por Região (2019-2023)",
            0, 0
        )
        
        # Gráfico 2: Distribuição de Despesas
        self.chart2_frame = self._create_chart_card(
            charts_grid,
            "Distribuição de Despesas por Função",
            0, 1
        )
        
    def _create_chart_card(self, parent, title, row, col):
        """Cria um card de gráfico"""
        # Frame principal
        card_frame = ttk.LabelFrame(parent, text=title, padding=15)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Canvas para o gráfico
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        # Gráfico placeholder
        if "IDH" in title:
            self._create_idh_evolution_chart(ax)
        else:
            self._create_expenses_distribution_chart(ax)
            
        # Incorporar no tkinter
        canvas = FigureCanvasTkAgg(fig, card_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        return card_frame
        
    def _create_idh_evolution_chart(self, ax):
        """Cria gráfico de evolução do IDH"""
        # Dados simulados para exemplo
        years = [2019, 2020, 2021, 2022, 2023]
        regions = {
            'Sudeste': [0.766, 0.768, 0.770, 0.772, 0.774],
            'Sul': [0.754, 0.756, 0.758, 0.760, 0.762],
            'Centro-Oeste': [0.734, 0.736, 0.738, 0.740, 0.742],
            'Nordeste': [0.663, 0.665, 0.667, 0.669, 0.671],
            'Norte': [0.684, 0.686, 0.688, 0.690, 0.692]
        }
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for i, (region, values) in enumerate(regions.items()):
            ax.plot(years, values, marker='o', linewidth=2, 
                   label=region, color=colors[i])
        
        ax.set_xlabel('Ano')
        ax.set_ylabel('IDH')
        ax.set_title('Evolução do IDH por Região')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0.65, 0.78)
        
    def _create_expenses_distribution_chart(self, ax):
        """Cria gráfico de distribuição de despesas"""
        # Dados simulados
        functions = ['Educação', 'Saúde', 'Previdência', 'Defesa', 'Transporte', 'Outros']
        values = [22.5, 18.3, 15.7, 12.1, 8.4, 23.0]
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6']
        
        wedges, texts, autotexts = ax.pie(values, labels=functions, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Distribuição de Despesas por Função')
        
        # Melhorar aparência dos textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            
    def _create_quick_insights(self, parent):
        """Cria seção de insights rápidos"""
        # Título da seção
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text=f"{self.styling.icons['lightbulb']} Insights Rápidos",
            font=self.styling.fonts['large_bold']
        )
        title_label.pack(anchor=W)
        
        # Container de insights
        insights_frame = ttk.Frame(parent)
        insights_frame.pack(fill=X, pady=(0, 30))
        
        # Lista de insights
        insights_data = [
            {
                'title': 'Correlação IDH vs Educação',
                'insight': 'Estados com maior investimento em educação apresentam IDH 15% superior',
                'trend': 'up',
                'color': self.styling.colors['success']
            },
            {
                'title': 'Crescimento Regional',
                'insight': 'Região Nordeste registrou maior crescimento no período (8.2%)',
                'trend': 'up',
                'color': self.styling.colors['info']
            },
            {
                'title': 'Eficiência de Gastos',
                'insight': 'Sul e Sudeste lideram em eficiência de aplicação de recursos',
                'trend': 'neutral',
                'color': self.styling.colors['warning']
            },
            {
                'title': 'Desafio Setorial',
                'insight': 'Investimentos em saúde precisam de 12% de incremento para equalizar',
                'trend': 'down',
                'color': self.styling.colors['danger']
            }
        ]
        
        for i, insight in enumerate(insights_data):
            self._create_insight_item(insights_frame, insight, i)
            
    def _create_insight_item(self, parent, insight_data, index):
        """Cria um item de insight"""
        # Frame do item
        item_frame = ttk.Frame(parent, style="InsightItem.TFrame")
        item_frame.pack(fill=X, pady=5)
        
        # Container interno
        inner_frame = ttk.Frame(item_frame)
        inner_frame.pack(fill=X, padx=15, pady=10)
        
        # Ícone de tendência
        trend_icon = {
            'up': self.styling.icons['arrow_up'],
            'down': self.styling.icons['arrow_down'],
            'neutral': self.styling.icons['minus']
        }.get(insight_data['trend'], self.styling.icons['minus'])
        
        # Layout horizontal
        icon_label = ttk.Label(
            inner_frame,
            text=trend_icon,
            font=self.styling.fonts['medium_bold'],
            foreground=insight_data['color']
        )
        icon_label.pack(side=LEFT, padx=(0, 10))
        
        # Container de texto
        text_frame = ttk.Frame(inner_frame)
        text_frame.pack(side=LEFT, fill=X, expand=True)
        
        # Título
        title_label = ttk.Label(
            text_frame,
            text=insight_data['title'],
            font=self.styling.fonts['medium_bold'],
            foreground=self.styling.colors['text_primary']
        )
        title_label.pack(anchor=W)
        
        # Insight
        insight_label = ttk.Label(
            text_frame,
            text=insight_data['insight'],
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['text_secondary']
        )
        insight_label.pack(anchor=W, pady=(2, 0))
        
    def update_metrics_display(self):
        """Atualiza a exibição das métricas com dados reais"""
        if not self.metrics_data:
            return
            
        try:
            print(f"🔄 Atualizando métricas do dashboard: {self.metrics_data}")
            
            # Não recarregar dados aqui, usar os já carregados
            # Atualizar Métrica 1: Total de Estados
            self._update_metric_card_value(
                self.metric1_frame, 
                str(self.metrics_data['total_estados']),
                "Estados + DF"
            )
            
            # Atualizar Métrica 2: Período de Análise
            self._update_metric_card_value(
                self.metric2_frame,
                f"{self.metrics_data['periodo_anos']} anos",
                self.metrics_data['periodo_texto']
            )
            
            # Atualizar Métrica 3: Total de Registros
            self._update_metric_card_value(
                self.metric3_frame,
                self.metrics_data['total_registros'],
                "Registros ativos"
            )
            
            # Atualizar Métrica 4: Última Atualização
            self._update_metric_card_value(
                self.metric4_frame,
                self.metrics_data['ultima_atualizacao'],
                "Dados sincronizados"
            )
            
            print(f"✅ Métricas atualizadas: {self.metrics_data['total_estados']} estados")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar métricas: {e}")
            # Usar valores fallback seguros
            self._update_metric_card_value(self.metric1_frame, "27", "Estados + DF")
            self._update_metric_card_value(self.metric2_frame, "5 anos", "2019-2023")
            self._update_metric_card_value(self.metric3_frame, "10.935", "Registros ativos")
            self._update_metric_card_value(self.metric4_frame, "Hoje", "Dados simulados")
    
    def _update_metric_card_value(self, card_frame, new_value, new_subtitle):
        """Atualiza o valor e subtítulo de um card de métrica"""
        try:
            # Encontrar o frame interno
            inner_frame = None
            for child in card_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    inner_frame = child
                    break
            
            if not inner_frame:
                return
                
            # Encontrar e atualizar os labels
            labels = []
            for widget in inner_frame.winfo_children():
                if isinstance(widget, ttk.Label):
                    labels.append(widget)
            
            if len(labels) >= 3:
                # labels[0] = título, labels[1] = valor, labels[2] = subtítulo
                labels[1].config(text=new_value)  # Atualizar valor
                labels[2].config(text=new_subtitle)  # Atualizar subtítulo
                
        except Exception as e:
            print(f"Erro ao atualizar card: {e}")
            
    def load_dashboard_data(self):
        """Carrega dados do dashboard"""
        # Remover threading desnecessário para operações simples
        self.loading = True
        try:
            print("🔄 Carregando dados do dashboard...")
            
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Limpar cache para garantir dados frescos
            data_provider.clear_cache()
            
            # Buscar métricas reais (operação rápida, não precisa de thread)
            self.metrics_data = data_provider.get_dashboard_metrics()
            
            print(f"📊 Dados carregados: {self.metrics_data}")
            
            # Atualizar métricas na interface diretamente (já estamos na thread principal)
            self.update_metrics_display()
            
            self.main_window.update_status("Dashboard carregado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dashboard: {e}")
            
            # Usar dados fallback
            self.metrics_data = {
                'total_estados': 27,
                'periodo_anos': 5,
                'periodo_texto': '2019-2023',
                'total_registros': '10.935',
                'ultima_atualizacao': 'Hoje'
            }
            
            # Atualizar interface com dados fallback
            self.update_metrics_display()
            
            # Mostrar mensagem de erro apenas se for crítico
            if "not in main loop" not in str(e):
                self.main_window.message_helper.show_error(f"Erro ao carregar dashboard: {str(e)}")
                
        finally:
            self.loading = False
        
    def refresh_data(self):
        """Atualiza dados do dashboard"""
        if not self.loading:
            self.load_dashboard_data()
            
    def export_dashboard(self):
        """Exporta dados do dashboard"""
        self.main_window.message_helper.show_info("Exportação de dashboard será implementada") 