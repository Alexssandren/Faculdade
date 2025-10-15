import java.util.Scanner;

public class Tarefa1_8 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Solicita ao usuário que insira o preço do produto
        System.out.print("Insira o preço do produto: ");
        double preco = scanner.nextDouble();

        // Solicita ao usuário que escolha a condição de pagamento
        System.out.println("Escolha a condição de pagamento:");
        System.out.println("1 - À vista em dinheiro ou cheque, recebe 10% de desconto");
        System.out.println("2 - À vista no cartão de crédito, recebe 15% de desconto");
        System.out.println("3 - Em duas vezes, preço normal de etiqueta sem juros");
        System.out.println("4 - Em duas vezes, preço normal de etiqueta mais juros de 10%");
        int opcao = scanner.nextInt();

        // Calcula o valor a ser pago de acordo com a condição de pagamento escolhida
        double valorFinal = 0.0;
        switch (opcao) {
            case 1:
                valorFinal = preco * 0.9; // 10% de desconto
                break;
            case 2:
                valorFinal = preco * 0.85; // 15% de desconto
                break;
            case 3:
                valorFinal = preco; // Sem juros
                System.out.println("O valor será pago em duas vezes de: " + preco / 2);
                break;
            case 4:
                valorFinal = preco * 1.1; // 10% de juros
                System.out.println("O valor será pago em duas vezes de: " + (preco * 1.1) / 2);
                break;
            default:
                System.out.println("Opção inválida.");
        }

        // Exibe o valor final a ser pago
        System.out.println("Valor a ser pago: " + valorFinal);

        scanner.close();
    }
}
