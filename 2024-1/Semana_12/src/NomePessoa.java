import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class NomePessoa {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String nome;

        try (BufferedWriter writer = new BufferedWriter(new FileWriter("nomes.txt", true))) {
            while (true) {
                System.out.print("Digite um nome (ou SAIR para encerrar): ");
                nome = scanner.nextLine();

                if (nome.equalsIgnoreCase("SAIR")) {
                    break;
                }

                writer.write(nome);
                writer.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        System.out.println("Nomes gravados no arquivo nomes.txt.");

        // Leitura dos nomes do arquivo
        System.out.println("\nNomes gravados no arquivo:");
        try (Scanner fileReader = new Scanner(new java.io.File("nomes.txt"))) {
            while (fileReader.hasNextLine()) {
                System.out.println(fileReader.nextLine());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    scanner.close();
    }
}
