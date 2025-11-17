# Sistema de Controle de Temperatura Fuzzy - Apresentacao

## Principais Componentes do Codigo

### 1. Classe TemperatureController

**Localizacao**: `fuzzy_logic.py`, linhas 11-166

Esta e a classe principal que implementa o controlador Fuzzy:

```python
class TemperatureController:
    """
    Controlador Fuzzy para sistema de ar-condicionado
    Baseado na diferenca entre temperatura ambiente e desejada, determina a potencia ideal
    """
```

#### Funcao `__init__()` (linhas 17-33)

- Define os universos de discurso para erro (-20°C a +20°C) e potencia (0% a 100%)
- Cria as variaveis Fuzzy (Antecedente e Consequente)
- Inicializa o sistema chamando os metodos de configuracao

#### Funcao `_define_error_membership()` (linhas 35-46)

Define as funcoes de pertinencia para a variavel de entrada (erro):

```python
def _define_error_membership(self):
    """Define as funcoes de pertinencia para o erro (temperatura desejada - atual)"""
    # Cinco conjuntos Fuzzy: muito_frio, frio, ideal, quente, muito_quente
    self.error['muito_frio'] = fuzz.trimf(self.error_range, [-20, -20, -12])
    self.error['frio'] = fuzz.trimf(self.error_range, [-16, -10, -4])
    self.error['ideal'] = fuzz.trimf(self.error_range, [-6, 0, 6])
    self.error['quente'] = fuzz.trimf(self.error_range, [4, 10, 16])
    self.error['muito_quente'] = fuzz.trimf(self.error_range, [12, 20, 20])
```

Cada conjunto utiliza uma funcao triangular (trimf) que define:

- Ponto esquerdo: inicio da pertinencia
- Pico: ponto de maxima pertinencia (pertinencia = 1.0)
- Ponto direito: fim da pertinencia

#### Funcao `_define_power_membership()` (linhas 48-59)

Define as funcoes de pertinencia para a variavel de saida (potencia):

```python
def _define_power_membership(self):
    """Define as funcoes de pertinencia para a potencia"""
    self.power['muito_baixa'] = fuzz.trimf(self.power_range, [0, 0, 20])
    self.power['baixa'] = fuzz.trimf(self.power_range, [10, 20, 40])
    self.power['media'] = fuzz.trimf(self.power_range, [30, 50, 70])
    self.power['alta'] = fuzz.trimf(self.power_range, [60, 80, 90])
    self.power['muito_alta'] = fuzz.trimf(self.power_range, [80, 100, 100])
```

#### Funcao `_define_rules()` (linhas 61-74)

Implementa as regras de inferencia Fuzzy:

```python
def _define_rules(self):
    """Define as regras fuzzy do sistema baseado no erro"""
    rule1 = ctrl.Rule(self.error['muito_frio'], self.power['muito_baixa'])
    rule2 = ctrl.Rule(self.error['frio'], self.power['baixa'])
    rule3 = ctrl.Rule(self.error['ideal'], self.power['muito_baixa'])
    rule4 = ctrl.Rule(self.error['quente'], self.power['alta'])
    rule5 = ctrl.Rule(self.error['muito_quente'], self.power['muito_alta'])
    self.rules = [rule1, rule2, rule3, rule4, rule5]
```

Cada regra conecta um estado do erro a uma potencia recomendada.

#### Funcao `get_power()` (linhas 81-103)

Metodo principal que calcula a potencia recomendada:

```python
def get_power(self, current_temp, desired_temp):
    error = desired_temp - current_temp
    error = max(-20, min(20, error))  # Limitacao do range

    power_sim = ctrl.ControlSystemSimulation(self.power_ctrl)
    power_sim.input['error'] = error
    power_sim.compute()

    return power_sim.output['power']
```

Este metodo:

1. Calcula o erro (diferenca entre desejada e atual)
2. Limita o erro ao range definido
3. Cria uma simulacao Fuzzy
4. Define a entrada (erro)
5. Executa a inferencia Fuzzy
6. Retorna a potencia defuzzificada

#### Funcao `get_membership_values()` (linhas 105-124)

Calcula os graus de pertinencia para debug e visualizacao:

```python
def get_membership_values(self, current_temp, desired_temp):
    error = desired_temp - current_temp
    error = max(-20, min(20, error))

    return {
        'muito_frio': fuzz.interp_membership(self.error_range, self.error['muito_frio'].mf, error),
        'frio': fuzz.interp_membership(self.error_range, self.error['frio'].mf, error),
        'ideal': fuzz.interp_membership(self.error_range, self.error['ideal'].mf, error),
        'quente': fuzz.interp_membership(self.error_range, self.error['quente'].mf, error),
        'muito_quente': fuzz.interp_membership(self.error_range, self.error['muito_quente'].mf, error)
    }
```

### 2. Funcao `control_temperature()` (linhas 131-142)

Funcao de conveniencia para uso direto:

```python
def control_temperature(current_temp, desired_temp):
    return temperature_controller.get_power(current_temp, desired_temp)
```

### 3. Aplicacao Web Flask (`app.py`)

#### Endpoint `/calculate` (linhas 23-54)

Processa requisicoes POST para calculo de potencia:

```python
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    current_temp = float(data.get('current_temperature', 25))
    desired_temp = float(data.get('desired_temperature', 22))

    error = desired_temp - current_temp
    power = temperature_controller.get_power(current_temp, desired_temp)
    membership = temperature_controller.get_membership_values(current_temp, desired_temp)

    return jsonify({
        'success': True,
        'current_temperature': current_temp,
        'desired_temperature': desired_temp,
        'error': round(error, 1),
        'power': round(power, 1),
        'membership': membership
    })
```

## Resultados e Validacao

### Testes Unitarios

O projeto inclui 11 testes unitarios que validam:

- Funcoes de pertinencia
- Calculos de potencia
- Sistema de controle Fuzzy
- Regras de inferencia
- Valores extremos
- Consistencia dos resultados

### Exemplos de Funcionamento

1. **Temperatura ideal** (erro = 0°C): Potencia ≈ 6.7% (manutencao minima)
2. **Ambiente frio** (erro = +7°C): Potencia ≈ 76% (aquecimento intenso)
3. **Ambiente quente** (erro = -10°C): Potencia ≈ 17% (resfriamento suave)
