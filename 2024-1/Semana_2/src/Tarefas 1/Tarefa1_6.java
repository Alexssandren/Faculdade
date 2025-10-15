import java.util.Scanner;

public class Tarefa1_6 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Solicita ao usuário que insira três valores inteiros diferentes
        System.out.print("Insira o primeiro valor inteiro: ");
        int valor1 = scanner.nextInt();
        System.out.print("Insira o segundo valor inteiro: ");
        int valor2 = scanner.nextInt();
        System.out.print("Insira o terceiro valor inteiro: ");
        int valor3 = scanner.nextInt();

        // Encontra o maior valor
        int max = Math.max(Math.max(valor1, valor2), valor3);
        // Encontra o menor valor
        int min = Math.min(Math.min(valor1, valor2), valor3);
        // Calcula o valor restante (o valor do meio)
        int meio = valor1 + valor2 + valor3 - max - min;

        // Imprime os valores em ordem decrescente
        System.out.println("Valores em ordem decrescente: " + max + ", " + meio + ", " + min);
        
        scanner.close();
    }
}
