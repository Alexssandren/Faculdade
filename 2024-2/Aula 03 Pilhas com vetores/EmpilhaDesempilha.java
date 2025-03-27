package pilhavetores;
import java.util.Scanner;

public class EmpilhaDesempilha {
    
    public static void main(String[] args){
        PilhaVetores p1 = new PilhaVetores(10);
        PilhaVetores p2 = new PilhaVetores(10);
        Scanner entrada = new Scanner(System.in);
        System.out.println("digite quantidade de elementos q deseja empilhar (max 10)");
        int qt = entrada.nextInt();
        int valor;
        int i = 0;
        while (i < qt && i < 10){
            System.out.println("digite valor para empilhar");
            valor = entrada.nextInt();
            p1.empilha(valor);
            i++;
        }
        System.out.println("Pilha 1 ->");
        p1.imprimePilha();
        
        while (!p1.vazia()){
            //p2.empilha(p1.desempilha());
            valor = p1.desempilha();
            p2.empilha(valor);
        
        }
        System.out.println("Pilha 2 ->");
        p2.imprimePilha();
   
    }
    
}
