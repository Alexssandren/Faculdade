
import java.util.Scanner;

public class tarefa2_5 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);
        
        System.out.println("Digite 10 números:");
        double numero = 0;

        for (int i = 0; i < 10; i ++){
            System.out.println("Insira o valor " + (i + 1) + ":");
            numero += dados.nextDouble();
        }

        dados.close();
        double media = (numero/10);
        System.out.println("A média aritmética dos valores digitados é: " + media);
    }
}
