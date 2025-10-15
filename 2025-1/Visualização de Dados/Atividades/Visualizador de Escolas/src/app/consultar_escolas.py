import sqlite3

def conectar_banco():
    """Conecta ao banco de dados"""
    return sqlite3.connect('escolas.db')

def mostrar_menu():
    """Mostra o menu de opções"""
    print("\n=== Sistema de Consulta de Escolas ===")
    print("1. Listar todas as regiões")
    print("2. Listar UFs de uma região")
    print("3. Listar municípios de uma UF")
    print("4. Listar escolas de um município")
    print("5. Buscar escola por nome")
    print("0. Sair")
    return input("\nEscolha uma opção: ")

def listar_regioes(conn):
    """Lista todas as regiões"""
    cursor = conn.cursor()
    cursor.execute('SELECT id_regiao, nome_regiao FROM regiao ORDER BY nome_regiao')
    regioes = cursor.fetchall()
    
    print("\n=== Regiões ===")
    for id_regiao, nome in regioes:
        print(f"{id_regiao}. {nome}")

def listar_ufs_regiao(conn):
    """Lista UFs de uma região específica"""
    id_regiao = input("\nDigite o ID da região: ")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id_uf, u.sigla_uf, u.nome_uf 
        FROM uf u 
        WHERE u.id_regiao = ? 
        ORDER BY u.nome_uf
    ''', (id_regiao,))
    
    ufs = cursor.fetchall()
    print(f"\n=== UFs da Região ===")
    for id_uf, sigla, nome in ufs:
        print(f"{id_uf}. {sigla} - {nome}")

def listar_municipios_uf(conn):
    """Lista municípios de uma UF específica"""
    id_uf = input("\nDigite o ID da UF: ")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id_municipio, m.nome_municipio 
        FROM municipio m 
        WHERE m.id_uf = ? 
        ORDER BY m.nome_municipio
    ''', (id_uf,))
    
    municipios = cursor.fetchall()
    print(f"\n=== Municípios da UF ===")
    for id_municipio, nome in municipios:
        print(f"{id_municipio}. {nome}")

def listar_escolas_municipio(conn):
    """Lista escolas de um município específico"""
    id_municipio = input("\nDigite o ID do município: ")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id_escola, e.nome_escola, e.endereco 
        FROM escola e 
        WHERE e.id_municipio = ? 
        ORDER BY e.nome_escola
    ''', (id_municipio,))
    
    escolas = cursor.fetchall()
    print(f"\n=== Escolas do Município ===")
    for id_escola, nome, endereco in escolas:
        endereco_str = f"\n   Endereço: {endereco}" if endereco else ""
        print(f"{id_escola}. {nome}{endereco_str}")

def buscar_escola(conn):
    """Busca escolas por nome"""
    nome = input("\nDigite parte do nome da escola: ")
    nome = f"%{nome}%"
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id_escola, e.nome_escola, m.nome_municipio, u.sigla_uf, r.nome_regiao 
        FROM escola e 
        JOIN municipio m ON e.id_municipio = m.id_municipio 
        JOIN uf u ON m.id_uf = u.id_uf 
        JOIN regiao r ON u.id_regiao = r.id_regiao 
        WHERE e.nome_escola LIKE ? 
        ORDER BY e.nome_escola
    ''', (nome,))
    
    escolas = cursor.fetchall()
    print(f"\n=== Resultados da Busca ===")
    for id_escola, nome, municipio, uf, regiao in escolas:
        print(f"{id_escola}. {nome}")
        print(f"   Localização: {municipio} - {uf} ({regiao})")

def main():
    conn = conectar_banco()
    
    while True:
        opcao = mostrar_menu()
        
        if opcao == '0':
            break
        elif opcao == '1':
            listar_regioes(conn)
        elif opcao == '2':
            listar_ufs_regiao(conn)
        elif opcao == '3':
            listar_municipios_uf(conn)
        elif opcao == '4':
            listar_escolas_municipio(conn)
        elif opcao == '5':
            buscar_escola(conn)
        else:
            print("\nOpção inválida!")
    
    conn.close()
    print("\nAté logo!")

if __name__ == '__main__':
    main() 