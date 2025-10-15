package Java.Tarefas4;

import java.time.LocalDate;
import java.util.Scanner;

public class tarefa4_1 {
    // Atributos
    private String nome;
    private String matricula;
    private double salario;
    private LocalDate dataAdmissao;
    private String cpf;

    // Construtor
    public tarefa4_1(String nome, String matricula, double salario, LocalDate dataAdmissao, String cpf) {
        this.nome = nome;
        this.matricula = matricula;
        this.salario = salario;
        this.dataAdmissao = dataAdmissao;
        this.cpf = cpf;
    }

    // Método para aumentar o salário
    public void receberAumento(double aumento) {
        this.salario += aumento;
    }

    // Método para calcular ganho bruto anual
    public double calcularGanhoBrutoAnual() {
        return this.salario * 12;
    }

    // Método para calcular o imposto pago pelo funcionário
    public double calcularImposto() {
        double imposto = 0;
        double salarioAnual = calcularGanhoBrutoAnual();

        // Calculando imposto de acordo com a faixa salarial
        if (salarioAnual <= 22847.76) {
            imposto = 0;
        } else if (salarioAnual <= 33919.80) {
            imposto = salarioAnual * 0.075 - 1713.58;
        } else if (salarioAnual <= 45012.60) {
            imposto = salarioAnual * 0.15 - 4257.57;
        } else if (salarioAnual <= 55976.16) {
            imposto = salarioAnual * 0.225 - 7633.51;
        } else {
            imposto = salarioAnual * 0.275 - 10432.32;
        }

        return imposto;
    }

    // Método para calcular ganho líquido mensal
    public double calcularGanhoLiquidoMensal() {
        double salarioLiquido = this.salario;

        // Desconto de INSS
        double inss = this.salario <= 1100.00 ? this.salario * 0.075 :
                this.salario <= 2203.48 ? this.salario * 0.09 :
                        this.salario <= 3305.22 ? this.salario * 0.12 : 393.55;
        salarioLiquido -= inss;

        // Desconto de IR se o salário for maior que R$ 2.500,00
        if (this.salario > 2500.00) {
            double excedente = this.salario - 2500.00;
            double ir = excedente * 0.175;
            salarioLiquido -= ir;
        }

        return salarioLiquido;
    }

    // Método para calcular ganho líquido anual
    public double calcularGanhoLiquidoAnual() {
        return calcularGanhoBrutoAnual() - calcularImposto();
    }

    // Método para receber dados do usuário e criar um objeto Funcionario
    public static tarefa4_1 criarFuncionarioComEntradaUsuario() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Digite o nome do funcionário:");
        String nome = scanner.nextLine();
        System.out.println("Digite a matrícula do funcionário:");
        String matricula = scanner.nextLine();
        System.out.println("Digite o salário do funcionário:");
        double salario = scanner.nextDouble();
        System.out.println("Digite a data de admissão do funcionário (no formato YYYY-MM-DD):");
        String dataAdmissaoStr = scanner.next();
        LocalDate dataAdmissao = LocalDate.parse(dataAdmissaoStr);
        System.out.println("Digite o CPF do funcionário:");
        String cpf = scanner.next();
        
        scanner.close();
        return new tarefa4_1(nome, matricula, salario, dataAdmissao, cpf);
    }

    // Método toString para representação da classe
    @Override
    public String toString() {
        return "Funcionario{" +
                "nome='" + nome + '\'' +
                ", matricula='" + matricula + '\'' +
                ", salario=" + salario +
                ", dataAdmissao=" + dataAdmissao +
                ", cpf='" + cpf + '\'' +
                '}';
    }

    // Método main apenas para teste
    public static void main(String[] args) {
        tarefa4_1 funcionario = criarFuncionarioComEntradaUsuario();
        System.out.println(funcionario);
        System.out.println("Salário líquido mensal: " + funcionario.calcularGanhoLiquidoMensal());
        System.out.println("Salário líquido anual: " + funcionario.calcularGanhoLiquidoAnual());
    }
}