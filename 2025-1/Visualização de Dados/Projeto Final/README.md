# Projeto de Visualização de Dados

## Correlação entre IDH e Despesas Públicas Federais por Estado Brasileiro

**Dashboard interativo com IA integrada** para análise da correlação entre o **Índice de Desenvolvimento Humano (IDH)** e as **despesas públicas federais** por estado brasileiro, utilizando **dados 100% oficiais** de fontes governamentais (2019-2023).

---

## Como Executar

### Execução Rápida (Recomendado)
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar API do Gemini
# Edite o arquivo Chave.env e adicione sua GEMINI_API_KEY

# 3. Executar projeto completo
python main.py
```

**Este comando único:**
- Processa todos os dados automaticamente
- Gera análises e visualizações
- Inicia o dashboard moderno
- Habilita chat com IA

---

## Funcionalidades Principais

### Dashboard Moderno
- **Interface Gemini-Style**: Design limpo e moderno
- **Navegação Intuitiva**: Sidebar recolhível com abas organizadas
- **Visualizações Interativas**: 30+ gráficos e mapas dinâmicos
- **Filtros Inteligentes**: Por ano, região e categoria de despesa

### Chat com IA (Gemini)
- **Consultas em Português**: Perguntas naturais sobre os dados
- **Respostas Factuais**: Dados precisos e contextualizados
- **Análises Inteligentes**: Rankings, comparações e tendências
- **Contexto Preservado**: Conversas fluidas e sequenciais

### Análises Disponíveis
- **Correlações Detalhadas**: IDH vs Gastos por múltiplas dimensões
- **Mapas Coropléticos**: Representação geográfica temporal
- **Rankings Dinâmicos**: Estados com maiores/menores indicadores
- **Tendências Temporais**: Evolução 2019-2023

---

## Exemplos de Perguntas para a IA

### IDH e Rankings
- "Qual foi o maior IDH de 2023?"
- "Quais os 3 estados com menor IDH na região Norte?"
- "Como evoluiu o IDH de São Paulo entre 2019 e 2023?"

### Gastos Públicos
- "Qual estado gastou mais em saúde em 2023?"
- "Quanto o Brasil investiu em educação em 2022?"
- "Qual o menor gasto em infraestrutura da região Nordeste?"

### Correlações e Comparações
- "Há correlação entre gastos em saúde e IDH?"
- "Compare os investimentos do Sudeste vs Nordeste"
- "Estados com maior IDH gastam mais em educação?"

---

## Dados Utilizados

### Fontes Oficiais
- **IDH**: Atlas Brasil - PNUD (Programa das Nações Unidas)
- **Despesas**: Portal da Transparência - Governo Federal
- **Período**: 2019-2023 (5 anos)
- **Cobertura**: 27 estados + DF

### Resumo Financeiro (2019-2023)
- **Total Investido**: R$ 1,013+ trilhão
- **Saúde**: R$ 345,4+ bilhões (34,1%)
- **Educação**: R$ 264,4+ bilhões (26,1%)
- **Infraestrutura**: R$ 224,3+ bilhões (22,1%)
- **Assistência Social**: R$ 178,8+ bilhões (17,7%)

---

## Tecnologias

### Stack Principal
- **Interface**: `PySide6/Qt` - Dashboard moderno e responsivo
- **IA**: `Google Gemini` - Consultas em linguagem natural
- **Banco**: `SQLite` - Persistência local eficiente
- **Visualização**: `Matplotlib`, `Plotly`, `Seaborn`
- **Análise**: `pandas`, `numpy`, `scipy`, `scikit-learn`
- **Geoespacial**: `geopandas` - Mapas e dados geográficos

### Dependências Principais
```txt
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.6.0
seaborn>=0.12.0
plotly>=5.0.0
geopandas>=0.13.0
scikit-learn>=1.3.0
scipy>=1.10.0
google-generativeai
python-dotenv
PySide6>=6.7.0
requests>=2.28.0
openpyxl>=3.1.0
```

---

## Estrutura do Projeto

```
Projeto Final/
├── main.py                    # Script principal
├── Chave.env                  # API Key do Gemini
├── requirements.txt           # Dependências
│
├── data/                      # Dados do projeto
│   ├── raw/                   # Dados brutos oficiais
│   ├── processed/             # Dados processados
│   │   ├── dataset_unificado.csv # Dataset principal
│   │   └── projeto_visualizacao.db # Banco SQLite
│   └── geospatial/            # Dados geográficos
│
├── src/                       # Código fonte
│   ├── app/                   # Dashboard PySide6
│   │   ├── gemini_style_dashboard.py
│   │   └── widgets/           # Componentes UI
│   ├── llm/                   # Sistema IA
│   │   └── llm_handler.py     # Handler do Gemini
│   ├── pipeline/              # Processamento de dados
│   ├── visualization/         # Geração de gráficos
│   ├── database/              # Sistema de banco
│   ├── data_collection/       # Coleta de dados
│   └── utils/                 # Utilitários
│
└── results/                   # Resultados gerados
    ├── exploratory_analysis/  # Análises exploratórias
    ├── advanced_analysis/     # Análises avançadas
    └── visualizations/        # Visualizações HTML
```

---

## Configuração

### 1. API Key do Gemini
1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Crie uma API Key gratuita
3. Edite o arquivo `Chave.env`:
```env
GEMINI_API_KEY="sua_chave_aqui"
```

### 2. Instalação
```bash
# Clonar/baixar o projeto
cd "Projeto Final"

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

---

## Principais Descobertas

### Análises Realizadas
- **Correlações Identificadas**: Métodos Pearson e Spearman
- **Padrões Regionais**: Análise por macrorregião brasileira
- **Outliers Documentados**: Estados com padrões atípicos
- **Eficiência de Investimentos**: Retorno social por real investido
- **Tendências Temporais**: Evolução 2019-2023

### Perguntas de Pesquisa Respondidas
1. **Relação IDH vs Investimentos**: Correlações identificadas e quantificadas
2. **Saúde vs IDH-Longevidade**: Padrões regionais mapeados
3. **Investimentos vs Vulnerabilidade**: Análise de direcionamento
4. **Evolução Temporal**: Tendências de 5 anos analisadas

---

## Objetivos Alcançados

- **Dashboard Moderno**: Interface responsiva e intuitiva
- **IA Integrada**: Chat funcional com Gemini
- **Dados Oficiais**: 100% fontes governamentais
- **Análises Robustas**: Múltiplas metodologias estatísticas
- **Visualizações Interativas**: 30+ gráficos e mapas
- **Sistema Escalável**: Arquitetura modular

---

## Suporte

### Execução Manual por Módulos
```bash
# Apenas coleta de dados
python -m src.pipeline.fase1_collect_data

# Apenas análises
python -m src.pipeline.fase2_explore_data

# Apenas dashboard
python -m src.app.gemini_style_dashboard
```

### Requisitos
- Python 3.8+
- Conexão com internet (para coleta de dados)
- API Key do Google Gemini
- ~2GB espaço em disco

---

**Projeto Completo de Visualização de Dados com IA**

Análise completa da correlação entre IDH e investimentos públicos federais no Brasil (2019-2023) com dashboard moderno e chat inteligente.