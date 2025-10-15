public class TestaHeap {

       
    public static void printVet(int a[]){
        for (int i = 0; i < a.length; i++)
            System.out.print(a[i]+" ");
        System.out.println();
    }
    
    public static void main(String[] args){
    
        HeapSort heap = new HeapSort();
        
        int a[] = {16, 4, 10, 14, 7, 9, 3, 2, 8, 1};
        printVet(a);
        heap.heapSort(a, 10);
        printVet(a);
        
    }
}
    

