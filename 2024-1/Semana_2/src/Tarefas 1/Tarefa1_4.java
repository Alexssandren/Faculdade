import java.util.Scanner;

public class Tarefa1_4 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Solicita ao usuário que insira dois valores booleanos
        System.out.print("Insira o primeiro valor booleano (true/false): ");
        boolean valor1 = scanner.nextBoolean();
        System.out.print("Insira o segundo valor booleano (true/false): ");
        boolean valor2 = scanner.nextBoolean();

        // Verifica se ambos os valores são VERDADEIROS ou FALSOS
        if (valor1 && valor2) {
            System.out.println("Ambos os valores são VERDADEIROS.");
        } else if (!valor1 && !valor2) {
            System.out.println("Ambos os valores são FALSOS.");
        } else {
            System.out.println("Um dos valores é VERDADEIRO e o outro é FALSO.");
        }
        
        scanner.close();
    }
}

