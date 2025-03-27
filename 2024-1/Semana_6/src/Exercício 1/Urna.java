class UrnaEletronica {   
    private int votosBrancos;
    private int votosNulos;
    private int[] votosCandidatos;
    private boolean apurada;
    private int totalCandidatos;

    // Construtor que inicializa a urna com a quantidade de candidatos
    public UrnaEletronica(int totalCandidatos) {
        this.totalCandidatos = totalCandidatos;
        this.votosBrancos = 0;
        this.votosNulos = 0;
        this.votosCandidatos = new int[totalCandidatos];
        this.apurada = false;
    }

    // Método para votar em um candidato específico
    public void votar(int numeroCandidato) {
        if (apurada) {
            System.out.println("Erro: A urna já foi apurada. Não é possível votar.");
            return;
        }
        
        if (numeroCandidato >= 0 && numeroCandidato < totalCandidatos) {
            votosCandidatos[numeroCandidato]++;
            System.out.println("Voto registrado para o candidato " + numeroCandidato);
        } else {
            System.out.println("Erro: Número de candidato inválido.");
        }
    }

    // Método para votar em branco
    public void votarBranco() {
        if (apurada) {
            System.out.println("Erro: A urna já foi apurada. Não é possível votar.");
            return;
        }
        
        votosBrancos++;
        System.out.println("Voto em branco registrado.");
    }

    // Método para votar nulo
    public void votarNulo() {
        if (apurada) {
            System.out.println("Erro: A urna já foi apurada. Não é possível votar.");
            return;
        }
        
        votosNulos++;
        System.out.println("Voto nulo registrado.");
    }

    // Método para apurar a eleição
    public void apurar() {
        apurada = true;
        System.out.println("\n=== RESULTADO DA APURAÇÃO ===");
        System.out.println("Votos em branco: " + votosBrancos);
        System.out.println("Votos nulos: " + votosNulos);
        
        System.out.println("Votos por candidato:");
        for (int i = 0; i < totalCandidatos; i++) {
            System.out.println("Candidato " + i + ": " + votosCandidatos[i] + " votos");
        }
        
        int totalVotos = votosBrancos + votosNulos;
        for (int votos : votosCandidatos) {
            totalVotos += votos;
        }
        System.out.println("Total de votos: " + totalVotos);
    }

    // Método para verificar se a urna foi apurada
    public boolean isApurada() {
        return apurada;
    }
}

public class Urna {
    public static void main(String[] args) {
        // Cria uma urna para 3 candidatos (0, 1 e 2)
        UrnaEletronica urna = new UrnaEletronica(3);
        
        // Registra alguns votos
        urna.votar(0);     // Voto para candidato 0
        urna.votar(1);     // Voto para candidato 1
        urna.votarBranco(); // Voto em branco
        urna.votar(2);     // Voto para candidato 2
        urna.votarNulo();   // Voto nulo
        urna.votar(1);     // Voto para candidato 1
        
        // Apura a eleição
        urna.apurar();
        
        // Tentativa de votar após apuração (não deve permitir)
        urna.votar(0);
    }
}