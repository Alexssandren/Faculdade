import java.io.*;
import java.util.ArrayList;

public class Disciplina {
    private ArrayList<Estudante> turma;

    public Disciplina() {
        turma = new ArrayList<>();
        carregaDados();
    }

    public void gravar() {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("estudantes.csv"))) {
            for (Estudante e : turma) {
                writer.write(e.getEstudanteCSV());
                writer.newLine();
            }
        } catch (IOException e) {
            System.out.println("Erro ao gravar dados: " + e.getMessage());
        }
    }

    public void carregaDados() {
        File file = new File("estudantes.csv");
        if (!file.exists()) return;

        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String linha;
            while ((linha = reader.readLine()) != null) {
                Estudante e = new Estudante(); // Construtor padrão
                e.setEstudanteCSV(linha);
                turma.add(e);
            }
        } catch (IOException e) {
            System.out.println("Erro ao carregar dados: " + e.getMessage());
        }
    }

    public void insereEstudante(Estudante e) {
        turma.add(e);
    }

    public void removerEstudante(String matricula) {
        turma.removeIf(e -> e.getMatricula().equals(matricula));
    }

    public Estudante buscarEstudante(String matricula) {
        for (Estudante e : turma) {
            if (e.getMatricula().equals(matricula)) {
                return e;
            }
        }
        return null;
    }

    public ArrayList<Estudante> getTurma() {
        return turma;
    }

    // Métodos adicionais omitidos por brevidade
}
