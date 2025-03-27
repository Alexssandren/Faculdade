import java.util.Scanner;

class Student {
    private String nome;
    private double notaTrimestre1;
    private double notaTrimestre2;
    private double notaTrimestre3;

    public Student(String nome, double notaTrimestre1, double notaTrimestre2, double notaTrimestre3) {
        this.nome = nome;
        this.notaTrimestre1 = notaTrimestre1;
        this.notaTrimestre2 = notaTrimestre2;
        this.notaTrimestre3 = notaTrimestre3;
    }

    public double calcularNotaFinal() {
        double notaFinal = (notaTrimestre1 * 0.3) + (notaTrimestre2 * 0.35) + (notaTrimestre3 * 0.35);
        return notaFinal;
    }

    public String getStatus() {
        double notaFinal = calcularNotaFinal();
        if (notaFinal >= 60.0) {
            return "PASS";
        } else {
            return "FAILED";
        }
    }

    public double pontosFaltantes() {
        double notaFinal = calcularNotaFinal();
        if (notaFinal >= 60.0) {
            return 0.0;
        } else {
            return 60.0 - notaFinal;
        }
    }
}

public class tarefa5_3 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Digite o nome do aluno:");
        String nome = scanner.nextLine();

        System.out.println("Digite a nota do primeiro trimestre:");
        double notaTrimestre1 = scanner.nextDouble();

        System.out.println("Digite a nota do segundo trimestre:");
        double notaTrimestre2 = scanner.nextDouble();

        System.out.println("Digite a nota do terceiro trimestre:");
        double notaTrimestre3 = scanner.nextDouble();

        Student aluno = new Student(nome, notaTrimestre1, notaTrimestre2, notaTrimestre3);

        System.out.println("Nota final do aluno: " + aluno.calcularNotaFinal());
        System.out.println("Status do aluno: " + aluno.getStatus());

        if (aluno.getStatus().equals("FAILED")) {
            System.out.println("Pontos faltantes para passar: " + aluno.pontosFaltantes());
        }

        scanner.close();
    }
}
