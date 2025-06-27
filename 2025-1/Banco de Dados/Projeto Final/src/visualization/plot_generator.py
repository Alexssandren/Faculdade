"""
Gerador de Visualizações - Sistema DEC7588
Gera gráficos e mapas a partir dos dados do banco
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np
import os
import sqlite3
from pathlib import Path

# Configurações
DB_FILE = "data/processed/dados_socioeconomicos.db"
OUTPUT_DIR = "outputs/visualizations"
SHAPEFILE_PATH = "data/geospatial/BR_UF_2024.shp"
GEOJSON_FILE = "data/geospatial/BR_UF_2024.geojson"

# Mapear cores para categorias
CORES_CATEGORIA = {
    "Saúde": "#FF6B6B",
    "Educação": "#4ECDC4", 
    "Assistência Social": "#45B7D1",
    "Previdência Social": "#96CEB4",
    "Trabalho": "#FFEAA7",
    "Defesa Nacional": "#DDA0DD",
    "Judiciário": "#F39C12",
    "Legislativo": "#E74C3C"
}

def main():
    """Função principal para gerar todas as visualizações"""
    
    # Verificar se o banco existe
    if not os.path.exists(DB_FILE):
        print(f"❌ ERRO: Banco de dados {DB_FILE} não encontrado. "
              f"Execute o script de importação primeiro.")
        return
    
    # Tentar carregar dados
    try:
        df = load_data_from_db()
        if df.empty:
            print("❌ Nenhum dado encontrado no banco.")
            return
        
        print(f"✅ Dados carregados com sucesso da tabela 'analise_unificada' ({len(df)} registros).")
        
        # Preparar dados
        df = prepare_data(df)
        
        # Criar diretório de output se não existir
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Gerar visualizações específicas removidas
        print("📊 Geração de mapas de calor removida - foco em dados tabulares.")
        
        # Gerar gráficos de bolhas removidos
        print("📊 Geração de gráficos de bolhas removida - foco em dados tabulares.")
        
        # Gerar mapas coropléticos removidos
        print("📊 Geração de mapas coropléticos removida - foco em dados tabulares.")
        
        # Gerar mapas coropléticos se dados geoespaciais disponíveis
        try:
            if df.empty:
                print("ℹ️ DataFrame vazio, pulando geração dos mapas coropléticos.")
                return
                
            # Verificar se shapefile existe
            if not os.path.exists(SHAPEFILE_PATH):
                print(f"❌ ERRO: Shapefile {SHAPEFILE_PATH} não encontrado. Mapas coropléticos não podem ser gerados.")
                
                # Tentar geojson como fallback
                if os.path.exists(GEOJSON_FILE):
                    print(f"ℹ️ Tentando usar {GEOJSON_FILE} como fallback.")
                else:
                    print(f"❌ ERRO: Arquivo {GEOJSON_FILE} também não encontrado.")
                    return
            
            generate_choropleth_maps(df)
            
        except Exception as e:
            print(f"❌ Erro ao gerar mapas coropléticos: {e}")
        
    except Exception as e:
        print(f"❌ ERRO ao carregar dados do banco de dados: {e}")

def generate_choropleth_maps(df):
    """Gera mapas coropléticos usando geopandas"""
    try:
        import geopandas as gpd
        
        # Ler shapefile
        print(f"🗺️ Lendo shapefile de {SHAPEFILE_PATH}")
        gdf = gpd.read_file(SHAPEFILE_PATH)
        
        # Mapas coropléticos
        print("🗺️ Gerando Mapas Coropléticos Interativos...")
        
        # Verificar se a coluna 'uf' existe no shapefile, senão tentar outras possibilidades
        if 'uf' not in gdf.columns:
            if 'SIGLA_UF' in gdf.columns:
                gdf = gdf.rename(columns={'SIGLA_UF': 'uf'})
            elif 'CD_UF' in gdf.columns:
                print("⚠️ Shapefile não tem 'uf' ou 'SIGLA_UF'. Tentando 'CD_UF' e esperando que o merge funcione ou necessite de mapeamento.")
                # Pode precisar de mapeamento adicional entre códigos e siglas
            else:
                print("❌ ERRO: Coluna 'uf' (ou equivalente como 'SIGLA_UF') não encontrada no GeoDataFrame após tentativas de renomear.")
                return
        
        # Determinar ano para o mapa (usar o último disponível)
        if 'ano' in df.columns and not df['ano'].isna().all():
            anos_disponiveis = sorted(df['ano'].dropna().unique())
            ano_para_mapa = anos_disponiveis[-1] if anos_disponiveis else None
        else:
            ano_para_mapa = None
        
        if ano_para_mapa is None:
            print("❌ Não há anos únicos no dataset para gerar mapas.")
            return
            
        # Filtrar dados para o ano específico
        df_ano = df[df['ano'] == ano_para_mapa].copy() if 'ano' in df.columns else df.copy()
        
        # Gerar mapa de IDH
        if 'idh_geral' in df_ano.columns and 'uf' in df_ano.columns:
            df_idh = df_ano.groupby('uf')['idh_geral'].mean().reset_index()
            gdf_merged = gdf.merge(df_idh, on='uf', how='left')
            
            fig, ax = plt.subplots(1, 1, figsize=(15, 10))
            gdf_merged.plot(column='idh_geral', cmap='YlOrRd', legend=True, ax=ax, 
                          missing_kwds={'color': 'lightgrey'})
            ax.set_title(f'IDH por Estado - {ano_para_mapa}', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            output_path_idh = os.path.join(OUTPUT_DIR, f'mapa_idh_{ano_para_mapa}.png')
            plt.tight_layout()
            plt.savefig(output_path_idh, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✅ Mapa Coroplético (IDH {ano_para_mapa}) salvo em: {output_path_idh}")
        
        # Gerar mapas por categoria de gasto
        categorias = df_ano['categoria_nome'].unique() if 'categoria_nome' in df_ano.columns else []
        for categoria in categorias[:3]:  # Limitar a 3 categorias principais
            categoria_nome_amigavel = categoria.replace(" ", "_").replace("/", "_")
            df_cat = df_ano[df_ano['categoria_nome'] == categoria]
            
            if df_cat.empty or 'valor_milhoes' not in df_cat.columns:
                print(f"    ⚠️ Dados de gasto para '{categoria_nome_amigavel}' ausentes no ano {ano_para_mapa}. Pulando mapas de gasto e relação.")
                continue
            
            # Mapa de gastos por categoria
            df_gastos = df_cat.groupby('uf')['valor_milhoes'].sum().reset_index()
            gdf_merged_gastos = gdf.merge(df_gastos, on='uf', how='left')
            
            fig, ax = plt.subplots(1, 1, figsize=(15, 10))
            gdf_merged_gastos.plot(column='valor_milhoes', cmap='Blues', legend=True, ax=ax,
                                 missing_kwds={'color': 'lightgrey'})
            ax.set_title(f'Gastos {categoria} por Estado - {ano_para_mapa} (em Milhões R$)', 
                        fontsize=14, fontweight='bold')
            ax.axis('off')
            
            output_path_gasto = os.path.join(OUTPUT_DIR, f'mapa_gastos_{categoria_nome_amigavel}_{ano_para_mapa}.png')
            plt.tight_layout()
            plt.savefig(output_path_gasto, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✅ Mapa Coroplético (Gasto {categoria_nome_amigavel} {ano_para_mapa}) salvo em: {output_path_gasto}")
            
            # Mapa de relação IDH/Gastos
            if 'idh_geral' in df_cat.columns:
                df_relacao = df_cat.groupby('uf').agg({
                    'idh_geral': 'mean',
                    'valor_milhoes': 'sum'
                }).reset_index()
                df_relacao['relacao_idh_gasto'] = df_relacao['idh_geral'] / (df_relacao['valor_milhoes'] / 1000)
                
                gdf_merged_rel = gdf.merge(df_relacao, on='uf', how='left')
                
                fig, ax = plt.subplots(1, 1, figsize=(15, 10))
                gdf_merged_rel.plot(column='relacao_idh_gasto', cmap='RdYlGn', legend=True, ax=ax,
                                  missing_kwds={'color': 'lightgrey'})
                ax.set_title(f'Relação IDH/Gasto {categoria} por Estado - {ano_para_mapa}', 
                            fontsize=14, fontweight='bold')
                ax.axis('off')
                
                output_path_rel = os.path.join(OUTPUT_DIR, f'mapa_relacao_idh_gasto_{categoria_nome_amigavel}_{ano_para_mapa}.png')
                plt.tight_layout()
                plt.savefig(output_path_rel, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"✅ Mapa Coroplético (Relação IDH/Gasto {categoria_nome_amigavel} {ano_para_mapa}) salvo em: {output_path_rel}")
    
    except ImportError:
        print("❌ GeoPandas não está instalado. Instale com: pip install geopandas")
    except Exception as e:
        print(f"❌ Erro ao gerar mapas coropléticos: {e}")

def load_data_from_db():
    """Carrega dados do banco SQLite"""
    conn = sqlite3.connect(DB_FILE)
    
    # Tentar carregar a tabela analise_unificada ou fazer join das tabelas necessárias
    query = """
    SELECT * FROM analise_unificada 
    ORDER BY ano, uf, categoria_nome
    LIMIT 10000
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def prepare_data(df):
    """Prepara e limpa os dados"""
    
    # Converter colunas numéricas
    numeric_columns = ['valor_milhoes', 'idh_geral', 'idh_educacao', 'idh_longevidade', 'idh_renda']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            print(f"⚠️ Atenção: Coluna {col} esperada para conversão numérica não encontrada no DataFrame.")
    
    # Remover linhas com valores críticos faltando
    df = df.dropna(subset=['uf'])
    
    return df

if __name__ == "__main__":
    print("🚀 Iniciando Geração de Visualizações Avançadas...")
    
    try:
        main()
    except Exception as e:
        print(f"❌ Erro geral na execução: {e}")
    else:
        print("✅ Geração de visualizações concluída!")
    
    print("📊 Para executar apenas as consultas principais, use:")
    print("python -m src.queries.analytics_queries")
    
    if not os.path.exists(DB_FILE):
        print("❌ Não foi possível carregar os dados. Geração de visualizações abortada.") 