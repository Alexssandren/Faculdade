// Sistema de Controle de Velocidade da Ventoinha Fuzzy - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const cpuTempInput = document.getElementById('cpu-temperature');
    const cpuLoadInput = document.getElementById('cpu-load');
    const calculateBtn = document.getElementById('calculate-btn');
    const fanSpeedResult = document.getElementById('fan-speed-result');

    // Elementos de pertinência da temperatura CPU
    const cpuTempBaixaValue = document.getElementById('cpu-temp-baixa-value');
    const cpuTempMediaValue = document.getElementById('cpu-temp-media-value');
    const cpuTempAltaValue = document.getElementById('cpu-temp-alta-value');
    const cpuTempBaixaBar = document.getElementById('cpu-temp-baixa-bar');
    const cpuTempMediaBar = document.getElementById('cpu-temp-media-bar');
    const cpuTempAltaBar = document.getElementById('cpu-temp-alta-bar');

    // Elementos de pertinência da carga CPU
    const cpuLoadBaixaValue = document.getElementById('cpu-load-baixa-value');
    const cpuLoadMediaValue = document.getElementById('cpu-load-media-value');
    const cpuLoadAltaValue = document.getElementById('cpu-load-alta-value');
    const cpuLoadBaixaBar = document.getElementById('cpu-load-baixa-bar');
    const cpuLoadMediaBar = document.getElementById('cpu-load-media-bar');
    const cpuLoadAltaBar = document.getElementById('cpu-load-alta-bar');

    const showPlotBtn = document.getElementById('show-plot-btn');
    const plotContainer = document.getElementById('plot-container');
    const plotImage = document.getElementById('plot-image');

    // Calcular velocidade quando os campos perdem o foco (blur) e têm valores
    cpuTempInput.addEventListener('blur', function() {
        if (this.value !== '' && cpuLoadInput.value !== '' && isValidInput()) {
            calculateFanSpeed();
        }
    });

    cpuLoadInput.addEventListener('blur', function() {
        if (this.value !== '' && cpuTempInput.value !== '' && isValidInput()) {
            calculateFanSpeed();
        }
    });

    // Botão de calcular
    calculateBtn.addEventListener('click', function() {
        calculateFanSpeed();
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

    // Função para verificar se os inputs são válidos
    function isValidInput() {
        const cpuTemp = parseFloat(cpuTempInput.value);
        const cpuLoad = parseFloat(cpuLoadInput.value);

        return !isNaN(cpuTemp) && cpuTemp >= 30 && cpuTemp <= 100 &&
               !isNaN(cpuLoad) && cpuLoad >= 0 && cpuLoad <= 100;
    }

    // Função para calcular velocidade da ventoinha
    function calculateFanSpeed() {
        const cpuTemp = parseFloat(cpuTempInput.value);
        const cpuLoad = parseFloat(cpuLoadInput.value);

        // Validação com alertas (só quando chamado explicitamente)
        if (isNaN(cpuTemp) || cpuTemp < 30 || cpuTemp > 100) {
            alert('Por favor, insira uma temperatura da CPU válida entre 30°C e 100°C');
            return;
        }

        if (isNaN(cpuLoad) || cpuLoad < 0 || cpuLoad > 100) {
            alert('Por favor, insira uma carga de processamento válida entre 0% e 100%');
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
                cpu_temperature: cpuTemp,
                cpu_load: cpuLoad
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
            alert('Erro ao calcular velocidade da ventoinha');
        })
        .finally(() => {
            // Restaurar botão
            calculateBtn.textContent = 'Calcular Velocidade';
            calculateBtn.disabled = false;
        });
    }

    // Função para atualizar resultados na interface
    function updateResults(data) {
        // Atualizar velocidade da ventoinha
        fanSpeedResult.textContent = data.fan_speed + '%';

        // Atualizar valores de pertinência da temperatura CPU
        cpuTempBaixaValue.textContent = data.membership.cpu_temp_baixa;
        cpuTempMediaValue.textContent = data.membership.cpu_temp_media;
        cpuTempAltaValue.textContent = data.membership.cpu_temp_alta;

        // Atualizar barras de progresso da temperatura CPU
        cpuTempBaixaBar.style.width = (data.membership.cpu_temp_baixa * 100) + '%';
        cpuTempMediaBar.style.width = (data.membership.cpu_temp_media * 100) + '%';
        cpuTempAltaBar.style.width = (data.membership.cpu_temp_alta * 100) + '%';

        // Atualizar valores de pertinência da carga CPU
        cpuLoadBaixaValue.textContent = data.membership.cpu_load_baixa;
        cpuLoadMediaValue.textContent = data.membership.cpu_load_media;
        cpuLoadAltaValue.textContent = data.membership.cpu_load_alta;

        // Atualizar barras de progresso da carga CPU
        cpuLoadBaixaBar.style.width = (data.membership.cpu_load_baixa * 100) + '%';
        cpuLoadMediaBar.style.width = (data.membership.cpu_load_media * 100) + '%';
        cpuLoadAltaBar.style.width = (data.membership.cpu_load_alta * 100) + '%';
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

    // Calcular velocidade inicial (55°C CPU, 50% carga) - sem validação para valores padrão
    setTimeout(() => {
        if (cpuTempInput.value !== '' && cpuLoadInput.value !== '') {
            calculateFanSpeedSilently();
        }
    }, 500);

    // Função para calcular sem mostrar alertas (para valores padrão)
    function calculateFanSpeedSilently() {
        const cpuTemp = parseFloat(cpuTempInput.value);
        const cpuLoad = parseFloat(cpuLoadInput.value);

        // Só calcula se os valores são válidos
        if (!isNaN(cpuTemp) && cpuTemp >= 30 && cpuTemp <= 100 &&
            !isNaN(cpuLoad) && cpuLoad >= 0 && cpuLoad <= 100) {

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
                    cpu_temperature: cpuTemp,
                    cpu_load: cpuLoad
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualizar resultados
                    updateResults(data);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
            })
            .finally(() => {
                // Restaurar botão
                calculateBtn.textContent = 'Calcular Velocidade';
                calculateBtn.disabled = false;
            });
        }
    }

    // Adicionar evento para tecla Enter nos inputs
    cpuTempInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculateFanSpeed();
        }
    });

    cpuLoadInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculateFanSpeed();
        }
    });
});
