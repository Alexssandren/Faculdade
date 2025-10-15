public class ED201802 {

    public static void imprime(int n){
        System.out.print(n + " ");
        if (n != 1) imprime(n-1);
    }
    
    public static int fatorial(int n){
        if (n == 0) 
            return 1;
        else 
            return n * fatorial(n-1);
    }
    
    public static void main(String[] args) {
        // TODO code application logic here
        //int x = fatorial(17);
        imprime(50);
        //System.out.println(x);
    }
    
}
