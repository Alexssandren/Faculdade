package Java.Tarefas3_Matriz;

import java.util.Scanner;

public class tarefa3_1 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Ler a matriz 5x5
        int[][] matriz = new int[5][5];
        System.out.println("Digite os elementos da matriz 5x5:");
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                System.out.print("Digite o elemento da posição [" + i + "][" + j + "]: ");
                matriz[i][j] = scanner.nextInt();
            }
        }

        // Ler o valor a ser buscado
        System.out.print("\nDigite o valor a ser buscado: ");
        int valorBuscado = scanner.nextInt();

        // Buscar o valor na matriz
        boolean encontrado = false;
        int linha = -1, coluna = -1;
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                if (matriz[i][j] == valorBuscado) {
                    encontrado = true;
                    linha = i;
                    coluna = j;
                    break;
                }
            }
            if (encontrado) {
                break;
            }
        }

        // Exibir resultado da busca
        if (encontrado) {
            System.out.println("O valor " + valorBuscado + " foi encontrado na posição [" + linha + "][" + coluna + "]");
        } else {
            System.out.println("O valor " + valorBuscado + " não foi encontrado na matriz.");
        }
        scanner.close();
    }
}
