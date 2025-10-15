import java.util.Scanner;

public class Tarefa1_9 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Solicita ao usuário que insira o número de identificação do aluno
        System.out.print("Insira o número de identificação do aluno: ");
        int idAluno = scanner.nextInt();

        // Solicita ao usuário que insira as três notas do aluno
        System.out.print("Insira a primeira nota: ");
        double nota1 = scanner.nextDouble();
        System.out.print("Insira a segunda nota: ");
        double nota2 = scanner.nextDouble();
        System.out.print("Insira a terceira nota: ");
        double nota3 = scanner.nextDouble();

        // Solicita ao usuário que insira a média dos exercícios
        System.out.print("Insira a média dos exercícios: ");
        double mediaExercicios = scanner.nextDouble();

        // Calcula a média de aproveitamento
        double mediaAproveitamento = (nota1 + nota2 * 2 + nota3 * 3 + mediaExercicios) / 7;

        // Determina o conceito de acordo com a média de aproveitamento
        String conceito;
        if (mediaAproveitamento >= 90) {
            conceito = "A";
        } else if (mediaAproveitamento >= 75) {
            conceito = "B";
        } else if (mediaAproveitamento >= 60) {
            conceito = "C";
        } else if (mediaAproveitamento >= 40) {
            conceito = "D";
        } else {
            conceito = "E";
        }

        // Exibe os resultados
        System.out.println("\nNúmero do aluno: " + idAluno);
        System.out.println("Notas: " + nota1 + ", " + nota2 + ", " + nota3);
        System.out.println("Média dos exercícios: " + mediaExercicios);
        System.out.println("Média de aproveitamento: " + mediaAproveitamento);
        System.out.println("Conceito: " + conceito);
        
        // Verifica se o aluno foi aprovado ou reprovado
        if (conceito.equals("A") || conceito.equals("B") || conceito.equals("C")) {
            System.out.println("Aprovado");
        } else {
            System.out.println("Reprovado");
        }

        scanner.close();
    }
}
