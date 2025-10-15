public class PesquisaBinaria {
    
    void printVet(int a[]){
        for (int i = 0; i < a.length; i++)
            System.out.print(a[i]+" ");
        System.out.println();
    }
    
    int busca_bin_rec(int a[], int ini, int fim, int valor){
        if (ini <= fim) {
            int meio = (ini + fim)/2;
            if (valor < a[meio]) 
                return busca_bin_rec(a, ini, meio-1, valor);
            else if (valor > a[meio]) 
                return busca_bin_rec (a, meio+1, fim, valor);
            else 
                return meio;
        }
        return -1;
    }
    
    int busca_binaria (int a[], int valor){
        int inicio = 0;
        int fim = a.length-1;
        while (inicio <= fim){
            int meio = (inicio + fim)/2;
            if (valor < a[meio]) fim = meio -1;
            else if (valor > a[meio]) inicio = meio + 1;
            else return meio;
        }
        return -1;
    }
}