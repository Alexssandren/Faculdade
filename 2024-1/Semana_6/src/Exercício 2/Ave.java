public class Ave extends Animal {
    private String tipoDeBico;

    public Ave(String nome, String especie, String familia, int idade, String tipoDeBico) {
        super(nome, especie, familia, idade);
        this.tipoDeBico = tipoDeBico;
    }

    @Override
    public String alimentar() {
        return "Ave se alimentando...";
    }

    public String voar() {
        return "Ave voando...";
    }

    // Getter e Setter
    public String getTipoDeBico() {
        return tipoDeBico;
    }

    public void setTipoDeBico(String tipoDeBico) {
        this.tipoDeBico = tipoDeBico;
    }
}