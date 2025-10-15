"""
Módulo de visualizações - Interface gráfica para análise de dados
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import numpy as np
import logging

class VisualizationsTab:
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.styling = main_window.styling
        self.logger = logging.getLogger(__name__)
        
        # Estado da aba
        self.current_visualization = None
        self.loading = False
        
        # Criar interface
        self._create_interface()
        
    def _create_interface(self):
        """Cria a interface de visualizações"""
        # Container principal
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Painel de controle (esquerda)
        self._create_control_panel(main_container)
        
        # Área de visualização (direita)
        self._create_visualization_area(main_container)
        
    def _create_control_panel(self, parent):
        """Cria painel de controle das visualizações"""
        # Frame do painel
        control_frame = ttk.LabelFrame(parent, text="Controles de Visualização", padding=15)
        control_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        # Título
        title_label = ttk.Label(
            control_frame,
            text=f"{self.styling.icons['settings']} Configurações",
            font=self.styling.fonts['medium_bold']
        )
        title_label.pack(anchor=W, pady=(0, 15))
        
        # Seleção de visualização
        viz_label = ttk.Label(control_frame, text="Tipo de Visualização:")
        viz_label.pack(anchor=W, pady=(0, 5))
        
        self.viz_var = tk.StringVar(value="ranking_idh_investimento")
        viz_options = [
            ("Ranking IDH vs. Investimento", "ranking_idh_investimento"),
            ("Evolução Temporal", "evolucao_temporal"),
            ("Análise Regional", "analise_regional"),
            ("Tendências Temporais", "tendencias_temporais"),
            ("Eficiência por Estado", "eficiencia_estados"),
            ("Distribuição Setorial", "distribuicao_setorial"),
            ("Análise Comparativa", "analise_comparativa")
        ]
        
        for text, value in viz_options:
            rb = ttk.Radiobutton(
                control_frame,
                text=text,
                variable=self.viz_var,
                value=value,
                command=self.on_visualization_changed
            )
            rb.pack(anchor=W, pady=2)
            
        # Separador
        ttk.Separator(control_frame, orient=HORIZONTAL).pack(fill=X, pady=15)
        
        # Filtros
        filters_label = ttk.Label(
            control_frame,
            text=f"{self.styling.icons['filter']} Filtros",
            font=self.styling.fonts['medium_bold']
        )
        filters_label.pack(anchor=W, pady=(0, 10))
        
        # Filtro de ano
        year_label = ttk.Label(control_frame, text="Ano:")
        year_label.pack(anchor=W, pady=(0, 5))
        
        self.year_var = tk.StringVar(value="2023")
        year_combo = ttk.Combobox(
            control_frame,
            textvariable=self.year_var,
            values=["2019", "2020", "2021", "2022", "2023", "Todos"],
            state="readonly",
            width=15
        )
        year_combo.pack(anchor=W, pady=(0, 10))
        year_combo.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        # Região fixada como "Todas" (filtro removido)
        self.region_var = tk.StringVar(value="Todas")
        
    def _create_visualization_area(self, parent):
        """Cria área principal de visualização"""
        # Frame da área de visualização
        viz_frame = ttk.LabelFrame(parent, text="Visualização", padding=15)
        viz_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill=X, pady=(0, 10))
        
        # Título da visualização atual
        self.viz_title_var = tk.StringVar(value="Ranking IDH vs Investimento Público")
        title_label = ttk.Label(
            toolbar_frame,
            textvariable=self.viz_title_var,
            font=self.styling.fonts['large_bold']
        )
        title_label.pack(side=LEFT)
        
        # Indicador de carregamento
        self.loading_label = ttk.Label(
            toolbar_frame,
            text=f"{self.styling.icons['loading']} Carregando...",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['warning']
        )
        
        # Container para gráfico
        self.chart_container = ttk.Frame(viz_frame)
        self.chart_container.pack(fill=BOTH, expand=True)
        
        # Criar visualização inicial
        self.on_visualization_changed()
        
    def create_visualization(self):
        """Cria a visualização baseada na seleção atual"""
        # Limpar container anterior
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Obter tipo de visualização
        viz_type = self.viz_var.get()

        # A nova análise de ranking gerencia seu próprio canvas e layout.
        if viz_type == "ranking_idh_investimento":
            self._create_idh_ranking_analysis()
            self.viz_title_var.set("Ranking IDH vs. Investimento Público")
            return  # Retorna pois a renderização é feita dentro do método
        elif viz_type == "evolucao_temporal":
            self._create_temporal_evolution_analysis()
            self.viz_title_var.set("Evolução Temporal de Indicadores (Nacional)")
            return
        elif viz_type == "analise_regional":
            self._create_regional_analysis()
            self.viz_title_var.set("Análise Comparativa Regional")
            return

        # Para as outras visualizações, criar figura matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        # Criar visualização específica
        if viz_type == "correlacao_idh":
            self._create_correlation_chart(ax)
            self.viz_title_var.set("Correlação IDH vs Despesas Públicas")
        elif viz_type == "tendencias_temporais":
            self._create_temporal_trends(ax)
            self.viz_title_var.set("Tendências Temporais (2019-2023)")
        elif viz_type == "eficiencia_estados":
            self._create_state_efficiency(ax)
            self.viz_title_var.set("Eficiência por Estado")
        elif viz_type == "distribuicao_setorial":
            self._create_sectoral_distribution(ax)
            self.viz_title_var.set("Distribuição Setorial de Despesas")
        elif viz_type == "analise_comparativa":
            self._create_comparative_analysis(ax)
            self.viz_title_var.set("Análise Comparativa Estados")
            
        # Incorporar no tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # Adicionar toolbar de navegação
        try:
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(canvas, self.chart_container)
            toolbar.update()
        except Exception as e:
            # Evitar crash se o container for destruído durante refresh
            print(f"⚠️ Erro ao adicionar toolbar: {e}")
        
    def _create_idh_ranking_analysis(self):
        """Cria a análise de Ranking IDH vs. Investimento com tabela e gráfico."""
        self.logger.info("Iniciando a criação da análise 'Ranking IDH vs. Investimento'")
        # Limpar container
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Layout com PanedWindow para dividir tabela e gráfico
        paned_window = ttk.PanedWindow(self.chart_container, orient=VERTICAL)
        paned_window.pack(fill=BOTH, expand=True)

        # Frame para a tabela
        table_frame = ttk.LabelFrame(paned_window, text="Dados da Consulta", padding=10)
        paned_window.add(table_frame, weight=1)

        # Frame para o gráfico
        graph_frame = ttk.LabelFrame(paned_window, text="Visualização Gráfica", padding=10)
        paned_window.add(graph_frame, weight=2)

        # 1. Criar a Tabela (Treeview)
        columns = {
            "posicao_ranking": "Pos.",
            "estado": "Estado",
            "uf": "UF",
            "regiao": "Região",
            "idh_geral": "IDH Geral",
            "total_investimento_milhoes": "Invest. Total (M)",
            "investimento_saude": "Inv. Saúde (M)",
            "investimento_educacao": "Inv. Educação (M)"
        }

        tree = ttk.Treeview(table_frame, columns=list(columns.keys()), show="headings", height=10)
        
        for col_id, col_text in columns.items():
            tree.heading(col_id, text=col_text)
            tree.column(col_id, width=100, anchor=CENTER)

        tree.pack(fill=BOTH, expand=True)

        # 2. Carregar os dados da consulta
        data = []
        try:
            from src.queries.analytics_queries import ConsultasAnalíticas
            analytics = ConsultasAnalíticas()
            year = int(self.year_var.get()) if self.year_var.get() != "Todos" else 2023
            self.logger.info(f"Carregando dados para o ano: {year}")
            data = analytics.consulta_1_ranking_idh_investimento(ano=year)
            self.logger.info(f"Dados carregados. Número de registros: {len(data) if data else 0}")
            if data:
                self.logger.debug(f"Primeiro registro de dados: {data[0]}")

            for item in data:
                values = (
                    item.get('posicao_ranking', ''),
                    item.get('estado', ''),
                    item.get('uf', ''),
                    item.get('regiao', ''),
                    f"{item.get('idh_geral', 0):.3f}",
                    f"{item.get('total_investimento_milhoes', 0):.2f}",
                    f"{item.get('investimento_saude', 0):.2f}",
                    f"{item.get('investimento_educacao', 0):.2f}"
                )
                tree.insert("", "end", values=values)

        except Exception as e:
            self.logger.error(f"Erro ao carregar dados da consulta: {e}", exc_info=True)
            tree.insert("", "end", values=("Erro ao carregar dados.", str(e), "", "", "", "", "", ""))

        # 3. Criar área para o gráfico
        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        if data:
            # Extrair dados para o gráfico
            estados = [item['uf'] for item in data]
            investimentos = [item['total_investimento_milhoes'] for item in data]
            idhs = [item['idh_geral'] for item in data]

            # Eixo primário (Barras - Investimento)
            ax1.set_xlabel("Estados", color=self.styling.colors['text_primary'])
            ax1.set_ylabel("Investimento Total (Milhões R$)", color=self.styling.colors['primary'], fontsize=12)
            bars = ax1.bar(estados, investimentos, color=self.styling.colors['secondary'], alpha=0.7, label="Investimento Total")
            ax1.tick_params(axis='y', labelcolor=self.styling.colors['primary'])
            ax1.tick_params(axis='x', rotation=45, labelsize=8)
            ax1.grid(False)

            # Eixo secundário (Linha - IDH)
            ax2 = ax1.twinx()
            ax2.set_ylabel("IDH Geral", color=self.styling.colors['info'], fontsize=12)
            line = ax2.plot(estados, idhs, color=self.styling.colors['info'], marker='o', linestyle='-', linewidth=2, label="IDH Geral")
            ax2.tick_params(axis='y', labelcolor=self.styling.colors['info'])
            ax2.grid(False)
            
            # Ajustes gerais
            fig.suptitle("IDH vs. Investimento Total por Estado", 
                         color=self.styling.colors['text_primary'], 
                         fontsize=16, 
                         fontweight='bold')
            fig.tight_layout(rect=[0, 0, 1, 0.96])
        else:
            # Fallback se não houver dados
            ax1.text(0.5, 0.5, "Não foi possível carregar os dados para o gráfico.", 
                    ha='center', va='center', fontsize=12, color='gray')
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        self.logger.info("Canvas do gráfico desenhado.")
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.logger.info("Widget do canvas empacotado na interface.")
        
    def _create_correlation_chart(self, ax):
        """Cria gráfico de correlação IDH vs Despesas"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter dados reais com filtros aplicados
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023  # Usar 2023 como padrão quando "Todos" selecionado
            else:
                year = int(year_str)
            region = self.region_var.get()
            
            data = data_provider.get_correlation_data(year=year, region=region)
            
            # Converter para numpy arrays e filtrar valores inválidos
            investimento_arr = np.array(data['investimento'], dtype=float)
            idh_arr = np.array(data['idh'], dtype=float)

            valid_mask = np.isfinite(investimento_arr) & np.isfinite(idh_arr)

            if valid_mask.sum() == 0:
                self._create_correlation_chart_fallback(ax)
                return

            # Plotar dados válidos
            ax.scatter(investimento_arr[valid_mask], idh_arr[valid_mask], alpha=0.6)
            ax.set_xlabel('Investimento per capita (R$)')
            ax.set_ylabel('IDH')
            ax.set_title(f'Correlação IDH vs Investimento Público ({year})')
            ax.tick_params(axis='y', colors=self.styling.colors['text_secondary'])
            ax.grid(True, linestyle='--', alpha=0.1)
            
            if valid_mask.sum() >= 2 and np.unique(investimento_arr[valid_mask]).size > 1:
                try:
                    z = np.polyfit(investimento_arr[valid_mask], idh_arr[valid_mask], 1)
                    p = np.poly1d(z)
                    ax.plot(investimento_arr[valid_mask], p(investimento_arr[valid_mask]), "r--", alpha=0.8)
                except Exception as poly_err:
                    # Se regressão falhar, continuar sem linha de tendência
                    print(f"⚠️ Falha na regressão linear: {poly_err}")
            
            estados = data.get('estados', [])
            for i, estado in enumerate(estados):
                if i < len(investimento_arr) and i < len(idh_arr) and valid_mask[i]:
                    ax.annotate(estado, (investimento_arr[i], idh_arr[i]), fontsize=8)
                
        except Exception as e:
            print(f"Erro ao criar gráfico de correlação: {e}")
            self._create_correlation_chart_fallback(ax)
            
    def _create_correlation_chart_fallback(self, ax):
        """Exibe placeholder quando não há dados reais"""
        ax.text(0.5, 0.5, 'Sem dados disponíveis',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12,
                color=self.styling.colors['text_secondary'])
        ax.set_axis_off()
        
    def _create_regional_analysis(self):
        """Cria a análise comparativa regional com tabela e gráfico."""
        # Limpar container
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        paned_window = ttk.PanedWindow(self.chart_container, orient=VERTICAL)
        paned_window.pack(fill=BOTH, expand=True)

        table_frame = ttk.LabelFrame(paned_window, text="Dados Comparativos por Região", padding=10)
        paned_window.add(table_frame, weight=1)

        graph_frame = ttk.LabelFrame(paned_window, text="Gráfico Comparativo", padding=10)
        paned_window.add(graph_frame, weight=2)

        # 1. Tabela
        columns = {
            "posicao": "Pos.", "regiao": "Região", "total_estados": "Nº Estados",
            "idh_regional_medio": "IDH Médio", "investimento_total_milhoes": "Invest. Total (Bi)",
            "nivel_desenvolvimento": "Nível"
        }
        tree = ttk.Treeview(table_frame, columns=list(columns.keys()), show="headings", height=5)
        for col_id, col_text in columns.items():
            tree.heading(col_id, text=col_text)
            tree.column(col_id, width=120, anchor=CENTER)
        tree.pack(fill=BOTH, expand=True)

        # 2. Carregar Dados
        data = {}
        try:
            from src.queries.analytics_queries import ConsultasAnalíticas
            analytics = ConsultasAnalíticas()
            data = analytics.consulta_3_analise_regional()
            
            for item in data.get('ranking_regioes', []):
                investimento_bilhoes = item.get('investimento_total_milhoes', 0) / 1000
                values = (
                    item.get('posicao'), item.get('regiao'), item.get('total_estados'),
                    f"{item.get('idh_regional_medio', 0):.3f}", f"{investimento_bilhoes:.2f}",
                    item.get('nivel_desenvolvimento')
                )
                tree.insert("", "end", values=values)
        except Exception as e:
            tree.insert("", "end", values=("Erro", str(e), "", "", "", ""))

        # 3. Gráfico
        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        ranking = data.get('ranking_regioes', [])
        if ranking:
            regioes = [item['regiao'] for item in ranking]
            idhs = [item['idh_regional_medio'] for item in ranking]
            investimentos = [item['investimento_total_milhoes'] / 1000 for item in ranking]

            x = np.arange(len(regioes))
            width = 0.35

            rects1 = ax1.bar(x - width/2, idhs, width, label='IDH Médio', color=self.styling.colors['info'])
            ax1.set_ylabel('IDH Médio', color=self.styling.colors['info'])
            ax1.tick_params(axis='y', labelcolor=self.styling.colors['info'])
            
            ax2 = ax1.twinx()
            rects2 = ax2.bar(x + width/2, investimentos, width, label='Investimento (Bi)', color=self.styling.colors['success'])
            ax2.set_ylabel('Investimento Total (Bilhões R$)', color=self.styling.colors['success'])
            ax2.tick_params(axis='y', labelcolor=self.styling.colors['success'])

            ax1.set_xticks(x)
            ax1.set_xticklabels(regioes)
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            fig.suptitle("Análise Regional: IDH vs. Investimento", fontsize=16, fontweight='bold', color=self.styling.colors['text_primary'])
            fig.tight_layout(rect=[0, 0, 1, 0.96])
        else:
            ax1.text(0.5, 0.5, "Dados não disponíveis para gerar o gráfico.", ha='center', va='center')

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        
    def _create_temporal_evolution_analysis(self):
        """Cria a análise de Evolução Temporal com tabela e gráfico."""
        # Limpar container
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        paned_window = ttk.PanedWindow(self.chart_container, orient=VERTICAL)
        paned_window.pack(fill=BOTH, expand=True)

        table_frame = ttk.LabelFrame(paned_window, text="Dados Anuais Consolidados", padding=10)
        paned_window.add(table_frame, weight=1)

        graph_frame = ttk.LabelFrame(paned_window, text="Gráfico de Evolução", padding=10)
        paned_window.add(graph_frame, weight=2)

        # 1. Tabela
        columns = {
            "ano": "Ano", "idh_geral": "IDH Médio", "investimento_total": "Invest. Total (M)",
            "variacao_idh_percent": "Var. IDH (%)", "variacao_investimento_percent": "Var. Invest. (%)"
        }
        tree = ttk.Treeview(table_frame, columns=list(columns.keys()), show="headings", height=5)
        for col_id, col_text in columns.items():
            tree.heading(col_id, text=col_text)
            tree.column(col_id, width=120, anchor=CENTER)
        tree.pack(fill=BOTH, expand=True)

        # 2. Carregar Dados
        data = {}
        try:
            from src.queries.analytics_queries import ConsultasAnalíticas
            analytics = ConsultasAnalíticas()
            # Esta consulta pode filtrar por estado, mas aqui faremos a nacional
            data = analytics.consulta_2_evolucao_temporal()
            
            for item in data.get('evolucao_anual', []):
                values = (
                    item.get('ano'), f"{item.get('idh_geral', 0):.3f}",
                    f"{item.get('investimento_total', 0):.2f}", f"{item.get('variacao_idh_percent', 0):.2f}%",
                    f"{item.get('variacao_investimento_percent', 0):.2f}%"
                )
                tree.insert("", "end", values=values)
        except Exception as e:
            tree.insert("", "end", values=("Erro", str(e), "", "", ""))

        # 3. Gráfico
        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        evolucao = data.get('evolucao_anual', [])
        if evolucao:
            anos = [item['ano'] for item in evolucao]
            idhs = [item['idh_geral'] for item in evolucao]
            investimentos = [item['investimento_total'] for item in evolucao]

            ax1.set_xlabel("Ano", color=self.styling.colors['text_primary'])
            ax1.set_ylabel("Investimento Total (Milhões R$)", color=self.styling.colors['primary'], fontsize=12)
            ax1.bar(anos, investimentos, color=self.styling.colors['secondary'], alpha=0.6, label="Invest. Total")
            ax1.tick_params(axis='y', labelcolor=self.styling.colors['primary'])
            ax1.grid(False)

            ax2 = ax1.twinx()
            ax2.set_ylabel("IDH Geral Médio", color=self.styling.colors['info'], fontsize=12)
            ax2.plot(anos, idhs, color=self.styling.colors['info'], marker='o', linestyle='-', label="IDH Médio")
            ax2.tick_params(axis='y', labelcolor=self.styling.colors['info'])
            ax2.grid(False)
            
            fig.suptitle("Evolução Anual: IDH vs. Investimento", fontsize=16, fontweight='bold', color=self.styling.colors['text_primary'])
            fig.tight_layout(rect=[0, 0, 1, 0.96])
        else:
            ax1.text(0.5, 0.5, "Dados não disponíveis para gerar o gráfico.", ha='center', va='center')

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        
    def _create_temporal_trends(self, ax):
        """Cria gráfico de tendências temporais"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter dados
            data = data_provider.get_temporal_data()
            
            # Verificar dados
            if not data or not data.get('anos'):
                raise ValueError("Dados temporais inválidos")
                
            # Plotar tendências
            ax.plot(data['anos'], data['idh_medio'], 'b-', label='IDH Médio')
            ax.set_xlabel('Ano')
            ax.set_ylabel('IDH Médio', color='b')
            
            # Criar segundo eixo Y para investimento
            ax2 = ax.twinx()
            ax2.plot(data['anos'], data['investimento_medio'], 'r-', label='Investimento Médio')
            ax2.set_ylabel('Investimento Médio (R$)', color='r')
            
            # Configurar gráfico
            ax.set_title('Evolução Temporal: IDH vs Investimento')
            ax.grid(True, alpha=0.3)
            
            # Adicionar legendas
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
        except Exception as e:
            print(f"Erro ao criar tendências temporais: {e}")
            self._create_temporal_trends_fallback(ax)
            
    def _create_temporal_trends_fallback(self, ax):
        """Exibe placeholder quando não há dados reais"""
        ax.text(0.5, 0.5, 'Sem dados disponíveis',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12,
                color=self.styling.colors['text_secondary'])
        ax.set_axis_off()
        
    def _create_state_efficiency(self, ax):
        """Cria gráfico de eficiência por estado"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter dados
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023
            else:
                year = int(year_str)
                
            data = data_provider.get_efficiency_data(year=year)
            
            # Verificar dados
            if not data or not data.get('estados'):
                raise ValueError("Dados de eficiência inválidos")
                
            # Calcular eficiência (IDH / Investimento normalizado)
            eficiencia = data['idh'] / (data['investimento'] / np.mean(data['investimento']))
            
            # Ordenar por eficiência
            idx = np.argsort(eficiencia)[::-1]
            estados = np.array(data['estados'])[idx]
            eficiencia = eficiencia[idx]
            
            # Plotar top 10 estados mais eficientes
            ax.bar(estados[:10], eficiencia[:10])
            ax.set_title(f'Top 10 Estados - Eficiência IDH/Investimento ({year})')
            ax.set_xlabel('Estado')
            ax.set_ylabel('Índice de Eficiência')
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de eficiência: {e}")
            self._create_state_efficiency_fallback(ax)
            
    def _create_state_efficiency_fallback(self, ax):
        """Exibe placeholder quando não há dados reais"""
        ax.text(0.5, 0.5, 'Sem dados disponíveis',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12,
                color=self.styling.colors['text_secondary'])
        ax.set_axis_off()
        
    def _create_sectoral_distribution(self, ax):
        """Cria gráfico de distribuição setorial"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter dados
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023
            else:
                year = int(year_str)
                
            data = data_provider.get_sectoral_data(year=year)
            
            # Verificar dados
            if not data or 'setores' not in data:
                raise ValueError("Dados setoriais inválidos")
                
            # Criar gráfico de pizza
            wedges, texts, autotexts = ax.pie(
                data['valores'],
                labels=data['setores'],
                autopct='%1.1f%%',
                startangle=90
            )
            
            # Configurar gráfico
            ax.set_title(f'Distribuição Setorial das Despesas ({year})')
            ax.axis('equal')
            
            # Ajustar legendas
            plt.setp(autotexts, size=8, weight="bold")
            plt.setp(texts, size=8)
            
        except Exception as e:
            print(f"Erro ao criar distribuição setorial: {e}")
            self._create_sectoral_distribution_fallback(ax)
            
    def _create_sectoral_distribution_fallback(self, ax):
        """Cria gráfico de distribuição setorial com dados simulados"""
        # Dados simulados
        setores = ['Educação', 'Saúde', 'Infraestrutura', 'Segurança',
                  'Assistência Social', 'Outros']
        valores = [25, 30, 20, 15, 5, 5]
        
        # Criar gráfico de pizza
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=setores,
            autopct='%1.1f%%',
            startangle=90
        )
        
        # Configurar gráfico
        ax.set_title('Distribuição Setorial das Despesas (Simulado)')
        ax.axis('equal')
        
        # Ajustar legendas
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)
        
        # Adicionar nota sobre dados simulados
        ax.text(-1.5, 1.2, 'ATENÇÃO: Dados Simulados',
                fontsize=10, color='red')
                
    def _create_comparative_analysis(self, ax):
        """Cria gráfico de análise comparativa"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter dados
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023
            else:
                year = int(year_str)
                
            data = data_provider.get_comparative_data(year=year)
            
            # Verificar dados
            if not data or 'estados' not in data:
                raise ValueError("Dados comparativos inválidos")
                
            # Criar gráfico de barras agrupadas
            x = np.arange(len(data['estados']))
            width = 0.35
            
            ax.bar(x - width/2, data['idh'], width, label='IDH')
            ax.bar(x + width/2, data['investimento_norm'], width,
                   label='Investimento (Normalizado)')
                   
            # Configurar gráfico
            ax.set_title(f'Análise Comparativa: IDH vs Investimento ({year})')
            ax.set_xticks(x)
            ax.set_xticklabels(data['estados'], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"Erro ao criar análise comparativa: {e}")
            self._create_comparative_analysis_fallback(ax)
            
    def _create_comparative_analysis_fallback(self, ax):
        """Cria gráfico de análise comparativa com dados simulados"""
        # Dados simulados
        estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE', 'CE', 'GO']
        idh = np.random.normal(0.8, 0.1, len(estados))
        investimento = np.random.normal(0.7, 0.2, len(estados))
        
        # Criar gráfico de barras agrupadas
        x = np.arange(len(estados))
        width = 0.35
        
        ax.bar(x - width/2, idh, width, label='IDH')
        ax.bar(x + width/2, investimento, width, label='Investimento (Normalizado)')
        
        # Configurar gráfico
        ax.set_title('Análise Comparativa: IDH vs Investimento (Simulado)')
        ax.set_xticks(x)
        ax.set_xticklabels(estados, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar nota sobre dados simulados
        ax.text(0.02, 0.98, 'ATENÇÃO: Dados Simulados',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top', color='red')
                
    def on_visualization_changed(self):
        """Callback para mudança de tipo de visualização"""
        self.refresh_visualization()
        
    def on_filter_changed(self, event=None):
        """Callback para mudança de filtros"""
        self.refresh_visualization()
        
    def refresh_visualization(self):
        """Atualiza a visualização atual com novos filtros (executado na thread principal)"""
        self.show_loading()

        def _refresh_in_ui_thread():
            try:
                self.create_visualization()
            except Exception as e:
                self.logger.error(f"Erro ao atualizar visualização: {e}", exc_info=True)
            finally:
                self.hide_loading()

        # Agendar para a thread principal do Tkinter
        self.chart_container.after(100, _refresh_in_ui_thread)
        
    def show_loading(self):
        """Mostra indicador de carregamento"""
        self.loading = True
        self.loading_label.pack(side=RIGHT, padx=10)
        
    def hide_loading(self):
        """Esconde indicador de carregamento"""
        self.loading = False
        self.loading_label.pack_forget()
