public class ContaCorrente extends Conta {
    public ContaCorrente(String titular, String numeroConta, String numeroAgencia, float saldo) {
        super(titular, numeroConta, numeroAgencia, saldo);
        this.percentual = 1.0f; // Sem rendimento
    }
}