import matplotlib
matplotlib.use('Agg') # Deve ser chamado ANTES de qualquer importação que possa usar matplotlib (ex: geopandas)
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
import geopandas as gpd

# Define o caminho para o diretório 'src' e garante que ele exista
SCRIPT_DIR = Path(__file__).parent # src/visualization
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Diretórios de dados e resultados
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
# Alterado para o novo local de resultados
RESULTS_VIS_DIR = PROJECT_ROOT / "results" / "visualizations"
RESULTS_VIS_DIR.mkdir(parents=True, exist_ok=True)

# Arquivo do Banco de Dados
DB_FILE = PROCESSED_DATA_DIR / "projeto_visualizacao.db"

# Arquivo GeoJSON (necessário para mapas coropléticos)
# Considerando que pode estar em data/geospatial/ como planejado anteriormente
GEOJSON_FILE = PROJECT_ROOT / "data" / "geospatial" / "bcim_2016_21_11_2018.gpkg" # Ajustar se o nome/local for diferente
# Ou se estiver em data/processed/ como no script original:
# GEOJSON_FILE = PROCESSED_DATA_DIR / "brazil_states.geojson" 


def load_data_from_db():
    """Carrega os dados da tabela analise_unificada do banco de dados SQLite."""
    if not DB_FILE.exists():
        print(f"❌ ERRO: Banco de dados {DB_FILE} não encontrado. "
              f"Execute a fase de configuração do banco de dados primeiro.")
        return None
    
    try:
        print(f"🔗 Conectando ao banco de dados: {DB_FILE}")
        conexao = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM analise_unificada", conexao)
        conexao.close()
        print(f"✅ Dados carregados com sucesso da tabela 'analise_unificada' ({len(df)} registros).")
        
        cols_to_numeric = ['idh', 'Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']
        if 'populacao' in df.columns:
            cols_to_numeric.append('populacao')
        
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                print(f"⚠️ Atenção: Coluna {col} esperada para conversão numérica não encontrada no DataFrame.")

        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce').astype('Int64')

        return df
    except Exception as e:
        print(f"❌ ERRO ao carregar dados do banco de dados: {e}")
        return None

def gerar_mapa_calor_relacional(df):
    """Função removida - não gera mais gráficos."""
    print("📊 Geração de mapas de calor removida - foco em dados tabulares.")

def gerar_grafico_bolhas_cruzado(df):
    """Função removida - não gera mais gráficos."""
    print("📊 Geração de gráficos de bolhas removida - foco em dados tabulares.")

def gerar_mapas_coropleticos(df):
    """Função removida - não gera mais gráficos."""
    print("📊 Geração de mapas coropléticos removida - foco em dados tabulares.")

def gerar_mapas_coropleticos_removido(df):
    """Gera mapas coropléticos relacionais (IDH, Gasto, Relação IDH/Gasto) para cada categoria e para cada ano."""
    if df is None or df.empty:
        print("ℹ️ DataFrame vazio, pulando geração dos mapas coropléticos.")
        return

    # Ajuste no caminho do GeoJSON. Precisa ser o SHP que foi baixado, ou um GeoJSON convertido dele.
    # O usuário mencionou que os arquivos foram baixados e inseridos.
    # Se o SHP estiver em data/geospatial/BR_UF_2024.shp
    shapefile_path = PROJECT_ROOT / "data" / "geospatial" / "BR_UF_2024.shp"
    if not shapefile_path.exists():
        print(f"❌ ERRO: Shapefile {shapefile_path} não encontrado. Mapas coropléticos não podem ser gerados.")
        # Tentar o GEOJSON_FILE original como fallback
        if GEOJSON_FILE.exists():
             print(f"ℹ️ Tentando usar {GEOJSON_FILE} como fallback.")
             geo_data = gpd.read_file(GEOJSON_FILE)
        else:
            print(f"❌ ERRO: Arquivo {GEOJSON_FILE} também não encontrado.")
            return
    else:
        print(f"🗺️ Lendo shapefile de {shapefile_path}")
        geo_data = gpd.read_file(shapefile_path)

    print("🗺️ Gerando Mapas Coropléticos Interativos...")
    if 'SIGLA_UF' in geo_data.columns and 'uf' not in geo_data.columns:
         geo_data = geo_data.rename(columns={'SIGLA_UF': 'uf'})
    elif 'CD_UF' in geo_data.columns and 'uf' not in geo_data.columns: # Outro nome comum para código UF
         # Se for código numérico, precisaria mapear para Sigla. 
         # Por agora, assumindo que 'uf' ou 'SIGLA_UF' exista ou o merge falhará.
         print("⚠️ Shapefile não tem 'uf' ou 'SIGLA_UF'. Tentando 'CD_UF' e esperando que o merge funcione ou necessite de mapeamento.")
         geo_data = geo_data.rename(columns={'CD_UF': 'uf'})
    
    if 'uf' not in geo_data.columns:
        print("❌ ERRO: Coluna 'uf' (ou equivalente como 'SIGLA_UF') não encontrada no GeoDataFrame após tentativas de renomear.")
        return
        
    geo_data['uf'] = geo_data['uf'].astype(str).str.upper() # Garantir que uf seja string e maiúscula para o merge
    df['uf'] = df['uf'].astype(str).str.upper()
    
    categorias_despesa_base = ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']
    colunas_despesa_mapa = {}
    for cat_base in categorias_despesa_base:
        col_per_capita = f"despesa_{cat_base.lower().replace(' ', '_').replace('ç', 'c').replace('ú', 'u')}_per_capita"
        if col_per_capita in df.columns:
            colunas_despesa_mapa[cat_base] = col_per_capita
        elif cat_base in df.columns:
            colunas_despesa_mapa[cat_base] = cat_base

    anos_unicos = sorted(df['ano'].dropna().unique(), reverse=True)
    if not anos_unicos:
        print("❌ Não há anos únicos no dataset para gerar mapas.")
        return
        
    for ano_para_mapa in anos_unicos:
        print(f"  -> Gerando mapas para o ano: {ano_para_mapa}")
        df_mapa_anual = df[df['ano'] == ano_para_mapa].copy()

        # Mapa do IDH (uma vez por ano)
        fig_idh = px.choropleth_mapbox(
            df_mapa_anual, geojson=geo_data, locations='uf', featureidkey='properties.uf',
            color='idh', color_continuous_scale="Viridis",
            mapbox_style="open-street-map", zoom=3, center = {"lat": -14.24, "lon": -51.925},
            opacity=0.7, hover_name='uf', hover_data={'idh': True, 'regiao': True},
            title=f'IDH por Estado - {ano_para_mapa}'
        )
        fig_idh.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        output_path_idh = RESULTS_VIS_DIR / f"mapa_coropletico_idh_{ano_para_mapa}.html"
        fig_idh.write_html(output_path_idh)
        print(f"✅ Mapa Coroplético (IDH {ano_para_mapa}) salvo em: {output_path_idh}")

        for categoria_nome_amigavel, coluna_gasto in colunas_despesa_mapa.items():
            print(f"  -> Gerando mapas para categoria: {categoria_nome_amigavel} (usando coluna {coluna_gasto})")
            df_categoria_mapa = df_mapa_anual[['uf', 'idh', coluna_gasto, 'regiao']].copy()
            if coluna_gasto not in df_categoria_mapa.columns or df_categoria_mapa[coluna_gasto].isnull().all():
                print(f"    ⚠️ Dados de gasto para '{categoria_nome_amigavel}' ausentes no ano {ano_para_mapa}. Pulando mapas de gasto e relação.")
                continue
                
            df_categoria_mapa['relacao_idh_gasto'] = df_categoria_mapa['idh'] / (df_categoria_mapa[coluna_gasto] + 1e-9)

            # Mapa de Gasto
            fig_gasto = px.choropleth_mapbox(
                df_categoria_mapa, geojson=geo_data, locations='uf', featureidkey='properties.uf',
                color=coluna_gasto, color_continuous_scale="Blues",
                mapbox_style="open-street-map", zoom=3, center = {"lat": -14.24, "lon": -51.925},
                opacity=0.7, hover_name='uf', hover_data={coluna_gasto: True, 'idh': True, 'regiao': True},
                title=f'Gasto em {categoria_nome_amigavel} por Estado - {ano_para_mapa}'
            )
            fig_gasto.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            output_path_gasto = RESULTS_VIS_DIR / f"mapa_coropletico_gasto_{categoria_nome_amigavel.lower().replace(' ', '_')}_{ano_para_mapa}.html"
            fig_gasto.write_html(output_path_gasto)
            print(f"✅ Mapa Coroplético (Gasto {categoria_nome_amigavel} {ano_para_mapa}) salvo em: {output_path_gasto}")

            # Mapa de Relação
            fig_rel = px.choropleth_mapbox(
                df_categoria_mapa, geojson=geo_data, locations='uf', featureidkey='properties.uf',
                color='relacao_idh_gasto', color_continuous_scale="RdYlGn",
                mapbox_style="open-street-map", zoom=3, center = {"lat": -14.24, "lon": -51.925},
                opacity=0.7, hover_name='uf', hover_data={'relacao_idh_gasto': True, 'idh': True, coluna_gasto: True, 'regiao': True},
                title=f'Relação IDH / Gasto em {categoria_nome_amigavel} - {ano_para_mapa}'
            )
            fig_rel.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            output_path_rel = RESULTS_VIS_DIR / f"mapa_coropletico_relacao_{categoria_nome_amigavel.lower().replace(' ', '_')}_{ano_para_mapa}.html"
            fig_rel.write_html(output_path_rel)
            print(f"✅ Mapa Coroplético (Relação IDH/Gasto {categoria_nome_amigavel} {ano_para_mapa}) salvo em: {output_path_rel}")

def main():
    """Função principal para gerar as visualizações avançadas.""" # Nome da Fase removido para generalizar
    print("🚀 Iniciando Geração de Visualizações Avançadas...")
    
    df_completo = load_data_from_db()
    
    if df_completo is not None and not df_completo.empty:
        gerar_mapa_calor_relacional(df_completo)
        gerar_grafico_bolhas_cruzado(df_completo)
        gerar_mapas_coropleticos(df_completo)
        print(f"🎉 Geração de visualizações concluída com sucesso! Visualizações salvas em {RESULTS_VIS_DIR.relative_to(PROJECT_ROOT)}")
    else:
        print("❌ Não foi possível carregar os dados. Geração de visualizações abortada.")

if __name__ == "__main__":
    main() 