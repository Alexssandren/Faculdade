import pandas as pd
import numpy as np
import os # Mantido por enquanto, mas verificar uso
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd # Mantido, mas verificar se GeoJSON ainda é usado aqui

# Definição de caminhos relativos à raiz do projeto
SCRIPT_DIR = Path(__file__).parent # src/pipeline
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Diretórios (ajustados)
# RAW_DIR não é mais necessário aqui
# PROC_DIR agora se refere ao diretório de saída para esta fase exploratória
EXPLORE_RESULTS_DIR = PROJECT_ROOT / "results" / "exploratory_analysis"
EXPLORE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Arquivo de entrada principal (dataset unificado gerado pelo DataCleaner)
UNIFIED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_unificado.csv"
GEOJSON_PATH = PROJECT_ROOT / "data" / "geospatial" / "BR_UF_2024.shp" # Usar o shapefile diretamente

def run_exploratory_analysis():
    print("🚀 Iniciando Fase de Análise Exploratória (Fase 2 - Exploração)...")

    # Carregar dataset unificado
    print(f'🔄 Carregando dataset unificado de {UNIFIED_DATASET_PATH}...')
    if not UNIFIED_DATASET_PATH.exists():
        print(f"❌ ERRO: Dataset unificado {UNIFIED_DATASET_PATH} não encontrado. "
              f"Execute a fase de processamento de dados (DataCleaner) primeiro.")
        return
    
    df_corr = pd.read_csv(UNIFIED_DATASET_PATH)
    print(f"✅ Dataset unificado carregado com {len(df_corr)} linhas e colunas: {df_corr.columns.tolist()}")

    if df_corr.empty:
        print("❌ Dataset unificado está vazio. Abortando análise exploratória.")
        return

    # --- 2.1. Análise Descritiva (Adaptada) ---
    # As estatísticas detalhadas de IDH e Despesas separadamente podem ser menos relevantes aqui,
    # já que temos o dataset unificado. Focaremos nas estatísticas do df_corr.
    print('📊 Análise descritiva do dataset unificado...')
    desc_unificado = df_corr.describe(include='all')
    desc_unificado.to_csv(EXPLORE_RESULTS_DIR / 'desc_dataset_unificado.csv')
    print(f"✅ Estatísticas descritivas salvas em: {EXPLORE_RESULTS_DIR / 'desc_dataset_unificado.csv'}")

    # Detecção de outliers pode ser mantida se relevante para as colunas principais de df_corr
    # Exemplo para 'idh' e uma coluna de despesa (ex: 'Saúde', se existir, ou uma calculada como 'Gasto Total Normalizado')
    def detectar_outliers(df, col):
        if col not in df.columns:
            print(f"⚠️ Coluna '{col}' não encontrada para detecção de outliers.")
            return pd.DataFrame()
        z = (df[col] - df[col].mean()) / df[col].std()
        return df[np.abs(z) > 3]

    if 'idh' in df_corr.columns:
        outliers_idh = detectar_outliers(df_corr, 'idh')
        if not outliers_idh.empty:
            outliers_idh.to_csv(EXPLORE_RESULTS_DIR / 'outliers_idh_unificado.csv', index=False)
            print(f"✅ Outliers de IDH (do unificado) salvos em: {EXPLORE_RESULTS_DIR / 'outliers_idh_unificado.csv'}")
    
    # Exemplo de coluna de despesa. O nome exato pode variar dependendo do DataCleaner.
    # Vamos assumir que existe uma coluna como 'despesa_saude_per_capita' ou similar.
    # Ou, se tivermos calculado 'Gasto Total Normalizado' no DataCleaner, poderíamos usá-la.
    # Por agora, deixarei um placeholder ou você pode especificar qual usar.
    col_despesa_exemplo = 'Saúde' # Tentar com a coluna base. Ajustar se o nome for diferente no CSV. 
                                 # No CSV unificado, as colunas de despesa são só os nomes das áreas.
    if col_despesa_exemplo in df_corr.columns:
        outliers_despesa = detectar_outliers(df_corr, col_despesa_exemplo)
        if not outliers_despesa.empty:
            outliers_despesa.to_csv(EXPLORE_RESULTS_DIR / f'outliers_{col_despesa_exemplo.lower()}_unificado.csv', index=False)
            print(f"✅ Outliers de {col_despesa_exemplo} (do unificado) salvos.")
    else:
        print(f"⚠️ Coluna '{col_despesa_exemplo}' não encontrada para análise de outliers de despesa.")

    # --- 2.2. Análise de Correlações (Mantida, usando df_corr) ---
    print('🔗 Análise de correlações (sobre dataset unificado)...')
    
    # As colunas de categoria de despesa já devem estar pivotadas no df_corr
    categorias_despesa = ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura'] # Base
    # Filtrar para categorias que realmente existem em df_corr
    categorias_existentes = [cat for cat in categorias_despesa if cat in df_corr.columns]

    if not categorias_existentes:
        print("⚠️ Nenhuma das colunas de categoria de despesa esperadas foi encontrada no dataset unificado.")
    else:
        correlacoes = {}
        for cat in categorias_existentes:
            correlacoes[cat] = {
                'pearson': df_corr['idh'].corr(df_corr[cat], method='pearson'),
                'spearman': df_corr['idh'].corr(df_corr[cat], method='spearman')
            }
        pd.DataFrame(correlacoes).to_csv(EXPLORE_RESULTS_DIR / 'correlacoes_por_categoria.csv')
        print(f"✅ Correlações por categoria salvas.")

        # Correlação por ano
        if 'ano' in df_corr.columns:
            correlacoes_ano = []
            for ano_val in sorted(df_corr['ano'].unique()):
                linha = {'ano': ano_val}
                sub = df_corr[df_corr['ano'] == ano_val]
                for cat in categorias_existentes:
                    linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
                    linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
                correlacoes_ano.append(linha)
            pd.DataFrame(correlacoes_ano).to_csv(EXPLORE_RESULTS_DIR / 'correlacoes_por_ano.csv', index=False)
            print(f"✅ Correlações por ano salvas.")

        # Correlação por estado (uf)
        if 'uf' in df_corr.columns:
            correlacoes_estado = []
            for uf_val in sorted(df_corr['uf'].unique()):
                linha = {'uf': uf_val}
                sub = df_corr[df_corr['uf'] == uf_val]
                for cat in categorias_existentes:
                    linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
                    linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
                correlacoes_estado.append(linha)
            pd.DataFrame(correlacoes_estado).to_csv(EXPLORE_RESULTS_DIR / 'correlacoes_por_estado.csv', index=False)
            print(f"✅ Correlações por estado salvas.")

        # Correlação por região
        if 'regiao' in df_corr.columns: # A coluna 'regiao' deve vir do dataset unificado
            correlacoes_regiao = []
            for reg_val in sorted(df_corr['regiao'].dropna().unique()):
                linha = {'regiao': reg_val}
                sub = df_corr[df_corr['regiao'] == reg_val]
                for cat in categorias_existentes:
                    linha[f'{cat}_pearson'] = sub['idh'].corr(sub[cat], method='pearson')
                    linha[f'{cat}_spearman'] = sub['idh'].corr(sub[cat], method='spearman')
                correlacoes_regiao.append(linha)
            pd.DataFrame(correlacoes_regiao).to_csv(EXPLORE_RESULTS_DIR / 'correlacoes_por_regiao.csv', index=False)
            print(f"✅ Correlações por região salvas.")
        else:
            print("⚠️ Coluna 'regiao' não encontrada no df_corr. Não foi possível calcular correlações por região.")

    # --- 2.3. Preparação para Visualizações (Simplificada) ---
    # Algumas agregações e variações já podem estar no dataset unificado ou ser parte da Fase 3.
    # Vamos manter a geração de arquivos CSV que podem ser úteis para relatórios.
    print('🛠️ Preparando dados agregados e métricas derivadas (do dataset unificado)...')
    if 'regiao' in df_corr.columns and 'ano' in df_corr.columns and 'idh' in df_corr.columns:
        df_idh_reg = df_corr.groupby(['ano', 'regiao'], as_index=False)['idh'].mean()
        df_idh_reg.to_csv(EXPLORE_RESULTS_DIR / 'idh_por_regiao_exploratorio.csv', index=False)
        print(f"✅ IDH por região (exploratório) salvo.")

    # A coluna 'populacao' é crucial para gráficos de bolha e cálculos per capita.
    # Ela deve estar no dataset_unificado.csv
    if 'populacao' not in df_corr.columns:
        print("⚠️ Coluna 'populacao' não encontrada no df_corr. Alguns gráficos podem falhar ou ser imprecisos.")

    # --- Gráficos Exploratórios (salvar como PNG e HTML) ---
    print('📈 Gerando gráficos exploratórios...')
    sns.set(style='whitegrid')
    
    if 'regiao' in df_corr.columns and 'idh' in df_corr.columns:
        plt.figure(figsize=(10,6))
        sns.boxplot(x='regiao', y='idh', data=df_corr)
        plt.title('Distribuição do IDH por Região (Dataset Unificado)')
        plt.savefig(EXPLORE_RESULTS_DIR / 'boxplot_idh_regiao.png')
        plt.close()
        print("✅ Boxplot IDH por Região salvo.")

    # Scatterplot IDH vs. gastos (agora usando colunas existentes em df_corr)
    for cat in categorias_existentes:
        if 'idh' in df_corr.columns:
            plt.figure(figsize=(8,6))
            sns.scatterplot(x=cat, y='idh', data=df_corr, hue='regiao' if 'regiao' in df_corr.columns else None, alpha=0.7)
            plt.title(f'IDH vs. Gastos em {cat}')
            plt.xlabel(f'Gasto em {cat}')
            plt.ylabel('IDH')
            plt.savefig(EXPLORE_RESULTS_DIR / f'scatter_idh_vs_gasto_{cat.lower().replace(" ", "_")}.png')
            plt.close()
            print(f"✅ Scatterplot IDH vs {cat} salvo.")

    # Heatmap de correlação (já calculado, agora plotando)
    cols_para_heatmap = ['idh'] + categorias_existentes
    if len(cols_para_heatmap) > 1: # Precisa de pelo menos duas colunas para correlacionar
        plt.figure(figsize=(8,6))
        sns.heatmap(df_corr[cols_para_heatmap].corr(), annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
        plt.title('Heatmap de Correlação (Dataset Unificado)')
        plt.tight_layout()
        plt.savefig(EXPLORE_RESULTS_DIR / 'heatmap_correlacao_unificado.png')
        plt.close()
        print(f"✅ Heatmap de Correlação salvo.")

    # --- Mapas Interativos (Adaptado) ---
    print('🌎 Gerando mapas interativos (exploratórios)...')

    # Mapa de Calor Relacional (Heatmap de correlação interativo)
    if len(cols_para_heatmap) > 1:
        heatmap_fig_px = px.imshow(
            df_corr[cols_para_heatmap].corr(),
            text_auto=True, # Mostra os valores de correlação no heatmap
            color_continuous_scale='RdBu_r', # Inverte para vermelho=positivo, azul=negativo
            aspect="auto",
            labels=dict(color="Correlação"),
            title='Heatmap Interativo: Correlação entre IDH e Gastos'
        )
        heatmap_fig_px.update_xaxes(title_text='')
        heatmap_fig_px.update_yaxes(title_text='')
        heatmap_fig_px.write_html(EXPLORE_RESULTS_DIR / 'heatmap_interativo_correlacao.html')
        print(f"✅ Heatmap interativo de correlação salvo.")

    # Gráfico de Bolhas Cruzado (IDH vs. gasto, tamanho=população)
    if 'populacao' in df_corr.columns and 'ano' in df_corr.columns and 'uf' in df_corr.columns and 'regiao' in df_corr.columns and 'idh' in df_corr.columns:
        for cat in categorias_existentes:
            bolha_fig = px.scatter(
                df_corr.sort_values(by='ano'), # Garante ordem para animação
                x=cat,
                y='idh',
                size='populacao', 
                color='regiao',
                hover_name='uf',
                animation_frame='ano',
                animation_group='uf',
                log_x=True, # Gastos podem ter grande variação
                size_max=60,
                title=f'Gráfico de Bolhas: IDH vs. Gasto em {cat}',
                labels={cat: f'Gasto em {cat} (log)', 'idh': 'IDH', 'populacao': 'População'}
            )
            bolha_fig.write_html(EXPLORE_RESULTS_DIR / f'bolhas_idh_vs_gasto_{cat.lower().replace(" ", "_")}.html')
            print(f"✅ Gráfico de bolhas IDH vs {cat} salvo.")
    else:
        print("⚠️ Não foi possível gerar gráficos de bolhas devido à falta de colunas: 'populacao', 'ano', 'uf', 'regiao' ou 'idh'.")

    # Mapa Coroplético (Simplificado para IDH e um exemplo de Gasto do ano mais recente)
    if GEOJSON_PATH.exists() and 'uf' in df_corr.columns and 'ano' in df_corr.columns:
        try:
            geo_data = gpd.read_file(GEOJSON_PATH)
            # Padronizar coluna de UF no shapefile
            if 'SIGLA_UF' in geo_data.columns:
                geo_data = geo_data.rename(columns={'SIGLA_UF': 'uf'})
            elif 'CD_UF' in geo_data.columns: # Outro nome comum
                 geo_data = geo_data.rename(columns={'CD_UF': 'uf'})
            elif 'SIGLA' in geo_data.columns:
                 geo_data = geo_data.rename(columns={'SIGLA': 'uf'})
            
            if 'uf' not in geo_data.columns:
                raise ValueError("Coluna 'uf' não encontrada no shapefile após tentativas de renomeação.")
            
            geo_data['uf'] = geo_data['uf'].astype(str).str.upper()
            df_corr['uf'] = df_corr['uf'].astype(str).str.upper()
            
            ano_max = df_corr['ano'].max()
            df_map = df_corr[df_corr['ano'] == ano_max].copy()

            if 'idh' in df_map.columns:
                fig_idh_map = px.choropleth_mapbox(
                    df_map, geojson=geo_data, locations='uf', featureidkey='properties.uf',
                    color='idh', color_continuous_scale="Viridis",
                    mapbox_style="carto-positron", zoom=3, center = {"lat": -14.24, "lon": -51.925},
                    opacity=0.7, hover_name='uf',
                    title=f'Mapa Coroplético: IDH por Estado ({ano_max})',
                    hover_data={'idh':True, 'regiao': True if 'regiao' in df_map else False}
                )
                fig_idh_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
                fig_idh_map.write_html(EXPLORE_RESULTS_DIR / f'mapa_coropletico_idh_{ano_max}.html')
                print(f"✅ Mapa coroplético de IDH ({ano_max}) salvo.")

            # Exemplo com uma categoria de gasto
            if categorias_existentes:
                cat_exemplo_mapa = categorias_existentes[0]
                if cat_exemplo_mapa in df_map.columns:
                    fig_gasto_map = px.choropleth_mapbox(
                        df_map, geojson=geo_data, locations='uf', featureidkey='properties.uf',
                        color=cat_exemplo_mapa, color_continuous_scale="Blues",
                        mapbox_style="carto-positron", zoom=3, center = {"lat": -14.24, "lon": -51.925},
                        opacity=0.7, hover_name='uf',
                        title=f'Mapa Coroplético: Gasto em {cat_exemplo_mapa} por Estado ({ano_max})',
                        hover_data={'idh':True, cat_exemplo_mapa:True, 'regiao': True if 'regiao' in df_map else False}
                    )
                    fig_gasto_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
                    fig_gasto_map.write_html(EXPLORE_RESULTS_DIR / f'mapa_coropletico_gasto_{cat_exemplo_mapa.lower().replace(" ", "_")}_{ano_max}.html')
                    print(f"✅ Mapa coroplético de Gasto ({cat_exemplo_mapa}, {ano_max}) salvo.")
        except Exception as e_map:
            print(f"⚠️ Erro ao gerar mapas coropléticos: {e_map}. Verifique o arquivo shapefile e as colunas.")

    else:
        print('⚠️ Shapefile não encontrado ou colunas de UF/ano ausentes. Mapas coropléticos não serão gerados.')

    print(f'✅ Análise Exploratória (Fase 2 - Exploração) concluída! Arquivos salvos em {EXPLORE_RESULTS_DIR.relative_to(PROJECT_ROOT)}.')

if __name__ == '__main__':
    run_exploratory_analysis() 