public class ListaEncadeadaGenerica<T> {
    private No<T> inicio;
    private int tamanho;

    private static class No<T> {
        T dado;
        No<T> proximo;

        public No(T dado) {
            this.dado = dado;
        }
    }

    public ListaEncadeadaGenerica() {
        inicio = null;
        tamanho = 0;
    }

    public void adicionarInicio(T dado) {
        No<T> novoNo = new No<>(dado);
        novoNo.proximo = inicio;
        inicio = novoNo;
        tamanho++;
    }

    public T removerInicio() {
        if (vazia()) {
            return null;
        }
        T dado = inicio.dado;
        inicio = inicio.proximo;
        tamanho--;
        return dado;
    }

    public boolean vazia() {
        return inicio == null;
    }

    public int tamanho() {
        return tamanho;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        No<T> atual = inicio;
        while (atual != null) {
            sb.append(atual.dado).append(" ");
            atual = atual.proximo;
        }
        return sb.toString();
    }
}
