# Sistema Multiagente de Gestão de Carteira de Investimentos

Sistema multiagente reativo desenvolvido em Python para gerenciar e manter a diversificação de uma carteira de investimentos automaticamente.

## Descrição

Este sistema resolve o problema de **dificuldade de manutenção e acompanhamento da diversificação da carteira de investimentos** através de três agentes reativos que trabalham em conjunto:

1. **WalletManager**: Gerencia saldo, liquidez e limites operacionais
2. **MarketAnalyst**: Monitora mercado e identifica oportunidades
3. **PortfolioManager**: Ajusta a diversificação da carteira automaticamente

## Arquitetura

### Agentes

#### 1. Agente WalletManager
**Responsabilidade**: Gerenciar saldo, liquidez e limites da carteira

**Perception**:
- Observa saldo total disponível em conta
- Observa entradas e saídas de capital (compras, vendas, rendimentos)
- Recebe relatórios dos agentes PortfolioManager e MarketAnalyst
- Monitora níveis de risco e liquidez mínima

**Capability**:
- Análise de liquidez da carteira
- Estabelecimento de limites de compra/venda
- Previsão de impacto financeiro de decisões
- Ajuste de orçamento alocado para cada classe de ativo

**Operations**:
- `calcularSaldoAtual()`
- `definirLimiteOperacional()`
- `atualizarFluxoCaixa()`
- `gerarRelatorioFinanceiro()`
- `enviarAutorizacaoOperacao()`

**Protocol**:
- Recebe relatórios do PortfolioManager e MarketAnalyst
- Envia autorizações de compra/venda para PortfolioManager
- Envia alertas de liquidez baixa

#### 2. Agente MarketAnalyst
**Responsabilidade**: Monitorar mercado e identificar oportunidades e riscos

**Perception**:
- Observa preços de ativos em tempo real
- Observa indicadores de mercado (Selic, IPCA, índices, câmbio)
- Monitora notícias e eventos macroeconômicos
- Recebe dados históricos para análise de tendência

**Capability**:
- Análise de tendências de preços
- Detecção de oportunidades de compra ou venda
- Previsão de cenários de risco
- Recomendação de ajustes de portfólio

**Operations**:
- `coletarDadosMercado()`
- `analisarTendencias()`
- `gerarSinaisDeCompraVenda()`
- `enviarAlertasDeRisco()`
- `produzirRelatorioDeMercado()`

**Protocol**:
- Envia recomendações ao PortfolioManager
- Envia alertas de risco ao WalletManager
- Recebe solicitações de análise do PortfolioManager

#### 3. Agente PortfolioManager
**Responsabilidade**: Decidir composição e diversificação da carteira

**Perception**:
- Observa ativos disponíveis no mercado e preços atuais
- Recebe limites de investimento do WalletManager
- Recebe análises de tendência do MarketAnalyst
- Monitora distribuição atual da carteira

**Capability**:
- Análise de diversificação da carteira
- Decisão sobre compra e venda de ativos
- Balanceamento de riscos entre setores e tipos de ativos
- Reação a alertas de mercado

**Operations**:
- `avaliarDistribuicaoCarteira()`
- `decidirCompraVenda()`
- `executarOperacao()`
- `atualizarPortfolio()`
- `notificarOperacoes()`

**Protocol**:
- Recebe autorização financeira do WalletManager antes de operar
- Solicita análises de tendência ao MarketAnalyst
- Envia relatórios de desempenho ao WalletManager

### Sistema de Comunicação

Os agentes se comunicam através de um **MessageBus** assíncrono que permite:
- Mensagens diretas entre agentes específicos
- Broadcast de mensagens para todos os agentes
- Fila de mensagens para processamento assíncrono

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório** (ou navegue até o diretório do projeto)

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure o ambiente**:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env conforme necessário (opcional)
```

4. **Popule o banco de dados**:
```bash
python scripts/populate_db.py
```
   > **Nota**: Este script **zera todas as tabelas** e cria uma carteira inicial com R$ 50.000,00 em saldo disponível. Execute sempre que quiser resetar o sistema.

5. **Execute o sistema**:
```bash
python main.py
```

6. **Acesse a interface web**:
Abra seu navegador em `http://localhost:8000`

### Inicialização Automática

Ao iniciar o sistema:
- A carteira começa com **R$ 50.000,00** em saldo disponível
- O **PortfolioManager** detecta automaticamente quando a carteira está vazia
- O sistema **inicia automaticamente a distribuição** do capital entre os tipos de ativos conforme a configuração de diversificação
- A distribuição inicial é acelerada (até 5 operações por ciclo) para investir rapidamente o capital disponível

## Estrutura do Projeto

```
SMA/
├── agents/                  # Módulo de agentes
│   ├── base_agent.py       # Classe base para agentes
│   ├── wallet_manager.py   # Agente WalletManager
│   ├── market_analyst.py   # Agente MarketAnalyst
│   └── portfolio_manager.py # Agente PortfolioManager
├── models/                 # Modelos de dados
│   ├── database.py         # Configuração do banco
│   ├── portfolio.py        # Modelos de carteira
│   └── market.py           # Modelos de mercado
├── services/               # Serviços auxiliares
│   ├── message_bus.py      # Sistema de mensageria
│   ├── market_simulator.py # Simulador de mercado
│   └── logger.py           # Sistema de logging
├── api/                    # API REST
│   ├── main.py             # Aplicação FastAPI
│   └── routes/              # Rotas da API
│       ├── portfolio.py    # Rotas de portfólio
│       ├── market.py       # Rotas de mercado
│       └── alerts.py       # Rotas de alertas
├── web/                    # Frontend
│   ├── static/             # Arquivos estáticos
│   │   ├── style.css       # Estilos
│   │   └── app.js          # JavaScript
│   └── templates/          # Templates HTML
│       └── index.html      # Página principal
├── scripts/                # Scripts utilitários
│   └── populate_db.py     # Popular banco de dados
├── logs/                   # Arquivos de log
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── main.py                # Ponto de entrada
└── README.md              # Este arquivo
```

## Configuração

As configurações podem ser ajustadas no arquivo `.env`:

```env
# Banco de dados
DATABASE_URL=sqlite:///./portfolio.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sma_system.log

# Sistema
UPDATE_INTERVAL=5                    # segundos entre atualizações
MIN_LIQUIDITY_THRESHOLD=1000.0      # liquidez mínima em reais
DEFAULT_CASH=50000.0                 # saldo inicial em reais
```

## Funcionalidades

### Gestão Automática de Carteira

- **Distribuição automática inicial**: O sistema detecta carteira vazia e inicia investimentos automaticamente
- **Rebalanceamento contínuo**: Mantém a diversificação conforme configuração alvo
- **Cálculo dinâmico do valor total**: `Valor Total = Valor das Posições (preço atual) + Saldo Disponível`
- **Controle de liquidez**: Monitora saldo mínimo e alerta quando necessário
- **Cooldown entre operações**: Evita operações excessivas no mesmo ativo (30 segundos)

### Interface Web

A interface web fornece:

- **Dashboard em tempo real** com:
  - Resumo da carteira (saldo disponível, valor total)
  - Distribuição da carteira por tipo de ativo
  - Lista de posições atuais
  - Alertas do sistema
  - Histórico de transações recentes

- **Atualização automática** a cada 5 segundos
- **WebSocket** para atualizações em tempo real
- **Visualização gráfica** da distribuição da carteira

### API REST

Endpoints disponíveis:

- `GET /api/status` - Status geral do sistema
- `GET /api/portfolio/carteira` - Informações da carteira
- `GET /api/portfolio/distribuicao` - Distribuição atual
- `GET /api/portfolio/posicoes` - Posições da carteira
- `GET /api/portfolio/transacoes` - Histórico de transações
- `GET /api/market/ativos` - Ativos disponíveis
- `GET /api/market/indicadores` - Indicadores de mercado
- `GET /api/alerts/` - Alertas do sistema

## Fluxo de Funcionamento

### Inicialização do Sistema

1. **População do banco**: O script `populate_db.py` zera todas as tabelas e cria:
   - Carteira inicial com R$ 50.000,00 em saldo disponível
   - 12 ativos de exemplo (ações, renda fixa, criptomoedas, fundos)
   - Indicadores de mercado simulados
   - Configuração de diversificação padrão

2. **Inicialização dos agentes**: Ao iniciar o sistema:
   - Todos os agentes são criados e iniciados
   - **PortfolioManager** detecta carteira vazia com saldo disponível
   - Sistema inicia **distribuição automática** do capital

### Ciclo Operacional Contínuo

1. **MarketSimulator** atualiza preços dos ativos periodicamente (a cada 5 segundos)
2. **MarketAnalyst** observa mudanças e analisa tendências
3. **PortfolioManager** avalia distribuição atual vs. alvo de diversificação
4. Se houver desequilíbrio, **PortfolioManager** solicita autorização ao **WalletManager**
5. **WalletManager** verifica liquidez e autoriza ou nega operações
6. **PortfolioManager** executa operações autorizadas
7. **Valor total da carteira** é atualizado: `valor_posições + saldo_disponível`
8. Todos os agentes atualizam seus estados e geram relatórios
9. Interface web exibe informações atualizadas em tempo real

### Distribuição Automática Inicial

Quando a carteira está vazia (sem posições) mas há saldo disponível:
- O sistema detecta automaticamente essa condição
- Executa até **5 operações por ciclo** para acelerar a distribuição inicial
- Distribui o capital conforme a configuração de diversificação:
  - **40%** em Ações
  - **30%** em Renda Fixa
  - **20%** em Criptomoedas
  - **10%** em Fundos de Investimento

## Logs

O sistema gera logs estruturados em:

- `logs/sma_system.log` - Log geral do sistema
- `logs/wallet_manager.log` - Logs do WalletManager
- `logs/market_analyst.log` - Logs do MarketAnalyst
- `logs/portfolio_manager.log` - Logs do PortfolioManager

## Dados Simulados

O sistema utiliza dados simulados para:

- **Ativos**: 12 ativos de exemplo:
  - **Ações**: PETR4, VALE3, ITUB4, BBDC4, ABEV3
  - **Renda Fixa**: CDB001, LCI001, TESOURO
  - **Criptomoedas**: BTC, ETH
  - **Fundos**: FUND001, FUND002
- **Indicadores**: Selic, IPCA, IBOVESPA, Dólar
- **Variações de preço**: Simuladas com diferentes níveis de volatilidade por tipo de ativo:
  - Ações: ~2% de volatilidade média
  - Renda Fixa: ~0.1% de volatilidade média
  - Criptomoedas: ~5% de volatilidade média
  - Fundos: ~1% de volatilidade média

### Configuração de Diversificação Padrão

O sistema vem configurado com a seguinte distribuição alvo:

| Tipo de Ativo | Porcentagem Alvo | Tolerância |
|---------------|------------------|------------|
| Ações | 40% | ±5% |
| Renda Fixa | 30% | ±5% |
| Criptomoedas | 20% | ±5% |
| Fundos | 10% | ±5% |

> **Nota**: A tolerância permite que o sistema não rebalanceie constantemente por pequenas variações. O rebalanceamento ocorre quando a diferença entre a distribuição atual e a alvo ultrapassa a tolerância.

## Tecnologias Utilizadas

- **Python 3.8+**
- **FastAPI** - Framework web assíncrono
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **WebSockets** - Comunicação em tempo real
- **JavaScript/HTML/CSS** - Interface web

## Referências

Este projeto foi desenvolvido como trabalho acadêmico sobre Sistemas Multiagente (SMA), seguindo os princípios de:

- Arquitetura de agentes reativos
- Comunicação entre agentes via mensageria
- Coordenação e cooperação de agentes
- Sistemas distribuídos assíncronos

## Autores

Desenvolvido como trabalho acadêmico da disciplina de Sistemas Multiagente.

## Licença

Este projeto é de uso acadêmico.

---

## Importante

- **Reset do banco**: Execute `python scripts/populate_db.py` sempre que quiser resetar o sistema. Este comando **zera todas as tabelas** e recria a carteira com R$ 50.000,00.
- **Dados simulados**: Este sistema utiliza dados simulados e é destinado exclusivamente para fins educacionais e de demonstração.
- **Valor total**: O valor total da carteira é calculado dinamicamente como a soma do valor atual de mercado das posições mais o saldo disponível. Isso reflete o valor real da carteira considerando variações de preço.
- **Distribuição automática**: O sistema inicia automaticamente a distribuição do capital quando detecta carteira vazia. Isso pode levar alguns ciclos para completar a distribuição inicial.

