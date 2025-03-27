
import java.util.Scanner;

//Faça um programa que leia o nome, o sexo e o estado civil de uma pessoa. Caso sexo seja “F” e
//estado civil seja “CASADA”, solicitar o tempo de casada (anos).

public class Tarefa1_2 {

    public static void main(String[] args) {

        //Classe de leitura de dados
        Scanner scanner = new Scanner(System.in);

        System.out.println("Insira seu nome:");
        String nome = scanner.nextLine();
        
        System.out.println("Insira seu sexo (M) ou (F):");
        char sexo = scanner.nextLine().charAt(0);

        System.out.println("Digite o estado civil (solteiro(a)/casado(a)/divorciado(a)/viuvo(a)): ");
        String ec = scanner.nextLine();

        //If
        if (ec.equals("casada")) {
            System.out.print("Insira o tempo que está casada (anos): ");
            int tempo = scanner.nextInt(); }
        scanner.close();
    }
}
