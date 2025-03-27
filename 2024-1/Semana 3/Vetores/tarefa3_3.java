package Java.Tarefas3_Vetor;
import java.util.ArrayList;
import java.util.Scanner;

public class tarefa3_3 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Digite os elementos do primeiro vetor:");
        int[] vetor1 = lerVetor(scanner);

        System.out.println("\nDigite os elementos do segundo vetor:");
        int[] vetor2 = lerVetor(scanner);

        int[] resultado = intersecaoVetores(vetor1, vetor2);
        System.out.print("\nA interseção entre os dois vetores é: ");
        imprimirVetor(resultado);
    }

    public static int[] lerVetor(Scanner scanner) {
        int[] vetor = new int[10];
        for (int i = 0; i < 10; i++) {
            System.out.print("Digite o elemento " + (i + 1) + ": ");
            vetor[i] = scanner.nextInt();
        }
        return vetor;
    }

    public static int[] intersecaoVetores(int[] vetor1, int[] vetor2) {
        ArrayList<Integer> intersecao = new ArrayList<>();
        for (int elemento : vetor1) {
            if (contemElemento(vetor2, elemento) && !intersecao.contains(elemento)) {
                intersecao.add(elemento);
            }
        }
        int[] resultado = new int[intersecao.size()];
        for (int i = 0; i < intersecao.size(); i++) {
            resultado[i] = intersecao.get(i);
        }
        return resultado;
    }

    public static boolean contemElemento(int[] vetor, int elemento) {
        for (int valor : vetor) {
            if (valor == elemento) {
                return true;
            }
        }
        return false;
    }

    public static void imprimirVetor(int[] vetor) {
        System.out.print("[");
        for (int i = 0; i < vetor.length; i++) {
            System.out.print(vetor[i]);
            if (i < vetor.length - 1) {
                System.out.print(", ");
            }
        }
        System.out.println("]");
    }
}
