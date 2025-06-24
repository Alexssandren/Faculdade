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
import os
import json
from datetime import datetime
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
        
        # Pasta para salvar gráficos
        self.graphs_cache_dir = self.project_root / "results" / "visualizations" / "dashboard_cache"
        self.graphs_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        self.gdf = None
        self._load_data()
        
        # Verificar e gerar cache de gráficos se necessário
        self._ensure_graphs_cache()

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
        """Carrega os dados do CSV e do shapefile."""
        try:
            if self.data_path.exists():
                self.df = pd.read_csv(self.data_path)
                print(f"✅ Dados carregados: {len(self.df)} registros")
            else:
                print(f"⚠️ Arquivo de dados não encontrado: {self.data_path}")
                self.df = pd.DataFrame()

            if self.shapefile_path.exists():
                self.gdf = gpd.read_file(self.shapefile_path)
                # Padronizar coluna UF
                if 'SIGLA_UF' in self.gdf.columns:
                    self.gdf = self.gdf.rename(columns={'SIGLA_UF': 'uf'})
                self.gdf['uf'] = self.gdf['uf'].astype(str).str.upper()
                print(f"✅ Shapefile carregado: {len(self.gdf)} estados")
            else:
                print(f"⚠️ Shapefile não encontrado: {self.shapefile_path}")
                self.gdf = gpd.GeoDataFrame()

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self.df = pd.DataFrame()
            self.gdf = gpd.GeoDataFrame()

    def _ensure_graphs_cache(self):
        """Verifica se o cache de gráficos existe e está atualizado. Se não, gera os gráficos."""
        if self.df.empty:
            print("⚠️ Sem dados disponíveis para gerar cache de gráficos.")
            return
            
        cache_info_path = self.graphs_cache_dir / "cache_info.json"
        data_modification_time = self.data_path.stat().st_mtime if self.data_path.exists() else 0
        
        # Verificar se o cache existe e está atualizado
        cache_valid = False
        if cache_info_path.exists():
            try:
                with open(cache_info_path, 'r') as f:
                    cache_info = json.load(f)
                    
                if cache_info.get('data_modification_time', 0) >= data_modification_time:
                    # Verificar se todos os arquivos de gráfico esperados existem
                    anos_unicos = sorted(self.df['ano'].dropna().unique())
                    all_files_exist = True
                    
                    for ano in anos_unicos:
                        expected_files = [
                            f"mapa_coropletico_{ano}.html",
                            f"grafico_pizza_{ano}.html", 
                            f"grafico_bolhas_{ano}.html",
                            f"treemap_{ano}.html"
                        ]
                        
                        for filename in expected_files:
                            if not (self.graphs_cache_dir / filename).exists():
                                all_files_exist = False
                                break
                        
                        if not all_files_exist:
                            break
                    
                    cache_valid = all_files_exist
            except Exception as e:
                print(f"⚠️ Erro ao verificar cache: {e}")
                cache_valid = False
        
        if not cache_valid:
            print("🔄 Gerando cache de gráficos...")
            self._generate_graphs_cache()
            
            # Salvar informações do cache
            cache_info = {
                'generated_at': datetime.now().isoformat(),
                'data_modification_time': data_modification_time,
                'total_graphs': len(self.df['ano'].dropna().unique()) * 4
            }
            
            with open(cache_info_path, 'w') as f:
                json.dump(cache_info, f, indent=2)
                
            print(f"✅ Cache de gráficos gerado com sucesso!")
        else:
            print("✅ Cache de gráficos válido encontrado.")

    def _generate_graphs_cache(self):
        """Gera e salva todos os gráficos necessários."""
        if self.df.empty:
            return
            
        anos_unicos = sorted(self.df['ano'].dropna().unique())
        
        for ano in anos_unicos:
            print(f"  -> Gerando gráficos para {ano}...")
            df_year = self.df[self.df['ano'] == ano]
            
            # 1. Mapa Coroplético
            self._save_choropleth_map(df_year, ano)
            
            # 2. Gráfico de Pizza  
            self._save_pie_chart(df_year, ano)
            
            # 3. Gráfico de Bolhas
            self._save_bubble_chart(df_year, ano)
            
            # 4. Treemap
            self._save_treemap_chart(df_year, ano)

    def _save_choropleth_map(self, df_year: pd.DataFrame, ano: int):
        """Gera e salva o mapa coroplético."""
        try:
            if self.gdf.empty or df_year.empty:
                return
                
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

            # Criar mapa com Plotly para salvar como HTML
            fig = px.choropleth_mapbox(
                map_data, 
                geojson=merged_gdf,
                locations='uf', 
                featureidkey='properties.uf',
                color='idh',
                color_continuous_scale="Viridis",
                mapbox_style="carto-darkmatter",  # Usar estilo escuro
                zoom=3,
                center={"lat": -14.24, "lon": -51.925},
                opacity=0.7,
                hover_name='uf',
                hover_data={'idh': True, 'gasto_total': True},
                title=f'IDH e Gasto Total por Estado - {ano}'
            )
            
            # Corrigir fundo para escuro
            fig.update_layout(
                margin={"r":0,"t":30,"l":0,"b":0},
                paper_bgcolor='#2b2b2b',
                plot_bgcolor='#2b2b2b',
                font=dict(color='white'),
                title=dict(font=dict(color='white', size=16))
            )
            
            output_path = self.graphs_cache_dir / f"mapa_coropletico_{ano}.html"
            fig.write_html(str(output_path))
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar mapa coroplético para {ano}: {e}")

    def _save_pie_chart(self, df_year: pd.DataFrame, ano: int):
        """Gera e salva o gráfico de pizza."""
        try:
            setores_map = {
                'despesa_saude': 'Saúde',
                'despesa_educacao': 'Educação', 
                'despesa_infraestrutura': 'Infraestrutura',
                'despesa_assistencia_social': 'Assistência Social'
            }
            setores_cols = [col for col in setores_map.keys() if col in df_year.columns]
            
            if not setores_cols:
                return
                
            gastos_setor = df_year[setores_cols].sum()
            gastos_setor.index = gastos_setor.index.map(setores_map)
            
            if gastos_setor.sum() > 0:
                fig = px.pie(
                    values=gastos_setor.values,
                    names=gastos_setor.index,
                    title=f'Distribuição de Gastos por Setor - {ano}',
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                )
                
                # Corrigir problema de porcentagem - usar texttemplate para controlar formato
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    texttemplate='<b>%{label}</b><br>%{percent}',
                    hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:.2f}M<br>Percentual: %{percent}<extra></extra>'
                )
                
                # Corrigir fundo para escuro
                fig.update_layout(
                    paper_bgcolor='#2b2b2b',
                    plot_bgcolor='#2b2b2b',
                    font=dict(color='white'),
                    title=dict(font=dict(color='white', size=16))
                )
                
                output_path = self.graphs_cache_dir / f"grafico_pizza_{ano}.html"
                fig.write_html(str(output_path))
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar gráfico de pizza para {ano}: {e}")

    def _save_bubble_chart(self, df_year: pd.DataFrame, ano: int):
        """Gera e salva o gráfico de bubble packing (nuvem de bolhas) usando matplotlib."""
        try:
            expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
            existing_expense_cols = [col for col in expense_cols if col in df_year.columns]
            
            df_year_copy = df_year.copy()
            df_year_copy['gasto_total'] = df_year_copy[existing_expense_cols].sum(axis=1)

            # Corrigir região do RJ
            df_year_copy['regiao'] = df_year_copy['regiao'].replace('Rio de Janeiro', 'Sudeste')

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
                # Criar figura matplotlib para bubble packing
                import matplotlib.pyplot as plt
                from matplotlib.patches import Circle
                import numpy as np
                
                fig, ax = plt.subplots(1, 1, figsize=(12, 8))
                fig.patch.set_facecolor('#2b2b2b')  # Fundo escuro
                ax.set_facecolor('#2b2b2b')
                fig.suptitle('Gastos Públicos por Estado - Bubble Packing', color='white', fontsize=16, fontweight='bold')
                
                # Usar gasto_total como tamanho das bolhas
                sizes = state_data['gasto_total'].values
                
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
                
                # Desenhar as bolhas
                for i, (x, y) in enumerate(positions):
                    if x is not None and y is not None:  # Verificar se posição é válida
                        circle = Circle((x, y), normalized_sizes[i], 
                                      facecolor=colors[i], 
                                      edgecolor='white', 
                                      linewidth=2, 
                                      alpha=0.8)
                        ax.add_patch(circle)
                        
                        # Adicionar texto do estado
                        ax.text(x, y, state_data.iloc[i]['uf'], 
                               ha='center', va='center', 
                               fontsize=min(12, max(8, normalized_sizes[i] * 3)), 
                               color='white', 
                               fontweight='bold',
                               bbox=dict(boxstyle="round,pad=0.1", 
                                       facecolor='black', 
                                       alpha=0.6))
                
                # Configurar eixos (padding menor para bolhas coladas)
                padding = max(normalized_sizes) * 0.2
                all_x = [pos[0] for pos in positions if pos[0] is not None]
                all_y = [pos[1] for pos in positions if pos[1] is not None]
                
                if all_x and all_y:  # Verificar se há posições válidas
                    ax.set_xlim(min(all_x) - padding, max(all_x) + padding)
                    ax.set_ylim(min(all_y) - padding, max(all_y) + padding)
                ax.set_aspect('equal')
                ax.axis('off')
                
                # Ajustar layout
                plt.tight_layout()
                
                # Salvar como HTML usando plotly
                try:
                    import plotly.graph_objects as go
                    
                    # Converter para Plotly para salvar como HTML
                    plotly_fig = go.Figure()
                    
                    for i, (x, y) in enumerate(positions):
                        if x is not None and y is not None:
                            plotly_fig.add_trace(go.Scatter(
                                x=[x], y=[y],
                                mode='markers+text',
                                marker=dict(
                                    size=normalized_sizes[i] * 40,  # Escala maior para bolhas mais visíveis
                                    color=colors[i] if isinstance(colors[i], str) else f'rgba({int(colors[i][0]*255)},{int(colors[i][1]*255)},{int(colors[i][2]*255)},0.8)',
                                    line=dict(color='white', width=2)
                                ),
                                text=state_data.iloc[i]['uf'],
                                textposition='middle center',
                                textfont=dict(color='white', size=12),
                                showlegend=False,
                                hovertemplate=f"<b>{state_data.iloc[i]['uf']}</b><br>" +
                                            f"Gasto Total: R$ {state_data.iloc[i]['gasto_total']:.2f}M<br>" +
                                            f"IDH: {state_data.iloc[i]['idh']:.3f}<br>" +
                                            f"Região: {state_data.iloc[i].get('regiao', 'N/A')}<extra></extra>"
                            ))
                    
                    plotly_fig.update_layout(
                        title=dict(
                            text='Gastos Públicos por Estado - Bubble Packing',
                            font=dict(color='white', size=16),
                            x=0.5
                        ),
                        paper_bgcolor='#2b2b2b',
                        plot_bgcolor='#2b2b2b',
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    output_path = self.graphs_cache_dir / f"grafico_bolhas_{ano}.html"
                    plotly_fig.write_html(str(output_path))
                    
                except Exception as e:
                    print(f"⚠️ Erro ao converter para Plotly: {e}")
                    # Fallback: salvar matplotlib como PNG e criar HTML simples
                    png_path = self.graphs_cache_dir / f"grafico_bolhas_{ano}.png"
                    fig.savefig(str(png_path), facecolor='#2b2b2b', dpi=150, bbox_inches='tight')
                    
                    # Criar HTML simples com a imagem
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Gráfico de Bolhas - {ano}</title></head>
                    <body style="background-color: #2b2b2b; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center;">
                        <img src="grafico_bolhas_{ano}.png" style="max-width: 100%; height: auto;">
                    </body>
                    </html>
                    """
                    
                    output_path = self.graphs_cache_dir / f"grafico_bolhas_{ano}.html"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                
                plt.close(fig)  # Liberar memória
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar gráfico de bolhas para {ano}: {e}")

    def _save_treemap_chart(self, df_year: pd.DataFrame, ano: int):
        """Gera e salva o treemap."""
        try:
            expense_cols = ['despesa_saude', 'despesa_educacao', 'despesa_infraestrutura', 'despesa_assistencia_social']
            existing_expense_cols = [col for col in expense_cols if col in df_year.columns]
            
            df_year_copy = df_year.copy()
            df_year_copy['gasto_total'] = df_year_copy[existing_expense_cols].sum(axis=1)

            # Corrigir região do RJ e outros problemas de mapeamento
            df_year_copy['regiao'] = df_year_copy['regiao'].replace({
                'Rio de Janeiro': 'Sudeste',
                'São Paulo': 'Sudeste', 
                'Minas Gerais': 'Sudeste',
                'Mato Grosso': 'Centro-Oeste',
                'Mato Grosso do Sul': 'Centro-Oeste',
                'Maranhão': 'Nordeste'
            })

            agg_dict = {'gasto_total': 'sum'}
            if 'populacao' in df_year_copy.columns:
                agg_dict['populacao'] = 'first'
            if 'regiao' in df_year_copy.columns:
                agg_dict['regiao'] = 'first'

            state_data = df_year_copy.groupby('uf').agg(agg_dict).reset_index()

            if not state_data.empty and 'populacao' in state_data.columns:
                state_data['gasto_per_capita'] = state_data['gasto_total'] / state_data['populacao'] * 1000000
                state_data = state_data[state_data['gasto_per_capita'].notna()]
                state_data = state_data[state_data['gasto_per_capita'] > 0]
                
                if not state_data.empty:
                    if 'regiao' in state_data.columns:
                        fig = px.treemap(
                            state_data, 
                            path=[px.Constant("Brasil"), 'regiao', 'uf'],
                            values='gasto_per_capita',
                            title=f'Gasto per Capita por Estado - {ano}',
                            hover_data=['gasto_total', 'populacao'],
                            color='gasto_per_capita',
                            color_continuous_scale='Viridis'
                        )
                    else:
                        fig = px.treemap(
                            state_data, 
                            path=[px.Constant("Brasil"), 'uf'],
                            values='gasto_per_capita',
                            title=f'Gasto per Capita por Estado - {ano}',
                            hover_data=['gasto_total'],
                            color='gasto_per_capita',
                            color_continuous_scale='Viridis'
                        )
                    
                    # Corrigir fundo para escuro
                    fig.update_layout(
                        paper_bgcolor='#2b2b2b',
                        plot_bgcolor='#2b2b2b',
                        font=dict(color='white'),
                        title={
                            'text': f'Gasto per Capita por Estado - {ano}',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 16, 'color': 'white'}
                        },
                        margin=dict(t=50, l=25, r=25, b=25)
                    )
                    
                    output_path = self.graphs_cache_dir / f"treemap_{ano}.html"
                    fig.write_html(str(output_path))
                    
        except Exception as e:
            print(f"⚠️ Erro ao salvar treemap para {ano}: {e}")
            
    def load_graphs_for_year(self, year: int | None):
        """Limpa a grade e carrega os gráficos para o ano especificado."""
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
        
        # --- Carregar Gráficos do Cache ---
        # 1. Mapa Coroplético
        map_widget = self._load_cached_graph(f"mapa_coropletico_{year}.html")
        if map_widget:
            self.grid_layout.addWidget(map_widget, 0, 0) # Linha 0, Coluna 0
            self.graph_widgets.append(map_widget)

        # 2. Gráfico de Pizza
        pie_widget = self._load_cached_graph(f"grafico_pizza_{year}.html")
        if pie_widget:
            self.grid_layout.addWidget(pie_widget, 0, 1) # Linha 0, Coluna 1
            self.graph_widgets.append(pie_widget)

        # 3. Gráfico de Bolhas
        bubble_widget = self._load_cached_graph(f"grafico_bolhas_{year}.html")
        if bubble_widget:
            self.grid_layout.addWidget(bubble_widget, 1, 0, 1, 2) # Linha 1, Ocupa 2 colunas
            self.graph_widgets.append(bubble_widget)

        # 4. Treemap
        treemap_widget = self._load_cached_graph(f"treemap_{year}.html")
        if treemap_widget:
            self.grid_layout.addWidget(treemap_widget, 2, 0, 1, 2) # Linha 2, Ocupa 2 colunas
            self.graph_widgets.append(treemap_widget)

    def _load_cached_graph(self, filename: str) -> QWidget | None:
        """Carrega um gráfico do cache."""
        try:
            graph_path = self.graphs_cache_dir / filename
            if graph_path.exists():
                web_view = QWebEngineView()
                web_view.load(f"file:///{graph_path.as_posix()}")
                web_view.setStyleSheet("background-color: #3c3c3c; border-radius: 10px;")
                return web_view
            else:
                print(f"⚠️ Arquivo de cache não encontrado: {filename}")
                return None
        except Exception as e:
            print(f"⚠️ Erro ao carregar gráfico do cache {filename}: {e}")
            return None

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
            all_x = [pos[0] for pos in positions if pos[0] is not None]
            all_y = [pos[1] for pos in positions if pos[1] is not None]
            
            if all_x and all_y:  # Verificar se há posições válidas
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

    class BubbleChart:
        """Classe para criar bubble charts com bolhas coladas usando algoritmo de colapso."""
        
        def __init__(self, area, bubble_spacing=0):
            """
            Setup para colapso de bolhas.
            
            Parameters
            ----------
            area : array-like
                Área das bolhas.
            bubble_spacing : float, default: 0
                Espaçamento mínimo entre bolhas após colapso.
            """
            import numpy as np
            area = np.asarray(area)
            r = np.sqrt(area / np.pi)

            self.bubble_spacing = bubble_spacing
            self.bubbles = np.ones((len(area), 4))
            self.bubbles[:, 2] = r
            self.bubbles[:, 3] = area
            self.maxstep = 2 * self.bubbles[:, 2].max() + self.bubble_spacing
            self.step_dist = self.maxstep / 2

            # Calcular layout inicial em grade para as bolhas
            length = np.ceil(np.sqrt(len(self.bubbles)))
            grid = np.arange(length) * self.maxstep
            gx, gy = np.meshgrid(grid, grid)
            self.bubbles[:, 0] = gx.flatten()[:len(self.bubbles)]
            self.bubbles[:, 1] = gy.flatten()[:len(self.bubbles)]

            self.com = self.center_of_mass()

        def center_of_mass(self):
            return np.average(
                self.bubbles[:, :2], axis=0, weights=self.bubbles[:, 3]
            )

        def center_distance(self, bubble, bubbles):
            return np.hypot(bubble[0] - bubbles[:, 0],
                            bubble[1] - bubbles[:, 1])

        def outline_distance(self, bubble, bubbles):
            center_distance = self.center_distance(bubble, bubbles)
            return center_distance - bubble[2] - \
                bubbles[:, 2] - self.bubble_spacing

        def check_collisions(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return len(distance[distance < 0])

        def collides_with(self, bubble, bubbles):
            distance = self.outline_distance(bubble, bubbles)
            return np.argmin(distance, keepdims=True)

        def collapse(self, n_iterations=50):
            """
            Mover bolhas para o centro de massa.
            
            Parameters
            ----------
            n_iterations : int, default: 50
                Número de movimentos a realizar.
            """
            for _i in range(n_iterations):
                moves = 0
                for i in range(len(self.bubbles)):
                    rest_bub = np.delete(self.bubbles, i, 0)
                    # Tentar mover diretamente em direção ao centro de massa
                    # Vetor direção da bolha para o centro de massa
                    dir_vec = self.com - self.bubbles[i, :2]

                    # Encurtar vetor direção para ter comprimento 1
                    norm = np.sqrt(dir_vec.dot(dir_vec))
                    if norm > 0:
                        dir_vec = dir_vec / norm
                    else:
                        continue  # Pular se já está no centro de massa

                    # Calcular nova posição da bolha
                    new_point = self.bubbles[i, :2] + dir_vec * self.step_dist
                    new_bubble = np.append(new_point, self.bubbles[i, 2:4])

                    # Verificar se nova bolha colide com outras bolhas
                    if not self.check_collisions(new_bubble, rest_bub):
                        self.bubbles[i, :] = new_bubble
                        self.com = self.center_of_mass()
                        moves += 1
                    else:
                        # Tentar mover ao redor de uma bolha com a qual colide
                        # Encontrar bolha colidindo
                        for colliding in self.collides_with(new_bubble, rest_bub):
                            # Calcular vetor direção
                            dir_vec = rest_bub[colliding, :2] - self.bubbles[i, :2]
                            norm = np.sqrt(dir_vec.dot(dir_vec))
                            if norm == 0:
                                continue
                            dir_vec = dir_vec / norm
                            # Calcular vetor ortogonal
                            orth = np.array([dir_vec[1], -dir_vec[0]])
                            # Testar qual direção seguir
                            new_point1 = (self.bubbles[i, :2] + orth *
                                          self.step_dist)
                            new_point2 = (self.bubbles[i, :2] - orth *
                                          self.step_dist)
                            dist1 = self.center_distance(
                                self.com, np.array([new_point1]))
                            dist2 = self.center_distance(
                                self.com, np.array([new_point2]))
                            new_point = new_point1 if dist1 < dist2 else new_point2
                            new_bubble = np.append(new_point, self.bubbles[i, 2:4])
                            if not self.check_collisions(new_bubble, rest_bub):
                                self.bubbles[i, :] = new_bubble
                                self.com = self.center_of_mass()

                if moves / len(self.bubbles) < 0.1:
                    self.step_dist = self.step_dist / 2

        def get_positions(self):
            """Retorna as posições das bolhas no formato esperado."""
            return [(bubble[0], bubble[1]) for bubble in self.bubbles]

    def _pack_bubbles(self, sizes):
        """Algoritmo de bubble packing usando a classe BubbleChart com normalização."""
        import numpy as np
        
        if len(sizes) == 0:
            return []
        
        # CORREÇÃO 1: Normalizar os tamanhos para evitar bolhas muito grandes
        sizes_array = np.array(sizes)
        # Normalizar para que a maior bolha tenha área 100 (raio ~5.6)
        max_area = 100
        normalized_sizes = (sizes_array / sizes_array.max()) * max_area
        
        # Usar os gastos normalizados como área das bolhas
        bubble_chart = self.BubbleChart(area=normalized_sizes, bubble_spacing=0)
        
        # Executar algoritmo de colapso para empacotamento
        bubble_chart.collapse(n_iterations=50)  # 50 iterações são suficientes
        
        positions = bubble_chart.get_positions()
        
        # CORREÇÃO 2: Normalizar posições para uma escala adequada para o Plotly
        if len(positions) > 0:
            positions_array = np.array(positions)
            
            # Centralizar em (0, 0)
            center_x = np.mean(positions_array[:, 0])
            center_y = np.mean(positions_array[:, 1])
            positions_array[:, 0] -= center_x
            positions_array[:, 1] -= center_y
            
            # Escalar para que o conjunto caiba em um espaço razoável (-10 a 10)
            max_coord = max(np.max(np.abs(positions_array[:, 0])), 
                           np.max(np.abs(positions_array[:, 1])))
            if max_coord > 0:
                scale_factor = 8.0 / max_coord  # Escala para caber em [-8, 8]
                positions_array *= scale_factor
            
            positions = [(x, y) for x, y in positions_array]
        
        return positions
    
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
