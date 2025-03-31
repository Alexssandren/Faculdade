public class ListaEncadeada {
    private Nodo inicio;
    
    private class Nodo{
        Integer dado;
        Nodo prox;
    }
    
    public ListaEncadeada(){
        inicio = null;
    }
    
    public Integer removeInicio(){
        if (inicio != null){
            Nodo aux = inicio;
            inicio = inicio.prox;
            return aux.dado;
        }
        else return null;
    }
    
    public void insereLista(Integer valor){
        Nodo novo = new Nodo();
        novo.dado = valor;
        novo.prox = inicio;
        inicio = novo;
    }
    
    public void imprimeLista(){
        for (Nodo i = inicio; i != null; i = i.prox){
            System.out.print(i.dado + "->");
        }
        System.out.println();
    }
    
    
}
