package encadeamento;

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
    
    public void insereInicio(Integer valor){
        Nodo novo = new Nodo();
        novo.dado = valor;
        novo.prox = inicio;
        inicio = novo;
    }
    
    public void insereOrdenado(Integer valor){
        Nodo anterior = null;
        Nodo temp = inicio; 
      
        Nodo novo = new Nodo();
        novo.dado = valor;
        // manter a ordem da expressão lógica
        // não pode ser ao contrario
        // não -> (temp.dado < valor && temp != null)
        
        while (temp != null && temp.dado < valor){
            anterior = temp; 
            temp = temp.prox;
        }
        //insercao inicio
        if (anterior == null){
            novo.prox = inicio;
            inicio = novo;
        }
        else {
            anterior.prox = novo;
            novo.prox = temp;
        }
    }
    
    Integer removeElemento(Integer valor){
        Nodo anterior = null;
        Nodo temp = inicio;
        
        while (temp != null && temp.dado != valor){
            anterior = temp;
            temp = temp.prox;
        }
        if (temp == null) return null;//elemento não existe
        
        //tratar elemento encontrado no inicio
        if (anterior == null) {
            Integer retira = temp.dado;
            inicio = inicio.prox;//inicio = temp.prox;
            return retira;
        }
        //encontrou um elemento no meio ou no final
        Integer retira = temp.dado;
        anterior.prox = temp.prox;
        return retira;
    }
    
    
    public void imprimeLista(){
        for (Nodo i = inicio; i != null; i = i.prox){
            System.out.print(i.dado + "->");
        }
        System.out.println();
    }
    
    
}
