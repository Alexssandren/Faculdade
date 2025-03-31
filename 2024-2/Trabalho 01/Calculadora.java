public class Calculadora {
    private PilhaGenerica<Double> pilhaValores;
    private PilhaGenerica<Character> pilhaOperadores;

    public Calculadora() {
        pilhaValores = new PilhaGenerica<>();
        pilhaOperadores = new PilhaGenerica<>();
    }

    public void empilharValor(double valor) {
        pilhaValores.empilhar(valor);
        System.out.println("Valor " + valor + " empilhado.");
    }

    public void empilharOperador(char operador) {
        if (operador == '+' || operador == '-' || operador == '*' || operador == '/') {
            pilhaOperadores.empilhar(operador);
            System.out.println("Operador " + operador + " empilhado.");
        } else {
            System.out.println("Operador inválido!");
        }
    }

    public void realizarCalculo() {
        if (pilhaValores.tamanho() < 2) {
            System.out.println("Erro: Não há valores suficientes para realizar o cálculo. São necessários dois valores.");
            return;
        }

        if (pilhaOperadores.vazia()) {
            System.out.println("Erro: Não há operador disponível para realizar o cálculo.");
            return;
        }

        double valor2 = pilhaValores.desempilhar();
        double valor1 = pilhaValores.desempilhar();
        char operador = pilhaOperadores.desempilhar();

        double resultado = 0;
        switch (operador) {
            case '+':
                resultado = valor1 + valor2;
                break;
            case '-':
                resultado = valor1 - valor2;
                break;
            case '*':
                resultado = valor1 * valor2;
                break;
            case '/':
                if (valor2 != 0) {
                    resultado = valor1 / valor2;
                } else {
                    System.out.println("Erro: Divisao por zero.");
                    pilhaValores.empilhar(valor1);
                    pilhaValores.empilhar(valor2);
                    return;
                }
                break;
            default:
                System.out.println("Erro: Operador invalido.");
                return;
        }

        System.out.println("Resultado: " + resultado);
        pilhaValores.empilhar(resultado);
    }

    public void imprimirPilhas() {
        System.out.println("Pilha de valores: " + pilhaValores);
        System.out.println("Pilha de operadores: " + pilhaOperadores);
    }
}
