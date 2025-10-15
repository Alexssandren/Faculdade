import java.util.Scanner;

public class TestaArvoreBinaria {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        ArvoreBinaria arvore = new ArvoreBinaria();
        ListaDuplamenteEncadeada lista = new ListaDuplamenteEncadeada();

        System.out.println("Digite números inteiros para adicionar à árvore (digite -1 para terminar):");
        while (true) {
            int valor = scanner.nextInt();
            if (valor == -1) {
                break;
            }
            arvore.inserir(valor);
        }

        System.out.println("Escolha uma opção:");
        System.out.println("1 - Inverter subárvores");
        System.out.println("2 - Verificar igualdade com outra árvore");
        System.out.println("3 - Exibir elementos em ordem em uma lista duplamente encadeada");
        int opcao = scanner.nextInt();

        switch (opcao) {
            case 1:
                arvore.inverte();
                System.out.println("Subárvores invertidas.");
                break;
            case 2:
                ArvoreBinaria outraArvore = new ArvoreBinaria();
                System.out.println("Digite números inteiros para a segunda árvore (digite -1 para terminar):");
                while (true) {
                    int outroValor = scanner.nextInt();
                    if (outroValor == -1) {
                        break;
                    }
                    outraArvore.inserir(outroValor);
                }
                boolean iguais = arvore.saoIguais(outraArvore);
                System.out.println("As árvores são " + (iguais ? "iguais." : "diferentes."));
                break;
            case 3:
                arvore.emOrdem(lista);
                System.out.println("Elementos em ordem:");
                lista.exibir();
                break;
            default:
                System.out.println("Opção inválida.");
        }

        scanner.close();
    }
}
