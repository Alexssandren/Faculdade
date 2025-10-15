import java.util.Scanner;

class Funcionario {
    private String nome;
    private double salarioBruto;
    private double imposto;

    public Funcionario(String nome, double salarioBruto, double imposto) {
        this.nome = nome;
        this.salarioBruto = salarioBruto;
        this.imposto = imposto;
    }

    public String getNome() {
        return nome;
    }

    public double getSalarioLiquido() {
        return salarioBruto - salarioBruto * imposto;
    }

    public void aumentarSalario(double percentualAumento) {
        salarioBruto += salarioBruto * (percentualAumento / 100.0);
    }
}

public class tarefa5_2 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Digite o nome do funcionário:");
        String nome = scanner.nextLine();

        System.out.println("Digite o salário bruto do funcionário:");
        double salarioBruto = scanner.nextDouble();

        System.out.println("Digite a porcentagem de imposto do funcionário:");
        double imposto = scanner.nextDouble();

        Funcionario funcionario = new Funcionario(nome, salarioBruto, imposto);

        System.out.println("Dados do funcionário:");
        System.out.println("Nome: " + funcionario.getNome());
        System.out.println("Salário líquido: " + funcionario.getSalarioLiquido());

        System.out.println("Digite a porcentagem de aumento do salário:");
        double percentualAumento = scanner.nextDouble();
        funcionario.aumentarSalario(percentualAumento);

        System.out.println("Dados atualizados do funcionário:");
        System.out.println("Nome: " + funcionario.getNome());
        System.out.println("Salário líquido: " + funcionario.getSalarioLiquido());

        scanner.close();
    }
}
