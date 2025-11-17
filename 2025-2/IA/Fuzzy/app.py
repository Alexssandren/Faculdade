"""
Aplicação Web Flask para Sistema de Controle de Temperatura Fuzzy
"""

from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Usar backend não-interativo
import matplotlib.pyplot as plt
import io
import base64
from fuzzy_logic import temperature_controller


app = Flask(__name__)


@app.route('/')
def index():
    """Página principal da aplicação"""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Endpoint para calcular potência baseada nas temperaturas"""
    try:
        data = request.get_json()
        current_temp = float(data.get('current_temperature', 25))
        desired_temp = float(data.get('desired_temperature', 22))

        # Calcular erro e potência
        error = desired_temp - current_temp
        power = temperature_controller.get_power(current_temp, desired_temp)
        membership = temperature_controller.get_membership_values(current_temp, desired_temp)

        return jsonify({
            'success': True,
            'current_temperature': current_temp,
            'desired_temperature': desired_temp,
            'error': round(error, 1),
            'power': round(power, 1),
            'membership': {
                'muito_frio': round(membership['muito_frio'], 2),
                'frio': round(membership['frio'], 2),
                'ideal': round(membership['ideal'], 2),
                'quente': round(membership['quente'], 2),
                'muito_quente': round(membership['muito_quente'], 2)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/plot')
def plot():
    """Gera gráfico das funções de pertinência"""
    try:
        # Criar figura
        plt.figure(figsize=(12, 8))

        # Plotar funções de pertinência do erro
        plt.subplot(2, 1, 1)
        plt.plot(temperature_controller.error_range,
                temperature_controller.error['muito_frio'].mf, 'c-', label='Muito Frio', linewidth=2)
        plt.plot(temperature_controller.error_range,
                temperature_controller.error['frio'].mf, 'b-', label='Frio', linewidth=2)
        plt.plot(temperature_controller.error_range,
                temperature_controller.error['ideal'].mf, 'g-', label='Ideal', linewidth=2)
        plt.plot(temperature_controller.error_range,
                temperature_controller.error['quente'].mf, 'y-', label='Quente', linewidth=2)
        plt.plot(temperature_controller.error_range,
                temperature_controller.error['muito_quente'].mf, 'r-', label='Muito Quente', linewidth=2)
        plt.title('Funções de Pertinência - Erro (Temperatura Desejada - Atual)')
        plt.xlabel('Erro (°C)')
        plt.ylabel('Grau de Pertinência')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plotar funções de pertinência da potência
        plt.subplot(2, 1, 2)
        plt.plot(temperature_controller.power_range,
                temperature_controller.power['muito_baixa'].mf, 'c-', label='Muito Baixa', linewidth=2)
        plt.plot(temperature_controller.power_range,
                temperature_controller.power['baixa'].mf, 'b-', label='Baixa', linewidth=2)
        plt.plot(temperature_controller.power_range,
                temperature_controller.power['media'].mf, 'g-', label='Média', linewidth=2)
        plt.plot(temperature_controller.power_range,
                temperature_controller.power['alta'].mf, 'y-', label='Alta', linewidth=2)
        plt.plot(temperature_controller.power_range,
                temperature_controller.power['muito_alta'].mf, 'r-', label='Muito Alta', linewidth=2)
        plt.title('Funções de Pertinência - Potência do Ar-Condicionado')
        plt.xlabel('Potência (%)')
        plt.ylabel('Grau de Pertinência')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({
            'success': True,
            'image': image_base64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    print("Iniciando Sistema de Controle de Temperatura Fuzzy...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
