import java.util.Scanner;

public class tarefa2_2 {
    public static void main(String[] args) {
        
        Scanner dados = new Scanner(System.in);
        System.out.println(("Insira um valor de 1 a 10:"));
        int valor = dados.nextInt();

        while(valor >10 || valor < 0){
            System.out.println("Valor inválido, digite outro:");
            valor = dados.nextInt();
        }
        dados.close();

        int resultado;
        for(int i = 1; i <=10; i++){
            resultado = valor * i;
            System.out.println(resultado);
        }






    }
}
