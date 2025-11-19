"""
Sistema de Controle de Velocidade de Ventoinha usando Lógica Fuzzy
Controla a velocidade da ventoinha baseada na temperatura da CPU e carga de processamento
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FanController:
    """
    Controlador Fuzzy para sistema de ventoinha de computador
    Baseado na temperatura da CPU e carga de processamento, determina a velocidade ideal da ventoinha
    """

    def __init__(self):
        self.cpu_temp_range = np.arange(30, 101, 1)
        self.cpu_load_range = np.arange(0, 101, 1)
        self.fan_speed_range = np.arange(0, 101, 1)

        self.cpu_temp = ctrl.Antecedent(self.cpu_temp_range, 'cpu_temp')
        self.cpu_load = ctrl.Antecedent(self.cpu_load_range, 'cpu_load')
        self.fan_speed = ctrl.Consequent(self.fan_speed_range, 'fan_speed')

        self._define_cpu_temp_membership()
        self._define_cpu_load_membership()
        self._define_fan_speed_membership()
        self._define_rules()
        self._create_control_system()

    def _define_cpu_temp_membership(self):
        """Define as funções de pertinência para a temperatura da CPU"""
        self.cpu_temp['baixa'] = fuzz.trimf(self.cpu_temp_range, [30, 30, 50])
        self.cpu_temp['media'] = fuzz.trimf(self.cpu_temp_range, [40, 55, 70])
        self.cpu_temp['alta'] = fuzz.trimf(self.cpu_temp_range, [60, 100, 100])

    def _define_cpu_load_membership(self):
        """Define as funções de pertinência para a carga de processamento"""
        self.cpu_load['baixa'] = fuzz.trimf(self.cpu_load_range, [0, 0, 30])
        self.cpu_load['media'] = fuzz.trimf(self.cpu_load_range, [20, 45, 70])
        self.cpu_load['alta'] = fuzz.trimf(self.cpu_load_range, [60, 100, 100])

    def _define_fan_speed_membership(self):
        """Define as funções de pertinência para a velocidade da ventoinha"""
        self.fan_speed['baixa'] = fuzz.trimf(self.fan_speed_range, [0, 0, 25])
        self.fan_speed['media'] = fuzz.trimf(self.fan_speed_range, [15, 30, 50])
        self.fan_speed['alta'] = fuzz.trimf(self.fan_speed_range, [40, 60, 75])
        self.fan_speed['muito_alta'] = fuzz.trimf(self.fan_speed_range, [70, 100, 100])

    def _define_rules(self):
        """Define as regras fuzzy do sistema baseado na temperatura CPU e carga de processamento"""
        rule1 = ctrl.Rule(self.cpu_temp['baixa'] & self.cpu_load['baixa'], self.fan_speed['baixa'])
        rule2 = ctrl.Rule(self.cpu_temp['baixa'] & self.cpu_load['media'], self.fan_speed['media'])
        rule3 = ctrl.Rule(self.cpu_temp['baixa'] & self.cpu_load['alta'], self.fan_speed['alta'])
        rule4 = ctrl.Rule(self.cpu_temp['media'] & self.cpu_load['baixa'], self.fan_speed['baixa'])
        rule5 = ctrl.Rule(self.cpu_temp['media'] & self.cpu_load['media'], self.fan_speed['media'])
        rule6 = ctrl.Rule(self.cpu_temp['media'] & self.cpu_load['alta'], self.fan_speed['alta'])
        rule7 = ctrl.Rule(self.cpu_temp['alta'] & self.cpu_load['baixa'], self.fan_speed['alta'])
        rule8 = ctrl.Rule(self.cpu_temp['alta'] & self.cpu_load['media'], self.fan_speed['muito_alta'])
        rule9 = ctrl.Rule(self.cpu_temp['alta'] & self.cpu_load['alta'], self.fan_speed['muito_alta'])

        self.rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]

    def _create_control_system(self):
        """Cria o sistema de controle fuzzy"""
        self.fan_ctrl = ctrl.ControlSystem(self.rules)
        self.fan_sim = ctrl.ControlSystemSimulation(self.fan_ctrl)

    def get_fan_speed(self, cpu_temp, cpu_load):
        """
        Calcula a velocidade da ventoinha baseada na temperatura da CPU e carga de processamento

        Args:
            cpu_temp (float): Temperatura da CPU em graus Celsius (30-100)
            cpu_load (float): Carga de processamento em porcentagem (0-100)

        Returns:
            float: Velocidade da ventoinha em porcentagem (0-100)
        """
        cpu_temp = max(30, min(100, cpu_temp))
        cpu_load = max(0, min(100, cpu_load))

        self.fan_sim.input['cpu_temp'] = cpu_temp
        self.fan_sim.input['cpu_load'] = cpu_load
        self.fan_sim.compute()

        return self.fan_sim.output['fan_speed']

    def get_membership_values(self, cpu_temp, cpu_load):
        """
        Retorna os valores de pertinência para a temperatura CPU e carga de processamento

        Args:
            cpu_temp (float): Temperatura da CPU em graus Celsius
            cpu_load (float): Carga de processamento em porcentagem

        Returns:
            dict: Valores de pertinência para cada conjunto fuzzy das entradas
        """
        cpu_temp = max(30, min(100, cpu_temp))
        cpu_load = max(0, min(100, cpu_load))

        return {
            'cpu_temp_baixa': fuzz.interp_membership(self.cpu_temp_range, self.cpu_temp['baixa'].mf, cpu_temp),
            'cpu_temp_media': fuzz.interp_membership(self.cpu_temp_range, self.cpu_temp['media'].mf, cpu_temp),
            'cpu_temp_alta': fuzz.interp_membership(self.cpu_temp_range, self.cpu_temp['alta'].mf, cpu_temp),
            'cpu_load_baixa': fuzz.interp_membership(self.cpu_load_range, self.cpu_load['baixa'].mf, cpu_load),
            'cpu_load_media': fuzz.interp_membership(self.cpu_load_range, self.cpu_load['media'].mf, cpu_load),
            'cpu_load_alta': fuzz.interp_membership(self.cpu_load_range, self.cpu_load['alta'].mf, cpu_load)
        }


fan_controller = FanController()


def control_fan_speed(cpu_temp, cpu_load):
    """
    Função de conveniência para controlar velocidade da ventoinha

    Args:
        cpu_temp (float): Temperatura da CPU em graus Celsius (30-100)
        cpu_load (float): Carga de processamento em porcentagem (0-100)

    Returns:
        float: Velocidade da ventoinha em porcentagem (0-100)
    """
    return fan_controller.get_fan_speed(cpu_temp, cpu_load)


if __name__ == "__main__":
    print("Sistema de Controle de Velocidade da Ventoinha Fuzzy")
    print("=" * 60)
    print("Testando diferentes combinações de temperatura CPU e carga")
    print("-" * 60)

    test_scenarios = [
        (35, 10),
        (45, 30),
        (65, 70),
        (80, 90),
        (55, 50),
    ]

    for cpu_temp, cpu_load in test_scenarios:
        fan_speed = control_fan_speed(cpu_temp, cpu_load)
        membership = fan_controller.get_membership_values(cpu_temp, cpu_load)
        print(f"CPU: {cpu_temp}°C | Carga: {cpu_load}% | Velocidade: {fan_speed:.1f}%")
        print(f"  Temp - Baixa: {membership['cpu_temp_baixa']:.2f}, Média: {membership['cpu_temp_media']:.2f}, Alta: {membership['cpu_temp_alta']:.2f}")
        print(f"  Carga - Baixa: {membership['cpu_load_baixa']:.2f}, Média: {membership['cpu_load_media']:.2f}, Alta: {membership['cpu_load_alta']:.2f}")
        print()
