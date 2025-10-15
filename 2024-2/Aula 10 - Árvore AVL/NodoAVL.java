public class NodoAVL {
    private NodoAVL esq;
    private int valor;
    private NodoAVL dir;
    
    NodoAVL(){
    }
    
    NodoAVL(int valor, NodoAVL esq, NodoAVL dir){
        this.valor = valor;
        this.esq = esq;
        this.dir = dir;
    }
    void imprimeSimetrico(NodoAVL arv){
        if (arv != null){
            System.out.print("<");
            imprimeSimetrico(arv.esq);
            System.out.print(arv.valor);
            imprimeSimetrico(arv.dir);
            System.out.print(">");
        }
    }
    
    void imprimePreOrdem(NodoAVL arv){
        if (arv != null){
            System.out.print("<");
            System.out.print(arv.valor);
            imprimePreOrdem(arv.esq);
            imprimePreOrdem(arv.dir);
            System.out.print(">");
        }
    }
    
    int max(int a, int b){
        if (a > b) return a;
        else return b;  
    }
    
    int quantidade(NodoAVL atual){
        if (atual == null) return 0;
        else {
            return 1 + quantidade(atual.esq) + quantidade(atual.dir);
        }
    
    }
    
    
    int altura(NodoAVL atual){
        if (atual == null) return -1;
        else {
            return 1 + 
                   max(altura(atual.esq), altura(atual.dir));
        }
    
    }
    
    
    
    NodoAVL remove(NodoAVL atual, int valor){
        if (atual == null) return null; //elemento não existia
        else if (valor < atual.valor) //continuar pela esquerda
            atual.esq = remove(atual.esq, valor);
        else if (valor > atual.valor) //continuar pela direita
            atual.dir = remove(atual.dir, valor);
        else {//achou o elemento - realizar a remoção
            //verificar os 3 cenários de remoção
            //cenário sem filhos
            if (atual.esq == null && atual.dir == null)
                return null;
            if (atual.dir == null) //só tem filho esquerda
                return atual.esq;
            if (atual.esq == null) //só tem filho direita
                return atual.dir;
            //tem 2 filhos
            NodoAVL temp = atual.esq;
            while (temp.dir != null)
                temp = temp.dir; //busca o antecedente de atual
            
            atual.valor = temp.valor;
            temp.valor = valor;//número buscado no parâmetro
            //segue a remoção na subarvore da esquerda
            atual.esq = remove(atual.esq, valor);
        }
        return atual;
    }
    
    
    NodoAVL insere(NodoAVL atual, int valor){
        if (atual == null ) 
            atual = new NodoAVL(valor, null, null);
        else if (valor < atual.valor)
            atual.esq = insere(atual.esq, valor);
        else
            atual.dir = insere(atual.dir, valor);
       
        return atual;
    }
    
    boolean buscaArvore(NodoAVL arv, int valor){
        if (arv == null) return false;
        else 
            if (arv.valor == valor) return true;
            else return buscaArvore(arv.esq, valor) || 
                        buscaArvore(arv.dir, valor);
    }
    NodoAVL rotacaoDireitaEsquerda(NodoAVL nodo){
        nodo.dir = nodo.dir.rotacaoDireita(nodo.dir);
        nodo = nodo.rotacaoEsquerda(nodo);
        return nodo;
    }
    
    NodoAVL rotacaoEsquerdaDireita(NodoAVL nodo){
        nodo.esq = nodo.esq.rotacaoEsquerda(nodo.esq);
        nodo = nodo.rotacaoDireita(nodo);
        return nodo;
    }
    
    
    NodoAVL rotacaoEsquerda(NodoAVL nodo){
        NodoAVL aux = nodo.dir;
        nodo.dir = aux.esq;
        aux.esq = nodo;
        return aux;   
    }
    
    NodoAVL rotacaoDireita(NodoAVL nodo){
        NodoAVL aux = nodo.esq;
        nodo.esq = aux.dir;
        aux.dir = nodo;
        return aux;
    }
    
}
