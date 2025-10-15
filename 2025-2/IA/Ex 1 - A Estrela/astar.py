from queue import PriorityQueue
import math

def heuristica(a, b):
    """Calcula a distância de Manhattan entre dois pontos"""
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def get_vizinhos(pos, grid):
    """Retorna os vizinhos válidos de uma posição"""
    vizinhos = []
    # Movimentos possíveis: cima, baixo, esquerda, direita
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        novo_x = pos[0] + dx
        novo_y = pos[1] + dy
        
        # Verifica se a posição é válida
        if (0 <= novo_x < len(grid) and 
            0 <= novo_y < len(grid[0]) and 
            grid[novo_x][novo_y] != '#'):  # '#' representa obstáculo
            vizinhos.append((novo_x, novo_y))
    
    return vizinhos

def a_estrela(grid, inicio, fim):
    """
    Implementa o algoritmo A*
    grid: matriz onde 0 representa espaço livre e # representa obstáculo
    inicio: tupla (x, y) representando o ponto inicial
    fim: tupla (x, y) representando o objetivo
    """
    fronteira = PriorityQueue()
    fronteira.put((0, inicio))
    
    # Dicionário para guardar de onde viemos
    veio_de = {inicio: None}
    
    # Dicionário para guardar o custo do caminho
    custo_g = {inicio: 0}
    
    while not fronteira.empty():
        _, atual = fronteira.get()
        
        # Se chegamos ao objetivo, reconstruir o caminho
        if atual == fim:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = veio_de[atual]
            return caminho[::-1]  # Inverte o caminho para ir do início ao fim
        
        # Explorar vizinhos
        for vizinho in get_vizinhos(atual, grid):
            novo_custo = custo_g[atual] + 1  # Custo de movimento é 1
            
            # Se encontramos um caminho melhor para o vizinho
            if vizinho not in custo_g or novo_custo < custo_g[vizinho]:
                custo_g[vizinho] = novo_custo
                prioridade = novo_custo + heuristica(vizinho, fim)
                fronteira.put((prioridade, vizinho))
                veio_de[vizinho] = atual
    
    return None  # Não encontrou caminho

# Exemplo de uso
def main():
    # Criar um grid de exemplo (0 = caminho livre, # = obstáculo)
    grid = [
        ["0", "0", "0", "0", "0"],
        ["#", "#", "0", "#", "0"],
        ["0", "0", "0", "0", "0"],
        ["0", "#", "#", "#", "0"],
        ["0", "0", "0", "0", "0"]
    ]
    
    inicio = (0, 0)  # Ponto inicial
    fim = (2, 3)     # Objetivo
    
    # Encontrar caminho
    caminho = a_estrela(grid, inicio, fim)
    
    # Imprimir o resultado
    if caminho:
        print("Caminho encontrado:")
        # Criar uma cópia do grid para mostrar o caminho
        grid_com_caminho = [linha[:] for linha in grid]
        for x, y in caminho:
            if (x, y) != inicio and (x, y) != fim:
                grid_com_caminho[x][y] = "*"
        
        # Marcar início e fim
        grid_com_caminho[inicio[0]][inicio[1]] = "S"
        grid_com_caminho[fim[0]][fim[1]] = "E"
        
        # Imprimir o grid
        for linha in grid_com_caminho:
            print(" ".join(linha))
    else:
        print("Caminho não encontrado!")

if __name__ == "__main__":
    main()
