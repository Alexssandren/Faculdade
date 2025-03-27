import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.Component;

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
    private JButton btnOk;

    public JanelaPoupanca() {
        setTitle("Poupex - Calculadora de Poupança");
        setSize(350, 250);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BoxLayout(getContentPane(), BoxLayout.Y_AXIS));

        JPanel panelForm = new JPanel();
        panelForm.setLayout(new SpringLayout());

        // Campos do formulário
        addLabelAndField(panelForm, "Juros ao mês %:", txtJurosMes = new JTextField(10));
        addLabelAndField(panelForm, "Número de anos:", txtNumAnos = new JTextField(10));
        addLabelAndField(panelForm, "Depósito mensal R$:", txtDepositoMensal = new JTextField(10));
        addLabelAndField(panelForm, "Total poupado R$:", txtTotalPoupado = new JTextField(10));
        txtTotalPoupado.setEditable(false);

        SpringUtilities.makeCompactGrid(panelForm, 4, 2, 6, 6, 6, 6);
        add(panelForm);

        // Painel do botão
        JPanel panelButton = new JPanel();
        btnOk = new JButton("OK");
        btnOk.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularPoupanca();
            }
        });
        panelButton.add(btnOk);
        add(panelButton);
    }

    private void addLabelAndField(JPanel panel, String labelText, JTextField textField) {
        JLabel label = new JLabel(labelText, JLabel.TRAILING);
        panel.add(label);
        label.setLabelFor(textField);
        panel.add(textField);
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

// Classe utilitária para layout (SpringUtilities.java)
class SpringUtilities {
    public static void makeCompactGrid(JPanel panel,
                                     int rows, int cols,
                                     int initialX, int initialY,
                                     int xPad, int yPad) {
        SpringLayout layout;
        try {
            layout = (SpringLayout) panel.getLayout();
        } catch (ClassCastException exc) {
            System.err.println("O primeiro argumento para makeCompactGrid deve ser um JPanel com SpringLayout.");
            return;
        }

        Spring x = Spring.constant(initialX);
        Spring y = Spring.constant(initialY);
        Spring width = Spring.constant(0);
        Spring height = Spring.constant(0);

        // Calcula o grid
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                Component c = panel.getComponent(i * cols + j);
                SpringLayout.Constraints constraints = layout.getConstraints(c);

                constraints.setX(x);
                constraints.setY(y);

                width = Spring.max(width, constraints.getWidth());
                height = Spring.max(height, constraints.getHeight());
            }

            x = Spring.sum(x, Spring.sum(width, Spring.constant(xPad)));
            width = Spring.constant(0);
        }

        for (int j = 0; j < cols; j++) {
            for (int i = 0; i < rows; i++) {
                Component c = panel.getComponent(i * cols + j);
                SpringLayout.Constraints constraints = layout.getConstraints(c);

                constraints.setWidth(width);
                constraints.setHeight(height);
            }

            y = Spring.sum(y, Spring.sum(height, Spring.constant(yPad)));
            height = Spring.constant(0);
        }
    }
}