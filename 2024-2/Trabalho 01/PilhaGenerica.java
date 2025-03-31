public class PilhaGenerica<T> {
    private ListaEncadeadaGenerica<T> lista;

    public PilhaGenerica() {
        lista = new ListaEncadeadaGenerica<>();
    }

    public void empilhar(T elemento) {
        lista.adicionarInicio(elemento);
    }

    public T desempilhar() {
        return lista.removerInicio();
    }

    public boolean vazia() {
        return lista.vazia();
    }

    public int tamanho() {
        return lista.tamanho();
    }

    @Override
    public String toString() {
        return lista.toString();
    }
}
