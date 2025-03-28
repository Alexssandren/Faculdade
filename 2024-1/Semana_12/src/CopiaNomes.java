import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class CopiaNomes {
    public static void main(String[] args) {
        try (BufferedReader reader = new BufferedReader(new FileReader("nomes.txt"));
            BufferedWriter writer = new BufferedWriter(new FileWriter("nomes_copia.txt"))) {

            String linha;
            while ((linha = reader.readLine()) != null) {
                writer.write(linha);
                writer.newLine();
            }

            System.out.println("Nomes copiados para o arquivo nomes_copia.txt.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
