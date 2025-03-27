import java.util.Scanner;

public class tarefa2_4 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);
        System.out.println(("Digite o valor A:"));
        int A = dados.nextInt();

        System.out.println(("Insira o valor B:"));
        int B = dados.nextInt();
    
        long fatorial1 = calcularFatorial(A);
        long fatorial2 = calcularFatorial(B);

        System.out.println("O fatorial de " + A + " é: " + fatorial1);
        System.out.println("O fatorial de " + B + " é: " + fatorial2);

        dados.close();
    }

    public static long calcularFatorial(int numero) {
        if (numero == 0 || numero == 1) {
            return 1;
        } else {
            long resultado = 1;
            for (int i = 2; i <= numero; i++) {
                resultado *= i;
            }
            return resultado;
        }
    }
}