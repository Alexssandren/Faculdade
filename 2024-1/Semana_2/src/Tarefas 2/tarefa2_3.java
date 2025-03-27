import java.util.Scanner;

public class tarefa2_3 {

    public static void main(String[] args) {
        Scanner dados = new Scanner(System.in);
        System.out.println(("Insira um valor qualquer maior que 1: "));
        int N = dados.nextInt();
    
        while(N <= 1){
            System.out.println("Valor inválido, digite outro:");
            N = dados.nextInt();
        }
        dados.close();

            for(int i = 1; i <= N; i++){
            System.out.println(i);
        }
    }
}
