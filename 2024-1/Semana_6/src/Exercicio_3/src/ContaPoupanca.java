public class ContaPoupanca extends Conta {
    public ContaPoupanca(String titular, String numeroConta, String numeroAgencia, float saldo) {
        super(titular, numeroConta, numeroAgencia, saldo);
        this.percentual = 1.005f; // 0.5% de rendimento
    }
}