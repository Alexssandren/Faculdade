import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class GerenciadorFuncionarios {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<Funcionario> funcionarios = new ArrayList<>();

        System.out.print("Quantos funcionários serão cadastrados? ");
        int n = sc.nextInt();

        for (int i = 1; i <= n; i++) {
            System.out.println("\nFuncionário #" + i + ":");
            
            System.out.print("ID: ");
            int id = sc.nextInt();
            while (existeId(funcionarios, id)) {
                System.out.print("ID já existe! Digite outro ID: ");
                id = sc.nextInt();
            }

            System.out.print("Nome: ");
            sc.nextLine(); // Limpar buffer
            String nome = sc.nextLine();

            System.out.print("Salário: ");
            double salario = sc.nextDouble();

            funcionarios.add(new Funcionario(id, nome, salario));
        }

        System.out.print("\nDigite o ID do funcionário que terá aumento: ");
        int idAumento = sc.nextInt();
        
        Funcionario func = buscarFuncionario(funcionarios, idAumento);
        if (func != null) {
            System.out.print("Digite a porcentagem de aumento: ");
            double porcentagem = sc.nextDouble();
            func.aumentarSalario(porcentagem);
        } else {
            System.out.println("Este ID não existe!");
        }

        System.out.println("\nLista de funcionários atualizada:");
        for (Funcionario f : funcionarios) {
            System.out.println(f);
        }

        sc.close();
    }

    private static boolean existeId(List<Funcionario> lista, int id) {
        for (Funcionario f : lista) {
            if (f.getId() == id) {
                return true;
            }
        }
        return false;
    }

    private static Funcionario buscarFuncionario(List<Funcionario> lista, int id) {
        for (Funcionario f : lista) {
            if (f.getId() == id) {
                return f;
            }
        }
        return null;
    }
}

class Funcionario {
    private final int id;
    private String nome;
    private double salario;

    public Funcionario(int id, String nome, double salario) {
        this.id = id;
        this.nome = nome;
        this.salario = salario;
    }

    public int getId() {
        return id;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public double getSalario() {
        return salario;
    }

    public void aumentarSalario(double porcentagem) {
        if (porcentagem > 0) {
            salario += salario * porcentagem / 100;
        }
    }

    @Override
    public String toString() {
        return String.format("%d, %s, R$ %.2f", id, nome, salario);
    }
}