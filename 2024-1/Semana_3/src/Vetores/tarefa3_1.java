package Java.Tarefas3_Vetor;

import java.util.Scanner;

public class tarefa3_1 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);

        //a
        int[] A = new int [6];
        A[0] = 1; A[1] = 0; A[2] = 5; A[3] = -2; A[4] = -5; A[5] = 7;
        
        //b
        int soma = A[0] + A[1] + A[5];
        System.out.println("A soma é: " + soma);

        //c
        A[3] = 100;

        //d
        int valor;
        for(int i = 0; i < 6; i++){
        valor = A[i];
        System.out.println(valor);
        }
        dados.close();
    }
}
