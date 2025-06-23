import sqlite3
import pandas as pd
from pathlib import Path

# Define o caminho para o diretório 'src' e garante que ele exista
# Este script espera ser executado da raiz do projeto, ou ter o PYTHONPATH configurado
SCRIPT_DIR = Path(__file__).parent # src/database
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Define os caminhos para os arquivos de dados e banco de dados
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DB_FILE = PROCESSED_DATA_DIR / "projeto_visualizacao.db"
UNIFIED_DATASET_CSV = PROCESSED_DATA_DIR / "dataset_unificado.csv"

def criar_tabelas(cursor):
    """Cria as tabelas no banco de dados."""
    # Tabela para o dataset unificado
    # As colunas serão inferidas do CSV, mas podemos definir tipos específicos se necessário
    # Por simplicidade, vamos criar uma tabela que espelha as colunas do CSV.
    # Idealmente, teríamos uma modelagem mais normalizada (tabelas separadas para IDH, Despesas, Estados, Anos etc.)
    # mas para este projeto, uma tabela unificada simplifica as consultas para o dashboard.
    
    # Obtendo cabeçalhos do CSV para criar a tabela dinamicamente
    if not UNIFIED_DATASET_CSV.exists():
        print(f"❌ ERRO: Arquivo {UNIFIED_DATASET_CSV} não encontrado. "
              f"Execute a fase de processamento de dados primeiro.")
        return False

    df_unified = pd.read_csv(UNIFIED_DATASET_CSV, nrows=0) # Ler apenas o cabeçalho
    cols_with_types = []
    for i, col_name_original in enumerate(df_unified.columns):
        print(f"  Coluna {i}: '{col_name_original}' (Tipo: {type(col_name_original)})")
    
    for col_name in df_unified.columns:
        # Limpeza: remover \n e \r explicitamente, depois strip para espaços nas extremidades.
        clean_col_name = str(col_name).replace("\n", "").replace("\r", "").strip()
        print(f"    -> Nome da coluna CSV original: '{col_name}', Processado para SQL: '{clean_col_name}' (repr: {repr(clean_col_name)})")

        # Simples mapeamento de tipo para SQLite
        # Usar clean_col_name para todas as verificações e para o nome final da coluna SQL
        col_type = "TEXT" # Default
        if clean_col_name.lower() in ["ano", "populacao"]:
            col_type = "INTEGER"
        elif clean_col_name.lower() in ["idh"] or clean_col_name in ['Saúde', 'Educação', 'Assistência Social', 'Infraestrutura']:
            col_type = "REAL"
        
        cols_with_types.append(f'\"{clean_col_name}\" {col_type}')
    
    for i, definition in enumerate(cols_with_types):
        print(f"  Item {i}: {definition}")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS analise_unificada (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {', '.join(cols_with_types)}
    );
    """
    print("--- INÍCIO SQL CREATE TABLE ---")
    print(create_table_sql.strip())
    print("--- FIM SQL CREATE TABLE ---")
    cursor.execute(create_table_sql)
    print("✅ Tabela 'analise_unificada' criada ou já existente.")
    return True

def carregar_dados(conexao, cursor):
    """Carrega os dados do CSV unificado para o banco de dados."""
    if not UNIFIED_DATASET_CSV.exists():
        print(f"❌ ERRO: Arquivo {UNIFIED_DATASET_CSV} não encontrado. "
              f"Execute a fase de processamento de dados primeiro.")
        return False

    print(f"🔄 Carregando dados de {UNIFIED_DATASET_CSV} para o banco de dados...")
    df_unified = pd.read_csv(UNIFIED_DATASET_CSV)

    if df_unified.empty:
        print(f"❌ DataFrame lido de {UNIFIED_DATASET_CSV} está vazio. Abortando carregamento.")
        return False

    # Verificar se a tabela está vazia antes de carregar
    cursor.execute("SELECT COUNT(*) FROM analise_unificada")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"⚠️ Tabela 'analise_unificada' já contém {count} registros. Limpando a tabela antes de recarregar.")
        cursor.execute("DELETE FROM analise_unificada") # Limpar dados antigos
        conexao.commit() # Commit da deleção
        print(f"✅ Tabela 'analise_unificada' limpa.")
        
    # Usar o método to_sql do pandas para carregar os dados
    # Os nomes das colunas no DataFrame devem corresponder exatamente aos da tabela (case-sensitive em alguns BDs, mas SQLite é flexível)
    # É crucial que as colunas no CSV correspondam às definidas em criar_tabelas
    try:
        print(f"⏳ Tentando executar df_unified.to_sql('analise_unificada', if_exists='replace', index=False) com {len(df_unified)} linhas...")
        # Tentar com if_exists='replace' para ver se isso resolve, já que a tabela é limpa antes.
        # 'replace' irá dropar a tabela primeiro se ela existir e criar uma nova.
        df_unified.to_sql("analise_unificada", conexao, if_exists="replace", index=False) 
        conexao.commit() # Commit após a inserção bem-sucedida
        print(f"✅ {len(df_unified)} registros carregados com sucesso na tabela 'analise_unificada' e salvos no BD.")
        return True
    except Exception as e:
        print(f"❌ ERRO DETALHADO ao carregar dados para 'analise_unificada': {repr(e)}")
        print(f"   Tipo do Erro: {type(e)}")
        print(f"   Colunas do DataFrame Pandas que seriam inseridas: {df_unified.columns.tolist()}")
        # Tentar obter o schema da tabela para comparação
        try:
            cursor.execute(f"PRAGMA table_info(analise_unificada)")
            schema_info = cursor.fetchall()
            print("   Schema da tabela 'analise_unificada' no BD:")
            for col_info in schema_info:
                print(f"     {col_info}")
        except Exception as e_schema:
            print(f"     Não foi possível obter o schema da tabela: {repr(e_schema)}")
        return False

def main():
    """Função principal para configurar o banco de dados."""
    print("🚀 Iniciando configuração do banco de dados...")
    
    # Garante que o diretório de dados processados exista
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Conectar ao banco de dados SQLite (ele será criado se não existir)
    try:
        conexao = sqlite3.connect(DB_FILE)
        cursor = conexao.cursor()
        print(f"🔗 Conectado ao banco de dados: {DB_FILE}")

        # Criar tabelas
        if not criar_tabelas(cursor):
            conexao.close()
            print("❌ Falha ao criar tabelas.")
            return False

        # Carregar dados
        if not carregar_dados(conexao, cursor):
            conexao.close()
            print("❌ Falha ao carregar dados.")
            return False
            
        # Salvar (commit) as mudanças e fechar a conexão
        conexao.commit()
        conexao.close()
        print("💾 Mudanças salvas e conexão fechada.")
        print("🎉 Configuração do banco de dados concluída com sucesso!")
        return True

    except sqlite3.Error as e:
        print(f"❌ Erro de SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado durante a configuração do banco de dados: {e}")
        return False

if __name__ == "__main__":
    main() 