import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.Scanner;
import java.util.Set;

public class VerificaNome {
    public static void main(String[] args) {
        Set<String> nomes = new HashSet<>();

        // Ler nomes do arquivo e armazenar no conjunto
        try (BufferedReader reader = new BufferedReader(new FileReader("nomes.txt"))) {
            String linha;
            while ((linha = reader.readLine()) != null) {
                nomes.add(linha.trim());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        Scanner scanner = new Scanner(System.in);
        System.out.print("Digite um nome para verificar (ou SAIR para encerrar): ");
        String nome = scanner.nextLine().trim();

        while (!nome.equalsIgnoreCase("SAIR")) {
            if (nomes.contains(nome)) {
                System.out.println("Nome já cadastrado.");
            } else {
                try (BufferedWriter writer = new BufferedWriter(new FileWriter("nomes.txt", true))) {
                    writer.write(nome);
                    writer.newLine();
                    nomes.add(nome);
                    System.out.println("Nome adicionado ao arquivo.");
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

            System.out.print("Digite um nome para verificar (ou SAIR para encerrar): ");
            nome = scanner.nextLine().trim();
        }
    scanner.close();
    }
}
