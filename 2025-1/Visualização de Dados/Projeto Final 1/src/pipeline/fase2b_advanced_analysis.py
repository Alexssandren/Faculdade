#!/usr/bin/env python3
"""
Módulo de Análises Estatísticas Avançadas
Complementa a Fase 2 com análises mais sofisticadas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats
from scipy.stats import normaltest, levene, ttest_ind
import warnings
import json
import os # Mudança: usar os para criar diretórios
from pathlib import Path

warnings.filterwarnings('ignore')

# Definição de caminhos relativos à raiz do projeto
SCRIPT_DIR = Path(__file__).resolve().parent # src/pipeline
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Caminho de entrada
UNIFIED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_unificado.csv"

# Caminho de saída para resultados desta fase
ADVANCED_RESULTS_DIR = PROJECT_ROOT / "results" / "advanced_analysis"
ADVANCED_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GRAFICOS_AVANCADOS_DIR = ADVANCED_RESULTS_DIR / "graficos"
GRAFICOS_AVANCADOS_DIR.mkdir(parents=True, exist_ok=True)

class AnalisesAvancadas:
    """Classe para análises estatísticas avançadas"""
    
    def __init__(self, df):
        """Inicializa com o dataset"""
        self.df = df.copy()
        self.resultados = {}
        
    def analise_regressao_multipla(self):
        """Análise de regressão múltipla: IDH vs múltiplas variáveis de despesa"""
        print("=== ANÁLISE DE REGRESSÃO MÚLTIPLA ===")
        
        # Variáveis independentes (despesas per capita)
        # Assegurar que as colunas existam no DataFrame
        X_cols_base = ['despesa_educacao_per_capita', 'despesa_saude_per_capita', 
                       'despesa_assistencia_social_per_capita', 'despesa_infraestrutura_per_capita']
        X_cols = [col for col in X_cols_base if col in self.df.columns]
        
        if not X_cols:
            print("⚠️ Nenhuma coluna de despesa per capita encontrada para regressão. Abortando.")
            return None, None, None
            
        if 'idh' not in self.df.columns:
            print("⚠️ Coluna 'idh' não encontrada para regressão. Abortando.")
            return None, None, None

        X = self.df[X_cols]
        y = self.df['idh']
        
        # Modelo de regressão
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Predições
        y_pred = modelo.predict(X)
        r2 = r2_score(y, y_pred)
        
        # Coeficientes
        coeficientes = pd.DataFrame({
            'variavel': X_cols,
            'coeficiente': modelo.coef_,
            'abs_coeficiente': np.abs(modelo.coef_)
        }).sort_values('abs_coeficiente', ascending=False)
        
        print(f"R² do modelo: {r2:.3f}")
        print(f"Intercepto: {modelo.intercept_:.3f}")
        print("\nCoeficientes (ordenados por importância):")
        for _, row in coeficientes.iterrows():
            print(f"  {row['variavel']}: {row['coeficiente']:.6f}")
        
        self.resultados['regressao'] = {
            'r2': r2,
            'intercepto': modelo.intercept_,
            'coeficientes': coeficientes.to_dict('records'),
            # 'modelo': modelo # Não serializável para JSON, remover ou lidar com isso
        }
        
        return modelo, r2, coeficientes
    
    def clustering_estados(self, n_clusters=4):
        """Clustering de estados baseado em IDH e despesas"""
        print(f"\n=== CLUSTERING DE ESTADOS (K={n_clusters}) ===")
        
        features_base = ['idh', 'despesa_total_per_capita', 'populacao']
        features = [f for f in features_base if f in self.df.columns]

        if len(features) < 2:
            print(f"⚠️ Features insuficientes ({features}) para clustering. Abortando.")
            return None, None

        X = self.df[features].copy()
        X.fillna(X.mean(), inplace=True)
        if X.empty:
            print("⚠️ DataFrame vazio após seleção de features para clustering. Abortando.")
            return None, None

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        clusters = kmeans.fit_predict(X_scaled)
        
        self.df['cluster'] = clusters
        
        agg_dict = {}
        if 'idh' in self.df.columns: agg_dict['idh'] = ['mean', 'std', 'count']
        if 'despesa_total_per_capita' in self.df.columns: agg_dict['despesa_total_per_capita'] = ['mean', 'std']
        if 'populacao' in self.df.columns: agg_dict['populacao'] = ['mean', 'std']
        if 'estado' in self.df.columns: agg_dict['estado'] = lambda x: list(x.unique())
        
        if not agg_dict:
            print("⚠️ Nenhuma coluna válida para agregar estatísticas de cluster. Abortando.")
            self.resultados['clustering'] = {'n_clusters': n_clusters, 'cluster_stats': None}
            return clusters, None

        cluster_stats_df = self.df.groupby('cluster').agg(agg_dict).round(3)
        
        # Achatando colunas do cluster_stats_df se for MultiIndex
        if isinstance(cluster_stats_df.columns, pd.MultiIndex):
            cluster_stats_df.columns = ["_".join(map(str,col)).strip() for col in cluster_stats_df.columns.values]
        
        print("Características dos clusters:")
        for i in range(n_clusters):
            cluster_data = self.df[self.df['cluster'] == i]
            print(f"\nCluster {i} ({len(cluster_data)} registros):")
            if 'idh' in cluster_data: print(f"  IDH médio: {cluster_data['idh'].mean():.3f}")
            if 'despesa_total_per_capita' in cluster_data: print(f"  Despesa per capita média: R$ {cluster_data['despesa_total_per_capita'].mean():.2f}")
            if 'estado' in cluster_data: print(f"  Estados: {', '.join(cluster_data['estado'].unique()[:5])}...")
        
        self.resultados['clustering'] = {
            'n_clusters': n_clusters,
            'cluster_stats': cluster_stats_df.to_dict(orient='index') if not cluster_stats_df.empty else None,
        }
        
        return clusters, cluster_stats_df
    
    def _flatten_column_names(self, df_multi_index_cols):
        """Converte colunas MultiIndex em colunas de string única."""
        if isinstance(df_multi_index_cols.columns, pd.MultiIndex):
            df_multi_index_cols.columns = ["_".join(map(str, col)).strip() for col in df_multi_index_cols.columns.values]
        return df_multi_index_cols

    def _convert_dict_for_json(self, item):
        """Converte recursivamente um item para ser compatível com JSON."""
        if isinstance(item, dict):
            new_dict = {}
            for k, v in item.items():
                new_key = "_".join(map(str, k)) if isinstance(k, tuple) else str(k)
                new_dict[new_key] = self._convert_dict_for_json(v)
            return new_dict
        elif isinstance(item, list):
            return [self._convert_dict_for_json(i) for i in item]
        elif isinstance(item, (np.int_, np.intc, np.intp, np.int8,
                               np.int16, np.int32, np.int64, np.uint8,
                               np.uint16, np.uint32, np.uint64)):
            return int(item)
        elif isinstance(item, (np.float64, np.float16, np.float32, np.bool_)):
            return float(item) if isinstance(item, (np.float64, np.float16, np.float32)) else bool(item)
        elif isinstance(item, (np.ndarray,)):
            return item.tolist()
        elif isinstance(item, pd.Timestamp):
            return item.isoformat()
        elif pd.isna(item): # Tratar NaT ou NaN do pandas que podem não ser None
            return None 
        # Se for um DataFrame ou Series, converte para dicionário (pode precisar de mais lógica aqui)
        elif isinstance(item, (pd.DataFrame, pd.Series)):
            if isinstance(item, pd.DataFrame):
                # Achatamos as colunas se forem MultiIndex ANTES de to_dict
                item_processed = self._flatten_column_names(item.copy())
                return item_processed.to_dict(orient='index') # ou 'records' ou 'list' dependendo do desejado
            else: # Series
                return item.to_dict()
        return item

    def testes_hipoteses(self):
        """Testes de hipóteses estatísticas"""
        print("\n=== TESTES DE HIPÓTESES ===")
        
        if 'idh' not in self.df.columns or 'regiao' not in self.df.columns:
            print("⚠️ Colunas 'idh' ou 'regiao' não encontradas. Testes de hipóteses não podem ser executados.")
            self.resultados['testes_hipoteses'] = None
            return None

        # 1. Teste de normalidade para IDH
        stat_norm, p_norm = normaltest(self.df['idh'].dropna())
        print(f"Teste de normalidade IDH: p-value = {p_norm:.3f}")
        print(f"  IDH {'segue' if p_norm > 0.05 else 'NÃO segue'} distribuição normal")
        
        # 2. Comparação IDH entre regiões (ANOVA)
        regioes = self.df['regiao'].dropna().unique()
        grupos_idh = [self.df[self.df['regiao'] == regiao]['idh'].dropna() for regiao in regioes]
        grupos_idh = [g for g in grupos_idh if len(g) > 1] # ANOVA precisa de grupos com mais de 1 elemento

        if len(grupos_idh) < 2:
            print("⚠️ Menos de dois grupos válidos para ANOVA. Abortando teste ANOVA.")
            p_anova = None
            f_stat = None
        else:
            f_stat, p_anova = stats.f_oneway(*grupos_idh)
            print(f"\nANOVA - IDH entre regiões: F={f_stat:.3f}, p-value={p_anova:.3f}")
            print(f"  {'Há' if p_anova is not None and p_anova < 0.05 else 'NÃO há'} diferença significativa entre regiões")
        
        # 3. Teste de Levene (homogeneidade de variâncias)
        if len(grupos_idh) < 2:
            print("⚠️ Menos de dois grupos válidos para Teste de Levene. Abortando.")
            p_levene = None
            levene_stat = None
        else:
            levene_stat, p_levene = levene(*grupos_idh)
            print(f"Teste de Levene: p-value = {p_levene:.3f}")
            print(f"  Variâncias {'são' if p_levene is not None and p_levene > 0.05 else 'NÃO são'} homogêneas")
        
        # 4. Comparação específica: Sul vs Nordeste
        idh_sul = self.df[(self.df['regiao'] == 'Sul') & self.df['idh'].notna()]['idh']
        idh_nordeste = self.df[(self.df['regiao'] == 'Nordeste') & self.df['idh'].notna()]['idh']
        
        if len(idh_sul) < 2 or len(idh_nordeste) < 2:
            print("⚠️ Dados insuficientes para teste t entre Sul e Nordeste. Abortando.")
            p_ttest = None
            t_stat = None
        else:
            t_stat, p_ttest = ttest_ind(idh_sul, idh_nordeste)
            print(f"\nTeste t - Sul vs Nordeste: t={t_stat:.3f}, p-value={p_ttest:.3f}")
            print(f"  Diferença {'é' if p_ttest is not None and p_ttest < 0.05 else 'NÃO é'} estatisticamente significativa")
        
        self.resultados['testes_hipoteses'] = {
            'normalidade_idh': {'estatistica': stat_norm, 'p_value': p_norm},
            'anova_regioes': {'f_estatistica': f_stat, 'p_value': p_anova},
            'levene': {'estatistica': levene_stat, 'p_value': p_levene},
            'ttest_sul_nordeste': {'t_estatistica': t_stat, 'p_value': p_ttest}
        }
        
        return self.resultados['testes_hipoteses']
    
    def analise_series_temporais(self):
        """Análise de séries temporais por estado"""
        print("\n=== ANÁLISE DE SÉRIES TEMPORAIS ===")
        
        if 'estado' not in self.df.columns or 'ano' not in self.df.columns or 'idh' not in self.df.columns:
            print("⚠️ Colunas 'estado', 'ano' ou 'idh' não encontradas. Análise de séries temporais não pode ser executada.")
            self.resultados['series_temporais'] = None
            return None, None

        tendencias_estados = {}
        
        for estado_val in self.df['estado'].dropna().unique():
            dados_estado = self.df[(self.df['estado'] == estado_val) & self.df['idh'].notna() & self.df['ano'].notna()].sort_values('ano')
            
            if len(dados_estado) >= 3:  # Mínimo 3 pontos para tendência
                anos = dados_estado['ano'].values
                idh_values = dados_estado['idh'].values
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(anos, idh_values)
                
                tendencias_estados[estado_val] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'tendencia': 'crescente' if slope > 0 else 'decrescente',
                    'significativa': p_value < 0.05
                }
        
        if not tendencias_estados:
            print("⚠️ Nenhuma tendência temporal pôde ser calculada.")
            self.resultados['series_temporais'] = None
            return None, None

        tendencias_df = pd.DataFrame(tendencias_estados).T
        tendencias_df = tendencias_df.sort_values('slope', ascending=False)
        
        print("Top 5 estados com maior crescimento do IDH:")
        for i, (est, dados) in enumerate(tendencias_df.head().iterrows(), 1):
            print(f"  {i}. {est}: {dados['slope']:.4f}/ano (R²={dados['r_squared']:.3f})")
        
        print("\nTop 5 estados com menor crescimento do IDH:")
        for i, (est, dados) in enumerate(tendencias_df.tail().iterrows(), 1):
            print(f"  {i}. {est}: {dados['slope']:.4f}/ano (R²={dados['r_squared']:.3f})")
        
        self.resultados['series_temporais'] = {
            'tendencias_estados': tendencias_estados,
            'ranking_crescimento': tendencias_df.to_dict('index')
        }
        
        return tendencias_estados, tendencias_df
    
    def analise_eficiencia_detalhada(self):
        """Análise detalhada de eficiência por categoria"""
        print("\n=== ANÁLISE DE EFICIÊNCIA DETALHADA ===")
        
        required_cols = [
            'idh_educacao', 'despesa_educacao_per_capita',
            'idh_longevidade', 'despesa_saude_per_capita',
            'idh_renda', 'despesa_total_per_capita', 'regiao', 'estado'
        ]
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            print(f"⚠️ Colunas ausentes para análise de eficiência: {missing_cols}. Abortando.")
            self.resultados['eficiencia_detalhada'] = None
            return None, None, None, None

        # Calcular eficiências específicas, tratando divisão por zero
        self.df['eficiencia_educacao'] = np.where(self.df['despesa_educacao_per_capita'] != 0, (self.df['idh_educacao'] / self.df['despesa_educacao_per_capita']) * 1000, 0)
        self.df['eficiencia_saude'] = np.where(self.df['despesa_saude_per_capita'] != 0, (self.df['idh_longevidade'] / self.df['despesa_saude_per_capita']) * 1000, 0)
        self.df['eficiencia_renda'] = np.where(self.df['despesa_total_per_capita'] != 0, (self.df['idh_renda'] / self.df['despesa_total_per_capita']) * 1000, 0)
        
        # Análise por região
        eficiencia_regiao = self.df.groupby('regiao').agg({
            'eficiencia_educacao': ['mean', 'std'],
            'eficiencia_saude': ['mean', 'std'],
            'eficiencia_renda': ['mean', 'std']
        }).round(3)
        
        # Estados mais eficientes por categoria
        top_educacao = self.df.groupby('estado')['eficiencia_educacao'].mean().sort_values(ascending=False).head()
        top_saude = self.df.groupby('estado')['eficiencia_saude'].mean().sort_values(ascending=False).head()
        top_renda = self.df.groupby('estado')['eficiencia_renda'].mean().sort_values(ascending=False).head()
        
        print("Top 5 - Eficiência Educação:")
        for i, (est, eff) in enumerate(top_educacao.items(), 1):
            print(f"  {i}. {est}: {eff:.2f}")
        
        print("\nTop 5 - Eficiência Saúde:")
        for i, (est, eff) in enumerate(top_saude.items(), 1):
            print(f"  {i}. {est}: {eff:.2f}")
        
        print("\nTop 5 - Eficiência Renda:")
        for i, (est, eff) in enumerate(top_renda.items(), 1):
            print(f"  {i}. {est}: {eff:.2f}")
        
        self.resultados['eficiencia_detalhada'] = {
            'por_regiao': eficiencia_regiao.to_dict(),
            'top_educacao': top_educacao.to_dict(),
            'top_saude': top_saude.to_dict(),
            'top_renda': top_renda.to_dict()
        }
        
        return eficiencia_regiao, top_educacao, top_saude, top_renda
    
    def gerar_visualizacoes_avancadas(self):
        """Gera visualizações das análises avançadas"""
        print("\n=== GERANDO VISUALIZAÇÕES AVANÇADAS ===")
        
        # 1. Clustering Scatter Plot
        if 'clustering' in self.resultados and self.resultados['clustering'] and 'cluster_stats' in self.resultados['clustering'] and self.resultados['clustering']['cluster_stats'] is not None and 'cluster' in self.df.columns:
            # Verificar se as colunas necessárias para o plot existem
            if 'despesa_total_per_capita' in self.df.columns and 'idh' in self.df.columns:
                plt.figure(figsize=(12, 8))
                scatter = plt.scatter(self.df['despesa_total_per_capita'], self.df['idh'], 
                                    c=self.df['cluster'], cmap='Set1', alpha=0.7, s=80)
                plt.colorbar(scatter, label='Cluster')
                plt.xlabel('Despesa Total Per Capita (R$)')
                plt.ylabel('IDH')
                plt.title('Clustering de Estados: IDH vs Despesas Per Capita')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(GRAFICOS_AVANCADOS_DIR / 'clustering_estados.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico de clustering salvo em: {GRAFICOS_AVANCADOS_DIR / 'clustering_estados.png'}")
            else:
                print("⚠️ Colunas 'despesa_total_per_capita' ou 'idh' ausentes para o gráfico de clustering.")
        else:
            print("⚠️ Resultados de clustering não disponíveis ou incompletos para gerar visualização.")

        # 2. Tendências Temporais por Estado (amostra)
        if 'series_temporais' in self.resultados and self.resultados['series_temporais'] and 'estado' in self.df.columns and 'ano' in self.df.columns and 'idh' in self.df.columns:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            axes = axes.flatten()
            
            estados_exemplo = ['São Paulo', 'Amazonas', 'Ceará', 'Rio Grande do Sul']
            estados_plotados = 0
            for i, estado_val in enumerate(estados_exemplo):
                if estado_val in self.df['estado'].unique():
                    if estados_plotados < len(axes):
                        dados_estado = self.df[(self.df['estado'] == estado_val) & self.df['idh'].notna()].sort_values('ano')
                        if len(dados_estado) >= 2:
                            axes[estados_plotados].plot(dados_estado['ano'], dados_estado['idh'], marker='o', linewidth=2)
                            axes[estados_plotados].set_title(f'Evolução IDH - {estado_val}')
                            axes[estados_plotados].set_ylabel('IDH')
                            axes[estados_plotados].grid(True, alpha=0.3)
                            
                            if len(dados_estado) >= 2: # Polyfit precisa de pelo menos 2 pontos
                                z = np.polyfit(dados_estado['ano'], dados_estado['idh'], 1)
                                p = np.poly1d(z)
                                axes[estados_plotados].plot(dados_estado['ano'], p(dados_estado['ano']), "r--", alpha=0.8)
                            estados_plotados += 1
            
            if estados_plotados > 0:
                plt.tight_layout()
                plt.savefig(GRAFICOS_AVANCADOS_DIR / 'tendencias_temporais.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico de tendências temporais salvo em: {GRAFICOS_AVANCADOS_DIR / 'tendencias_temporais.png'}")
            else:
                print("⚠️ Nenhum estado de exemplo com dados suficientes para plotar tendências temporais.")
        else:
            print("⚠️ Resultados de séries temporais ou colunas necessárias não disponíveis para gerar visualização.")

        # 3. Eficiência por Categoria
        if 'eficiencia_detalhada' in self.resultados and self.resultados['eficiencia_detalhada']:
            try:
                fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
                
                top_ed = pd.Series(self.resultados['eficiencia_detalhada'].get('top_educacao', {})).sort_values(ascending=False).head(10)
                top_sa = pd.Series(self.resultados['eficiencia_detalhada'].get('top_saude', {})).sort_values(ascending=False).head(10)
                top_re = pd.Series(self.resultados['eficiencia_detalhada'].get('top_renda', {})).sort_values(ascending=False).head(10)
                
                if not top_ed.empty:
                    ax1.barh(top_ed.index, top_ed.values)
                    ax1.set_title('Top 10 - Eficiência Educação')
                    ax1.invert_yaxis()
                else: ax1.text(0.5, 0.5, 'Dados Indisponíveis', ha='center', va='center', transform=ax1.transAxes)

                if not top_sa.empty:
                    ax2.barh(top_sa.index, top_sa.values)
                    ax2.set_title('Top 10 - Eficiência Saúde')
                    ax2.invert_yaxis()
                else: ax2.text(0.5, 0.5, 'Dados Indisponíveis', ha='center', va='center', transform=ax2.transAxes)
                
                if not top_re.empty:
                    ax3.barh(top_re.index, top_re.values)
                    ax3.set_title('Top 10 - Eficiência Renda')
                    ax3.invert_yaxis()
                else: ax3.text(0.5, 0.5, 'Dados Indisponíveis', ha='center', va='center', transform=ax3.transAxes)
                
                plt.tight_layout()
                plt.savefig(GRAFICOS_AVANCADOS_DIR / 'eficiencia_categorias.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Gráfico de eficiência por categorias salvo em: {GRAFICOS_AVANCADOS_DIR / 'eficiencia_categorias.png'}")
            except Exception as e_eff_plot:
                print(f"⚠️ Erro ao gerar gráfico de eficiência: {e_eff_plot}")
        else:
            print("⚠️ Resultados de eficiência detalhada não disponíveis para gerar visualização.")
        
        print(f"Visualizações avançadas salvas em: {GRAFICOS_AVANCADOS_DIR.relative_to(PROJECT_ROOT)}")
    
    def executar_analises_completas(self):
        """Executa todas as análises avançadas"""
        print("INICIANDO ANÁLISES ESTATÍSTICAS AVANÇADAS")
        print("=" * 50)
        
        self.analise_regressao_multipla()
        self.clustering_estados()
        self.testes_hipoteses()
        self.analise_series_temporais()
        self.analise_eficiencia_detalhada()
        self.gerar_visualizacoes_avancadas()
        
        output_path = ADVANCED_RESULTS_DIR / "analises_avancadas.json"
        try:
            # Converter todo o dicionário de resultados para ser compatível com JSON
            resultados_serializaveis = self._convert_dict_for_json(self.resultados)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resultados_serializaveis, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Resultados JSON salvos em: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados JSON: {e}")
            import traceback
            print(traceback.format_exc())
        
        print("\n" + "=" * 50)
        print("ANÁLISES AVANÇADAS CONCLUÍDAS!")
        print("=" * 50)
        
        return self.resultados

def main():
    """Função principal para executar análises avançadas"""
    print(f"🚀 Iniciando script de Análises Avançadas...")
    print(f"🔄 Carregando dados de: {UNIFIED_DATASET_PATH}")
    
    if not UNIFIED_DATASET_PATH.exists():
        print(f"❌ ERRO: Dataset unificado {UNIFIED_DATASET_PATH} não encontrado. "
              f"Execute a fase de processamento de dados (DataCleaner) primeiro.")
        return None
    try:
        df = pd.read_csv(UNIFIED_DATASET_PATH)
        if df.empty:
            print("❌ ERRO: Dataset unificado está vazio.")
            return None
        
        print(f"✅ Dataset carregado com {len(df)} linhas.")
        
        analisador = AnalisesAvancadas(df)
        resultados = analisador.executar_analises_completas()
        
        return resultados
        
    except Exception as e:
        print(f"❌ ERRO FATAL no script de análises avançadas: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 