# Sistema de Controle de Velocidade da Ventoinha Fuzzy - Apresentação

## Principais Componentes do Código

### 1. Classe FanController

**Localização**: `fuzzy_logic.py`, linhas 11-166

Esta é a classe principal que implementa o controlador Fuzzy para ventoinha:

```python
class FanController:
    """
    Controlador Fuzzy para sistema de ventoinha de computador
    Baseado na temperatura da CPU e carga de processamento, determina a velocidade ideal da ventoinha
    """
```

#### Função `__init__()` (linhas 17-33)

- Define os universos de discurso para temperatura CPU (30-100°C), carga processamento (0-100%) e velocidade ventoinha (0-100%)
- Cria as variáveis Fuzzy (duas Antecedentes e uma Consequente)
- Inicializa o sistema chamando os métodos de configuração

#### Função `_define_cpu_temp_membership()` (linhas 35-46)

Define as funções de pertinência para a temperatura da CPU:

```python
def _define_cpu_temp_membership(self):
    """Define as funções de pertinência para a temperatura da CPU"""
    # Três conjuntos Fuzzy: baixa, media, alta
    self.cpu_temp['baixa'] = fuzz.trimf(self.cpu_temp_range, [30, 30, 50])
    self.cpu_temp['media'] = fuzz.trimf(self.cpu_temp_range, [40, 55, 70])
    self.cpu_temp['alta'] = fuzz.trimf(self.cpu_temp_range, [60, 100, 100])
```

#### Função `_define_cpu_load_membership()` (linhas 48-55)

Define as funções de pertinência para a carga de processamento:

```python
def _define_cpu_load_membership(self):
    """Define as funções de pertinência para a carga de processamento"""
    self.cpu_load['baixa'] = fuzz.trimf(self.cpu_load_range, [0, 0, 30])
    self.cpu_load['media'] = fuzz.trimf(self.cpu_load_range, [20, 45, 70])
    self.cpu_load['alta'] = fuzz.trimf(self.cpu_load_range, [60, 100, 100])
```

#### Função `_define_fan_speed_membership()` (linhas 57-66)

Define as funções de pertinência para a velocidade da ventoinha:

```python
def _define_fan_speed_membership(self):
    """Define as funções de pertinência para a velocidade da ventoinha"""
    self.fan_speed['baixa'] = fuzz.trimf(self.fan_speed_range, [0, 0, 25])
    self.fan_speed['media'] = fuzz.trimf(self.fan_speed_range, [15, 30, 50])
    self.fan_speed['alta'] = fuzz.trimf(self.fan_speed_range, [40, 60, 75])
    self.fan_speed['muito_alta'] = fuzz.trimf(self.fan_speed_range, [70, 100, 100])
```

#### Função `_define_rules()` (linhas 68-87)

Implementa as 9 regras de inferência Fuzzy baseadas em combinações de temperatura e carga:

```python
def _define_rules(self):
    """Define as regras fuzzy do sistema baseado na temperatura CPU e carga de processamento"""
    # Regras baseadas na combinação de temperatura CPU e carga de processamento
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
```

Cada regra conecta uma combinação específica de temperatura e carga a uma velocidade de ventoinha apropriada.

#### Função `get_fan_speed()` (linhas 92-111)

Método principal que calcula a velocidade da ventoinha:

```python
def get_fan_speed(self, cpu_temp, cpu_load):
    # Limitar valores aos ranges válidos
    cpu_temp = max(30, min(100, cpu_temp))
    cpu_load = max(0, min(100, cpu_load))

    # Usar a simulação existente e resetar entradas
    self.fan_sim.input['cpu_temp'] = cpu_temp
    self.fan_sim.input['cpu_load'] = cpu_load
    self.fan_sim.compute()

    return self.fan_sim.output['fan_speed']
```

Este método:

1. Limita os valores de entrada aos ranges válidos
2. Define as duas entradas do sistema Fuzzy (temperatura e carga)
3. Executa a inferência Fuzzy com as 9 regras
4. Retorna a velocidade defuzzificada da ventoinha

#### Função `get_membership_values()` (linhas 113-127)

Calcula os graus de pertinência para debug e visualização:

```python
def get_membership_values(self, cpu_temp, cpu_load):
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
```

### 2. Função `control_fan_speed()` (linhas 134-142)

Função de conveniência para uso direto:

```python
def control_fan_speed(cpu_temp, cpu_load):
    return fan_controller.get_fan_speed(cpu_temp, cpu_load)
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

1. **Computador ocioso** (CPU 35°C, carga 10%): Velocidade ≈ 9.0% (ventoinha lenta)
2. **Trabalho office** (CPU 55°C, carga 50%): Velocidade ≈ 31.7% (ventoinha moderada)
3. **Gaming intenso** (CPU 80°C, carga 90%): Velocidade ≈ 88.3% (ventoinha máxima)
