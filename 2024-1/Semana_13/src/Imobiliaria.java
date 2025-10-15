import java.util.ArrayList;
import java.util.Scanner;

public class Imobiliaria {
    private ArrayList<Imovel> listaDeImoveis;

    public Imobiliaria() {
        listaDeImoveis = new ArrayList<>();
    }

    public void cadastrarImovel(Imovel imovel) {
        listaDeImoveis.add(imovel);
    }

    public void listarImoveis() {
        if (listaDeImoveis.isEmpty()) {
            System.out.println("Nenhum imóvel cadastrado.");
        } else {
            for (Imovel imovel : listaDeImoveis) {
                System.out.println(imovel);
            }
        }
    }

    public void listarImoveisPorTipo(int tipo) {
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getTipo() == tipo) {
                System.out.println(imovel);
            }
        }
    }

    public void listarImoveisPorCidade(String cidade) {
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getLocalizacao().getCidade().equalsIgnoreCase(cidade)) {
                System.out.println(imovel);
            }
        }
    }

    public void listarImoveisPorBairroECidade(String cidade, String bairro) {
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getLocalizacao().getCidade().equalsIgnoreCase(cidade) &&
                    imovel.getLocalizacao().getBairro().equalsIgnoreCase(bairro)) {
                System.out.println(imovel);
            }
        }
    }

    public void listarImoveisPorFaixaDePreco(float minPreco, float maxPreco) {
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getPreco() >= minPreco && imovel.getPreco() <= maxPreco) {
                System.out.println(imovel);
            }
        }
    }

    public void listarImoveisPorNumeroDeQuartos(int minQuartos) {
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getNumeroQuartos() >= minQuartos) {
                System.out.println(imovel);
            }
        }
    }

    public void excluirImovel(int codigo) {
        Imovel imovelParaRemover = null;
        for (Imovel imovel : listaDeImoveis) {
            if (imovel.getCodigo() == codigo) {
                imovelParaRemover = imovel;
                break;
            }
        }
        if (imovelParaRemover != null) {
            listaDeImoveis.remove(imovelParaRemover);
            System.out.println("Imóvel removido com sucesso.");
        } else {
            System.out.println("Imóvel não encontrado.");
        }
    }

    public void alterarImovel(int codigo, Imovel imovelAlterado) {
        for (int i = 0; i < listaDeImoveis.size(); i++) {
            if (listaDeImoveis.get(i).getCodigo() == codigo) {
                listaDeImoveis.set(i, imovelAlterado);
                System.out.println("Imóvel alterado com sucesso.");
                return;
            }
        }
        System.out.println("Imóvel não encontrado.");
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Imobiliaria imobiliaria = new Imobiliaria();

        while (true) {
            System.out.println("Menu:");
            System.out.println("1 - Cadastro de um novo imovel");
            System.out.println("2 - Listagem de todos os imoveis");
            System.out.println("3 - Listagem de imoveis por criterios");
            System.out.println("4 - Exclusao de imoveis");
            System.out.println("5 - Alteracao de imoveis");
            System.out.println("6 - Sair");
            System.out.print("Escolha uma opçao: ");

            int opcao = scanner.nextInt();
            scanner.nextLine(); // Consumir a nova linha

            switch (opcao) {
                case 1:
                    System.out.print("Código: ");
                    int codigo = scanner.nextInt();
                    System.out.print("Área Construída: ");
                    float areaConstruida = scanner.nextFloat();
                    System.out.print("Área Total: ");
                    float areaTotal = scanner.nextFloat();
                    System.out.print("Número de Quartos: ");
                    int numeroQuartos = scanner.nextInt();
                    System.out.print("Tipo (0 - Casa, 1 - Apartamento): ");
                    int tipo = scanner.nextInt();
                    System.out.print("Preço: ");
                    float preco = scanner.nextFloat();
                    scanner.nextLine(); // Consumir a nova linha
                    System.out.print("Cidade: ");
                    String cidade = scanner.nextLine();
                    System.out.print("Bairro: ");
                    String bairro = scanner.nextLine();

                    Endereco endereco = new Endereco(cidade, bairro);
                    Imovel imovel = new Imovel(codigo, areaConstruida, areaTotal, numeroQuartos, tipo, preco, endereco);
                    imobiliaria.cadastrarImovel(imovel);
                    System.out.println("Imóvel cadastrado com sucesso.");
                    break;

                case 2:
                    imobiliaria.listarImoveis();
                    break;

                case 3:
                    System.out.println("1 - Listar por tipo de imóvel (Casa ou Apartamento)");
                    System.out.println("2 - Listar por cidade");
                    System.out.println("3 - Listar por bairro e cidade");
                    System.out.println("4 - Listar por faixa de preço");
                    System.out.println("5 - Listar por número mínimo de quartos");
                    System.out.print("Escolha uma opção: ");
                    int subOpcao = scanner.nextInt();
                    scanner.nextLine(); // Consumir a nova linha

                    switch (subOpcao) {
                        case 1:
                            System.out.print("Tipo (0 - Casa, 1 - Apartamento): ");
                            int tipoImovel = scanner.nextInt();
                            imobiliaria.listarImoveisPorTipo(tipoImovel);
                            break;
                        case 2:
                            System.out.print("Cidade: ");
                            String cidadeImovel = scanner.nextLine();
                            imobiliaria.listarImoveisPorCidade(cidadeImovel);
                            break;
                        case 3:
                            System.out.print("Cidade: ");
                            String cidadeBairroImovel = scanner.nextLine();
                            System.out.print("Bairro: ");
                            String bairroImovel = scanner.nextLine();
                            imobiliaria.listarImoveisPorBairroECidade(cidadeBairroImovel, bairroImovel);
                            break;
                        case 4:
                            System.out.print("Preço mínimo: ");
                            float minPreco = scanner.nextFloat();
                            System.out.print("Preço máximo: ");
                            float maxPreco = scanner.nextFloat();
                            imobiliaria.listarImoveisPorFaixaDePreco(minPreco, maxPreco);
                            break;
                        case 5:
                            System.out.print("Número mínimo de quartos: ");
                            int minQuartos = scanner.nextInt();
                            imobiliaria.listarImoveisPorNumeroDeQuartos(minQuartos);
                            break;
                        default:
                            System.out.println("Opção inválida.");
                    }
                    break;

                case 4:
                    System.out.print("Código do imóvel a ser excluído: ");
                    int codigoExcluir = scanner.nextInt();
                    imobiliaria.excluirImovel(codigoExcluir);
                    break;

                case 5:
                    System.out.print("Código do imóvel a ser alterado: ");
                    int codigoAlterar = scanner.nextInt();
                    System.out.print("Nova Área Construída: ");
                    float novaAreaConstruida = scanner.nextFloat();
                    System.out.print("Nova Área Total: ");
                    float novaAreaTotal = scanner.nextFloat();
                    System.out.print("Novo Número de Quartos: ");
                    int novoNumeroQuartos = scanner.nextInt();
                    System.out.print("Novo Tipo (0 - Casa, 1 - Apartamento): ");
                    int novoTipo = scanner.nextInt();
                    System.out.print("Novo Preço: ");
                    float novoPreco = scanner.nextFloat();
                    scanner.nextLine(); // Consumir a nova linha
                    System.out.print("Nova Cidade: ");
                    String novaCidade = scanner.nextLine();
                    System.out.print("Novo Bairro: ");
                    String novoBairro = scanner.nextLine();

                    Endereco novoEndereco = new Endereco(novaCidade, novoBairro);
                    Imovel imovelAlterado = new Imovel(codigoAlterar, novaAreaConstruida, novaAreaTotal, novoNumeroQuartos, novoTipo, novoPreco, novoEndereco);
                    imobiliaria.alterarImovel(codigoAlterar, imovelAlterado);
                    break;

                case 6:
                    System.out.println("Saindo do sistema...");
                    scanner.close();
                    return;

                default:
                    System.out.println("Opção inválida.");
            }
        }
    }
}
