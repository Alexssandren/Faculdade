public class ArvoreBinaria {
    private NodoArvore raiz;
    
    ArvoreBinaria(){
        
        raiz = null;
    }
    
    void imprimePreOrdem(){
        raiz.imprimePreOrdem(raiz);
    }
    
    void imprimeSimetrico(){
        raiz.imprimeSimetrico(raiz);
    }
    void removeArvore(int valor){
        if (raiz != null) 
            raiz.remove(raiz, valor);
    }
    int getQuantidade(){
        return raiz.quantidade();
    
    
    int getAltura(){
        return raiz.altura(raiz);
    }
    
    
    void insereArvore(int valor){
        if (raiz == null) 
            raiz = new NodoArvore(valor, null, null);
        else
            raiz.insere(raiz, valor);
    }
    
 
    
    
    
}
