public class Endereco {
    private String cidade;
    private String bairro;

    public Endereco(String cidade, String bairro) {
        this.cidade = cidade;
        this.bairro = bairro;
    }

    public String getCidade() {
        return cidade;
    }

    public void setCidade(String cidade) {
        this.cidade = cidade;
    }

    public String getBairro() {
        return bairro;
    }

    public void setBairro(String bairro) {
        this.bairro = bairro;
    }

    @Override
    public String toString() {
        return bairro + ", " + cidade;
    }
}
