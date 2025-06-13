import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Qt

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
        main_layout.setContentsMargins(20, 70, 20, 20)
        main_layout.setSpacing(15)

        # Título que informa o ano selecionado
        self.title_label = QLabel("Selecione um ano para visualizar os dados")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0; padding: 10px;")
        main_layout.addWidget(self.title_label)
        
        # --- Grade para os Gráficos ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        main_layout.addLayout(self.grid_layout)

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
                self.gdf = gpd.read_file(self.shapefile_path)
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
            # Aqui poderíamos mostrar gráficos agregados de todos os anos
            # Por enquanto, mostraremos uma mensagem
            placeholder = QLabel("Visualizações de dados agregados ainda não implementadas.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 2)
            self.graph_widgets.append(placeholder)
            return

        if self.df.empty:
            self.title_label.setText(f"Dados para {year}")
            placeholder = QLabel("Não foi possível carregar os dados para gerar os gráficos.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 2)
            self.graph_widgets.append(placeholder)
            return

        self.title_label.setText(f"Análise de Dados para o Ano de {year}")
        
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

    def _create_matplotlib_widget(self, fig: Figure) -> QWidget:
        """Cria um widget QCanvas a partir de uma figura Matplotlib."""
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #3c3c3c; border-radius: 10px;")
        # Forçar um fundo transparente para a figura para que o estilo do canvas apareça
        fig.patch.set_facecolor('none')
        return canvas

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
            wedges, texts, autotexts = ax.pie(
                gastos_setor, 
                autopct='%1.1f%%', 
                startangle=90, 
                pctdistance=0.85,
                colors=plt.cm.Pastel2.colors
            )
            ax.legend(wedges, gastos_setor.index, title="Setores", loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1),
                      title_fontproperties={'weight': 'bold', 'size': 10},
                      facecolor='#424242', labelcolor='white')
            for text in texts:
                text.set_color('dimgrey')
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'Não há dados de gastos para este ano.', ha='center', va='center', color='white')


        ax.axis('equal')
        plt.tight_layout(rect=[0, 0, 0.8, 0.95])
        return self._create_matplotlib_widget(fig)
        
    def _create_bubble_chart(self, df_year: pd.DataFrame) -> QWidget:
        """Cria o gráfico de bolhas de IDH vs. Gasto."""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        fig.suptitle('Gasto Público vs. IDH por Estado', color='white', fontsize=14, fontweight='bold')

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

        state_data = df_year_copy.groupby('uf').agg(agg_dict).reset_index()

        if not state_data.empty:
            sizes = state_data['gasto_total'] * 10 

            scatter = ax.scatter(
                x=state_data['gasto_total'],
                y=state_data['idh'],
                s=sizes,
                alpha=0.7,
                c=state_data['idh'],
                cmap='viridis'
            )
            
            for i, row in state_data.iterrows():
                ax.text(row['gasto_total'], row['idh'], row['uf'], 
                        ha='center', va='center', fontsize=8, color='white', fontweight='bold')

            ax.set_xlabel('Gasto Total (em R$ Milhões)', color='white')
            ax.set_ylabel('IDH Médio', color='white')
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.tick_params(colors='white')
            
            ax.xaxis.set_major_formatter(lambda x, pos: f'R$ {x:.0f}M')

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Nível de IDH', color='white')
            cbar.ax.tick_params(colors='white')

        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        return self._create_matplotlib_widget(fig)
