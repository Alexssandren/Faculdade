// Configuração WebSocket
let ws = null;
let reconnectInterval = null;

// Estado da aplicação
const state = {
    carteira: null,
    distribuicao: [],
    posicoes: [],
    transacoes: [],
    alertas: []
};

// Conectar WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket conectado');
        updateStatus(true);
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
        console.error('Erro WebSocket:', error);
        updateStatus(false);
    };
    
    ws.onclose = () => {
        console.log('WebSocket desconectado');
        updateStatus(false);
        // Tentar reconectar após 3 segundos
        reconnectInterval = setInterval(() => {
            connectWebSocket();
        }, 3000);
    };
}

function updateStatus(connected) {
    const indicator = document.querySelector('.status-dot');
    const text = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        indicator.classList.remove('disconnected');
        text.textContent = 'Conectado';
    } else {
        indicator.classList.add('disconnected');
        indicator.classList.remove('connected');
        text.textContent = 'Desconectado';
    }
}

function handleWebSocketMessage(data) {
    // Processar mensagens do WebSocket
    console.log('Mensagem recebida:', data);
}

// Funções de API
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`/api${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Erro ao buscar ${endpoint}:`, error);
        return null;
    }
}

async function loadCarteira() {
    const data = await fetchAPI('/portfolio/carteira');
    if (data) {
        state.carteira = data;
        updateCarteiraUI();
    }
}

async function loadDistribuicao() {
    const data = await fetchAPI('/portfolio/distribuicao');
    if (data && data.distribuicao) {
        state.distribuicao = data.distribuicao;
        updateDistribuicaoUI();
    }
}

async function loadPosicoes() {
    const data = await fetchAPI('/portfolio/posicoes');
    if (data && data.posicoes) {
        state.posicoes = data.posicoes;
        updatePosicoesUI();
    }
}

async function loadTransacoes() {
    const data = await fetchAPI('/portfolio/transacoes?limit=10');
    if (data && data.transacoes) {
        state.transacoes = data.transacoes;
        updateTransacoesUI();
    }
}

async function loadAlertas() {
    const data = await fetchAPI('/alerts/?limit=10&resolvido=false');
    if (data && data.alertas) {
        state.alertas = data.alertas;
        updateAlertasUI();
    }
}

// Funções de atualização da UI
function updateCarteiraUI() {
    if (!state.carteira) return;
    
    document.getElementById('saldoDisponivel').textContent = 
        formatCurrency(state.carteira.saldo_disponivel);
    document.getElementById('valorTotal').textContent = 
        formatCurrency(state.carteira.valor_total);
}

function updateDistribuicaoUI() {
    const container = document.getElementById('distribuicaoList');
    if (!state.distribuicao || state.distribuicao.length === 0) {
        container.innerHTML = '<div class="loading">Nenhuma posição encontrada</div>';
        return;
    }
    
    container.innerHTML = state.distribuicao.map(item => `
        <div class="distribuicao-item">
            <span class="tipo">${item.tipo_ativo}</span>
            <span class="porcentagem">${item.porcentagem.toFixed(2)}%</span>
            <span class="valor">${formatCurrency(item.valor)}</span>
        </div>
    `).join('');
    
    // Atualizar gráfico (simplificado)
    drawDistribuicaoChart();
}

function drawDistribuicaoChart() {
    const canvas = document.getElementById('distribuicaoCanvas');
    if (!canvas || !state.distribuicao || state.distribuicao.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = 200;
    
    ctx.clearRect(0, 0, width, height);
    
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
    let startAngle = 0;
    const total = state.distribuicao.reduce((sum, item) => sum + item.porcentagem, 0);
    
    state.distribuicao.forEach((item, index) => {
        const sliceAngle = (item.porcentagem / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(width / 2, height / 2);
        ctx.arc(width / 2, height / 2, Math.min(width, height) / 2 - 10, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[index % colors.length];
        ctx.fill();
        
        startAngle += sliceAngle;
    });
}

function updatePosicoesUI() {
    const tbody = document.getElementById('posicoesBody');
    if (!state.posicoes || state.posicoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Nenhuma posição encontrada</td></tr>';
        return;
    }
    
    tbody.innerHTML = state.posicoes.map(pos => {
        const variacaoClass = pos.variacao_percentual >= 0 ? 'variacao-positiva' : 'variacao-negativa';
        const variacaoSymbol = pos.variacao_percentual >= 0 ? '+' : '';
        
        return `
            <tr>
                <td><strong>${pos.ativo_codigo}</strong><br><small>${pos.ativo_nome}</small></td>
                <td>${pos.quantidade.toFixed(4)}</td>
                <td>${formatCurrency(pos.preco_atual)}</td>
                <td>${formatCurrency(pos.valor_total)}</td>
                <td class="${variacaoClass}">${variacaoSymbol}${pos.variacao_percentual.toFixed(2)}%</td>
            </tr>
        `;
    }).join('');
}

function updateTransacoesUI() {
    const tbody = document.getElementById('transacoesBody');
    if (!state.transacoes || state.transacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Nenhuma transação encontrada</td></tr>';
        return;
    }
    
    tbody.innerHTML = state.transacoes.map(trans => {
        const tipoClass = trans.tipo === 'Compra' ? 'variacao-negativa' : 'variacao-positiva';
        const date = new Date(trans.timestamp);
        
        return `
            <tr>
                <td>${date.toLocaleString('pt-BR')}</td>
                <td><strong>${trans.ativo_codigo}</strong><br><small>${trans.ativo_nome}</small></td>
                <td class="${tipoClass}">${trans.tipo}</td>
                <td>${trans.quantidade.toFixed(4)}</td>
                <td>${formatCurrency(trans.valor_total)}</td>
            </tr>
        `;
    }).join('');
}

function updateAlertasUI() {
    const container = document.getElementById('alertasList');
    if (!state.alertas || state.alertas.length === 0) {
        container.innerHTML = '<div class="loading">Nenhum alerta ativo</div>';
        return;
    }
    
    container.innerHTML = state.alertas.map(alerta => {
        const date = new Date(alerta.timestamp);
        
        return `
            <div class="alerta-item ${alerta.severidade}">
                <div class="alerta-header">
                    <span class="alerta-agente">${alerta.agente_origem}</span>
                    <span class="alerta-timestamp">${date.toLocaleString('pt-BR')}</span>
                </div>
                <div class="alerta-mensagem">${alerta.mensagem}</div>
            </div>
        `;
    }).join('');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Carregar dados iniciais
async function loadAllData() {
    await Promise.all([
        loadCarteira(),
        loadDistribuicao(),
        loadPosicoes(),
        loadTransacoes(),
        loadAlertas()
    ]);
}

// Atualizar dados periodicamente
function startAutoRefresh() {
    setInterval(() => {
        loadAllData();
    }, 5000); // Atualiza a cada 5 segundos
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    loadAllData();
    startAutoRefresh();
});

