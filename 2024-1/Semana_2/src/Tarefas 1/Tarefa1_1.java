
import java.util.Scanner;

//Faça um programa que leia os valores A, B, C e imprima na tela se a soma de A + B é menor que C.


public class Tarefa1_1 {

    public static void main(String[] args) {
        
        //Classe de leitura de dados
        @SuppressWarnings("resource")
        Scanner dados = new Scanner(System.in);
        
        System.out.println("Insira o valor A:");
        double A = dados.nextDouble();

        System.out.println("Insira o valor B:");
        double B = dados.nextDouble();

        System.out.println("Insira o valor C:");
        double C = dados.nextDouble();

        //Soma de A e B
        double soma = A + B;

        //If
        if (soma<C)  {
            System.out.println("A soma de A com B é menor que C");
        } else if (soma>C)  {
            System.out.println("A soma de A com B é maior que C");
        }
    }
}
