public class ContaInvestimento extends Conta {
    public ContaInvestimento(String titular, String numeroConta, String numeroAgencia, float saldo) {
        super(titular, numeroConta, numeroAgencia, saldo);
        this.percentual = 1.01f; // 1% de rendimento
    }
}