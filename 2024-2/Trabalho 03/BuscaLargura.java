import java.util.*;

public class BuscaLargura {

    // Função para realizar a busca em largura (BFS)
    public static void realizarBusca(Grafo grafo, int verticeInicio) {
        int numVertices = grafo.getNumVertices();
        int[][] matrizAdjacencia = grafo.getMatrizAdjacencia();
        
        if (verticeInicio < 0 || verticeInicio >= numVertices) {
            System.out.println("Vértice de origem inválido.");
            return;
        }

        boolean[] visitado = new boolean[numVertices];
        Queue<Integer> fila = new LinkedList<>();
        
        // Iniciar a busca em largura
        fila.add(verticeInicio);
        visitado[verticeInicio] = true;
        System.out.println("Busca em Largura a partir do vértice " + verticeInicio + ":");
        
        while (!fila.isEmpty()) {
            int vertice = fila.poll();
            System.out.print(vertice + " ");

            for (int i = 0; i < numVertices; i++) {
                if (matrizAdjacencia[vertice][i] == 1 && !visitado[i]) {
                    fila.add(i);
                    visitado[i] = true;
                }
            }
        }
        System.out.println();
    }
}
