public class ArvoreBinaria {
    private NodoArvore raiz;

    public ArvoreBinaria() {
        this.raiz = null;
    }

    public void inserir(int valor) {
        this.raiz = inserirRecursivo(this.raiz, valor);
    }

    private NodoArvore inserirRecursivo(NodoArvore nodo, int valor) {
        if (nodo == null) {
            return new NodoArvore(valor);
        }
        if (valor < nodo.valor) {
            nodo.esquerda = inserirRecursivo(nodo.esquerda, valor);
        } else if (valor > nodo.valor) {
            nodo.direita = inserirRecursivo(nodo.direita, valor);
        }
        return nodo;
    }

    public void inverte() {
        if (this.raiz != null) {
            this.raiz.inverte();
        }
    }

    public boolean saoIguais(ArvoreBinaria outra) {
        return this.raiz == null && outra.raiz == null ||
               this.raiz != null && this.raiz.saoIguais(outra.raiz);
    }

    public void emOrdem(ListaDuplamenteEncadeada lista) {
        emOrdemRecursivo(this.raiz, lista);
    }

    private void emOrdemRecursivo(NodoArvore nodo, ListaDuplamenteEncadeada lista) {
        if (nodo != null) {
            emOrdemRecursivo(nodo.esquerda, lista);
            lista.adicionar(nodo.valor);
            emOrdemRecursivo(nodo.direita, lista);
        }
    }
}
