"""
Aplicação Web Flask para Sistema de Controle de Velocidade de Ventoinha Fuzzy
"""

from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Usar backend não-interativo
import matplotlib.pyplot as plt
import io
import base64
from fuzzy_logic import fan_controller


app = Flask(__name__)


@app.route('/')
def index():
    """Página principal da aplicação"""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Endpoint para calcular velocidade da ventoinha baseada na temperatura CPU e carga"""
    try:
        data = request.get_json()
        cpu_temp = float(data.get('cpu_temperature', 55))
        cpu_load = float(data.get('cpu_load', 50))

        # Calcular velocidade da ventoinha
        fan_speed = fan_controller.get_fan_speed(cpu_temp, cpu_load)
        membership = fan_controller.get_membership_values(cpu_temp, cpu_load)

        return jsonify({
            'success': True,
            'cpu_temperature': cpu_temp,
            'cpu_load': cpu_load,
            'fan_speed': round(fan_speed, 1),
            'membership': {
                'cpu_temp_baixa': round(membership['cpu_temp_baixa'], 2),
                'cpu_temp_media': round(membership['cpu_temp_media'], 2),
                'cpu_temp_alta': round(membership['cpu_temp_alta'], 2),
                'cpu_load_baixa': round(membership['cpu_load_baixa'], 2),
                'cpu_load_media': round(membership['cpu_load_media'], 2),
                'cpu_load_alta': round(membership['cpu_load_alta'], 2)
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
        # Criar figura com 3 subplots
        plt.figure(figsize=(15, 10))

        # Plotar funções de pertinência da temperatura CPU
        plt.subplot(3, 1, 1)
        plt.plot(fan_controller.cpu_temp_range,
                fan_controller.cpu_temp['baixa'].mf, 'b-', label='Baixa', linewidth=2)
        plt.plot(fan_controller.cpu_temp_range,
                fan_controller.cpu_temp['media'].mf, 'g-', label='Média', linewidth=2)
        plt.plot(fan_controller.cpu_temp_range,
                fan_controller.cpu_temp['alta'].mf, 'r-', label='Alta', linewidth=2)
        plt.title('Funções de Pertinência - Temperatura da CPU')
        plt.xlabel('Temperatura (°C)')
        plt.ylabel('Grau de Pertinência')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plotar funções de pertinência da carga de processamento
        plt.subplot(3, 1, 2)
        plt.plot(fan_controller.cpu_load_range,
                fan_controller.cpu_load['baixa'].mf, 'b-', label='Baixa', linewidth=2)
        plt.plot(fan_controller.cpu_load_range,
                fan_controller.cpu_load['media'].mf, 'g-', label='Média', linewidth=2)
        plt.plot(fan_controller.cpu_load_range,
                fan_controller.cpu_load['alta'].mf, 'r-', label='Alta', linewidth=2)
        plt.title('Funções de Pertinência - Carga de Processamento')
        plt.xlabel('Carga (%)')
        plt.ylabel('Grau de Pertinência')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plotar funções de pertinência da velocidade da ventoinha
        plt.subplot(3, 1, 3)
        plt.plot(fan_controller.fan_speed_range,
                fan_controller.fan_speed['baixa'].mf, 'b-', label='Baixa', linewidth=2)
        plt.plot(fan_controller.fan_speed_range,
                fan_controller.fan_speed['media'].mf, 'g-', label='Média', linewidth=2)
        plt.plot(fan_controller.fan_speed_range,
                fan_controller.fan_speed['alta'].mf, 'y-', label='Alta', linewidth=2)
        plt.plot(fan_controller.fan_speed_range,
                fan_controller.fan_speed['muito_alta'].mf, 'r-', label='Muito Alta', linewidth=2)
        plt.title('Funções de Pertinência - Velocidade da Ventoinha')
        plt.xlabel('Velocidade (%)')
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
    print("Iniciando Sistema de Controle de Velocidade da Ventoinha Fuzzy...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
