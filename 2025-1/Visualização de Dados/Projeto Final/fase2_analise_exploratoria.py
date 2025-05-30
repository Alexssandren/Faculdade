import pandas as pd
import numpy as np
import os
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd

# Diretórios
RAW_DIR = Path('data/raw')
PROC_DIR = Path('data/processed')
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Arquivos de entrada
IDH_FILE = RAW_DIR / 'idh_oficial_real.csv'
DESPESAS_FILE = RAW_DIR / 'despesas_publicas_oficiais_real.csv'

# Carregar dados
print('🔄 Carregando dados...')
df_idh = pd.read_csv(IDH_FILE)
df_desp = pd.read_csv(DESPESAS_FILE)

# --- 2.1. Análise Descritiva ---
print('📊 Análise descritiva...')
# Estatísticas IDH
desc_idh = df_idh.describe(include='all')
desc_idh.to_csv(PROC_DIR / 'estatisticas_idh.csv')
# Estatísticas Despesas
desc_desp = df_desp.describe(include='all')
desc_desp.to_csv(PROC_DIR / 'estatisticas_despesas.csv')

# Outliers (z-score > 3)
def detectar_outliers(df, col):
    z = (df[col] - df[col].mean()) / df[col].std()
    return df[np.abs(z) > 3]

outliers_idh = detectar_outliers(df_idh, 'idh')
outliers_idh.to_csv(PROC_DIR / 'outliers_idh.csv', index=False)
outliers_desp = detectar_outliers(df_desp, 'valor_pago')
outliers_desp.to_csv(PROC_DIR / 'outliers_despesas.csv', index=False)

# --- 2.2. Análise de Correlações ---
print('🔗 Análise de correlações...')
# Preparar dados agregados para correlação
# Gastos totais por estado/ano/categoria
df_gastos = df_desp.groupby(['ano', 'uf', 'categoria'], as_index=False)['valor_pago'].sum()
# Gastos per capita
pop = df_idh[['ano', 'uf', 'populacao']].drop_duplicates()
df_gastos = df_gastos.merge(pop, on=['ano', 'uf'], how='left')
df_gastos['valor_per_capita'] = df_gastos['valor_pago'] / df_gastos['populacao']
# Pivotar para facilitar correlação
pivot_gastos = df_gastos.pivot_table(index=['ano', 'uf'], columns='categoria', values='valor_per_capita').reset_index()
df_idh_ano_uf = df_idh.groupby(['ano', 'uf'], as_index=False)['idh'].mean()
df_corr = df_idh_ano_uf.merge(pivot_gastos, on=['ano', 'uf'])
# Correlação por categoria
correlacoes = {}
for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
    if cat in df_corr:
        correlacoes[cat] = {
            'pearson': df_corr['idh'].corr(df_corr[cat], method='pearson'),
            'spearman': df_corr['idh'].corr(df_corr[cat], method='spearman')
        }
pd.DataFrame(correlacoes).to_csv(PROC_DIR / 'correlacoes_por_categoria.csv')
# Correlação por ano
correlacoes_ano = []
for ano in sorted(df_corr['ano'].unique()):
    linha = {'ano': ano}
    for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
        if cat in df_corr:
            sub = df_corr[df_corr['ano'] == ano]
            linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
            linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
    correlacoes_ano.append(linha)
pd.DataFrame(correlacoes_ano).to_csv(PROC_DIR / 'correlacoes_por_ano.csv', index=False)
# Correlação por estado
correlacoes_estado = []
for uf in sorted(df_corr['uf'].unique()):
    linha = {'uf': uf}
    for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
        if cat in df_corr:
            sub = df_corr[df_corr['uf'] == uf]
            linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
            linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
    correlacoes_estado.append(linha)
pd.DataFrame(correlacoes_estado).to_csv(PROC_DIR / 'correlacoes_por_estado.csv', index=False)
# Correlação por região
regioes = df_idh[['uf', 'regiao']].drop_duplicates()
df_corr = df_corr.merge(regioes, on='uf', how='left')
correlacoes_regiao = []
for reg in sorted(df_corr['regiao'].unique()):
    linha = {'regiao': reg}
    for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
        if cat in df_corr:
            sub = df_corr[df_corr['regiao'] == reg]
            linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
            linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
    correlacoes_regiao.append(linha)
pd.DataFrame(correlacoes_regiao).to_csv(PROC_DIR / 'correlacoes_por_regiao.csv', index=False)

# --- 2.3. Preparação para Visualizações ---
print('🛠️ Preparando dados agregados e métricas derivadas...')
# Adicionar coluna regiao ao df_gastos
regioes = df_idh[['uf', 'regiao']].drop_duplicates()
df_gastos = df_gastos.merge(regioes, on='uf', how='left')
# Agregação por região
df_idh_reg = df_idh.groupby(['ano', 'regiao'], as_index=False)['idh'].mean()
df_gastos_reg = df_gastos.groupby(['ano', 'regiao', 'categoria'], as_index=False)[['valor_pago', 'valor_per_capita']].sum()
df_idh_reg.to_csv(PROC_DIR / 'idh_por_regiao.csv', index=False)
df_gastos_reg.to_csv(PROC_DIR / 'gastos_por_regiao.csv', index=False)
# Variação anual de IDH e gastos
df_idh_var = df_idh.groupby(['uf', 'ano'], as_index=False)['idh'].mean()
df_idh_var['idh_var_ano'] = df_idh_var.groupby('uf')['idh'].diff()
df_idh_var.to_csv(PROC_DIR / 'variacao_anual_idh.csv', index=False)
df_gastos_var = df_gastos.groupby(['uf', 'categoria', 'ano'], as_index=False)['valor_per_capita'].sum()
df_gastos_var['gasto_var_ano'] = df_gastos_var.groupby(['uf', 'categoria'])['valor_per_capita'].diff()
df_gastos_var.to_csv(PROC_DIR / 'variacao_anual_gastos.csv', index=False)
# Gastos per capita final
df_gastos[['ano', 'uf', 'categoria', 'valor_per_capita']].to_csv(PROC_DIR / 'gastos_per_capita.csv', index=False)

# --- Gráficos Exploratórios (salvar como PNG) ---
print('📈 Gerando gráficos exploratórios...')
sns.set(style='whitegrid')
# Boxplot IDH por região
plt.figure(figsize=(10,6))
sns.boxplot(x='regiao', y='idh', data=df_idh)
plt.title('Distribuição do IDH por Região')
plt.savefig(PROC_DIR / 'boxplot_idh_regiao.png')
plt.close()
# Boxplot gastos per capita por região/categoria
plt.figure(figsize=(12,6))
sns.boxplot(x='regiao', y='valor_per_capita', hue='categoria', data=df_gastos)
plt.title('Gastos Públicos Per Capita por Região e Categoria')
plt.savefig(PROC_DIR / 'boxplot_gastos_per_capita_regiao_categoria.png')
plt.close()
# Scatterplot IDH vs. gastos per capita (todas categorias)
for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
    if cat in df_corr:
        plt.figure(figsize=(8,6))
        sns.scatterplot(x=cat, y='idh', data=df_corr)
        plt.title(f'IDH vs. Gastos Per Capita - {cat}')
        plt.xlabel(f'Gasto Per Capita ({cat})')
        plt.ylabel('IDH')
        plt.savefig(PROC_DIR / f'scatter_idh_vs_gasto_per_capita_{cat.lower()}.png')
        plt.close()
# Heatmap de correlação
plt.figure(figsize=(8,6))
sns.heatmap(df_corr[['idh', 'Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']].corr(), annot=True, cmap='coolwarm')
plt.title('Heatmap de Correlação entre IDH e Gastos Per Capita')
plt.savefig(PROC_DIR / 'heatmap_correlacao.png')
plt.close()
# Séries temporais IDH e gastos
for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
    if cat in df_corr:
        plt.figure(figsize=(10,6))
        for uf in df_corr['uf'].unique():
            sub = df_corr[df_corr['uf'] == uf]
            plt.plot(sub['ano'], sub[cat], label=uf, alpha=0.3)
        plt.title(f'Evolução Temporal do Gasto Per Capita - {cat}')
        plt.xlabel('Ano')
        plt.ylabel(f'Gasto Per Capita ({cat})')
        plt.savefig(PROC_DIR / f'serie_temporal_gasto_per_capita_{cat.lower()}.png')
        plt.close()

# --- Mapas Interativos ---
print('🌎 Gerando mapas interativos...')

# 1. Mapa de Calor Relacional (heatmap de correlação entre variáveis)
heatmap_fig = px.imshow(
    df_corr[['idh', 'Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']].corr(),
    text_auto=True,
    color_continuous_scale='RdBu',
    title='Heatmap de Correlação entre IDH e Gastos Per Capita'
)
heatmap_fig.write_html(PROC_DIR / 'heatmap_interativo_correlacao.html')

# 2. Gráfico de Bolhas Cruzado (IDH vs. gasto per capita, tamanho=população)
for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
    if cat in df_corr:
        bolha_fig = px.scatter(
            df_corr,
            x=cat,
            y='idh',
            size=df_corr['ano'].map(lambda x: 10 + 2*(x-2019)),  # só para variar o tamanho
            color='regiao',
            hover_name='uf',
            animation_frame='ano',
            title=f'Gráfico de Bolhas Cruzado: IDH vs. Gasto Per Capita - {cat}',
            labels={cat: f'Gasto Per Capita ({cat})', 'idh': 'IDH'}
        )
        bolha_fig.write_html(PROC_DIR / f'bolhas_idh_vs_gasto_per_capita_{cat.lower()}.html')

# 3. Mapa Coroplético Relacional (IDH, gasto per capita, relação IDH/gasto)
# Carregar GeoJSON dos estados do Brasil
geojson_path = PROC_DIR / 'brazil_states.geojson'
if geojson_path.exists():
    # Padronizar nomes de estados para merge
    geo = gpd.read_file(geojson_path)
    geo['uf'] = geo['sigla'] = geo['sigla'].str.upper()
    # Usar dados do último ano disponível
    ano_max = df_corr['ano'].max()
    for cat in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
        if cat in df_corr:
            df_map = df_corr[df_corr['ano'] == ano_max][['uf', 'idh', cat, 'regiao']]
            df_map = df_map.rename(columns={cat: 'gasto_per_capita'})
            # Mapa coroplético do IDH
            fig_idh = px.choropleth(
                df_map, geojson=geo, locations='uf', featureidkey='properties.sigla',
                color='idh', color_continuous_scale='Viridis',
                title=f'Mapa Coroplético: IDH por Estado ({ano_max})',
                hover_data=['gasto_per_capita', 'regiao']
            )
            fig_idh.update_geos(fitbounds="locations", visible=False)
            fig_idh.write_html(PROC_DIR / f'mapa_coropletico_idh_{cat.lower()}.html')
            # Mapa coroplético do gasto per capita
            fig_gasto = px.choropleth(
                df_map, geojson=geo, locations='uf', featureidkey='properties.sigla',
                color='gasto_per_capita', color_continuous_scale='Blues',
                title=f'Mapa Coroplético: Gasto Per Capita ({cat}) por Estado ({ano_max})',
                hover_data=['idh', 'regiao']
            )
            fig_gasto.update_geos(fitbounds="locations", visible=False)
            fig_gasto.write_html(PROC_DIR / f'mapa_coropletico_gasto_{cat.lower()}.html')
            # Mapa coroplético relacional (IDH/gasto)
            df_map['relacao_idh_gasto'] = df_map['idh'] / (df_map['gasto_per_capita'] + 1e-6)
            fig_rel = px.choropleth(
                df_map, geojson=geo, locations='uf', featureidkey='properties.sigla',
                color='relacao_idh_gasto', color_continuous_scale='RdYlGn',
                title=f'Mapa Coroplético Relacional: IDH/Gasto Per Capita ({cat}) por Estado ({ano_max})',
                hover_data=['idh', 'gasto_per_capita', 'regiao']
            )
            fig_rel.update_geos(fitbounds="locations", visible=False)
            fig_rel.write_html(PROC_DIR / f'mapa_coropletico_relacional_{cat.lower()}.html')
else:
    print('⚠️ Arquivo GeoJSON dos estados do Brasil não encontrado. Mapas coropléticos não serão gerados.')

print('✅ Fase 2 concluída! Todos os arquivos salvos em data/processed/.')
