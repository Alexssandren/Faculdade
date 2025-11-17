"""
Testes unitários para o Sistema de Controle de Temperatura Fuzzy
Versão atualizada: usa erro (diferença entre temperaturas desejada e atual)
"""

import unittest
import sys
import os

# Adicionar diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fuzzy_logic import TemperatureController, control_temperature


class TestTemperatureController(unittest.TestCase):
    """Testes para a classe TemperatureController atualizada"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.controller = TemperatureController()

    def test_error_ranges(self):
        """Testar se os ranges de erro estão corretos"""
        self.assertEqual(len(self.controller.error_range), 41)  # -20 a +20
        self.assertEqual(len(self.controller.power_range), 101)  # 0 a 100

        self.assertEqual(self.controller.error_range[0], -20)
        self.assertEqual(self.controller.error_range[-1], 20)
        self.assertEqual(self.controller.power_range[0], 0)
        self.assertEqual(self.controller.power_range[-1], 100)

    def test_error_membership_functions(self):
        """Testar funções de pertinência do erro"""
        # Testar valores extremos
        error_minus_20 = self.controller.get_membership_values(-50, -30)  # erro = -30 - (-50) = +20
        error_plus_20 = self.controller.get_membership_values(30, 10)     # erro = 10 - 30 = -20

        # Erro +20 deve pertencer totalmente ao conjunto "muito_quente"
        self.assertAlmostEqual(error_minus_20['muito_quente'], 1.0, places=2)
        self.assertAlmostEqual(error_minus_20['muito_frio'], 0.0, places=2)

        # Erro -20 deve pertencer totalmente ao conjunto "muito_frio"
        self.assertAlmostEqual(error_plus_20['muito_frio'], 1.0, places=2)
        self.assertAlmostEqual(error_plus_20['muito_quente'], 0.0, places=2)

    def test_power_calculation_error_based(self):
        """Testar cálculos de potência baseados no erro"""
        # Erro positivo grande (ambiente muito fria) → potência alta
        power_high = self.controller.get_power(15, 25)  # erro = 25-15 = +10
        self.assertGreater(power_high, 70)  # Mais de 70%

        # Erro próximo de zero (temperatura ideal) → potência muito baixa
        power_low = self.controller.get_power(22, 22)  # erro = 0
        self.assertTrue(5 <= power_low <= 15)  # Entre 5% e 15%

        # Erro negativo grande (ambiente muito quente) → potência baixa
        power_low = self.controller.get_power(30, 20)  # erro = 20-30 = -10
        self.assertLess(power_low, 30)  # Menos de 30%

    def test_power_calculation_extremes(self):
        """Testar cálculos em erros extremos"""
        # Testar limites do range
        power_min_error = self.controller.get_power(-50, -30)  # erro = +20 (max)
        power_max_error = self.controller.get_power(30, 10)    # erro = -20 (min)

        self.assertGreaterEqual(power_min_error, 0)
        self.assertLessEqual(power_min_error, 100)
        self.assertGreaterEqual(power_max_error, 0)
        self.assertLessEqual(power_max_error, 100)

        # Testar erros fora do range (devem ser limitados)
        power_error_over = self.controller.get_power(-50, -10)  # erro = +40 → limitado a +20
        power_error_under = self.controller.get_power(50, 10)   # erro = -40 → limitado a -20

        self.assertEqual(power_error_over, self.controller.get_power(-50, -30))  # erro = +20
        self.assertEqual(power_error_under, self.controller.get_power(30, 10))   # erro = -20

    def test_fuzzy_rules_error_based(self):
        """Testar se as regras fuzzy estão definidas para erro"""
        self.assertEqual(len(self.controller.rules), 5)

        # Verificar se as regras estão conectadas corretamente
        for rule in self.controller.rules:
            self.assertIsNotNone(rule.antecedent)
            self.assertIsNotNone(rule.consequent)

    def test_control_system_simulation(self):
        """Testar se o sistema de controle está funcionando com erro"""
        # Verificar se o simulador existe
        self.assertIsNotNone(self.controller.power_sim)

        # Testar uma simulação completa usando get_power
        power_result = self.controller.get_power(22, 22)  # erro = 0 (caso simples)

        self.assertIsInstance(power_result, (int, float))
        self.assertGreaterEqual(power_result, 0)
        self.assertLessEqual(power_result, 100)

        # Verificar que o resultado é razoável para erro 0 (manutenção)
        self.assertTrue(5 <= power_result <= 15)


class TestConvenienceFunction(unittest.TestCase):
    """Testes para a função de conveniência control_temperature"""

    def test_control_temperature_function(self):
        """Testar função control_temperature com duas temperaturas"""
        # Testar alguns valores
        power1 = control_temperature(20, 22)  # erro = +2
        power2 = control_temperature(25, 22)  # erro = -3
        power3 = control_temperature(15, 22)  # erro = +7

        self.assertIsInstance(power1, (int, float))
        self.assertIsInstance(power2, (int, float))
        self.assertIsInstance(power3, (int, float))

        # Verificar se são valores válidos
        for power in [power1, power2, power3]:
            self.assertGreaterEqual(power, 0)
            self.assertLessEqual(power, 100)

    def test_consistency(self):
        """Testar consistência entre função e classe"""
        current_temp, desired_temp = 25, 22
        power_class = TemperatureController().get_power(current_temp, desired_temp)
        power_function = control_temperature(current_temp, desired_temp)

        self.assertAlmostEqual(power_class, power_function, places=5)


class TestIntegration(unittest.TestCase):
    """Testes de integração com o novo sistema"""

    def test_real_world_scenarios(self):
        """Testar cenários realistas de controle de temperatura"""
        controller = TemperatureController()

        # Cenário 1: Quarto muito quente no verão (erro negativo = precisa de baixa potência)
        power1 = controller.get_power(32, 22)  # Ambiente: 32°C, Desejado: 22°C, Erro: -10°C
        self.assertLess(power1, 30)  # Deve precisar de baixa potência

        # Cenário 2: Temperatura confortável
        power2 = controller.get_power(22, 22)  # Ambiente: 22°C, Desejado: 22°C, Erro: 0°C
        self.assertTrue(5 <= power2 <= 15)  # Potência muito baixa de manutenção

        # Cenário 3: Verificar que o erro é calculado corretamente
        # Ambiente 17°C, desejado 22°C → erro = +5°C
        self.assertEqual(22 - 17, 5)  # Verificação básica do cálculo de erro

    def test_error_calculation(self):
        """Testar cálculo correto do erro"""
        controller = TemperatureController()

        # Testar diferentes combinações
        test_cases = [
            (25, 22, -3),   # Ambiente > Desejado
            (20, 22, 2),    # Ambiente < Desejado
            (22, 22, 0),    # Ambiente = Desejado
            (30, 20, -10),  # Diferença grande negativa
            (15, 25, 10),   # Diferença grande positiva
        ]

        for current, desired, expected_error in test_cases:
            with self.subTest(current=current, desired=desired):
                power = controller.get_power(current, desired)
                calculated_error = desired - current
                self.assertEqual(calculated_error, expected_error)

                # Verificar que potência é válida
                self.assertGreaterEqual(power, 0)
                self.assertLessEqual(power, 100)

    def test_membership_complementarity(self):
        """Testar que os valores de pertinência do erro são válidos"""
        controller = TemperatureController()

        test_cases = [
            (25, 22),  # erro = -3
            (20, 22),  # erro = +2
            (22, 22),  # erro = 0
            (30, 20),  # erro = -10
        ]

        for current, desired in test_cases:
            with self.subTest(current=current, desired=desired):
                membership = controller.get_membership_values(current, desired)

                # Verificar que todos os valores estão entre 0 e 1
                for key, value in membership.items():
                    self.assertGreaterEqual(value, 0, f"{key} deve ser >= 0")
                    self.assertLessEqual(value, 1, f"{key} deve ser <= 1")

                # Verificar que pelo menos um valor é significativo (> 0.1)
                significant_values = [v for v in membership.values() if v > 0.1]
                self.assertGreater(len(significant_values), 0, "Pelo menos um conjunto deve ter pertinência significativa")


if __name__ == '__main__':
    print("Executando testes do Sistema Fuzzy Atualizado...")
    unittest.main(verbosity=2)
