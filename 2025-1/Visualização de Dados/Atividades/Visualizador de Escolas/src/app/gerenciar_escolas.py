import sqlite3
import matplotlib.pyplot as plt

def conectar_banco():
    """Conecta ao banco de dados"""
    return sqlite3.connect('escolas.db')

def mostrar_menu():
    """Mostra o menu de opções"""
    print("\n=== Sistema de Gerenciamento de Escolas ===")
    print("1. Adicionar nova escola")
    print("2. Editar escola existente")
    print("3. Remover escola")
    print("4. Gerar gráficos")
    print("0. Sair")
    return input("\nEscolha uma opção: ")

def selecionar_municipio(conn):
    """Auxilia na seleção de um município"""
    cursor = conn.cursor()
    
    # Lista regiões
    cursor.execute('SELECT id_regiao, nome_regiao FROM regiao ORDER BY nome_regiao')
    regioes = cursor.fetchall()
    print("\n=== Regiões ===")
    for id_regiao, nome in regioes:
        print(f"{id_regiao}. {nome}")
    
    id_regiao = input("\nDigite o ID da região: ")
    
    # Lista UFs da região
    cursor.execute('SELECT id_uf, sigla_uf, nome_uf FROM uf WHERE id_regiao = ? ORDER BY nome_uf', (id_regiao,))
    ufs = cursor.fetchall()
    print("\n=== UFs da Região ===")
    for id_uf, sigla, nome in ufs:
        print(f"{id_uf}. {sigla} - {nome}")
    
    id_uf = input("\nDigite o ID da UF: ")
    
    # Lista municípios da UF
    cursor.execute('SELECT id_municipio, nome_municipio FROM municipio WHERE id_uf = ? ORDER BY nome_municipio', (id_uf,))
    municipios = cursor.fetchall()
    print("\n=== Municípios da UF ===")
    for id_municipio, nome in municipios:
        print(f"{id_municipio}. {nome}")
    
    return input("\nDigite o ID do município: ")

def adicionar_escola(conn):
    """Adiciona uma nova escola"""
    print("\n=== Adicionar Nova Escola ===")
    
    # Seleciona o município
    id_municipio = selecionar_municipio(conn)
    
    # Coleta dados da escola
    nome = input("\nNome da escola: ")
    endereco = input("Endereço (opcional, pressione Enter para pular): ").strip() or None
    
    # Insere a escola
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO escola (nome_escola, endereco, id_municipio) VALUES (?, ?, ?)',
        (nome, endereco, id_municipio)
    )
    conn.commit()
    print("\nEscola adicionada com sucesso!")

def editar_escola(conn):
    """Edita uma escola existente"""
    print("\n=== Editar Escola ===")
    
    # Busca a escola
    nome_busca = input("Digite parte do nome da escola que deseja editar: ")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id_escola, e.nome_escola, e.endereco, m.nome_municipio, u.sigla_uf
        FROM escola e
        JOIN municipio m ON e.id_municipio = m.id_municipio
        JOIN uf u ON m.id_uf = u.id_uf
        WHERE e.nome_escola LIKE ?
        ORDER BY e.nome_escola
    ''', (f'%{nome_busca}%',))
    
    escolas = cursor.fetchall()
    if not escolas:
        print("\nNenhuma escola encontrada!")
        return
    
    print("\n=== Escolas Encontradas ===")
    for id_escola, nome, endereco, municipio, uf in escolas:
        endereco_str = f", Endereço: {endereco}" if endereco else ""
        print(f"{id_escola}. {nome} ({municipio} - {uf}{endereco_str})")
    
    id_escola = input("\nDigite o ID da escola que deseja editar: ")
    
    # Coleta novos dados
    novo_nome = input("Novo nome (pressione Enter para manter o atual): ").strip()
    novo_endereco = input("Novo endereço (pressione Enter para manter o atual): ").strip()
    
    # Atualiza os dados
    updates = []
    params = []
    if novo_nome:
        updates.append("nome_escola = ?")
        params.append(novo_nome)
    if novo_endereco:
        updates.append("endereco = ?")
        params.append(novo_endereco)
    
    if updates:
        params.append(id_escola)
        cursor.execute(
            f'UPDATE escola SET {", ".join(updates)} WHERE id_escola = ?',
            tuple(params)
        )
        conn.commit()
        print("\nEscola atualizada com sucesso!")
    else:
        print("\nNenhuma alteração realizada!")

def remover_escola(conn):
    """Remove uma escola"""
    print("\n=== Remover Escola ===")
    
    # Busca a escola
    nome_busca = input("Digite parte do nome da escola que deseja remover: ")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id_escola, e.nome_escola, m.nome_municipio, u.sigla_uf
        FROM escola e
        JOIN municipio m ON e.id_municipio = m.id_municipio
        JOIN uf u ON m.id_uf = u.id_uf
        WHERE e.nome_escola LIKE ?
        ORDER BY e.nome_escola
    ''', (f'%{nome_busca}%',))
    
    escolas = cursor.fetchall()
    if not escolas:
        print("\nNenhuma escola encontrada!")
        return
    
    print("\n=== Escolas Encontradas ===")
    for id_escola, nome, municipio, uf in escolas:
        print(f"{id_escola}. {nome} ({municipio} - {uf})")
    
    id_escola = input("\nDigite o ID da escola que deseja remover: ")
    confirmacao = input(f"Tem certeza que deseja remover a escola? (s/N): ")
    
    if confirmacao.lower() == 's':
        cursor.execute('DELETE FROM escola WHERE id_escola = ?', (id_escola,))
        conn.commit()
        print("\nEscola removida com sucesso!")
    else:
        print("\nOperação cancelada!")

def gerar_graficos(conn):
    """Gera gráficos relacionados ao dataset"""
    cursor = conn.cursor()
    
    # 1. Número de escolas por região
    print("\nGerando gráfico de escolas por região...")
    cursor.execute('''
        SELECT r.nome_regiao, COUNT(e.id_escola) as total
        FROM regiao r
        JOIN uf u ON r.id_regiao = u.id_regiao
        JOIN municipio m ON u.id_uf = m.id_uf
        JOIN escola e ON m.id_municipio = e.id_municipio
        GROUP BY r.nome_regiao
        ORDER BY total DESC
    ''')
    dados = cursor.fetchall()
    regioes = [r[0] for r in dados]
    totais = [r[1] for r in dados]
    
    plt.figure(figsize=(10, 6))
    plt.bar(regioes, totais)
    plt.title('Número de Escolas por Região')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('escolas_por_regiao.png')
    plt.close()
    
    # 2. Número de escolas por UF (top 10)
    print("Gerando gráfico de escolas por UF...")
    cursor.execute('''
        SELECT u.sigla_uf, COUNT(e.id_escola) as total
        FROM uf u
        JOIN municipio m ON u.id_uf = m.id_uf
        JOIN escola e ON m.id_municipio = e.id_municipio
        GROUP BY u.sigla_uf
        ORDER BY total DESC
        LIMIT 10
    ''')
    dados = cursor.fetchall()
    ufs = [r[0] for r in dados]
    totais = [r[1] for r in dados]
    
    plt.figure(figsize=(10, 6))
    plt.bar(ufs, totais)
    plt.title('Número de Escolas por UF (Top 10)')
    plt.tight_layout()
    plt.savefig('escolas_por_uf.png')
    plt.close()
    
    # 3. Número de escolas por município (top 10)
    print("Gerando gráfico de escolas por município...")
    cursor.execute('''
        SELECT m.nome_municipio || ' - ' || u.sigla_uf as municipio, COUNT(e.id_escola) as total
        FROM municipio m
        JOIN uf u ON m.id_uf = u.id_uf
        JOIN escola e ON m.id_municipio = e.id_municipio
        GROUP BY m.id_municipio
        ORDER BY total DESC
        LIMIT 10
    ''')
    dados = cursor.fetchall()
    municipios = [r[0] for r in dados]
    totais = [r[1] for r in dados]
    
    plt.figure(figsize=(12, 6))
    plt.bar(municipios, totais)
    plt.title('Número de Escolas por Município (Top 10)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('escolas_por_municipio.png')
    plt.close()
    
    print("\nGráficos gerados com sucesso!")
    print("Arquivos salvos: escolas_por_regiao.png, escolas_por_uf.png, escolas_por_municipio.png")

def main():
    conn = conectar_banco()
    
    while True:
        opcao = mostrar_menu()
        
        if opcao == '0':
            break
        elif opcao == '1':
            adicionar_escola(conn)
        elif opcao == '2':
            editar_escola(conn)
        elif opcao == '3':
            remover_escola(conn)
        elif opcao == '4':
            gerar_graficos(conn)
        else:
            print("\nOpção inválida!")
    
    conn.close()
    print("\nAté logo!")

if __name__ == '__main__':
    main() 