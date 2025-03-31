public class ListaDuplamenteEncadeada {
    private class Nodo {
        int valor;
        Nodo proximo, anterior;

        Nodo(int valor) {
            this.valor = valor;
            this.proximo = null;
            this.anterior = null;
        }
    }

    private Nodo inicio, fim;

    public ListaDuplamenteEncadeada() {
        this.inicio = null;
        this.fim = null;
    }

    public void adicionar(int valor) {
        Nodo novoNodo = new Nodo(valor);
        if (this.inicio == null) {
            this.inicio = novoNodo;
            this.fim = novoNodo;
        } else {
            this.fim.proximo = novoNodo;
            novoNodo.anterior = this.fim;
            this.fim = novoNodo;
        }
    }

    public void exibir() {
        Nodo atual = this.inicio;
        while (atual != null) {
            System.out.print(atual.valor + " ");
            atual = atual.proximo;
        }
        System.out.println();
    }
}
