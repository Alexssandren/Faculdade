import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import plotly.express as px
import plotly.offline as pyo
from plotly.offline import plot
import plotly.graph_objects as go
import numpy as np
import math
from matplotlib.patches import Circle
import matplotlib.patches as patches
try:
    import mplcursors
    MPLCURSORS_AVAILABLE = True
except ImportError:
    MPLCURSORS_AVAILABLE = False

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

class GraphsContainerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GraphsContainer")

        # --- Configuração Inicial ---
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.data_path = self.project_root / "data" / "processed" / "dataset_unificado.csv"
        self.shapefile_path = self.project_root / "data" / "geospatial" / "BR_UF_2024.shp"
        
        self.df = None
        self.gdf = None
        self._load_data()

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 5, 20, 20)  # Margem superior mínima para aba Visão Geral
        main_layout.setSpacing(5)  # Espaçamento mínimo entre elementos

        # Título que informa o ano selecionado
        self.title_label = QLabel("Selecione um ano para visualizar os dados")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; padding: 2px;")  # Título mais compacto
        main_layout.addWidget(self.title_label)
        
        # --- Área de Scroll ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        main_layout.addWidget(scroll_area, 1)  # Permitir expansão vertical normal
        
        # Widget conteúdo dentro do scroll
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # --- Grade para os Gráficos ---
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(10)  # Reduzir espaçamento entre gráficos
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens internas do grid
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinhar conteúdo no topo
        
        # Tamanho mínimo será definido dinamicamente em load_graphs_for_year()

        # Placeholder para widgets de gráfico
        self.graph_widgets: list[QWidget] = []

    def _load_data(self):
        """Carrega o dataset principal e o shapefile."""
        try:
            if self.data_path.exists():
                self.df = pd.read_csv(self.data_path)
                # Adicionar conversões e preparações necessárias aqui se houver
            else:
                print(f"⚠️  Arquivo de dados não encontrado em: {self.data_path}")
                self.df = pd.DataFrame() # DataFrame vazio para evitar erros

            if self.shapefile_path.exists():
                self.gdf = gpd.read_file(self.shapefile_path, layer='BR_UF_2024')
                # Renomear colunas para o merge
                self.gdf = self.gdf.rename(columns={'SIGLA_UF': 'uf', 'NM_UF': 'NOME_UF'})
            else:
                print(f"⚠️  Shapefile não encontrado em: {self.shapefile_path}")
                self.gdf = gpd.GeoDataFrame() # GeoDataFrame vazio

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self.df = pd.DataFrame()
            self.gdf = gpd.GeoDataFrame()
            
    def load_graphs_for_year(self, year: int | None):
        """Limpa a grade e gera os novos gráficos para o ano especificado."""
        # Limpar widgets antigos da grade
        for widget in self.graph_widgets:
            self.grid_layout.removeWidget(widget)
            widget.deleteLater()
        self.graph_widgets.clear()

        if year is None:
            self.title_label.setText("Visão Geral - Dados Agregados")
            
            # Gráfico de Evolução Temporal - apenas na visão geral
            line_widget = self._create_line_chart()
            self.grid_layout.addWidget(line_widget, 0, 0, 1, 2) # Linha 0, Ocupa 2 colunas
            self.graph_widgets.append(line_widget)
            return

        if self.df.empty:
            self.title_label.setText(f"Dados para {year}")
            placeholder = QLabel("Não foi possível carregar os dados para gerar os gráficos.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 2)
            self.graph_widgets.append(placeholder)
            return

        self.title_label.setText(f"Análise de Dados para o Ano de {year}")
        
        # Ajustar tamanho mínimo para anos específicos (múltiplos gráficos)
        scroll_content = self.grid_layout.parent()
        scroll_content.setMinimumSize(1200, 1800)  # Altura maior para múltiplos gráficos
        
        df_year = self.df[self.df['ano'] == year]

        # --- Gerar e Adicionar Gráficos ---
        # 1. Mapa Coroplético
        map_widget = self._create_choropleth_map(df_year)
        self.grid_layout.addWidget(map_widget, 0, 0) # Linha 0, Coluna 0
        self.graph_widgets.append(map_widget)

        # 2. Gráfico de Pizza
        pie_widget = self._create_pie_chart(df_year)
        self.grid_layout.addWidget(pie_widget, 0, 1) # Linha 0, Coluna 1
        self.graph_widgets.append(pie_widget)

        # 3. Gráfico de Bolhas
        bubble_widget = self._create_bubble_chart(df_year)
        self.grid_layout.addWidget(bubble_widget, 1, 0, 1, 2) # Linha 1, Ocupa 2 colunas
        self.graph_widgets.append(bubble_widget)

        # 4. Treemap de Gasto per capita
        treemap_widget = self._create_treemap_chart(df_year)
        self.grid_layout.addWidget(treemap_widget, 2, 0, 1, 2) # Linha 2, Ocupa 2 colunas
        self.graph_widgets.append(treemap_widget)

    def _create_matplotlib_widget(self, fig: Figure) -> QWidget:
        """Cria um widget QCanvas a partir de uma figura Matplotlib."""
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #3c3c3c; border-radius: 10px;")
        # Forçar um fundo transparente para a figura para que o estilo do canvas apareça
        fig.patch.set_facecolor('none')
        
        # Garantir que o canvas pode receber eventos de mouse
        canvas.setMouseTracking(True)
        
        return canvas
    
    def _create_plotly_widget(self, fig) -> QWidget:
        """Cria um widget QWebEngineView a partir de uma figura Plotly."""
        # Configurar apenas o essencial para desabilitar scroll
        config = {
            'scrollZoom': False,
            'displayModeBar': False,  # Remove a barra de ferramentas
            'staticPlot': False  # Manter hover funcionando
        }
        
        # Gerar HTML do gráfico Plotly com configurações
        html_string = fig.to_html(include_plotlyjs='cdn', config=config)
        
        # Criar widget de visualização web
        web_view = QWebEngineView()
        web_view.setHtml(html_string)
        web_view.setStyleSheet("background-color: #3c3c3c; border-radius: 10px;")
        
        return web_view

    def _create_choropleth_map(self, df_year: pd.DataFrame) -> QWidget:
        """Cria o mapa coroplético do IDH e gastos."""
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        fig.suptitle('IDH e Gasto Total por Estado', color='white', fontsize=14, fontweight='bold')
        
        if not self.gdf.empty and not df_year.empty:
            expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
            
            agg_dict = {'idh': 'mean'}
            for col in expense_cols:
                if col in df_year.columns:
                    agg_dict[col] = 'sum'

            map_data = df_year.groupby('uf').agg(agg_dict).reset_index()
            
            existing_expense_cols = [col for col in expense_cols if col in map_data.columns]
            map_data['gasto_total'] = map_data[existing_expense_cols].sum(axis=1)
            
            merged_gdf = self.gdf.merge(map_data, on='uf', how='left')
            merged_gdf['gasto_total'] = merged_gdf['gasto_total'].fillna(0)
            merged_gdf['idh'] = merged_gdf['idh'].fillna(0)

            merged_gdf.plot(column='idh', cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
            
            for idx, row in merged_gdf.iterrows():
                if row.geometry.centroid.is_empty: continue
                gasto_milhoes = row['gasto_total']
                label = f"IDH: {row['idh']:.3f}\nGasto: R${gasto_milhoes:.2f}M"

        ax.set_axis_off()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        return self._create_matplotlib_widget(fig)

    def _create_pie_chart(self, df_year: pd.DataFrame) -> QWidget:
        """Cria o gráfico de pizza com a distribuição de gastos."""
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        fig.suptitle('Distribuição de Gastos por Setor', color='white', fontsize=14, fontweight='bold')
        
        setores_map = {
            'despesa_saude': 'Saúde',
            'despesa_educacao': 'Educação',
            'despesa_infraestrutura': 'Infraestrutura',
            'despesa_assistencia_social': 'Assistência Social'
        }
        setores_cols = [col for col in setores_map.keys() if col in df_year.columns]
        
        if not setores_cols:
            # Lidar com o caso de não haver colunas de despesa
            ax.text(0.5, 0.5, 'Dados de despesa não disponíveis', ha='center', va='center', color='white')
            return self._create_matplotlib_widget(fig)

        gastos_setor = df_year[setores_cols].sum()
        # Usar nomes amigáveis para a legenda
        gastos_setor.index = gastos_setor.index.map(setores_map)
        
        if not gastos_setor.empty and gastos_setor.sum() > 0:
            # Cores vivas e distintas para cada setor
            cores_vivas = [
                '#FF6B6B',  # Vermelho vibrante - Saúde
                '#4ECDC4',  # Turquesa - Educação  
                '#45B7D1',  # Azul vibrante - Infraestrutura
                '#96CEB4',  # Verde menta - Assistência Social
            ]
            
            wedges, texts, autotexts = ax.pie(
                gastos_setor, 
                autopct='%1.1f%%', 
                startangle=90, 
                pctdistance=0.85,
                colors=cores_vivas[:len(gastos_setor)],  # Usar apenas as cores necessárias
                explode=[0.05] * len(gastos_setor)  # Separar ligeiramente as fatias para melhor visualização
            )
            ax.legend(wedges, gastos_setor.index, title="Setores", loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1),
                      title_fontproperties={'weight': 'bold', 'size': 10},
                      facecolor='#424242', labelcolor='white')
            for text in texts:
                text.set_color('white')  # Cor branca para melhor contraste
                text.set_fontweight('bold')
            for autotext in autotexts:
                autotext.set_color('white')  # Texto branco para melhor contraste com cores vivas
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)  # Aumentar tamanho da fonte
        else:
            ax.text(0.5, 0.5, 'Não há dados de gastos para este ano.', ha='center', va='center', color='white')


        ax.axis('equal')
        plt.tight_layout(rect=[0, 0, 0.8, 0.95])
        return self._create_matplotlib_widget(fig)
        
    def _create_bubble_chart(self, df_year: pd.DataFrame) -> QWidget:
        """Cria o gráfico de bubble packing (nuvem de bolhas) usando matplotlib."""
        expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
        existing_expense_cols = [col for col in expense_cols if col in df_year.columns]
        
        df_year_copy = df_year.copy()
        df_year_copy['gasto_total'] = df_year_copy[existing_expense_cols].sum(axis=1)

        agg_dict = {
            'idh': 'mean',
            'gasto_total': 'sum',
        }
        if 'populacao' in df_year_copy.columns:
            agg_dict['populacao'] = 'first'
        if 'regiao' in df_year_copy.columns:
            agg_dict['regiao'] = 'first'

        state_data = df_year_copy.groupby('uf').agg(agg_dict).reset_index()

        if not state_data.empty:
            # Criar figura matplotlib
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            fig.suptitle('Gastos Públicos por Estado - Bubble Packing', color='white', fontsize=16, fontweight='bold')
            
            # Usar gasto_total como prioridade para definir o tamanho das bolhas
            size_column = 'gasto_total' if 'gasto_total' in state_data.columns else 'populacao'
            sizes = state_data[size_column].values
            
            # Normalizar tamanhos para raios das bolhas (entre 0.5 e 4.0)
            min_size, max_size = sizes.min(), sizes.max()
            if max_size > min_size:
                normalized_sizes = 0.5 + 3.5 * (sizes - min_size) / (max_size - min_size)
            else:
                normalized_sizes = np.full_like(sizes, 2.0)
            
            # Cores por região
            if 'regiao' in state_data.columns:
                regions = state_data['regiao'].unique()
                color_map = plt.cm.Set3(np.linspace(0, 1, len(regions)))
                region_colors = {region: color_map[i] for i, region in enumerate(regions)}
                colors = [region_colors[region] for region in state_data['regiao']]
            else:
                # Cores baseadas no IDH
                colors = plt.cm.viridis(state_data['idh'] / state_data['idh'].max())
            
            # Algoritmo de bubble packing
            positions = self._pack_bubbles(normalized_sizes)
            
            # Armazenar referências dos círculos para tooltips
            circles = []
            bubble_data = []
            
            # Desenhar as bolhas
            for i, (x, y) in enumerate(positions):
                circle = Circle((x, y), normalized_sizes[i], 
                              facecolor=colors[i], 
                              edgecolor='white', 
                              linewidth=2, 
                              alpha=0.8)
                ax.add_patch(circle)
                circles.append(circle)
                
                # Armazenar dados da bolha para tooltip
                bubble_info = {
                    'uf': state_data.iloc[i]['uf'],
                    'idh': state_data.iloc[i]['idh'],
                    'gasto_total': state_data.iloc[i]['gasto_total'],
                    'regiao': state_data.iloc[i].get('regiao', 'N/A'),
                    'populacao': state_data.iloc[i].get('populacao', 'N/A')
                }
                bubble_data.append(bubble_info)
                
                # Adicionar texto do estado
                ax.text(x, y, state_data.iloc[i]['uf'], 
                       ha='center', va='center', 
                       fontsize=min(12, max(8, normalized_sizes[i] * 3)), 
                       color='white', 
                       fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.1", 
                               facecolor='black', 
                               alpha=0.6))
            
            # Configurar eixos
            padding = max(normalized_sizes) * 0.5
            all_x = [pos[0] for pos in positions]
            all_y = [pos[1] for pos in positions]
            
            ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
            ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Configurar tooltips usando eventos matplotlib
            self._setup_bubble_tooltips(fig, ax, positions, normalized_sizes, bubble_data)
            
            # Ajustar layout
            plt.tight_layout()
            
            return self._create_matplotlib_widget(fig)
        else:
            # Retornar widget vazio se não há dados
            placeholder = QLabel("Não há dados suficientes para gerar o gráfico de bolhas.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: white; font-size: 14px;")
            return placeholder
    
    def _create_treemap_chart(self, df_year: pd.DataFrame) -> QWidget:
        """Cria o gráfico treemap com gasto per capita por estado usando Plotly."""
        expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
        existing_expense_cols = [col for col in expense_cols if col in df_year.columns]
        
        df_year_copy = df_year.copy()
        df_year_copy['gasto_total'] = df_year_copy[existing_expense_cols].sum(axis=1)

        agg_dict = {
            'gasto_total': 'sum',
        }
        if 'populacao' in df_year_copy.columns:
            agg_dict['populacao'] = 'first'
        if 'regiao' in df_year_copy.columns:
            agg_dict['regiao'] = 'first'

        state_data = df_year_copy.groupby('uf').agg(agg_dict).reset_index()

        if not state_data.empty and 'populacao' in state_data.columns:
            # Calcular gasto per capita
            state_data['gasto_per_capita'] = state_data['gasto_total'] / state_data['populacao'] * 1000000  # Converter para reais
            
            # Remover valores infinitos ou NaN
            state_data = state_data[state_data['gasto_per_capita'].notna()]
            state_data = state_data[state_data['gasto_per_capita'] > 0]
            
            if not state_data.empty:
                import plotly.express as px
                import plotly.graph_objects as go
                
                # Criar treemap usando Plotly Express (método mais simples e confiável)
                try:
                    # Adicionar hierarquia se temos regiões
                    if 'regiao' in state_data.columns:
                        # Com hierarquia: Região -> Estado
                        fig = px.treemap(
                            state_data, 
                            path=[px.Constant("Brasil"), 'regiao', 'uf'],
                            values='gasto_per_capita',
                            title='Gasto per Capita por Estado - Treemap',
                            hover_data=['gasto_total', 'populacao'],
                            color='gasto_per_capita',
                            color_continuous_scale='Viridis'
                        )
                    else:
                        # Sem hierarquia: apenas estados
                        fig = px.treemap(
                            state_data, 
                            path=[px.Constant("Brasil"), 'uf'],
                            values='gasto_per_capita',
                            title='Gasto per Capita por Estado - Treemap',
                            hover_data=['gasto_total'],
                            color='gasto_per_capita',
                            color_continuous_scale='Viridis'
                        )
                    
                    # Configurar layout
                    fig.update_layout(
                        title={
                            'text': 'Gasto per Capita por Estado - Treemap',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 16, 'color': 'white'}
                        },
                        font=dict(size=12, color='white'),
                        paper_bgcolor='#2b2b2b',
                        plot_bgcolor='#2b2b2b',
                        margin=dict(t=50, l=25, r=25, b=25),
                        height=1000  # Aumentar ainda mais a altura para mostrar tudo
                    )
                    
                    # Personalizar o texto e hover
                    fig.update_traces(
                        textinfo="label+value",
                        texttemplate="<b>%{label}</b><br>R$ %{value:.0f}",
                        hovertemplate='<b>%{label}</b><br>Gasto per Capita: R$ %{value:.0f}<br>%{customdata}<extra></extra>'
                    )
                    
                    return self._create_plotly_widget(fig)
                    
                except Exception as e:
                    print(f"Erro ao criar treemap com px.treemap: {e}")
                    # Fallback para versão mais simples
                    pass
                
                # Fallback - versão simplificada usando apenas estados
                try:
                    fig = px.treemap(
                        state_data, 
                        names='uf',  # Usar names ao invés de path para versão mais simples
                        values='gasto_per_capita',
                        title='Gasto per Capita por Estado - Treemap'
                    )
                    
                    # Configurar layout
                    fig.update_layout(
                        title={
                            'text': 'Gasto per Capita por Estado - Treemap',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 16, 'color': 'white'}
                        },
                        font=dict(size=12, color='white'),
                        paper_bgcolor='#2b2b2b',
                        plot_bgcolor='#2b2b2b',
                        margin=dict(t=50, l=25, r=25, b=25),
                        height=1000  # Aumentar ainda mais a altura para mostrar tudo
                    )
                    
                    return self._create_plotly_widget(fig)
                    
                except Exception as e:
                    print(f"Erro ao criar treemap simplificado: {e}")
                    pass
        
        # Retornar widget vazio se não há dados
        placeholder = QLabel("Não há dados suficientes para gerar o treemap.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: white; font-size: 14px;")
        return placeholder

    def _create_line_chart(self) -> QWidget:
        """Cria o gráfico de linha simples com IDH médio vs gasto total por ano."""
        if self.df.empty:
            placeholder = QLabel("Não há dados suficientes para gerar o gráfico de evolução temporal.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: white; font-size: 14px;")
            return placeholder

        # Calcular métricas anuais
        expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
        existing_expense_cols = [col for col in expense_cols if col in self.df.columns]
        
        df_copy = self.df.copy()
        df_copy['gasto_total'] = df_copy[existing_expense_cols].sum(axis=1)
        
        # Agregar por ano
        yearly_data = df_copy.groupby('ano').agg({
            'idh': 'mean',
            'gasto_total': 'sum'  # Somar todos os gastos do ano
        }).reset_index()
        
        if yearly_data.empty:
            placeholder = QLabel("Não há dados anuais suficientes para gerar o gráfico de evolução temporal.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: white; font-size: 14px;")
            return placeholder

        # Criar figura matplotlib com tamanho balanceado
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))  # Tamanho mais adequado
        fig.suptitle('Relação: IDH Médio vs Gasto Total por Ano', color='white', fontsize=16, fontweight='bold')
        
        # Configurar o gráfico
        color = '#1f77b4'  # Azul
        ax.set_xlabel('Gasto Total (R$ Bilhões)', color='white', fontweight='bold')
        ax.set_ylabel('IDH Médio', color='white', fontweight='bold')
        
        # Converter valores para bilhões para melhor legibilidade
        yearly_data['gasto_total_bilhoes'] = yearly_data['gasto_total'] / 1000
        
        # Plotar a linha conectando os pontos por ano
        line = ax.plot(yearly_data['gasto_total_bilhoes'], yearly_data['idh'], 
                      color=color, marker='o', linewidth=3, markersize=10, 
                      label='Evolução por Ano', alpha=0.8)
        
        # Configurar cores dos ticks
        ax.tick_params(axis='both', colors='white')
        ax.grid(True, alpha=0.3, color='white')
        
        # Formatar eixo X para mostrar valores em bilhões de forma mais limpa
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:.1f}B'))
        
        # Adicionar rótulos dos anos nos pontos
        for i, row in yearly_data.iterrows():
            ax.annotate(f'{int(row["ano"])}', 
                       (row['gasto_total_bilhoes'], row['idh']),
                       textcoords="offset points", 
                       xytext=(8, 8), 
                       ha='left', 
                       fontsize=10, 
                       color='white',
                       fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", 
                               facecolor=color, 
                               alpha=0.7))
        
        # Configurar fundo
        ax.set_facecolor('#2b2b2b')
        fig.patch.set_facecolor('#2b2b2b')
        
        # Adicionar informações estatísticas
        correlation = yearly_data['idh'].corr(yearly_data['gasto_total'])
        correlation_text = f"Correlação: {correlation:.3f}"
        if correlation > 0.7:
            correlation_desc = "📈 Forte correlação positiva"
        elif correlation > 0.3:
            correlation_desc = "📊 Correlação positiva moderada"
        elif correlation > -0.3:
            correlation_desc = "📊 Correlação fraca"
        elif correlation > -0.7:
            correlation_desc = "📉 Correlação negativa moderada"
        else:
            correlation_desc = "📉 Forte correlação negativa"
            
        info_text = f"{correlation_text}\n{correlation_desc}"
        ax.text(0.02, 0.98, info_text, 
               transform=ax.transAxes, 
               fontsize=11, 
               color='white',
               verticalalignment='top',
               horizontalalignment='left',
               bbox=dict(boxstyle="round,pad=0.3", 
                       facecolor='black', 
                       alpha=0.8))
        
        # Adicionar legenda
        legend = ax.legend(loc='lower right',
                          facecolor='#424242', 
                          edgecolor='white',
                          labelcolor='white')
        legend.get_frame().set_alpha(0.9)
        
        plt.tight_layout()
        widget = self._create_matplotlib_widget(fig)
        widget.setMinimumHeight(350)  # Garantir altura mínima adequada
        return widget

    def _pack_bubbles(self, sizes):
        """Algoritmo de bubble packing otimizado para criar layout compacto como nuvem de palavras."""
        positions = []
        
        if len(sizes) == 0:
            return positions
        
        # Ordenar bolhas por tamanho (maiores primeiro para melhor packing)
        sorted_indices = np.argsort(sizes)[::-1]
        sorted_sizes = sizes[sorted_indices]
        
        # Primeira bolha (maior) no centro
        positions_temp = [(0.0, 0.0)]
        
        if len(sorted_sizes) == 1:
            return [(0.0, 0.0)]
        
        # Para cada bolha subsequente, encontrar a posição mais próxima possível
        for i in range(1, len(sorted_sizes)):
            radius = sorted_sizes[i]
            best_position = None
            best_distance_from_center = float('inf')
            
            # Tentar posições ao redor de cada bolha já posicionada
            for ref_idx, (ref_x, ref_y) in enumerate(positions_temp):
                ref_radius = sorted_sizes[ref_idx]
                
                # Distância mínima necessária entre centros
                min_distance = radius + ref_radius + 0.05  # pequeno gap
                
                # Tentar ângulos ao redor da bolha de referência
                for angle in np.linspace(0, 2 * np.pi, 36):  # 36 ângulos (10 graus cada)
                    x = ref_x + min_distance * np.cos(angle)
                    y = ref_y + min_distance * np.sin(angle)
                    
                    # Verificar colisão com todas as bolhas existentes
                    collision = False
                    for j, (px, py) in enumerate(positions_temp):
                        existing_radius = sorted_sizes[j]
                        distance_between = np.sqrt((x - px)**2 + (y - py)**2)
                        required_distance = radius + existing_radius + 0.05
                        
                        if distance_between < required_distance:
                            collision = True
                            break
                    
                    # Se não há colisão, considerar esta posição
                    if not collision:
                        distance_from_center = np.sqrt(x**2 + y**2)
                        if distance_from_center < best_distance_from_center:
                            best_distance_from_center = distance_from_center
                            best_position = (x, y)
            
            # Se encontrou uma posição válida, usar ela; senão, posição em espiral
            if best_position is not None:
                positions_temp.append(best_position)
            else:
                # Posicionamento em espiral como fallback
                spiral_angle = i * 0.5  # ângulo crescente
                spiral_radius = radius * 2 + i * 0.5
                x = spiral_radius * np.cos(spiral_angle)
                y = spiral_radius * np.sin(spiral_angle)
                positions_temp.append((x, y))
        
        # Reordenar posições de volta à ordem original
        final_positions = [None] * len(sizes)
        for i, original_idx in enumerate(sorted_indices):
            final_positions[original_idx] = positions_temp[i]
        
        return final_positions
    
    def _setup_bubble_tooltips(self, fig, ax, positions, sizes, bubble_data):
        """Configura tooltips interativos usando eventos matplotlib."""
        # Inicializar tooltip como atributo da instância
        if not hasattr(self, 'tooltip_annotation'):
            self.tooltip_annotation = None
        
        def on_hover(event):
            if event.inaxes != ax:
                if self.tooltip_annotation:
                    self.tooltip_annotation.set_visible(False)
                    try:
                        fig.canvas.draw_idle()
                    except:
                        pass
                return
            
            # Verificar se o mouse está sobre alguma bolha
            mouse_x, mouse_y = event.xdata, event.ydata
            if mouse_x is None or mouse_y is None:
                return
            
            bubble_found = False
            for i, (bubble_x, bubble_y) in enumerate(positions):
                # Calcular distância do mouse ao centro da bolha
                distance = np.sqrt((mouse_x - bubble_x)**2 + (mouse_y - bubble_y)**2)
                
                # Se está dentro do raio da bolha (com uma margem extra para facilitar a detecção)
                if distance <= (sizes[i] + 0.1):
                    # Exibir tooltip
                    data = bubble_data[i]
                    
                    tooltip_text = f"Estado: {data['uf']}\n"
                    tooltip_text += f"IDH: {data['idh']:.3f}\n"
                    tooltip_text += f"Gasto Total: R$ {data['gasto_total']:,.2f}M"
                    
                    if data['regiao'] != 'N/A':
                        tooltip_text += f"\nRegião: {data['regiao']}"
                    
                    if data['populacao'] != 'N/A':
                        tooltip_text += f"\nPopulação: {data['populacao']:,.0f}"
                    
                    # Criar ou atualizar annotation
                    if self.tooltip_annotation:
                        try:
                            self.tooltip_annotation.remove()
                        except:
                            pass
                    
                    # Calcular posição do tooltip para não sair da tela
                    offset_x = 20 if bubble_x < 0 else -20
                    offset_y = 20 if bubble_y < 0 else -20
                    
                    self.tooltip_annotation = ax.annotate(
                        tooltip_text,
                        xy=(bubble_x, bubble_y),
                        xytext=(offset_x, offset_y),
                        textcoords='offset points',
                        bbox=dict(
                            boxstyle="round,pad=0.5",
                            facecolor='#2c3e50',
                            edgecolor='white',
                            alpha=0.95
                        ),
                        fontsize=9,
                        color='white',
                        ha='left',
                        zorder=1000  # Garantir que fica no topo
                    )
                    
                    bubble_found = True
                    try:
                        fig.canvas.draw_idle()
                    except:
                        pass
                    break
            
            # Se não encontrou bolha, ocultar tooltip
            if not bubble_found and self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                try:
                    fig.canvas.draw_idle()
                except:
                    pass
        
        def on_leave(event):
            if self.tooltip_annotation:
                self.tooltip_annotation.set_visible(False)
                try:
                    fig.canvas.draw_idle()
                except:
                    pass
        
        # Conectar eventos com captura de exceções
        try:
            fig.canvas.mpl_connect('motion_notify_event', on_hover)
            fig.canvas.mpl_connect('axes_leave_event', on_leave)
            fig.canvas.mpl_connect('figure_leave_event', on_leave)
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível configurar tooltips interativos: {e}")
