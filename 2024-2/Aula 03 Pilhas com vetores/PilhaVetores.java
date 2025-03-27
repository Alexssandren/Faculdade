package pilhavetores;

public class PilhaVetores {
    private Integer[] dados;
    private int qt;
    
    PilhaVetores(int tam){
        dados = new Integer[tam];
        qt = 0;
    }
    
    public int get_qt(){
        return qt;
    }
    
    public void empilha(int novo){
        if (dados.length != qt){
            dados[qt] = novo;
            qt++;
        }
    }
    
    public Integer desempilha(){
        if (qt != 0){
            Integer item = dados[qt-1];
            dados[qt-1] = null;//extremamente opcional, altamente dispensável
            qt--;
            return item;
        }
        return null;
    }
    public boolean vazia(){
        return qt == 0;
        /*if (qt == 0){
            return true;
        }
        else {
            return false;
        }*/
    }
    
    public void imprimePilha(){
        for (int i = 0; i < qt; i++){
           System.out.print(dados[i] + " ");
        }
        System.out.println();
    }
}
