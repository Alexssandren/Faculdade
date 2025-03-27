import java.util.Scanner;

public class Tarefa1_5 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Solicita ao usuário que insira um número
        System.out.print("Insira um número inteiro: ");
        int numero = scanner.nextInt();

        // Verifica se o número é par ou ímpar e faz a multiplicação correspondente
        int resultado;
        if (numero % 2 == 0) {
            resultado = numero * 5;
            System.out.println("O número é par. Multiplicando por 5: " + resultado);
        } else {
            resultado = numero * 7;
            System.out.println("O número é ímpar. Multiplicando por 7: " + resultado);
        }
        
        scanner.close();
    }
}
