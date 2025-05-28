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

warnings.filterwarnings('ignore')

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
        X_cols = ['despesa_educacao_per_capita', 'despesa_saude_per_capita', 
                  'despesa_assistencia_social_per_capita', 'despesa_infraestrutura_per_capita']
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
            'modelo': modelo
        }
        
        return modelo, r2, coeficientes
    
    def clustering_estados(self, n_clusters=4):
        """Clustering de estados baseado em IDH e despesas"""
        print(f"\n=== CLUSTERING DE ESTADOS (K={n_clusters}) ===")
        
        # Variáveis para clustering
        features = ['idh', 'despesa_total_per_capita', 'populacao']
        X = self.df[features]
        
        # Padronização
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Adicionar clusters ao dataframe
        self.df['cluster'] = clusters
        
        # Análise dos clusters
        cluster_stats = self.df.groupby('cluster').agg({
            'idh': ['mean', 'std', 'count'],
            'despesa_total_per_capita': ['mean', 'std'],
            'populacao': ['mean', 'std'],
            'estado': lambda x: list(x.unique())
        }).round(3)
        
        print("Características dos clusters:")
        for i in range(n_clusters):
            cluster_data = self.df[self.df['cluster'] == i]
            print(f"\nCluster {i} ({len(cluster_data)} registros):")
            print(f"  IDH médio: {cluster_data['idh'].mean():.3f}")
            print(f"  Despesa per capita média: R$ {cluster_data['despesa_total_per_capita'].mean():.2f}")
            print(f"  Estados: {', '.join(cluster_data['estado'].unique()[:5])}...")
        
        self.resultados['clustering'] = {
            'n_clusters': n_clusters,
            'cluster_stats': cluster_stats,
            'scaler': scaler,
            'kmeans': kmeans
        }
        
        return clusters, cluster_stats
    
    def testes_hipoteses(self):
        """Testes de hipóteses estatísticas"""
        print("\n=== TESTES DE HIPÓTESES ===")
        
        # 1. Teste de normalidade para IDH
        stat_norm, p_norm = normaltest(self.df['idh'])
        print(f"Teste de normalidade IDH: p-value = {p_norm:.3f}")
        print(f"  IDH {'segue' if p_norm > 0.05 else 'NÃO segue'} distribuição normal")
        
        # 2. Comparação IDH entre regiões (ANOVA)
        regioes = self.df['regiao'].unique()
        grupos_idh = [self.df[self.df['regiao'] == regiao]['idh'] for regiao in regioes]
        
        f_stat, p_anova = stats.f_oneway(*grupos_idh)
        print(f"\nANOVA - IDH entre regiões: F={f_stat:.3f}, p-value={p_anova:.3f}")
        print(f"  {'Há' if p_anova < 0.05 else 'NÃO há'} diferença significativa entre regiões")
        
        # 3. Teste de Levene (homogeneidade de variâncias)
        levene_stat, p_levene = levene(*grupos_idh)
        print(f"Teste de Levene: p-value = {p_levene:.3f}")
        print(f"  Variâncias {'são' if p_levene > 0.05 else 'NÃO são'} homogêneas")
        
        # 4. Comparação específica: Sul vs Nordeste
        idh_sul = self.df[self.df['regiao'] == 'Sul']['idh']
        idh_nordeste = self.df[self.df['regiao'] == 'Nordeste']['idh']
        
        t_stat, p_ttest = ttest_ind(idh_sul, idh_nordeste)
        print(f"\nTeste t - Sul vs Nordeste: t={t_stat:.3f}, p-value={p_ttest:.3f}")
        print(f"  Diferença {'é' if p_ttest < 0.05 else 'NÃO é'} estatisticamente significativa")
        
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
        
        # Calcular tendências por estado
        tendencias_estados = {}
        
        for estado in self.df['estado'].unique():
            dados_estado = self.df[self.df['estado'] == estado].sort_values('ano')
            
            if len(dados_estado) >= 3:  # Mínimo 3 pontos para tendência
                anos = dados_estado['ano'].values
                idh_values = dados_estado['idh'].values
                
                # Regressão linear simples
                slope, intercept, r_value, p_value, std_err = stats.linregress(anos, idh_values)
                
                tendencias_estados[estado] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'tendencia': 'crescente' if slope > 0 else 'decrescente',
                    'significativa': p_value < 0.05
                }
        
        # Ordenar por slope (maior crescimento)
        tendencias_df = pd.DataFrame(tendencias_estados).T
        tendencias_df = tendencias_df.sort_values('slope', ascending=False)
        
        print("Top 5 estados com maior crescimento do IDH:")
        for i, (estado, dados) in enumerate(tendencias_df.head().iterrows(), 1):
            print(f"  {i}. {estado}: {dados['slope']:.4f}/ano (R²={dados['r_squared']:.3f})")
        
        print("\nTop 5 estados com menor crescimento do IDH:")
        for i, (estado, dados) in enumerate(tendencias_df.tail().iterrows(), 1):
            print(f"  {i}. {estado}: {dados['slope']:.4f}/ano (R²={dados['r_squared']:.3f})")
        
        self.resultados['series_temporais'] = {
            'tendencias_estados': tendencias_estados,
            'ranking_crescimento': tendencias_df.to_dict('index')
        }
        
        return tendencias_estados, tendencias_df
    
    def analise_eficiencia_detalhada(self):
        """Análise detalhada de eficiência por categoria"""
        print("\n=== ANÁLISE DE EFICIÊNCIA DETALHADA ===")
        
        # Calcular eficiências específicas
        self.df['eficiencia_educacao'] = self.df['idh_educacao'] / self.df['despesa_educacao_per_capita'] * 1000
        self.df['eficiencia_saude'] = self.df['idh_longevidade'] / self.df['despesa_saude_per_capita'] * 1000
        self.df['eficiencia_renda'] = self.df['idh_renda'] / self.df['despesa_total_per_capita'] * 1000
        
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
        for i, (estado, eff) in enumerate(top_educacao.items(), 1):
            print(f"  {i}. {estado}: {eff:.2f}")
        
        print("\nTop 5 - Eficiência Saúde:")
        for i, (estado, eff) in enumerate(top_saude.items(), 1):
            print(f"  {i}. {estado}: {eff:.2f}")
        
        print("\nTop 5 - Eficiência Renda:")
        for i, (estado, eff) in enumerate(top_renda.items(), 1):
            print(f"  {i}. {estado}: {eff:.2f}")
        
        self.resultados['eficiencia_detalhada'] = {
            'por_regiao': eficiencia_regiao,
            'top_educacao': top_educacao.to_dict(),
            'top_saude': top_saude.to_dict(),
            'top_renda': top_renda.to_dict()
        }
        
        return eficiencia_regiao, top_educacao, top_saude, top_renda
    
    def gerar_visualizacoes_avancadas(self):
        """Gera visualizações das análises avançadas"""
        print("\n=== GERANDO VISUALIZAÇÕES AVANÇADAS ===")
        
        import os
        os.makedirs('results/fase2/graficos_avancados', exist_ok=True)
        
        # 1. Clustering Scatter Plot
        if 'clustering' in self.resultados:
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(self.df['despesa_total_per_capita'], self.df['idh'], 
                                c=self.df['cluster'], cmap='Set1', alpha=0.7, s=80)
            plt.colorbar(scatter, label='Cluster')
            plt.xlabel('Despesa Total Per Capita (R$)')
            plt.ylabel('IDH')
            plt.title('Clustering de Estados: IDH vs Despesas Per Capita')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('results/fase2/graficos_avancados/clustering_estados.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Tendências Temporais por Estado (amostra)
        if 'series_temporais' in self.resultados:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            axes = axes.flatten()
            
            # Selecionar 4 estados representativos
            estados_exemplo = ['São Paulo', 'Amazonas', 'Ceará', 'Rio Grande do Sul']
            
            for i, estado in enumerate(estados_exemplo):
                if estado in self.df['estado'].values:
                    dados_estado = self.df[self.df['estado'] == estado].sort_values('ano')
                    axes[i].plot(dados_estado['ano'], dados_estado['idh'], marker='o', linewidth=2)
                    axes[i].set_title(f'Evolução IDH - {estado}')
                    axes[i].set_ylabel('IDH')
                    axes[i].grid(True, alpha=0.3)
                    
                    # Linha de tendência
                    z = np.polyfit(dados_estado['ano'], dados_estado['idh'], 1)
                    p = np.poly1d(z)
                    axes[i].plot(dados_estado['ano'], p(dados_estado['ano']), "r--", alpha=0.8)
            
            plt.tight_layout()
            plt.savefig('results/fase2/graficos_avancados/tendencias_temporais.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Eficiência por Categoria
        if 'eficiencia_detalhada' in self.resultados:
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
            
            # Top 10 por categoria
            top_ed = pd.Series(self.resultados['eficiencia_detalhada']['top_educacao']).head(10)
            top_sa = pd.Series(self.resultados['eficiencia_detalhada']['top_saude']).head(10)
            top_re = pd.Series(self.resultados['eficiencia_detalhada']['top_renda']).head(10)
            
            ax1.barh(range(len(top_ed)), top_ed.values)
            ax1.set_yticks(range(len(top_ed)))
            ax1.set_yticklabels(top_ed.index, fontsize=8)
            ax1.set_title('Top 10 - Eficiência Educação')
            ax1.invert_yaxis()
            
            ax2.barh(range(len(top_sa)), top_sa.values)
            ax2.set_yticks(range(len(top_sa)))
            ax2.set_yticklabels(top_sa.index, fontsize=8)
            ax2.set_title('Top 10 - Eficiência Saúde')
            ax2.invert_yaxis()
            
            ax3.barh(range(len(top_re)), top_re.values)
            ax3.set_yticks(range(len(top_re)))
            ax3.set_yticklabels(top_re.index, fontsize=8)
            ax3.set_title('Top 10 - Eficiência Renda')
            ax3.invert_yaxis()
            
            plt.tight_layout()
            plt.savefig('results/fase2/graficos_avancados/eficiencia_categorias.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print("Visualizações avançadas salvas em results/fase2/graficos_avancados/")
    
    def executar_analises_completas(self):
        """Executa todas as análises avançadas"""
        print("INICIANDO ANÁLISES ESTATÍSTICAS AVANÇADAS")
        print("=" * 50)
        
        # Executar análises
        self.analise_regressao_multipla()
        self.clustering_estados()
        self.testes_hipoteses()
        self.analise_series_temporais()
        self.analise_eficiencia_detalhada()
        self.gerar_visualizacoes_avancadas()
        
        # Salvar resultados
        import json
        with open('results/fase2/analises_avancadas.json', 'w', encoding='utf-8') as f:
            # Converter objetos não serializáveis
            resultados_serializaveis = {}
            for key, value in self.resultados.items():
                if key in ['regressao', 'clustering']:
                    # Remover objetos sklearn que não são serializáveis
                    value_copy = value.copy()
                    if 'modelo' in value_copy:
                        del value_copy['modelo']
                    if 'scaler' in value_copy:
                        del value_copy['scaler']
                    if 'kmeans' in value_copy:
                        del value_copy['kmeans']
                    resultados_serializaveis[key] = value_copy
                else:
                    resultados_serializaveis[key] = value
            
            json.dump(resultados_serializaveis, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n" + "=" * 50)
        print("ANÁLISES AVANÇADAS CONCLUÍDAS!")
        print("=" * 50)
        print("Resultados salvos em results/fase2/analises_avancadas.json")
        
        return self.resultados

def main():
    """Função principal para executar análises avançadas"""
    try:
        # Carregar dados
        df = pd.read_csv('data/processed/dataset_unificado.csv')
        
        # Executar análises
        analisador = AnalisesAvancadas(df)
        resultados = analisador.executar_analises_completas()
        
        return resultados
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 