# 🎯 Projeto Final - Visualização de Dados

## 📊 Correlação entre IDH e Despesas Públicas Federais por Estado Brasileiro

Este projeto analisa a correlação entre o **Índice de Desenvolvimento Humano (IDH)** e as **despesas e investimentos governamentais federais** por estado brasileiro em diversas áreas como educação, saúde, assistência social e infraestrutura, utilizando **dados 100% REAIS e OFICIAIS** de fontes governamentais.

## ❓ Perguntas de Pesquisa

### 🔍 Questões Centrais a serem Respondidas:
1. **🔗 Há relação entre IDH e investimentos públicos federais?**
2. **🏥 Estados que recebem mais investimentos em saúde possuem IDH-Longevidade mais alto?**
3. **📍 O investimento público acompanha as regiões de maior vulnerabilidade social?**
4. **📈 O IDH tem melhorado proporcionalmente aos investimentos públicos federais nas últimas décadas?**

## 📋 Regras e Requisitos do Projeto

### ✅ Critérios Obrigatórios Atendidos:
- ✅ **Correlação de dados**: IDH por estado × Despesas governamentais por área
- ✅ **100% dados REAIS e OFICIAIS**: Fontes governamentais verificadas
- ✅ **Mais de 10.000 linhas**: 10.936+ registros totais
- ✅ **Período de 5 anos**: 2019-2023
- ✅ **Correlação temporal**: Mesmos anos e estados para análise
- ✅ **Interface gráfica interativa**: Dashboard moderno com PySide6/Qt
- ✅ **Integração com LLM**: Consultas em linguagem natural com OpenAI
- ✅ **Banco de dados**: Persistência em SQLite

## 🏛️ Datasets Oficiais Utilizados

### 📊 1. Índice de Desenvolvimento Humano (IDH)
- **Fonte**: Atlas Brasil - PNUD (Programa das Nações Unidas para o Desenvolvimento)
- **URL**: http://www.atlasbrasil.org.br/
- **Registros**: 136 (27 estados + DF × 5 anos)
- **Período**: 2019-2023
- **Componentes**: IDH Geral, IDH-Educação, IDH-Longevidade, IDH-Renda, População

### 💰 2. Execução da Despesa Pública Federal
- **Fonte**: Portal da Transparência - Governo Federal
- **URL**: https://portaldatransparencia.gov.br/
- **Registros**: 10.800+ (27 estados × 4 categorias × 5 anos × 20 subcategorias)
- **Período**: 2019-2023
- **Categorias**: Saúde, Educação, Assistência Social, Infraestrutura
- **Valor Total**: R$ 1,013+ trilhão

## 🚀 Progresso do Projeto - Estado Atual

### ✅ FASE 1: Coleta e Preparação dos Dados - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### Implementações Realizadas:
- ✅ **Coleta Automatizada**: Módulos especializados em `src/data_collection/`
  - `idh_oficial_collector.py` - Coleta dados do Atlas Brasil
  - `despesas_oficiais_collector.py` - Coleta dados do Portal da Transparência
- ✅ **Validação de Dados**: Sistema de validação em `src/utils/data_validator.py`
- ✅ **Limpeza e Estruturação**: Pipeline automatizado em `src/pipeline/fase1b_clean_data.py`

### ✅ FASE 2: Análise Exploratória e Correlações - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### Análises Implementadas:
- ✅ **Análise Descritiva**: Estatísticas completas dos datasets
- ✅ **Análise de Correlações**: Pearson e Spearman por categoria, ano, estado e região
- ✅ **Dataset Unificado**: `data/processed/dataset_unificado.csv` como base consolidada
- ✅ **Visualizações Exploratórias**: 15+ gráficos e mapas interativos
- ✅ **Análises Avançadas**: Clustering, análises de eficiência e tendências temporais

### ✅ FASE 2.5: Persistência de Dados em Banco de Dados - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### Sistema de Banco de Dados:
- ✅ **SQLite Database**: `data/processed/projeto_visualizacao.db`
- ✅ **Setup Automatizado**: Módulo `src/database/setup_database.py`
- ✅ **Esquema Dinâmico**: Criação automática baseada no dataset unificado
- ✅ **Prevenção de Duplicatas**: Sistema robusto de validação

### ✅ FASE 3: Visualizações Estáticas - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### Visualizações Geradas:
- ✅ **Mapas Coropléticos**: IDH e gastos por estado (2019-2023)
- ✅ **Gráficos de Bolhas**: Correlações interativas IDH vs Gastos
- ✅ **Mapas de Calor**: Correlações temporais e regionais
- ✅ **30+ Visualizações HTML**: Todas interativas usando Plotly
- ✅ **Geração Automatizada**: Sistema de batch processing

### ✅ FASE 4: Dashboard Interativo Moderno - **CONCLUÍDA** 
**Status**: ✅ Finalizada em 100%
**Tecnologia**: `PySide6/Qt (Gemini Style Dashboard)`

#### 🎨 Interface Moderna Implementada:
- ✅ **Design Gemini-Inspired**: Interface limpa e moderna
- ✅ **Sidebar Recolhível**: Navegação intuitiva e responsiva
- ✅ **Sistema de Abas**: Organização clara do conteúdo
- ✅ **Visualizações Integradas**: Matplotlib embedado com Qt
- ✅ **Chat LLM Interface**: Interface de conversação fluida
- ✅ **Filtros Dinâmicos**: Controles interativos por ano, região, categoria

#### 🛠️ Arquitetura Modular:
- ✅ **Componentes Reutilizáveis**: Widgets especializados
  - `CollapsibleSidebar` - Navegação lateral
  - `GraphsContainer` - Container para visualizações
- ✅ **Separação de Responsabilidades**: UI, lógica e dados separados
- ✅ **Sistema de Eventos**: Comunicação entre componentes

### ✅ FASE 4.5: Integração de LLM - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%
**Tecnologia**: `OpenAI (gpt-4o-mini)`

#### 🤖 Sistema LLM Avançado:
- ✅ **Consultas Factuais**: Busca inteligente por IDH e gastos específicos
- ✅ **Herança de Contexto**: Continuidade em conversas
- ✅ **Consultas Top N**: "os 3 maiores IDHs", "5 menores gastos em saúde"
- ✅ **Filtros Inteligentes**: Aplicação automática de filtros baseada em perguntas
- ✅ **Cenários Múltiplos**: 15+ tipos de consulta factual implementados

#### 🧠 Funcionalidades Inteligentes:
- ✅ **Extração de Intenções**: Identificação automática de UF, ano, categoria
- ✅ **Validação Contextual**: Verificação de dados antes da resposta
- ✅ **Respostas Estruturadas**: Formatação clara e informativa
- ✅ **Tratamento de Erros**: Respostas adequadas para dados não encontrados

### ✅ FASE 5: Pipeline Integrado - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### 🔄 Sistema de Orquestração:
- ✅ **Execução Inteligente**: Verificação automática de artefatos existentes
- ✅ **Pipeline Completo**: `main.py` executa todas as fases automaticamente
- ✅ **Validação de Dependências**: Verificação de pré-requisitos entre fases
- ✅ **Logs Detalhados**: Acompanhamento completo do progresso
- ✅ **Inicialização Automática**: Dashboard inicia após conclusão do pipeline

## 🛠️ Tecnologias Principais

### 🔧 Stack Tecnológico Implementado:
- **🖥️ Interface**: `PySide6/Qt` - Dashboard moderno e responsivo ✅
- **🤖 IA**: `OpenAI (gpt-4o-mini)` - Consultas em linguagem natural ✅
- **🗄️ Banco de Dados**: `SQLite` - Persistência local eficiente ✅
- **📊 Visualização**: `Matplotlib`, `Plotly`, `Seaborn` ✅
- **🔄 Processamento**: `pandas`, `numpy`, `scipy` ✅
- **🗺️ Geoespacial**: `geopandas`, `shapely` ✅
- **🌐 Coleta**: `requests`, `BeautifulSoup` ✅

### 📦 Dependências Completas:
```bash
pip install -r requirements.txt
```

**Bibliotecas principais:**
- `PySide6>=6.0.0` - Interface gráfica moderna ✅
- `openai>=1.0.0` - Integração LLM ✅
- `pandas>=2.0.0` - Manipulação de dados ✅
- `matplotlib>=3.7.0` - Visualizações ✅
- `plotly>=5.0.0` - Gráficos interativos ✅
- `geopandas>=0.10.0` - Dados geoespaciais ✅
- `sqlite3` - Banco de dados (built-in) ✅

## 🚀 Como Executar

### 🎯 Execução Completa (Recomendado)
```bash
python main.py
```
**Este comando único:**
- ✅ Executa todo o pipeline automaticamente
- ✅ Verifica artefatos existentes (evita reprocessamento)
- ✅ Inicia o dashboard moderno automaticamente
- ✅ Valida dependências entre fases

### 🔧 Execução Manual por Fases

#### Fase 1: Coleta de Dados
```bash
python -m src.pipeline.fase1_collect_data
```

#### Fase 1b: Limpeza de Dados
```bash
python -m src.pipeline.fase1b_clean_data
```

#### Fase 2: Análise Exploratória
```bash
python -m src.pipeline.fase2_explore_data
```

#### Fase 2b: Análises Avançadas
```bash
python -m src.pipeline.fase2b_advanced_analysis
```

#### Configuração do Banco de Dados
```bash
python -m src.database.setup_database
```

#### Dashboard Apenas
```bash
python -m src.app.gemini_style_dashboard
```

## 📁 Estrutura Técnica do Projeto

```
Projeto Final 1/
├── 🚀 main.py                          # Script principal - orquestração completa
├── 🔑 Chave.env                        # Chave API OpenAI (não commitado)
├── 📋 requirements.txt                 # Dependências Python
├── 📖 README.md                        # Esta documentação
│
├── 📊 data/                            # Dados do projeto
│   ├── raw/                           # Dados brutos originais
│   ├── processed/                     # Dados processados e limpos  
│   │   ├── dataset_unificado.csv      # Dataset consolidado principal
│   │   └── projeto_visualizacao.db    # Banco de dados SQLite
│   └── geospatial/                    # Shapefiles e dados geográficos
│
├── 🎯 src/                            # Código fonte modularizado
│   ├── app/                           # Dashboard PySide6/Qt
│   │   ├── gemini_style_dashboard.py  # Dashboard principal
│   │   ├── assets/                    # Recursos gráficos
│   │   └── widgets/                   # Componentes UI reutilizáveis
│   │       ├── collapsible_sidebar.py # Sidebar recolhível
│   │       └── graphs_container.py    # Container de gráficos
│   │
│   ├── 🤖 llm/                        # Sistema LLM
│   │   └── llm_handler.py             # Handler principal do LLM
│   │
│   ├── 🔄 pipeline/                   # Pipeline de processamento
│   │   ├── fase1_collect_data.py      # Coleta de dados
│   │   ├── fase1b_clean_data.py       # Limpeza de dados
│   │   ├── fase2_explore_data.py      # Análise exploratória
│   │   └── fase2b_advanced_analysis.py # Análises avançadas
│   │
│   ├── 📈 visualization/              # Sistema de visualizações
│   │   └── plot_generator.py          # Gerador de gráficos
│   │
│   ├── 🗄️ database/                   # Sistema de banco de dados
│   │   └── setup_database.py          # Configuração SQLite
│   │
│   ├── 🌐 data_collection/            # Coletores especializados
│   │   ├── idh_oficial_collector.py   # Coletor IDH
│   │   └── despesas_oficiais_collector.py # Coletor despesas
│   │
│   └── 🛠️ utils/                      # Utilitários
│       └── data_validator.py          # Validação de dados
│
└── 📊 results/                        # Resultados gerados
    ├── exploratory_analysis/          # Análises exploratórias
    ├── advanced_analysis/             # Análises avançadas
    └── visualizations/                # Visualizações HTML
```

## 📊 Resultados Obtidos

### 💰 Resumo Financeiro (2019-2023):
- **Total Investido**: R$ 1,013+ trilhão
- **Saúde**: R$ 345,4+ bilhões (34,1%)
- **Educação**: R$ 264,4+ bilhões (26,1%)
- **Infraestrutura**: R$ 224,3+ bilhões (22,1%)
- **Assistência Social**: R$ 178,8+ bilhões (17,7%)

### 📈 Análises Geradas:
- **📊 30+ Visualizações Interativas**: Mapas, gráficos de bolha, heatmaps
- **📋 15+ Análises Estatísticas**: Correlações detalhadas por múltiplas dimensões
- **🗺️ Mapas Coropléticos**: Representação geográfica temporal
- **🤖 Sistema LLM**: 15+ cenários de consulta factual implementados
- **📈 Análises de Tendência**: Evolução temporal por estado e região

### 🔗 Principais Descobertas:
- **Correlações Identificadas**: Métodos Pearson e Spearman
- **Outliers Documentados**: Estados com padrões atípicos
- **Padrões Regionais**: Análise por macrorregião brasileira
- **Eficiência de Investimentos**: Análise de retorno social por real investido

## 🎨 Interface do Dashboard

### 🖥️ Características da Interface:
- **🎨 Design Moderno**: Inspirado no Gemini (Google AI)
- **📱 Layout Responsivo**: Adaptável a diferentes resoluções
- **🎛️ Controles Intuitivos**: Filtros e navegação simplificada
- **💬 Chat Inteligente**: Interação em linguagem natural
- **📊 Visualizações Integradas**: Gráficos embedados e interativos

### 🔧 Funcionalidades Implementadas:
- **🗂️ Navegação por Abas**: Visão geral, correlações, mapas, chat
- **📊 Filtros Dinâmicos**: Por ano, região, categoria de despesa
- **🤖 Consultas LLM**: Perguntas em português sobre os dados
- **📈 Gráficos Interativos**: Zoom, pan, hover para detalhes
- **🎯 Análises Contextuais**: Insights automáticos baseados em seleções

## 🔍 Funcionalidades do LLM

### 🤖 Tipos de Consulta Suportados:
- **📊 Consultas Específicas**: "Qual o IDH de São Paulo em 2023?"
- **🏆 Rankings**: "Os 5 estados com maior IDH"
- **💰 Análises de Gastos**: "Menores investimentos em saúde por região"
- **🔗 Correlações**: "Relação entre IDH e gastos em educação"
- **📈 Comparações**: "Evolução do IDH no Nordeste vs Sudeste"

### 🧠 Inteligência Contextual:
- **🔄 Herança de Contexto**: Perguntas de acompanhamento
- **📍 Reconhecimento Geográfico**: Estados, regiões, siglas
- **📅 Contexto Temporal**: Anos específicos ou períodos
- **💡 Sugestões Inteligentes**: Análises relacionadas automáticas

## 🛡️ Garantias de Qualidade

- ✅ **Dados 100% Oficiais**: Fontes governamentais verificadas
- ✅ **Validação Automática**: Sistema robusto de verificação
- ✅ **Documentação Completa**: Código bem documentado
- ✅ **Rastreabilidade Total**: Todas as fontes identificadas
- ✅ **Análises Robustas**: Múltiplas metodologias estatísticas
- ✅ **Arquitetura Modular**: Código escalável e manutenível
- ✅ **Testes Integrados**: Validação em múltiplos cenários

## 🔬 Metodologia Científica

### 📊 Processo de Análise:
1. **Coleta**: APIs oficiais e web scraping estruturado
2. **Validação**: Verificação de integridade e consistência
3. **Processamento**: Limpeza, padronização e agregação
4. **Análise**: Correlações Pearson/Spearman multidimensionais
5. **Visualização**: Três tipos específicos de gráficos relacionais
6. **Interpretação**: LLM para análises em linguagem natural

### 🎯 Critérios de Validação:
- **Consistência Temporal**: Mesmos períodos para todos os dados
- **Consistência Geográfica**: Padronização de nomenclaturas
- **Integridade Estatística**: Tratamento adequado de outliers
- **Reprodutibilidade**: Pipeline completamente automatizado

## 🏆 Status Final do Projeto

**📊 Progresso Total**: ✅ **100% CONCLUÍDO**

### ✅ Todas as Fases Implementadas:
- ✅ **Fase 1**: Coleta de dados oficiais (100%)
- ✅ **Fase 2**: Análise exploratória e correlações (100%)
- ✅ **Fase 2.5**: Banco de dados SQLite (100%)
- ✅ **Fase 3**: Visualizações estáticas (100%)
- ✅ **Fase 4**: Dashboard moderno PySide6/Qt (100%)
- ✅ **Fase 4.5**: Integração LLM avançada (100%)
- ✅ **Fase 5**: Pipeline integrado e orquestração (100%)

### 🎯 Objetivos Alcançados:
- ✅ **Correlação IDH vs Despesas**: Análise completa implementada
- ✅ **Interface Moderna**: Dashboard responsivo e intuitivo
- ✅ **IA Integrada**: Consultas em linguagem natural funcionais
- ✅ **Dados Oficiais**: 100% de fontes governamentais verificadas
- ✅ **Análises Robustas**: Múltiplas metodologias estatísticas
- ✅ **Visualizações Interativas**: 30+ gráficos e mapas
- ✅ **Sistema Escalável**: Arquitetura modular e bem documentada

### 🚀 Execução:
```bash
# Comando único para execução completa
python main.py
```

---

**🎉 Projeto de Visualização de Dados Completo e Funcional!**

**📈 Análise completa da correlação entre IDH e investimentos públicos federais no Brasil (2019-2023) com interface moderna, IA integrada e dados 100% oficiais.**