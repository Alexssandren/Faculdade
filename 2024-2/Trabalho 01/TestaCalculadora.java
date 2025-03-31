import java.util.Scanner;

public class TestaCalculadora {
    public static void main(String[] args) {
        Calculadora calculadora = new Calculadora();
        Scanner scanner = new Scanner(System.in);
        int opcao;

        do {
            System.out.println("Escolha uma opcao:");
            System.out.println("1. Empilhar valor real");
            System.out.println("2. Empilhar operador");
            System.out.println("3. Realizar calculo");
            System.out.println("4. Imprimir pilhas");
            System.out.println("5. Sair");
            opcao = scanner.nextInt();
            scanner.nextLine();

            switch (opcao) {
                case 1:
                    System.out.println("Digite um valor real:");
                    double valor = scanner.nextDouble();
                    calculadora.empilharValor(valor);
                    break;
                case 2:
                    System.out.println("Digite um operador (+, -, *, /):");
                    char operador = scanner.nextLine().charAt(0);
                    calculadora.empilharOperador(operador);
                    break;
                case 3:
                    calculadora.realizarCalculo();
                    break;
                case 4:
                    calculadora.imprimirPilhas();
                    break;
                case 5:
                    System.out.println("Saindo...");
                    break;
                default:
                    System.out.println("Opção invalida!");
            }
        } while (opcao != 5);

        scanner.close();
    }
}
