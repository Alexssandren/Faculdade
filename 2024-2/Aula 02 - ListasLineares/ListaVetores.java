/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package listavetores;

/**
 *
 * @author cechinel
 */
public class ListaVetores {
    
    private Integer[] dados;
    private int quantidade;
    
    ListaVetores(int tamanho){
        dados = new Integer[tamanho];
        quantidade = 0;
    }

    
    
    public int getQuantidade() {
        return quantidade;
    }
    
    private void resize(int max){
        Integer[] novo = new Integer[max];
        for (int i = 0 ; i < quantidade; i++){
            novo[i] = dados[i];
        }
        dados = novo;
        }

    public void add(int n){
        if (quantidade == dados.length)
            resize(dados.length*2);
        dados[quantidade] = n;
        quantidade++;
    }
    
    
    public void add_fixo(int n){
        if (quantidade != dados.length){
            dados[quantidade] = n;
            quantidade++;
        }
    }
    
    public void imprimeLista(){
        for (int i = 0; i < quantidade; i++)
            System.out.print(dados[i]+ " ");
        System.out.println();
            
    }
    
    public boolean vazia(){
        if (quantidade == 0) 
            return true;
        return false;
    }
    
    public Integer removeUltimo(){
        if (quantidade == 0) return null;
        else {
            Integer item = dados[quantidade -1];
            quantidade--;
            if (quantidade > 0 && quantidade == dados.length/4) 
                resize(dados.length/2);
            return item;
        }
    }

    public Integer removeUltimoFixo(){
        if (quantidade == 0) return null;
        
        Integer item = dados[quantidade -1];
        dados[quantidade -1] = null;//extremamente opcional
        quantidade--;
        return item;
        
    }
    
    public Integer remove(int i){
        if (i <0 || i >= quantidade) return null;
        else {
            Integer item = dados[i];
            for (int j = i+1; j < quantidade; j++){
                dados[j-1] = dados[j];
            }
            dados[quantidade-1] = null;
            quantidade--;
            return item;
        }
    }
    
}
