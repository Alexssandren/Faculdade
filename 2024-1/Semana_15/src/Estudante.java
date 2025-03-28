public class Estudante {
    private String nome;
    private String cpf;
    private String matricula;
    private double nota01;
    private double nota02;

    // Construtor padrão
    public Estudante() {}

    public Estudante(String nome, String cpf, String matricula, double nota01, double nota02) {
        this.nome = nome;
        this.cpf = cpf;
        this.matricula = matricula;
        this.nota01 = nota01;
        this.nota02 = nota02;
    }

    public String getEstudanteCSV() {
        return nome + ";" + cpf + ";" + matricula + ";" + nota01 + ";" + nota02;
    }

    public void setEstudanteCSV(String linha) {
        String[] dados = linha.split(";");
        this.nome = dados[0];
        this.cpf = dados[1];
        this.matricula = dados[2];
        this.nota01 = Double.parseDouble(dados[3]);
        this.nota02 = Double.parseDouble(dados[4]);
    }

    public double getMedia() {
        return (nota01 + nota02) / 2.0;
    }

    // Getters
    public String getNome() {
        return nome;
    }

    public String getCpf() {
        return cpf;
    }

    public String getMatricula() {
        return matricula;
    }

    public double getNota01() {
        return nota01;
    }

    public double getNota02() {
        return nota02;
    }

    // Setters
    public void setNome(String nome) {
        this.nome = nome;
    }

    public void setCpf(String cpf) {
        this.cpf = cpf;
    }

    public void setMatricula(String matricula) {
        this.matricula = matricula;
    }

    public void setNota01(double nota01) {
        this.nota01 = nota01;
    }

    public void setNota02(double nota02) {
        this.nota02 = nota02;
    }
}
