
public class ListaEncadeada02 {
    private Nodo inicio;
    private Nodo fim;
    
    private class Nodo{
        Integer dado;
        Nodo prox;
    }
    public ListaEncadeada02(){
        inicio = null; fim = null;
    }
    //remoção no inicio
    public Integer removeInicio(){
        //a lista não pode estar vazia
        if (inicio == null) return null;
        
        Integer valor = inicio.dado;
        //avalia se existe apenas um elemento
        if (inicio == fim){
            inicio = null; fim = null;
        }
        else {//quando a lista tiver mais de um elemento
            inicio = inicio.prox;
        }
        return valor;
    
    
    }
  
    
    
    //remoção no final 
    public void insereInicio(Integer valor){
        Nodo novo = new Nodo();
        novo.dado = valor;
        //lista vazia
        if (inicio == null){
            inicio = novo;
            fim = novo;
            novo.prox = null;
        }
        else {
            novo.prox = inicio;
            inicio = novo;
        }
    }
    
    
    public void insereFinal(Integer valor){
        Nodo novo = new Nodo();
        novo.dado = valor; 
        novo.prox = null;
        //verifica se está vazia
        if (inicio == null) {
            inicio = novo;
            fim = novo;
        }
        else {
            fim.prox = novo;
            fim = novo;
        }
    }
    
    public void imprimeLista(){
        for (Nodo i = inicio; i != null; i = i.prox){
            System.out.print(i.dado + "->");
        }
        System.out.println();
    }
}
