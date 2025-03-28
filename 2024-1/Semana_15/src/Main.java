import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Disciplina disciplina = new Disciplina();

        Estudante estudante1 = new Estudante("João", "11111111111", "20240001", 10, 8);
        Estudante estudante2 = new Estudante("Pedro", "22222222222", "20240002", 6, 4);
        int opcao;
        do {
            System.out.println("Menu:");
            System.out.println("1. Cadastrar um novo estudante");
            System.out.println("2. Alterar dados de um estudante");
            System.out.println("3. Remover um estudante");
            System.out.println("4. Consultar um estudante");
            System.out.println("5. Listar estudantes");
            System.out.println("6. Listar estudantes com média abaixo de 6.0");
            System.out.println("7. Listar estudantes com média acima de 6.0");
            System.out.println("8. Mostrar média da turma");
            System.out.println("9. Sair");
            System.out.print("Escolha uma opção: ");
            opcao = scanner.nextInt();
            scanner.nextLine(); // Consumir a nova linha

            switch (opcao) {
                case 1:
                    System.out.print("Nome: ");
                    String nome = scanner.nextLine();
                    System.out.print("CPF: ");
                    String cpf = scanner.nextLine();
                    System.out.print("Matrícula: ");
                    String matricula = scanner.nextLine();
                    System.out.print("Nota 01: ");
                    double nota01 = scanner.nextDouble();
                    System.out.print("Nota 02: ");
                    double nota02 = scanner.nextDouble();
                    scanner.nextLine(); // Consumir a nova linha
                    disciplina.insereEstudante(new Estudante(nome, cpf, matricula, nota01, nota02));
                    System.out.println("Estudante cadastrado com sucesso.");
                    break;
                case 2:
                    System.out.print("Informe a matrícula do estudante a ser alterado: ");
                    String matriculaAlterar = scanner.nextLine();
                    Estudante estudanteAlterar = disciplina.buscarEstudante(matriculaAlterar);
                    if (estudanteAlterar != null) {
                        System.out.print("Novo Nome: ");
                        estudanteAlterar.setNome(scanner.nextLine());
                        System.out.print("Novo CPF: ");
                        estudanteAlterar.setCpf(scanner.nextLine());
                        System.out.print("Nova Nota 01: ");
                        estudanteAlterar.setNota01(scanner.nextDouble());
                        System.out.print("Nova Nota 02: ");
                        estudanteAlterar.setNota02(scanner.nextDouble());
                        scanner.nextLine(); // Consumir a nova linha
                        System.out.println("Dados do estudante alterados com sucesso.");
                    } else {
                        System.out.println("Estudante não encontrado.");
                    }
                    break;
                case 3:
                    System.out.print("Informe a matrícula do estudante a ser removido: ");
                    String matriculaRemover = scanner.nextLine();
                    disciplina.removerEstudante(matriculaRemover);
                    System.out.println("Estudante removido com sucesso.");
                    break;
                case 4:
                    System.out.print("Informe a matrícula do estudante a ser consultado: ");
                    String matriculaConsulta = scanner.nextLine();
                    Estudante estudanteConsulta = disciplina.buscarEstudante(matriculaConsulta);
                    if (estudanteConsulta != null) {
                        System.out.println("Nome: " + estudanteConsulta.getNome());
                        System.out.println("CPF: " + estudanteConsulta.getCpf());
                        System.out.println("Matrícula: " + estudanteConsulta.getMatricula());
                        System.out.println("Nota 01: " + estudanteConsulta.getNota01());
                        System.out.println("Nota 02: " + estudanteConsulta.getNota02());
                        System.out.println("Média: " + estudanteConsulta.getMedia());
                    } else {
                        System.out.println("Estudante não encontrado.");
                    }
                    break;
                case 5:
                    System.out.println("Lista de estudantes:");
                    for (Estudante e : disciplina.getTurma()) {
                        System.out.println("Nome: " + e.getNome() + ", Matrícula: " + e.getMatricula() +
                                ", Nota 01: " + e.getNota01() + ", Nota 02: " + e.getNota02() +
                                ", Média: " + e.getMedia());
                    }
                    break;
                case 6:
                    System.out.println("Estudantes com média abaixo de 6.0:");
                    for (Estudante e : disciplina.getTurma()) {
                        if (e.getMedia() < 6.0) {
                            System.out.println("Nome: " + e.getNome() + ", Matrícula: " + e.getMatricula() +
                                    ", Nota 01: " + e.getNota01() + ", Nota 02: " + e.getNota02() +
                                    ", Média: " + e.getMedia());
                        }
                    }
                    break;
                case 7:
                    System.out.println("Estudantes com média acima de 6.0:");
                    for (Estudante e : disciplina.getTurma()) {
                        if (e.getMedia() >= 6.0) {
                            System.out.println("Nome: " + e.getNome() + ", Matrícula: " + e.getMatricula() +
                                    ", Nota 01: " + e.getNota01() + ", Nota 02: " + e.getNota02() +
                                    ", Média: " + e.getMedia());
                        }
                    }
                    break;
                case 8:
                    double somaMedias = 0.0;
                    for (Estudante e : disciplina.getTurma()) {
                        somaMedias += e.getMedia();
                    }
                    double mediaTurma = somaMedias / disciplina.getTurma().size();
                    System.out.println("Média da turma: " + mediaTurma);
                    break;
                case 9:
                    disciplina.gravar();
                    System.out.println("Saindo do sistema...");
                    break;
                default:
                    System.out.println("Opção inválida!");
            }
        } while (opcao != 9);

        scanner.close();
    }
}
