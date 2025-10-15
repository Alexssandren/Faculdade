import java.util.Scanner;

public class TestaGrafo {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Grafo grafo = null;
        int opcao;

        while (true) {
            System.out.println("\nMenu:");
            System.out.println("1) Criar um grafo");
            System.out.println("2) Adicionar Aresta");
            System.out.println("3) Remover Aresta");
            System.out.println("4) Adicionar Vértice");
            System.out.println("5) Remover Vértice");
            System.out.println("6) Imprimir Matriz de Adjacência");
            System.out.println("7) Realizar Busca em Largura");
            System.out.println("8) Sair");
            System.out.print("Escolha uma opção: ");
            opcao = scanner.nextInt();

            switch (opcao) {
                case 1:
                    System.out.print("Digite o número de vértices do grafo: ");
                    int tamanho = scanner.nextInt();
                    grafo = new Grafo(tamanho);
                    System.out.println("Grafo criado com " + tamanho + " vértices.");
                    break;

                case 2:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    System.out.print("Digite o vértice de origem: ");
                    int origem = scanner.nextInt();
                    System.out.print("Digite o vértice de destino: ");
                    int destino = scanner.nextInt();
                    grafo.adicionarAresta(origem, destino);
                    break;

                case 3:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    System.out.print("Digite o vértice de origem: ");
                    origem = scanner.nextInt();
                    System.out.print("Digite o vértice de destino: ");
                    destino = scanner.nextInt();
                    grafo.removerAresta(origem, destino);
                    break;

                case 4:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    grafo.adicionarVertice();
                    System.out.println("Vértice adicionado.");
                    break;

                case 5:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    System.out.print("Digite o vértice para remover: ");
                    int vertice = scanner.nextInt();
                    grafo.removerVertice(vertice);
                    break;

                case 6:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    grafo.imprimirMatrizAdjacencia();
                    break;

                case 7:
                    if (grafo == null) {
                        System.out.println("Você precisa criar um grafo primeiro.");
                        break;
                    }
                    System.out.print("Digite o vértice de origem para a busca em largura: ");
                    int verticeInicio = scanner.nextInt();
                    BuscaLargura.realizarBusca(grafo, verticeInicio);
                    break;

                case 8:
                    System.out.println("Saindo...");
                    scanner.close();
                    return;

                default:
                    System.out.println("Opção inválida.");
                    break;
            }
        }
    }
}
