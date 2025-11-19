"""
Testes unitários para o Sistema de Controle de Velocidade da Ventoinha Fuzzy
Versão atualizada: usa temperatura CPU e carga de processamento
"""

import unittest
import sys
import os

# Adicionar diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fuzzy_logic import FanController, control_fan_speed


class TestFanController(unittest.TestCase):
    """Testes para a classe FanController atualizada"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.controller = FanController()

    def test_fan_ranges(self):
        """Testar se os ranges da ventoinha estão corretos"""
        self.assertEqual(len(self.controller.cpu_temp_range), 71)  # 30 a 100
        self.assertEqual(len(self.controller.cpu_load_range), 101) # 0 a 100
        self.assertEqual(len(self.controller.fan_speed_range), 101) # 0 a 100

        self.assertEqual(self.controller.cpu_temp_range[0], 30)
        self.assertEqual(self.controller.cpu_temp_range[-1], 100)
        self.assertEqual(self.controller.cpu_load_range[0], 0)
        self.assertEqual(self.controller.cpu_load_range[-1], 100)
        self.assertEqual(self.controller.fan_speed_range[0], 0)
        self.assertEqual(self.controller.fan_speed_range[-1], 100)

    def test_fan_membership_functions(self):
        """Testar funções de pertinência da ventoinha"""
        # Testar valores extremos
        temp_min = self.controller.get_membership_values(30, 50)  # CPU 30°C, carga 50%
        temp_max = self.controller.get_membership_values(100, 50) # CPU 100°C, carga 50%
        load_min = self.controller.get_membership_values(55, 0)   # CPU 55°C, carga 0%
        load_max = self.controller.get_membership_values(55, 100) # CPU 55°C, carga 100%

        # Temperatura mínima deve pertencer totalmente ao conjunto "baixa"
        self.assertAlmostEqual(temp_min['cpu_temp_baixa'], 1.0, places=2)
        self.assertAlmostEqual(temp_min['cpu_temp_alta'], 0.0, places=2)

        # Temperatura máxima deve pertencer totalmente ao conjunto "alta"
        self.assertAlmostEqual(temp_max['cpu_temp_alta'], 1.0, places=2)
        self.assertAlmostEqual(temp_max['cpu_temp_baixa'], 0.0, places=2)

        # Carga mínima deve pertencer totalmente ao conjunto "baixa"
        self.assertAlmostEqual(load_min['cpu_load_baixa'], 1.0, places=2)
        self.assertAlmostEqual(load_min['cpu_load_alta'], 0.0, places=2)

        # Carga máxima deve pertencer totalmente ao conjunto "alta"
        self.assertAlmostEqual(load_max['cpu_load_alta'], 1.0, places=2)
        self.assertAlmostEqual(load_max['cpu_load_baixa'], 0.0, places=2)

    def test_fan_speed_calculation(self):
        """Testar cálculos de velocidade baseados na temperatura CPU e carga"""
        # CPU fria + baixa carga → velocidade baixa
        speed_low = self.controller.get_fan_speed(35, 10)  # CPU 35°C, carga 10%
        self.assertLess(speed_low, 20)  # Menos de 20%

        # CPU quente + alta carga → velocidade alta
        speed_high = self.controller.get_fan_speed(80, 90)  # CPU 80°C, carga 90%
        self.assertGreater(speed_high, 80)  # Mais de 80%

        # CPU em temperatura normal + carga média → velocidade média
        speed_medium = self.controller.get_fan_speed(55, 50)  # CPU 55°C, carga 50%
        self.assertTrue(25 <= speed_medium <= 45)  # Entre 25% e 45%

    def test_fan_speed_extremes(self):
        """Testar cálculos em valores extremos"""
        # Testar limites do range
        speed_min_temp = self.controller.get_fan_speed(30, 50)  # Temp mínima
        speed_max_temp = self.controller.get_fan_speed(100, 50) # Temp máxima
        speed_min_load = self.controller.get_fan_speed(55, 0)   # Carga mínima
        speed_max_load = self.controller.get_fan_speed(55, 100) # Carga máxima

        # Todos os valores devem estar no range válido
        for speed in [speed_min_temp, speed_max_temp, speed_min_load, speed_max_load]:
            self.assertGreaterEqual(speed, 0)
            self.assertLessEqual(speed, 100)

        # Testar valores fora do range (devem ser limitados)
        speed_temp_over = self.controller.get_fan_speed(120, 50)  # Temp > 100°C → limitado a 100°C
        speed_temp_under = self.controller.get_fan_speed(20, 50)  # Temp < 30°C → limitado a 30°C
        speed_load_over = self.controller.get_fan_speed(55, 120)  # Carga > 100% → limitado a 100%
        speed_load_under = self.controller.get_fan_speed(55, -10) # Carga < 0% → limitado a 0%

        self.assertEqual(speed_temp_over, self.controller.get_fan_speed(100, 50))
        self.assertEqual(speed_temp_under, self.controller.get_fan_speed(30, 50))
        self.assertEqual(speed_load_over, self.controller.get_fan_speed(55, 100))
        self.assertEqual(speed_load_under, self.controller.get_fan_speed(55, 0))

    def test_fuzzy_rules_fan_based(self):
        """Testar se as regras fuzzy estão definidas para temperatura CPU e carga"""
        self.assertEqual(len(self.controller.rules), 9)  # 3x3 = 9 regras

        # Verificar se as regras estão conectadas corretamente
        for rule in self.controller.rules:
            self.assertIsNotNone(rule.antecedent)
            self.assertIsNotNone(rule.consequent)

    def test_control_system_simulation(self):
        """Testar se o sistema de controle está funcionando com temperatura CPU e carga"""
        # Verificar se o simulador existe
        self.assertIsNotNone(self.controller.fan_sim)

        # Testar uma simulação completa usando get_fan_speed
        speed_result = self.controller.get_fan_speed(55, 50)  # Caso médio

        self.assertIsInstance(speed_result, (int, float))
        self.assertGreaterEqual(speed_result, 0)
        self.assertLessEqual(speed_result, 100)

        # Verificar que o resultado é razoável para condições normais
        self.assertTrue(25 <= speed_result <= 45)


class TestConvenienceFunction(unittest.TestCase):
    """Testes para a função de conveniência control_fan_speed"""

    def test_control_fan_speed_function(self):
        """Testar função control_fan_speed com temperatura CPU e carga"""
        # Testar alguns valores
        speed1 = control_fan_speed(35, 20)  # CPU fria, baixa carga
        speed2 = control_fan_speed(70, 80)  # CPU quente, alta carga
        speed3 = control_fan_speed(55, 50)  # Condições normais

        self.assertIsInstance(speed1, (int, float))
        self.assertIsInstance(speed2, (int, float))
        self.assertIsInstance(speed3, (int, float))

        # Verificar se são valores válidos
        for speed in [speed1, speed2, speed3]:
            self.assertGreaterEqual(speed, 0)
            self.assertLessEqual(speed, 100)

    def test_consistency(self):
        """Testar consistência entre função e classe"""
        cpu_temp, cpu_load = 70, 60
        speed_class = FanController().get_fan_speed(cpu_temp, cpu_load)
        speed_function = control_fan_speed(cpu_temp, cpu_load)

        self.assertAlmostEqual(speed_class, speed_function, places=5)


class TestIntegration(unittest.TestCase):
    """Testes de integração com o novo sistema de controle de ventoinha"""

    def test_real_world_scenarios(self):
        """Testar cenários realistas de controle de ventoinha"""
        controller = FanController()

        # Cenário 1: Computador ocioso (CPU fria, baixa carga)
        speed1 = controller.get_fan_speed(35, 10)  # CPU: 35°C, Carga: 10%
        self.assertLess(speed1, 20)  # Deve ter velocidade baixa

        # Cenário 2: Trabalho normal (CPU morna, carga média)
        speed2 = controller.get_fan_speed(55, 50)  # CPU: 55°C, Carga: 50%
        self.assertTrue(25 <= speed2 <= 45)  # Velocidade média

        # Cenário 3: Gaming intenso (CPU quente, alta carga)
        speed3 = controller.get_fan_speed(80, 90)  # CPU: 80°C, Carga: 90%
        self.assertGreater(speed3, 80)  # Deve ter velocidade muito alta

    def test_fan_speed_calculation(self):
        """Testar cálculo correto da velocidade da ventoinha"""
        controller = FanController()

        # Testar diferentes combinações
        test_cases = [
            (35, 10, "baixa"),     # CPU fria, baixa carga
            (55, 50, "media"),     # CPU normal, carga média
            (80, 90, "muito_alta"), # CPU quente, alta carga
            (45, 80, "alta"),      # CPU morna, alta carga
            (75, 20, "alta"),      # CPU quente, baixa carga
        ]

        for cpu_temp, cpu_load, expected_level in test_cases:
            with self.subTest(cpu_temp=cpu_temp, cpu_load=cpu_load):
                speed = controller.get_fan_speed(cpu_temp, cpu_load)

                # Verificar que velocidade é válida
                self.assertGreaterEqual(speed, 0)
                self.assertLessEqual(speed, 100)

                # Verificar faixas aproximadas baseadas no nível esperado
                if expected_level == "baixa":
                    self.assertLess(speed, 25)
                elif expected_level == "media":
                    self.assertTrue(15 <= speed <= 50)
                elif expected_level == "alta":
                    self.assertTrue(40 <= speed <= 75)
                elif expected_level == "muito_alta":
                    self.assertGreater(speed, 70)

    def test_membership_complementarity(self):
        """Testar que os valores de pertinência são válidos"""
        controller = FanController()

        test_cases = [
            (35, 20),  # CPU fria, baixa carga
            (55, 50),  # CPU normal, carga média
            (80, 80),  # CPU quente, alta carga
            (45, 70),  # CPU morna, carga alta
        ]

        for cpu_temp, cpu_load in test_cases:
            with self.subTest(cpu_temp=cpu_temp, cpu_load=cpu_load):
                membership = controller.get_membership_values(cpu_temp, cpu_load)

                # Verificar que todos os valores estão entre 0 e 1
                for key, value in membership.items():
                    self.assertGreaterEqual(value, 0, f"{key} deve ser >= 0")
                    self.assertLessEqual(value, 1, f"{key} deve ser <= 1")

                # Verificar que pelo menos um valor é significativo (> 0.1) para cada tipo
                temp_values = [v for k, v in membership.items() if k.startswith('cpu_temp') and v > 0.1]
                load_values = [v for k, v in membership.items() if k.startswith('cpu_load') and v > 0.1]

                self.assertGreater(len(temp_values), 0, "Pelo menos um conjunto de temperatura deve ter pertinência significativa")
                self.assertGreater(len(load_values), 0, "Pelo menos um conjunto de carga deve ter pertinência significativa")


if __name__ == '__main__':
    print("Executando testes do Sistema de Controle de Ventoinha Fuzzy...")
    unittest.main(verbosity=2)
