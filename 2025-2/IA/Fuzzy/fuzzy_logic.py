"""
Sistema de Controle de Temperatura usando Lógica Fuzzy
Controla a potência do ar-condicionado baseada na diferença entre temperatura ambiente e desejada
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class TemperatureController:
    """
    Controlador Fuzzy para sistema de ar-condicionado
    Baseado na diferença entre temperatura ambiente e desejada, determina a potência ideal
    """

    def __init__(self):
        # Definir universos de discurso
        self.error_range = np.arange(-20, 21, 1)  # Diferença de -20°C a +20°C
        self.power_range = np.arange(0, 101, 1)   # 0% a 100% de potência

        # Criar variáveis fuzzy
        self.error = ctrl.Antecedent(self.error_range, 'error')  # Erro = Temp_desejada - Temp_atual
        self.power = ctrl.Consequent(self.power_range, 'power')

        # Definir funções de pertinência para erro
        self._define_error_membership()
        # Definir funções de pertinência para potência
        self._define_power_membership()
        # Definir regras fuzzy
        self._define_rules()
        # Criar sistema de controle
        self._create_control_system()

    def _define_error_membership(self):
        """Define as funções de pertinência para o erro (temperatura desejada - atual)"""
        # Erro negativo grande: ambiente muito fria (-20 a -12°C)
        self.error['muito_frio'] = fuzz.trimf(self.error_range, [-20, -20, -12])
        # Erro negativo médio: ambiente fria (-16 a -4°C)
        self.error['frio'] = fuzz.trimf(self.error_range, [-16, -10, -4])
        # Erro pequeno: temperatura próxima da desejada (-6 a +6°C)
        self.error['ideal'] = fuzz.trimf(self.error_range, [-6, 0, 6])
        # Erro positivo médio: ambiente quente (+4 a +16°C)
        self.error['quente'] = fuzz.trimf(self.error_range, [4, 10, 16])
        # Erro positivo grande: ambiente muito quente (+12 a +20°C)
        self.error['muito_quente'] = fuzz.trimf(self.error_range, [12, 20, 20])

    def _define_power_membership(self):
        """Define as funções de pertinência para a potência"""
        # Potência muito baixa: triangular de 0% a 20% (quando está muito frio)
        self.power['muito_baixa'] = fuzz.trimf(self.power_range, [0, 0, 20])
        # Potência baixa: triangular de 10% a 40%
        self.power['baixa'] = fuzz.trimf(self.power_range, [10, 20, 40])
        # Potência média: triangular de 30% a 70%
        self.power['media'] = fuzz.trimf(self.power_range, [30, 50, 70])
        # Potência alta: triangular de 60% a 90%
        self.power['alta'] = fuzz.trimf(self.power_range, [60, 80, 90])
        # Potência muito alta: triangular de 80% a 100%
        self.power['muito_alta'] = fuzz.trimf(self.power_range, [80, 100, 100])

    def _define_rules(self):
        """Define as regras fuzzy do sistema baseado no erro"""
        # Se erro indica muito frio (ambiente << desejada) → potência muito baixa (pouco aquecimento necessário)
        rule1 = ctrl.Rule(self.error['muito_frio'], self.power['muito_baixa'])
        # Se erro indica frio (ambiente < desejada) → potência baixa
        rule2 = ctrl.Rule(self.error['frio'], self.power['baixa'])
        # Se erro é muito pequeno (temperatura praticamente ideal) → potência muito baixa (manutenção mínima)
        rule3 = ctrl.Rule(self.error['ideal'], self.power['muito_baixa'])
        # Se erro indica quente (ambiente > desejada) → potência alta
        rule4 = ctrl.Rule(self.error['quente'], self.power['alta'])
        # Se erro indica muito quente (ambiente >> desejada) → potência muito alta
        rule5 = ctrl.Rule(self.error['muito_quente'], self.power['muito_alta'])

        self.rules = [rule1, rule2, rule3, rule4, rule5]

    def _create_control_system(self):
        """Cria o sistema de controle fuzzy"""
        self.power_ctrl = ctrl.ControlSystem(self.rules)
        self.power_sim = ctrl.ControlSystemSimulation(self.power_ctrl)

    def get_power(self, current_temp, desired_temp):
        """
        Calcula a potência recomendada baseada na diferença entre temperaturas

        Args:
            current_temp (float): Temperatura ambiente atual em graus Celsius
            desired_temp (float): Temperatura desejada em graus Celsius

        Returns:
            float: Potência recomendada em porcentagem (0-100)
        """
        # Calcular erro: temperatura desejada - temperatura atual
        error = desired_temp - current_temp

        # Limitar erro ao range válido (-20 a +20)
        error = max(-20, min(20, error))

        # Criar nova simulação para evitar problemas de estado
        power_sim = ctrl.ControlSystemSimulation(self.power_ctrl)
        power_sim.input['error'] = error
        power_sim.compute()

        return power_sim.output['power']

    def get_membership_values(self, current_temp, desired_temp):
        """
        Retorna os valores de pertinência para o erro calculado

        Args:
            current_temp (float): Temperatura ambiente atual
            desired_temp (float): Temperatura desejada

        Returns:
            dict: Valores de pertinência para cada conjunto fuzzy do erro
        """
        error = desired_temp - current_temp
        error = max(-20, min(20, error))

        return {
            'muito_frio': fuzz.interp_membership(self.error_range, self.error['muito_frio'].mf, error),
            'frio': fuzz.interp_membership(self.error_range, self.error['frio'].mf, error),
            'ideal': fuzz.interp_membership(self.error_range, self.error['ideal'].mf, error),
            'quente': fuzz.interp_membership(self.error_range, self.error['quente'].mf, error),
            'muito_quente': fuzz.interp_membership(self.error_range, self.error['muito_quente'].mf, error)
        }


# Instância global do controlador para uso fácil
temperature_controller = TemperatureController()


def control_temperature(current_temp, desired_temp):
    """
    Função de conveniência para controlar temperatura

    Args:
        current_temp (float): Temperatura ambiente atual em graus Celsius
        desired_temp (float): Temperatura desejada em graus Celsius

    Returns:
        float: Potência recomendada em porcentagem
    """
    return temperature_controller.get_power(current_temp, desired_temp)


if __name__ == "__main__":
    # Teste básico do sistema
    print("Sistema de Controle de Temperatura Fuzzy")
    print("=" * 50)
    print("Testando com temperatura desejada = 22°C")
    print("-" * 50)

    # Temperatura desejada fixa para teste
    desired_temp = 22

    # Testar diferentes temperaturas ambientes
    current_temps = [15, 18, 20, 22, 25, 28, 32]

    for current_temp in current_temps:
        error = desired_temp - current_temp
        power = control_temperature(current_temp, desired_temp)
        membership = temperature_controller.get_membership_values(current_temp, desired_temp)
        print(f"Atual: {current_temp}°C | Desejada: {desired_temp}°C | Erro: {error:+.0f}°C | Potência: {power:.1f}%")
        print(f"  Pertinências - Muito Frio: {membership['muito_frio']:.2f}, Frio: {membership['frio']:.2f}, Ideal: {membership['ideal']:.2f}, Quente: {membership['quente']:.2f}, Muito Quente: {membership['muito_quente']:.2f}")
        print()
