package Java.Tarefas3_Matriz;

import java.util.Scanner;

public class tarefa3_3 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Ler a matriz 3x6 com valores reais
        double[][] matriz = new double[3][6];
        System.out.println("Digite os valores da matriz 3x6:");
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 6; j++) {
                System.out.print("Digite o elemento da posição [" + i + "][" + j + "]: ");
                matriz[i][j] = scanner.nextDouble();
            }
        }

        // Imprimir a soma de todos os elementos das colunas ímpares
        double somaColunasImpares = 0;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 6; j++) {
                if (j % 2 != 0) { // Colunas ímpares
                    somaColunasImpares += matriz[i][j];
                }
            }
        }
        System.out.println("\nSoma dos elementos das colunas ímpares: " + somaColunasImpares);

        // Calcular a média aritmética dos elementos da segunda e quarta colunas
        double somaSegundaColuna = 0, somaQuartaColuna = 0;
        for (int i = 0; i < 3; i++) {
            somaSegundaColuna += matriz[i][1]; // Segunda coluna
            somaQuartaColuna += matriz[i][3];  // Quarta coluna
        }
        double mediaSegundaQuartaColunas = (somaSegundaColuna + somaQuartaColuna) / 6;
        System.out.println("Média aritmética dos elementos da segunda e quarta colunas: " + mediaSegundaQuartaColunas);

        // Substituir os valores da sexta coluna pela soma dos valores das colunas 1 e 2
        for (int i = 0; i < 3; i++) {
            matriz[i][5] = matriz[i][0] + matriz[i][1];
        }

        // Imprimir a matriz modificada
        System.out.println("\nMatriz modificada:");
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 6; j++) {
                System.out.print(matriz[i][j] + "\t");
            }
            System.out.println();
        }
    scanner.close();
    }
}
