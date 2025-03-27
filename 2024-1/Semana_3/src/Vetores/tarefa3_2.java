package Java.Tarefas3_Vetor;

import java.util.Scanner;

public class tarefa3_2 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);

        int[] numeros = new int [10];
        
        for(int i = 0; i < 10; i++) {
                System.out.println("Insira um valor: ");
                int numero = dados.nextInt();

                while (existenumero(numeros, numero, i)) {
                    System.out.println("Número já inserido. Digite outro: ");
                    numero = dados.nextInt();
                }

                numeros[i] = numero;
            }
        System.out.println("Números inseridos no vetor:");
        for (int num : numeros) {
            System.out.println(num + " ");
        }
    dados.close();
    }
        public static boolean existenumero(int[] vetor, int numero, int indice) {
            for (int i = 0; i < 10; i++) {
                if (vetor[i] == numero) {
                    return true;
                }
            }
            return false;
        }
    }
