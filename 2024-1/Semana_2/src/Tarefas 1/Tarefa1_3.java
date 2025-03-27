
import java.util.Scanner;

public class Tarefa1_3 {

    public static void main(String[] args) {
    
        Scanner dados = new Scanner(System.in);

        System.out.println("Insira o valor A:");
        double A = dados.nextDouble();

        System.out.println("Insira o valor B:");
        double B = dados.nextDouble();
        dados.close();

        double soma = A + B;
        double multi = A * B;
            if (A==B) {
                System.out.println(soma);}
            else {
                System.out.println(multi);}
            }
        }


