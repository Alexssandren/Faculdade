public class TestaArvore {
    public static void main(String[] args){
        NodoAVL nodo = new NodoAVL(10, null, null);
        nodo.insere(nodo, 5);
        nodo.insere(nodo, 8);
        nodo.imprimeSimetrico(nodo);
        System.out.println();
        nodo = nodo.rotacaoEsquerdaDireita(nodo);
        nodo.imprimeSimetrico(nodo);

    }
    
}
