import java.util.Scanner;

class Retangulo {
    private double largura;
    private double altura;

    public Retangulo(double largura, double altura) {
        this.largura = largura;
        this.altura = altura;
    }

    public double calcularArea() {
        return largura * altura;
    }

    public double calcularPerimetro() {
        return 2 * (largura + altura);
    }

    public double calcularDiagonal() {
        return Math.sqrt(Math.pow(largura, 2) + Math.pow(altura, 2));
    }
}

public class tarefa5_1 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Digite a largura do retângulo:");
        double largura = scanner.nextDouble();

        System.out.println("Digite a altura do retângulo:");
        double altura = scanner.nextDouble();

        Retangulo retangulo = new Retangulo(largura, altura);

        double area = retangulo.calcularArea();
        double perimetro = retangulo.calcularPerimetro();
        double diagonal = retangulo.calcularDiagonal();

        System.out.println("Área do retângulo: " + area);
        System.out.println("Perímetro do retângulo: " + perimetro);
        System.out.println("Diagonal do retângulo: " + diagonal);

        scanner.close();
    }
}
