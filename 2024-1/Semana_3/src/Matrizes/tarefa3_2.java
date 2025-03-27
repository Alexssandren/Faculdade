package Java.Tarefas3_Matriz;

import java.util.Scanner;

public class tarefa3_2 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Ler as notas dos alunos
        double[][] notas = new double[10][3];
        for (int i = 0; i < 10; i++) {
            System.out.println("Digite as notas do aluno " + (i + 1) + ":");
            for (int j = 0; j < 3; j++) {
                System.out.print("Nota " + (j + 1) + ": ");
                notas[i][j] = scanner.nextDouble();
            }
        }

        // Contagem de alunos cuja pior nota é em cada prova
        int piorNotaProva1 = 0, piorNotaProva2 = 0, piorNotaProva3 = 0;
        for (int i = 0; i < 10; i++) {
            double menorNota = Math.min(Math.min(notas[i][0], notas[i][1]), notas[i][2]);
            if (menorNota == notas[i][0]) {
                piorNotaProva1++;
            } else if (menorNota == notas[i][1]) {
                piorNotaProva2++;
            } else {
                piorNotaProva3++;
            }
        }

        scanner.close();
        // Exibir resultados
        System.out.println("\nNúmero de alunos cuja pior nota foi na prova 1: " + piorNotaProva1);
        System.out.println("Número de alunos cuja pior nota foi na prova 2: " + piorNotaProva2);
        System.out.println("Número de alunos cuja pior nota foi na prova 3: " + piorNotaProva3);
    }
}
