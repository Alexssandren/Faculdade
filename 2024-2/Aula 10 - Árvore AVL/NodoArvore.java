public class NodoArvore {
    private int valor;
    private NodoArvore esquerda;
    private NodoArvore direita;

    public NodoArvore(int valor, NodoArvore esquerda, NodoArvore direita) {
        this.valor = valor;
        this.esquerda = esquerda;
        this.direita = direita;
    }

    public void imprimePreOrdem(NodoArvore nodo) {
        if (nodo != null) {
            System.out.print(nodo.valor + " ");
            imprimePreOrdem(nodo.esquerda);
            imprimePreOrdem(nodo.direita);
        }
    }

    public void imprimeSimetrico(NodoArvore nodo) {
        if (nodo != null) {
            imprimeSimetrico(nodo.esquerda);
            System.out.print(nodo.valor + " ");
            imprimeSimetrico(nodo.direita);
        }
    }

    public void remove(NodoArvore nodo, int valor) {
        if (nodo != null) {
            if (valor < nodo.valor) {
                remove(nodo.esquerda, valor);
            } else if (valor > nodo.valor) {
                remove(nodo.direita, valor);
            } else {
                // Implementar remoção
            }
        }
    }

    public int altura(NodoArvore nodo) {
        if (nodo == null) return -1;
        return Math.max(altura(nodo.esquerda), altura(nodo.direita)) + 1;
    }

    public void insere(NodoArvore nodo, int valor) {
        if (valor < nodo.valor) {
            if (nodo.esquerda == null)
                nodo.esquerda = new NodoArvore(valor, null, null);
            else
                insere(nodo.esquerda, valor);
        } else if (valor > nodo.valor) {
            if (nodo.direita == null)
                nodo.direita = new NodoArvore(valor, null, null);
            else
                insere(nodo.direita, valor);
        }
    }
}
