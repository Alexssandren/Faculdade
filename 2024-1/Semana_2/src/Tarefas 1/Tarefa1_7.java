
import java.util.Scanner;

public class Tarefa1_7 {

    public static void main(String[] args) {

        //Classe de leitura de dados
        Scanner dados = new Scanner(System.in);

        //Leia Peso e Altura de uma pessoa adulta
        System.out.println("Peso (Kg): ");
        double peso = dados.nextDouble();
        
        System.out.print("Altura (metro): ");
        double altura = dados.nextDouble();

        //Formula IMC
        double imc = peso / (altura * altura);

        System.out.printf("IMC = %.2f%n", + imc);
        dados.close();

        //Com If
        if (imc<=18.5)  {
            System.out.println("Abaixo do peso");
        } else if(imc<=25) {
        System.out.println("Peso normal");
        } else if(imc<=30) {
            System.out.println("Acima do peso");
        } else if(imc>30) {
            System.out.println("Obeso");
        }
    }
}