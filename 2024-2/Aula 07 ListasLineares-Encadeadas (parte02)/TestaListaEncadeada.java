
package encadeamento;

public class TestaListaEncadeada {
    public static void main(String[] args){
        
        ListaEncadeada02 lis = new ListaEncadeada02();
        lis.insereInicio(45);
        lis.insereInicio(20);
        lis.insereInicio(34);
        lis.insereInicio(89);
        lis.insereInicio(3);
        
        lis.imprimeLista();
        lis.insereFinal(66);
        lis.imprimeLista();
        lis.removeInicio();
        lis.removeInicio();
        
        lis.imprimeLista();

        
               
              
    
    }
}
