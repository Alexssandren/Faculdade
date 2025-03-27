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
public class TestaLista {
    public static void main(String[] args){
        ListaVetores lista = new ListaVetores(3);
        lista.add(4);
        lista.add(5);
        lista.add(6);
        lista.imprimeLista();
        lista.add(7);
        lista.imprimeLista();
        //int valor = lista.remove(0);
        //System.out.println(valor);
        lista.imprimeLista();
        lista.add(8);
        lista.add(80);
        lista.add(800);
        lista.imprimeLista();
        Integer x = lista.removeUltimo();
        System.out.println(x);
        
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
         x = lista.removeUltimo();
        System.out.println(x);
        
        //System.out.println(lista.getQuantidade());
        
    }
    
}
