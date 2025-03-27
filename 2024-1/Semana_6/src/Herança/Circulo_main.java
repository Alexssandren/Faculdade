// Classe Ponto (classe pai)
class Ponto {
    private int x;       // Atributo privado (acessível apenas dentro da classe Ponto)
    protected int y;     // Atributo protegido (acessível na classe Ponto e suas subclasses)
    
    // Construtor
    public Ponto(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    // Métodos getters (encapsulamento)
    public int getX() {
        return x;
    }
    
    public int getY() {
        return y;
    }
    
    // Método para exibir informações
    public void exibir() {
        System.out.println("Ponto (" + x + ", " + y + ")");
    }
}

// Classe Circulo (herda de Ponto)
class Circulo extends Ponto {
    private double raio;
    
    // Construtor
    public Circulo(int x, int y, double raio) {
        super(x, y);  // Chama o construtor da classe pai
        this.raio = raio;
    }
    
    // Método para calcular área
    public double calcularArea() {
        return Math.PI * raio * raio;
    }
    
    // Sobrescrita do método exibir()
    @Override
    public void exibir() {
        // Acesso PERMITIDO ao atributo protected y da classe pai
        System.out.println("Círculo - Centro: (" + getX() + ", " + y + "), Raio: " + raio);
        
        // Tentativa de acesso ao atributo private x da classe pai (GERARIA ERRO)
        // System.out.println("Tentando acessar x diretamente: " + x); // ERRO DE COMPILAÇÃO!
    }
}

// Classe principal para teste
public class Circulo_main {
    public static void main(String[] args) {
        System.out.println("=== TESTE DA CLASSE PONTO ===");
        Ponto p = new Ponto(3, 4);
        p.exibir();
        System.out.println("X (via getter): " + p.getX());
        System.out.println("Y (via getter): " + p.getY());
        
        System.out.println("\n=== TESTE DA CLASSE CÍRCULO ===");
        Circulo c = new Circulo(1, 2, 5.0);
        c.exibir();
        System.out.println("Área: " + c.calcularArea());
        
        System.out.println("\n=== VERIFICAÇÃO DE ACESSO ===");
        System.out.println("Acesso a Y (protected - permitido): " + c.getY());
        // System.out.println("Acesso a X (private - não permitido): " + c.x); // ERRO!
        
        System.out.println("\n=== DEMONSTRAÇÃO DE ENCAPSULAMENTO ===");
        System.out.println("Atributo private x só é acessível via getX()");
        System.out.println("Atributo protected y é acessível diretamente na subclasse");
    }
}