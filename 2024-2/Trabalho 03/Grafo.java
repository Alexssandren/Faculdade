public class Grafo {

    private int[][] matrizAdjacencia;
    private int numVertices;

    // Construtor para criar um grafo com um número de vértices
    public Grafo(int tamanho) {
        this.numVertices = tamanho;
        this.matrizAdjacencia = new int[tamanho][tamanho];
    }

    // Função para adicionar uma aresta
    public void adicionarAresta(int origem, int destino) {
        if (origem >= 0 && origem < numVertices && destino >= 0 && destino < numVertices) {
            matrizAdjacencia[origem][destino] = 1;
            matrizAdjacencia[destino][origem] = 1; // Grafo não direcionado
        } else {
            System.out.println("Vértice inválido.");
        }
    }

    // Função para remover uma aresta
    public void removerAresta(int origem, int destino) {
        if (origem >= 0 && origem < numVertices && destino >= 0 && destino < numVertices) {
            matrizAdjacencia[origem][destino] = 0;
            matrizAdjacencia[destino][origem] = 0; // Grafo não direcionado
        } else {
            System.out.println("Vértice inválido.");
        }
    }

    // Função para adicionar um vértice
    public void adicionarVertice() {
        int[][] novaMatriz = new int[numVertices + 1][numVertices + 1];
        
        // Copiar a matriz antiga para a nova matriz
        for (int i = 0; i < numVertices; i++) {
            for (int j = 0; j < numVertices; j++) {
                novaMatriz[i][j] = matrizAdjacencia[i][j];
            }
        }

        matrizAdjacencia = novaMatriz;
        numVertices++;
    }

    // Função para remover um vértice
    public void removerVertice(int vertice) {
        if (vertice >= 0 && vertice < numVertices) {
            int[][] novaMatriz = new int[numVertices - 1][numVertices - 1];
            
            for (int i = 0, newI = 0; i < numVertices; i++) {
                if (i == vertice) continue;
                for (int j = 0, newJ = 0; j < numVertices; j++) {
                    if (j == vertice) continue;
                    novaMatriz[newI][newJ] = matrizAdjacencia[i][j];
                    newJ++;
                }
                if (i != vertice) newI++;
            }
            
            matrizAdjacencia = novaMatriz;
            numVertices--;
        } else {
            System.out.println("Vértice inválido.");
        }
    }

    // Função para imprimir a matriz de adjacência
    public void imprimirMatrizAdjacencia() {
        System.out.println("Matriz de Adjacência:");
        for (int i = 0; i < numVertices; i++) {
            for (int j = 0; j < numVertices; j++) {
                System.out.print(matrizAdjacencia[i][j] + " ");
            }
            System.out.println();
        }
    }

    // Getter para o número de vértices
    public int getNumVertices() {
        return numVertices;
    }

    // Getter para a matriz de adjacência
    public int[][] getMatrizAdjacencia() {
        return matrizAdjacencia;
    }
}
