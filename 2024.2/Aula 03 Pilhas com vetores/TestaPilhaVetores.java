/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package pilhavetores;

/**
 *
 * @author cechinel
 */
public class TestaPilhaVetores {
    public static void main(String[] args){
        PilhaVetores nossapilha = new PilhaVetores(10);
        nossapilha.empilha(2);
        nossapilha.empilha(4);
        nossapilha.empilha(6);
        Integer i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        nossapilha.empilha(4);
        nossapilha.empilha(6);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        i = nossapilha.desempilha();
        System.out.println("desempilhou "+ i);
        
    }
    
}
