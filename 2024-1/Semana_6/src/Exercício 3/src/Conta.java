public class Conta {
    protected String titular;
    protected String numeroConta;
    protected String numeroAgencia;
    protected float saldo;
    protected String status; // "positivo" ou "negativo"
    protected float percentual;

    public Conta(String titular, String numeroConta, String numeroAgencia, float saldo) {
        this.titular = titular;
        this.numeroConta = numeroConta;
        this.numeroAgencia = numeroAgencia;
        this.saldo = saldo;
        this.alteraStatus();
        this.percentual = 1.0f; // Sem rendimento padrão
    }

    public int saque(float valor) {
        if (valor <= 0) return -1; // Valor inválido
        if (saldo < valor) return -2; // Saldo insuficiente
        
        saldo -= valor;
        alteraStatus();
        atualizar();
        return 0; // Sucesso
    }

    public int deposito(float valor) {
        if (valor <= 0) return -1; // Valor inválido
        
        saldo += valor;
        alteraStatus();
        atualizar();
        return 0; // Sucesso
    }

    public void alteraStatus() {
        this.status = (saldo >= 0) ? "positivo" : "negativo";
    }

    public void atualizar() {
        this.saldo = this.saldo * percentual;
    }

    public void transferePara(Conta destino, float valor) {
        if (this.saque(valor) == 0) {
            destino.deposito(valor);
        }
    }

    @Override
    public String toString() {
        return "Conta{" +
                "titular='" + titular + '\'' +
                ", numeroConta='" + numeroConta + '\'' +
                ", numeroAgencia='" + numeroAgencia + '\'' +
                ", saldo=" + saldo +
                ", status='" + status + '\'' +
                '}';
    }

    // Getters
    public String getTitular() { return titular; }
    public String getNumeroConta() { return numeroConta; }
    public String getNumeroAgencia() { return numeroAgencia; }
    public float getSaldo() { return saldo; }
    public String getStatus() { return status; }
}