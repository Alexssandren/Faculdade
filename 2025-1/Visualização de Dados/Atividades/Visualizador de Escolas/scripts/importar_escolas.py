import sqlite3
import csv
import os

def criar_banco():
    """Cria o banco de dados e as tabelas"""
    db_path = os.path.join('data', 'processed', 'escolas.db')
    schema_path = os.path.join('src', 'database', 'schema.sql')
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as sql_file:
        conn.executescript(sql_file.read())
    return conn

def importar_dados(arquivo_csv):
    """Importa os dados do CSV para o banco SQLite"""
    # Conecta ao banco
    conn = criar_banco()
    cursor = conn.cursor()
    
    # Lê o CSV
    with open(arquivo_csv, 'r', encoding='latin1') as f:
        # Pula o cabeçalho
        reader = csv.reader(f, delimiter=';')
        colunas = next(reader)
        
        # Índices das colunas que precisamos
        idx_regiao = colunas.index('NO_REGIAO')
        idx_uf = colunas.index('NO_UF')
        idx_sigla_uf = colunas.index('SG_UF')
        idx_municipio = colunas.index('NO_MUNICIPIO')
        idx_escola = colunas.index('NO_ENTIDADE')
        idx_endereco = colunas.index('DS_ENDERECO')
        idx_bairro = colunas.index('NO_BAIRRO')
        
        # Dicionários para armazenar IDs
        regioes = {}
        ufs = {}
        municipios = {}
        
        # Processa cada linha
        for linha in reader:
            # Região
            regiao = linha[idx_regiao]
            if regiao not in regioes:
                cursor.execute(
                    'INSERT INTO regiao (nome_regiao) VALUES (?)',
                    (regiao,)
                )
                regioes[regiao] = cursor.lastrowid
            
            # UF
            uf_nome = linha[idx_uf]
            if uf_nome not in ufs:
                cursor.execute(
                    'INSERT INTO uf (nome_uf, sigla_uf, id_regiao) VALUES (?, ?, ?)',
                    (uf_nome, linha[idx_sigla_uf], regioes[regiao])
                )
                ufs[uf_nome] = cursor.lastrowid
            
            # Município
            municipio = (linha[idx_municipio], ufs[uf_nome])
            if municipio not in municipios:
                cursor.execute(
                    'INSERT INTO municipio (nome_municipio, id_uf) VALUES (?, ?)',
                    municipio
                )
                municipios[municipio] = cursor.lastrowid
            
            # Escola
            endereco = None
            if linha[idx_endereco] and linha[idx_bairro]:
                endereco = f"{linha[idx_endereco]}, {linha[idx_bairro]}"
            
            cursor.execute(
                'INSERT INTO escola (nome_escola, endereco, id_municipio) VALUES (?, ?, ?)',
                (linha[idx_escola], endereco, municipios[municipio])
            )
    
    conn.commit()
    conn.close()
    print("Importação concluída com sucesso!")

if __name__ == '__main__':
    # Usa o arquivo definido na variável de ambiente ou o padrão
    arquivo_csv = os.getenv('ARQUIVO_CSV', 'microdados_ed_basica_2024.csv')
    importar_dados(arquivo_csv) 