// Sistema de Controle de Temperatura Fuzzy - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const currentTempInput = document.getElementById('current-temperature');
    const desiredTempInput = document.getElementById('desired-temperature');
    const calculateBtn = document.getElementById('calculate-btn');
    const errorResult = document.getElementById('error-result');
    const powerResult = document.getElementById('power-result');
    const muitoFrioValue = document.getElementById('muito-frio-value');
    const frioValue = document.getElementById('frio-value');
    const idealValue = document.getElementById('ideal-value');
    const quenteValue = document.getElementById('quente-value');
    const muitoQuenteValue = document.getElementById('muito-quente-value');
    const muitoFrioBar = document.getElementById('muito-frio-bar');
    const frioBar = document.getElementById('frio-bar');
    const idealBar = document.getElementById('ideal-bar');
    const quenteBar = document.getElementById('quente-bar');
    const muitoQuenteBar = document.getElementById('muito-quente-bar');
    const showPlotBtn = document.getElementById('show-plot-btn');
    const plotContainer = document.getElementById('plot-container');
    const plotImage = document.getElementById('plot-image');

    // Calcular potência automaticamente quando qualquer temperatura muda
    currentTempInput.addEventListener('input', function() {
        if (this.value !== '' && desiredTempInput.value !== '') {
            calculatePower();
        }
    });

    desiredTempInput.addEventListener('input', function() {
        if (this.value !== '' && currentTempInput.value !== '') {
            calculatePower();
        }
    });

    // Botão de calcular
    calculateBtn.addEventListener('click', function() {
        calculatePower();
    });

    // Botão para mostrar gráficos
    showPlotBtn.addEventListener('click', function() {
        if (plotContainer.classList.contains('hidden')) {
            showPlot();
        } else {
            plotContainer.classList.add('hidden');
            this.textContent = 'Mostrar Gráficos';
        }
    });

    // Função para calcular potência
    function calculatePower() {
        const currentTemp = parseFloat(currentTempInput.value);
        const desiredTemp = parseFloat(desiredTempInput.value);

        if (isNaN(currentTemp) || currentTemp < 0 || currentTemp > 40) {
            alert('Por favor, insira uma temperatura ambiente válida entre 0°C e 40°C');
            return;
        }

        if (isNaN(desiredTemp) || desiredTemp < 15 || desiredTemp > 30) {
            alert('Por favor, insira uma temperatura desejada válida entre 15°C e 30°C');
            return;
        }

        // Mostrar loading
        calculateBtn.textContent = 'Calculando...';
        calculateBtn.disabled = true;

        // Fazer requisição AJAX
        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                current_temperature: currentTemp,
                desired_temperature: desiredTemp
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Atualizar resultados
                updateResults(data);
            } else {
                alert('Erro: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao calcular potência');
        })
        .finally(() => {
            // Restaurar botão
            calculateBtn.textContent = 'Calcular Potência';
            calculateBtn.disabled = false;
        });
    }

    // Função para atualizar resultados na interface
    function updateResults(data) {
        // Atualizar erro e potência
        errorResult.textContent = data.error + ' °C';
        powerResult.textContent = data.power + '%';

        // Atualizar valores de pertinência
        muitoFrioValue.textContent = data.membership.muito_frio;
        frioValue.textContent = data.membership.frio;
        idealValue.textContent = data.membership.ideal;
        quenteValue.textContent = data.membership.quente;
        muitoQuenteValue.textContent = data.membership.muito_quente;

        // Atualizar barras de progresso
        muitoFrioBar.style.width = (data.membership.muito_frio * 100) + '%';
        frioBar.style.width = (data.membership.frio * 100) + '%';
        idealBar.style.width = (data.membership.ideal * 100) + '%';
        quenteBar.style.width = (data.membership.quente * 100) + '%';
        muitoQuenteBar.style.width = (data.membership.muito_quente * 100) + '%';
    }

    // Função para mostrar gráficos
    function showPlot() {
        showPlotBtn.textContent = 'Carregando...';
        showPlotBtn.disabled = true;

        fetch('/plot')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                plotImage.src = 'data:image/png;base64,' + data.image;
                plotContainer.classList.remove('hidden');
                showPlotBtn.textContent = 'Ocultar Gráficos';
            } else {
                alert('Erro ao carregar gráfico: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar gráfico');
        })
        .finally(() => {
            showPlotBtn.disabled = false;
        });
    }

    // Calcular potência inicial (25°C ambiente, 22°C desejada)
    setTimeout(() => {
        calculatePower();
    }, 500);

    // Adicionar evento para tecla Enter nos inputs
    currentTempInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculatePower();
        }
    });

    desiredTempInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculatePower();
        }
    });
});
