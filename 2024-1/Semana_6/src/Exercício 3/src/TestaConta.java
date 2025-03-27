public class TestaConta {
    public static void main(String[] args) {
        // Criando contas
        ContaCorrente cc = new ContaCorrente("João Silva", "12345-6", "001", 1000);
        ContaPoupanca cp = new ContaPoupanca("Maria Souza", "54321-0", "001", 2000);
        ContaInvestimento ci = new ContaInvestimento("Carlos Andrade", "98765-4", "002", 5000);

        // Testando operações
        cc.deposito(500);
        cc.saque(200);
        cc.transferePara(cp, 300);

        cp.saque(100);
        cp.deposito(400);

        ci.deposito(1000);
        ci.saque(500);

        // Imprimindo resultados
        System.out.println("=== Conta Corrente ===");
        System.out.println(cc);
        System.out.println("\n=== Conta Poupança ===");
        System.out.println(cp);
        System.out.println("\n=== Conta Investimento ===");
        System.out.println(ci);

        // Testando atualização com rendimentos
        System.out.println("\n=== Após atualização com rendimentos ===");
        cc.atualizar();
        cp.atualizar();
        ci.atualizar();

        System.out.println("Conta Poupança (0.5%): " + cp.getSaldo());
        System.out.println("Conta Investimento (1%): " + ci.getSaldo());
    }
}