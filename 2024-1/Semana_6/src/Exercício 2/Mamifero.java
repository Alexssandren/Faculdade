public class Mamifero extends Animal {
    private String tipoPelagem;

    public Mamifero(String nome, String especie, String familia, int idade, String tipoPelagem) {
        super(nome, especie, familia, idade);
        this.tipoPelagem = tipoPelagem;
    }

    @Override
    public String alimentar() {
        return "Mamífero se alimentando...";
    }

    // Getter e Setter
    public String getTipoPelagem() {
        return tipoPelagem;
    }

    public void setTipoPelagem(String tipoPelagem) {
        this.tipoPelagem = tipoPelagem;
    }
}