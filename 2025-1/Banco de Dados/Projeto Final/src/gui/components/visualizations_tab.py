import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

class VisualizationsTab:
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.styling = main_window.styling
        
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
        
        self.viz_var = tk.StringVar(value="correlacao_idh")
        viz_options = [
            ("Correlação IDH vs Despesas", "correlacao_idh"),
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
        
        # Seção de Ações removida conforme solicitado
        
    def _create_visualization_area(self, parent):
        """Cria área principal de visualização"""
        # Frame da área de visualização
        viz_frame = ttk.LabelFrame(parent, text="Visualização", padding=15)
        viz_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill=X, pady=(0, 10))
        
        # Título da visualização atual
        self.viz_title_var = tk.StringVar(value="Correlação IDH vs Despesas Públicas")
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
        # Não fazer pack inicialmente (só quando carregando)
        
        # Container para gráfico
        self.chart_container = ttk.Frame(viz_frame)
        self.chart_container.pack(fill=BOTH, expand=True)
        
        # Criar visualização inicial
        self.create_visualization()
        
    def create_visualization(self):
        """Cria a visualização baseada na seleção atual"""
        # Limpar container anterior
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Obter tipo de visualização
        viz_type = self.viz_var.get()
        
        # Criar figura matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.styling.colors['background'])
        
        # Criar visualização específica
        if viz_type == "correlacao_idh":
            self._create_correlation_chart(ax)
            self.viz_title_var.set("Correlação IDH vs Despesas Públicas")
        elif viz_type == "analise_regional":
            self._create_regional_analysis(ax)
            self.viz_title_var.set("Análise Regional Comparativa")
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
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.chart_container)
        toolbar.update()
        
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
            
            idh_values = np.array(data['idh_values'])
            despesas_values = np.array(data['despesas_values'])
            estados = data['estados']
            regioes = data['regioes']
            correlation = data['correlation']
            
            # Cores por região
            region_colors = {
                'Norte': '#e74c3c',
                'Nordeste': '#f39c12', 
                'Sudeste': '#2ecc71',
                'Sul': '#3498db',
                'Centro-Oeste': '#9b59b6'
            }
            
            colors = [region_colors.get(r, '#95a5a6') for r in regioes]
            
            # Criar scatter plot
            scatter = ax.scatter(idh_values, despesas_values, 
                               c=colors, alpha=0.7, s=100, edgecolors='black', linewidth=1)
            
            # Configurações do gráfico
            ax.set_xlabel('IDH (Índice de Desenvolvimento Humano)')
            ax.set_ylabel('Despesas Públicas per capita (R$ mil)')
            
            # Título com ano
            title = f'Correlação IDH vs Despesas Públicas ({year})'
            ax.set_title(title)
            
            # Linha de tendência
            if len(idh_values) > 1:
                z = np.polyfit(idh_values, despesas_values, 1)
                p = np.poly1d(z)
                ax.plot(idh_values, p(idh_values), "r--", alpha=0.8, linewidth=2)
                
                # Texto com correlação
                ax.text(0.05, 0.95, f'Correlação: {correlation:.3f}', 
                       transform=ax.transAxes, fontsize=12, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
                
            # Adicionar labels dos estados
            for i, (x, y, estado) in enumerate(zip(idh_values, despesas_values, estados)):
                ax.annotate(estado, (x, y), xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.8)
            
            # Legenda por região
            handles = [plt.Line2D([0], [0], marker='o', color='w', 
                                markerfacecolor=color, markersize=10, label=region)
                      for region, color in region_colors.items()]
            ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))
            
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados de correlação: {e}")
            # Fallback para gráfico básico
            self._create_correlation_chart_fallback(ax)
            
    def _create_correlation_chart_fallback(self, ax):
        """Gráfico de correlação com dados simulados (fallback)"""
        # Dados simulados
        np.random.seed(42)
        n_states = 27
        
        idh_values = np.random.normal(0.75, 0.05, n_states)
        idh_values = np.clip(idh_values, 0.6, 0.85)
        
        despesas_per_capita = 2000 + (idh_values - 0.6) * 8000 + np.random.normal(0, 500, n_states)
        despesas_per_capita = np.clip(despesas_per_capita, 1500, 4500)
        
        scatter = ax.scatter(idh_values, despesas_per_capita, 
                           c=idh_values, cmap='viridis', 
                           s=100, alpha=0.7, edgecolors='black')
        
        z = np.polyfit(idh_values, despesas_per_capita, 1)
        p = np.poly1d(z)
        ax.plot(idh_values, p(idh_values), "r--", alpha=0.8, linewidth=2)
        
        ax.set_xlabel('Índice de Desenvolvimento Humano (IDH)', fontsize=12)
        ax.set_ylabel('Despesas Per Capita (R$)', fontsize=12)
        ax.set_title('Correlação IDH vs Despesas Públicas per Capita (Demo)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('IDH', rotation=270, labelpad=20)
        
        correlation = np.corrcoef(idh_values, despesas_per_capita)[0, 1]
        ax.text(0.05, 0.95, f'Correlação: {correlation:.3f} (Demo)', 
                transform=ax.transAxes, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
        
    def _create_regional_analysis(self, ax):
        """Cria análise regional comparativa"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter filtro de ano
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023  # Usar 2023 como padrão
            else:
                year = int(year_str)
            
            # Buscar dados regionais
            data = data_provider.get_regional_analysis_data(year=year)
            
            regions = data['regioes']
            idh_means = data['idh_values']
            despesas_means = data['gastos_values']  # Corrigir nome do campo
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados regionais: {e}")
            # Usar dados padrão em caso de erro
            regions = ['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste']
            idh_means = [0.684, 0.663, 0.766, 0.754, 0.734]
            despesas_means = [2.8, 2.2, 3.5, 3.3, 3.0]
        
        # Criar gráfico de barras duplas
        x = np.arange(len(regions))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, idh_means, width, label='IDH', 
                      color=self.styling.colors['primary'], alpha=0.8)
        bars2 = ax.bar(x + width/2, despesas_means, width, label='Investimento (norm.)', 
                      color=self.styling.colors['secondary'], alpha=0.8)
        
        # Configurações
        ax.set_xlabel('Região')
        ax.set_ylabel('Valores')
        
        # Obter filtro de ano para o título
        year_str = self.year_var.get()
        if year_str == "Todos":
            title = 'Análise Regional: IDH vs Investimentos (Geral)'
        else:
            title = f'Análise Regional: IDH vs Investimentos ({year_str})'
        ax.set_title(title)
        
        ax.set_xticks(x)
        ax.set_xticklabels(regions)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.3f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
            
    def _create_temporal_trends(self, ax):
        """Cria gráfico de tendências temporais"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter filtro de ano
            year_filter = self.year_var.get()
            
            # Buscar dados temporais do data_provider
            data = data_provider.get_temporal_trends_data(region=self.region_var.get())
            
            years = data.get('anos', [2019, 2020, 2021, 2022, 2023])
            regions_data = data.get('regioes_data', {})
            
            # Se não há dados, usar dados padrão
            if not regions_data:
                regions_data = {
                    'Norte': [0.682, 0.684, 0.686, 0.688, 0.690],
                    'Nordeste': [0.661, 0.663, 0.665, 0.667, 0.669],
                    'Sudeste': [0.764, 0.766, 0.768, 0.770, 0.772],
                    'Sul': [0.752, 0.754, 0.756, 0.758, 0.760],
                    'Centro-Oeste': [0.732, 0.734, 0.736, 0.738, 0.740]
                }
            
            # Filtrar por ano se não for "Todos"
            if year_filter != "Todos":
                year_selected = int(year_filter)
                if year_selected in years:
                    year_index = years.index(year_selected)
                    years = [year_selected]
                    for region in regions_data:
                        regions_data[region] = [regions_data[region][year_index]]
            
            colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
            
            for i, (region, values) in enumerate(regions_data.items()):
                if len(years) == 1:
                    # Para um ano específico, mostrar barras
                    ax.bar(i, values[0], color=colors[i], alpha=0.7, label=region)
                else:
                    # Para todos os anos, mostrar linha temporal
                    ax.plot(years, values, marker='o', linewidth=3, 
                           label=region, color=colors[i], markersize=8)
            
            if len(years) == 1:
                ax.set_xlabel('Região')
                ax.set_ylabel('IDH')
                ax.set_title(f'IDH por Região ({year_filter})')
                ax.set_xticks(range(len(regions_data)))
                ax.set_xticklabels(regions_data.keys(), rotation=45)
            else:
                ax.set_xlabel('Ano')
                ax.set_ylabel('IDH Médio')
                ax.set_title('Evolução Temporal do IDH por Região (2019-2023)')
                
        except Exception as e:
            print(f"Erro ao carregar dados temporais: {e}")
            # Fallback com dados simulados ajustados para o ano
            year_filter = self.year_var.get()
            
            years = [2019, 2020, 2021, 2022, 2023]
            regions_data = {
                'Sudeste': [0.764, 0.766, 0.768, 0.770, 0.772],
                'Sul': [0.752, 0.754, 0.756, 0.758, 0.760],
                'Centro-Oeste': [0.732, 0.734, 0.736, 0.738, 0.740],
                'Norte': [0.682, 0.684, 0.686, 0.688, 0.690],
                'Nordeste': [0.661, 0.663, 0.665, 0.667, 0.669]
            }
            
            # Filtrar por ano se não for "Todos"
            if year_filter != "Todos":
                year_selected = int(year_filter)
                if year_selected in years:
                    year_index = years.index(year_selected)
                    years = [year_selected]
                    for region in regions_data:
                        regions_data[region] = [regions_data[region][year_index]]
            
            colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
            
            for i, (region, values) in enumerate(regions_data.items()):
                if len(years) == 1:
                    # Para um ano específico, mostrar barras
                    ax.bar(i, values[0], color=colors[i], alpha=0.7, label=region)
                else:
                    # Para todos os anos, mostrar linha temporal
                    ax.plot(years, values, marker='o', linewidth=3, 
                           label=region, color=colors[i], markersize=8)
            
            if len(years) == 1:
                ax.set_xlabel('Região')
                ax.set_ylabel('IDH')
                ax.set_title(f'IDH por Região ({year_filter})')
                ax.set_xticks(range(len(regions_data)))
                ax.set_xticklabels(regions_data.keys(), rotation=45)
            else:
                ax.set_xlabel('Ano')
                ax.set_ylabel('IDH Médio')
                ax.set_title('Evolução Temporal do IDH por Região (2019-2023)')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _create_state_efficiency(self, ax):
        """Cria gráfico de eficiência por estado"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter filtro de ano
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023  # Usar 2023 como padrão
            else:
                year = int(year_str)
            
            # Buscar dados de eficiência (sempre usar dados simulados se dados reais falham)
            data = data_provider.get_state_efficiency_data(year=year)
            
            states = data['estados']
            efficiency = data['efficiency_values']
            media_nacional = data['media_nacional']
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados de eficiência: {e}")
            # Usar método demo diretamente do data_provider
            from src.gui.data_integration import data_provider
            year_str = self.year_var.get()
            year = 2023 if year_str == "Todos" else int(year_str)
            data = data_provider._get_demo_efficiency_data(year)
            
            states = data['estados']
            efficiency = data['efficiency_values']
            media_nacional = data['media_nacional']
        
        # Cores baseadas na eficiência
        colors = ['green' if e > media_nacional else 'orange' if e > media_nacional*0.8 else 'red' for e in efficiency]
        
        bars = ax.bar(states, efficiency, color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Estado')
        ax.set_ylabel('Eficiência (IDH/Despesa per capita)')
        ax.set_title(f'Eficiência dos Estados: IDH vs Investimento ({year})')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Linha de referência
        ax.axhline(y=media_nacional, color='blue', linestyle='--', 
                  label=f'Média Nacional: {media_nacional:.3f}')
        ax.legend()
        
        # Rotacionar labels dos estados para melhor visualização
        ax.tick_params(axis='x', rotation=45)
        
    def _create_sectoral_distribution(self, ax):
        """Cria distribuição setorial de despesas"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter filtro de ano
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023  # Usar 2023 como padrão
            else:
                year = int(year_str)
            
            # Buscar dados setoriais (sempre usar dados simulados se dados reais falham)
            data = data_provider.get_sectoral_distribution_data(year=year)
            
            sectors = data['setores']
            values = data['valores']
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados setoriais: {e}")
            # Usar método demo diretamente do data_provider
            from src.gui.data_integration import data_provider
            year_str = self.year_var.get()
            year = 2023 if year_str == "Todos" else int(year_str)
            data = data_provider._get_demo_sectoral_data(year)
            
            sectors = data['setores']
            values = data['valores']
        
        # Gráfico de pizza com explosão
        explode = (0.1, 0.05, 0, 0, 0, 0)[:len(sectors)]
        colors = plt.cm.Set3(np.linspace(0, 1, len(sectors)))
        
        wedges, texts, autotexts = ax.pie(values, labels=sectors, colors=colors, 
                                         autopct='%1.1f%%', startangle=90,
                                         explode=explode, shadow=True)
        
        # Título dinâmico baseado no filtro de ano
        year_str = self.year_var.get()
        if year_str == "Todos":
            title = 'Distribuição Percentual de Investimentos por Setor (Geral)'
        else:
            title = f'Distribuição Percentual de Investimentos por Setor ({year_str})'
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Melhorar aparência
        try:
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
        except:
            pass
            
    def _create_comparative_analysis(self, ax):
        """Cria análise comparativa de estados"""
        try:
            # Importar provedor de dados
            from src.gui.data_integration import data_provider
            
            # Obter filtro de ano
            year_str = self.year_var.get()
            if year_str == "Todos":
                year = 2023  # Usar 2023 como padrão
            else:
                year = int(year_str)
            
            # Buscar dados comparativos (sempre usar dados simulados se dados reais falham)
            data = data_provider.get_comparative_analysis_data(year=year)
            
            # Extrair dados com estrutura correta
            states_top = data['top_states']['estados']
            idh_top = data['top_states']['idh_values']
            states_bottom = data['bottom_states']['estados']
            idh_bottom = data['bottom_states']['idh_values']
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados comparativos: {e}")
            # Usar método demo diretamente do data_provider
            from src.gui.data_integration import data_provider
            data = data_provider._get_demo_comparative_data()
            
            states_top = data['top_states']['estados']
            idh_top = data['top_states']['idh_values']
            states_bottom = data['bottom_states']['estados']
            idh_bottom = data['bottom_states']['idh_values']
        
        # Posições no gráfico
        y_pos_top = np.arange(len(states_top))
        y_pos_bottom = np.arange(len(states_bottom)) + len(states_top) + 1
        
        # Barras horizontais
        bars_top = ax.barh(y_pos_top, idh_top, color='green', alpha=0.7, label='Melhores IDH')
        bars_bottom = ax.barh(y_pos_bottom, idh_bottom, color='red', alpha=0.7, label='Menores IDH')
        
        # Configurações
        ax.set_xlabel('IDH')
        
        # Título com ano
        year_str = self.year_var.get()
        if year_str == "Todos":
            title = 'Análise Comparativa: Estados com Maior e Menor IDH (Geral)'
        else:
            title = f'Análise Comparativa: Estados com Maior e Menor IDH ({year_str})'
        ax.set_title(title)
        
        ax.set_yticks(list(y_pos_top) + list(y_pos_bottom))
        ax.set_yticklabels(states_top + states_bottom)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Linha de separação
        ax.axhline(y=len(states_top) - 0.5, color='black', linestyle='-', linewidth=2)
        
        # Adicionar valores nas barras
        for i, (bar, value) in enumerate(zip(bars_top, idh_top)):
            ax.text(value + 0.005, bar.get_y() + bar.get_height()/2, 
                   f'{value:.3f}', va='center', fontsize=9)
                   
        for i, (bar, value) in enumerate(zip(bars_bottom, idh_bottom)):
            ax.text(value + 0.005, bar.get_y() + bar.get_height()/2, 
                   f'{value:.3f}', va='center', fontsize=9)
        
    def on_visualization_changed(self):
        """Callback para mudança de visualização"""
        self.create_visualization()
        self.main_window.update_status(f"Visualização alterada: {self.viz_title_var.get()}")
        
    def on_filter_changed(self, event=None):
        """Callback para mudança de filtros"""
        year = self.year_var.get()
        region = self.region_var.get()
        
        # Limpar cache de dados para forçar recarregamento
        try:
            from src.gui.data_integration import data_provider
            data_provider.clear_cache()
        except Exception as e:
            pass
            
        # Recriar visualização com novos filtros
        self.create_visualization()
        
        self.main_window.update_status(f"Filtros aplicados: {year} - {region}")
        
        # Atualizar título da visualização para refletir o filtro de ano
        current_viz = self.viz_var.get()
        if current_viz == "correlacao_idh":
            self.viz_title_var.set(f"Correlação IDH vs Despesas Públicas ({year})")
        elif current_viz == "analise_regional":
            title = f"Análise Regional Comparativa ({year})" if year != "Todos" else "Análise Regional Comparativa (Geral)"
            self.viz_title_var.set(title)
        elif current_viz == "tendencias_temporais":
            title = f"Tendências Temporais ({year})" if year != "Todos" else "Tendências Temporais (2019-2023)"
            self.viz_title_var.set(title)
        elif current_viz == "eficiencia_estados":
            self.viz_title_var.set(f"Eficiência por Estado ({year})")
        elif current_viz == "distribuicao_setorial":
            self.viz_title_var.set(f"Distribuição Setorial de Despesas ({year})")
        elif current_viz == "analise_comparativa":
            self.viz_title_var.set(f"Análise Comparativa Estados ({year})")
        
    def refresh_visualization(self):
        """Atualiza visualização atual"""
        self.show_loading()
        
        def refresh_task():
            try:
                # Simular carregamento
                import time
                time.sleep(1)
                self.main_window.root.after(0, self.create_visualization)
                self.main_window.root.after(0, self.hide_loading)
                self.main_window.update_status("Visualização atualizada com sucesso")
            except Exception as e:
                self.main_window.message_helper.show_error(f"Erro ao atualizar: {str(e)}")
                self.main_window.root.after(0, self.hide_loading)
                
        self.main_window.thread_manager.run_thread(refresh_task)
        
    def export_visualization(self):
        """Exporta visualização atual"""
        self.main_window.message_helper.show_info("Funcionalidade de exportação será implementada")
        
    def open_advanced_settings(self):
        """Abre configurações avançadas"""
        self.main_window.message_helper.show_info("Configurações avançadas serão implementadas")
        
    def show_loading(self):
        """Mostra indicador de carregamento"""
        self.loading = True
        self.loading_label.pack(side=RIGHT)
        
    def hide_loading(self):
        """Esconde indicador de carregamento"""
        self.loading = False
        self.loading_label.pack_forget() 