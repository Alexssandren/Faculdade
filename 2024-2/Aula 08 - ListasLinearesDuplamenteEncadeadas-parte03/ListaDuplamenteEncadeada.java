public class ListaDuplamenteEncadeada {
    Nodo inicio;
    Nodo fim;
    
    private class Nodo{
        Integer dado;
        Nodo prox; 
        Nodo ant;
    }
    
    public ListaDuplamenteEncadeada(){
        inicio = fim = null;
    }
    
    public void insereInicio(Integer valor){
        Nodo novo = new Nodo();
        novo.dado = valor;
        novo.ant = null;
        novo.prox = inicio;// null
        //avaliar se a lista vazia 
        if (inicio == null) {
            inicio = novo;
            fim = novo;
        }
        else {
            inicio.ant = novo;
            inicio = novo;
        }
            
    }        
    public Integer removeInicio(){
        //ver se é vazia
        if (inicio == null) return null;
           
        Integer aux = inicio.dado;
        //ver se existe apenas 1 único elemento
        if (inicio == fim)
            inicio = fim = null;
        else {// existem mais de um elementos
            inicio.prox.ant = null;
            inicio = inicio.prox;
        
        }
        return aux;
    
    }
            
            
    public void imprime(){
        for (Nodo temp = inicio; temp != null; temp = temp.prox)
            System.out.print(temp.dado + "->");
        System.out.println();
    
    }
    public void imprimeInverso(){
        for (Nodo temp = fim; temp != null; temp = temp.ant)
            System.out.print(temp.dado + "->");
        
        System.out.println();
    
    }
}