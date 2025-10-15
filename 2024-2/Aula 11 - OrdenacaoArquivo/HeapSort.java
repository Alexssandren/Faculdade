public class HeapSort {
    
    int left(int i) {
        return 2*i + 1;    
    }

    int right(int i) {
        return 2*i + 2;    
    }

    int father(int i) {
        return (i-1)/2;
    }

    void maxHeapfy(int a[], int i, int n) {
        int maior;
        int esq = left(i);
        int dir = right(i);

        if ((esq < n) && (a[esq] > a[i])){
           maior = esq;
        }
        else maior = i;

        if ((dir < n) && (a[dir] > a[maior])){ 
           maior = dir;
        }
           
        if (maior != i) {
           int aux = a[maior];
           a[maior] = a[i];
           a[i] = aux;
           
           maxHeapfy(a, maior, n);
        }
    }               



    void buildMaxHeap(int a[], int n) {
        int i;
        for (i = (n-1)/2; i>=0; i--) {
            maxHeapfy(a, i, n);
        }
}

    void heapSort(int a[], int n) {
     
     int i;
     buildMaxHeap(a, n);
     for (i = n-1; i >= 1; i--){
         int aux = a[0];
         a[0] = a[i];
         a[i] = aux;
         n--;
         maxHeapfy(a, 0, n);
     }
     
    }

 
}
