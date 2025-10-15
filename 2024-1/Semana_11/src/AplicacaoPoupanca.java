import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class AplicacaoPoupanca {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new JanelaPoupanca().setVisible(true);
        });
    }
}

class JanelaPoupanca extends JFrame {
    private JTextField txtJurosMes;
    private JTextField txtNumAnos;
    private JTextField txtDepositoMensal;
    private JTextField txtTotalPoupado;

    public JanelaPoupanca() {
        setTitle("Poupex - Calculadora de Poupança");
        setSize(350, 250);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        
        // Usando GridBagLayout para melhor organização
        setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.anchor = GridBagConstraints.WEST;
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Adicionando componentes
        gbc.gridx = 0;
        gbc.gridy = 0;
        add(new JLabel("Juros ao mês %:"), gbc);
        
        gbc.gridx = 1;
        txtJurosMes = new JTextField(10);
        add(txtJurosMes, gbc);

        gbc.gridx = 0;
        gbc.gridy = 1;
        add(new JLabel("Número de anos:"), gbc);
        
        gbc.gridx = 1;
        txtNumAnos = new JTextField(10);
        add(txtNumAnos, gbc);

        gbc.gridx = 0;
        gbc.gridy = 2;
        add(new JLabel("Depósito mensal R$:"), gbc);
        
        gbc.gridx = 1;
        txtDepositoMensal = new JTextField(10);
        add(txtDepositoMensal, gbc);

        gbc.gridx = 0;
        gbc.gridy = 3;
        add(new JLabel("Total poupado R$:"), gbc);
        
        gbc.gridx = 1;
        txtTotalPoupado = new JTextField(10);
        txtTotalPoupado.setEditable(false);
        add(txtTotalPoupado, gbc);

        // Botão OK
        gbc.gridx = 0;
        gbc.gridy = 4;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.CENTER;
        JButton btnOk = new JButton("OK");
        btnOk.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularPoupanca();
            }
        });
        add(btnOk, gbc);
    }

    private void calcularPoupanca() {
        try {
            // Validação dos campos
            if (txtJurosMes.getText().isEmpty() || 
                txtNumAnos.getText().isEmpty() || 
                txtDepositoMensal.getText().isEmpty()) {
                JOptionPane.showMessageDialog(this, 
                    "Preencha todos os campos para calcular!", 
                    "Atenção", JOptionPane.WARNING_MESSAGE);
                return;
            }

            double jurosMes = Double.parseDouble(txtJurosMes.getText()) / 100;
            int numAnos = Integer.parseInt(txtNumAnos.getText());
            double depositoMensal = Double.parseDouble(txtDepositoMensal.getText());

            // Cálculo do total poupado
            int numMeses = numAnos * 12;
            double total = 0;
            
            for (int i = 0; i < numMeses; i++) {
                total += depositoMensal;
                total *= (1 + jurosMes);
            }

            txtTotalPoupado.setText(String.format("R$ %.2f", total));

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, 
                "Digite valores numéricos válidos!", 
                "Erro", JOptionPane.ERROR_MESSAGE);
        }
    }
}