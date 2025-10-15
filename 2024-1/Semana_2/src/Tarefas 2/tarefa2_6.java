import java.util.Scanner;

public class tarefa2_6 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);
        
        System.out.println("Digite 10 números:");
        double numero = 0;
        double soma = 0;

        for (int i = 0; i < 10; i ++){
            System.out.println("Insira o valor " + (i + 1) + ":");
            numero = dados.nextDouble();
            if(numero < 40){
                soma += numero;
            }
        }

        dados.close();
        System.out.println(soma);
    }
}