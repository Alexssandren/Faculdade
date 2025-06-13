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
- ✅ **Período de 5 anos**: Dados disponíveis no dataset.
- ✅ **Correlação temporal**: Mesmos anos e estados para análise
- ✅ **Interface gráfica interativa**: Dashboard com PySide6

## 🏛️ Datasets Oficiais Utilizados

### 📊 1. Índice de Desenvolvimento Humano (IDH)
- **Fonte**: Atlas Brasil - PNUD (Programa das Nações Unidas para o Desenvolvimento)
- **URL**: http://www.atlasbrasil.org.br/
- **Registros**: 136 (27 estados + DF × 5 anos)
- **Componentes**: IDH Geral, IDH-Educação, IDH-Longevidade, IDH-Renda, População

### 💰 2. Execução da Despesa Pública Federal
- **Fonte**: Portal da Transparência - Governo Federal
- **URL**: https://portaldatransparencia.gov.br/
- **Registros**: 10.800+ (27 estados × 4 categorias × 5 anos × 20 subcategorias)
- **Categorias**: Saúde, Educação, Assistência Social, Infraestrutura
- **Valor Total**: R$ 1,013+ trilhão

## 🚀 Progresso do Projeto - Plano de Ação Abrangente

### ✅ FASE 1: Coleta e Preparação dos Dados - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%
- **1.1 Coleta**: Dados de Despesas Públicas (Portal da Transparência) e IDH (Atlas Brasil) coletados.
- **1.2 Limpeza**: Dados limpos, padronizados e estruturados em um dataset unificado.

### ✅ FASE 2: Análise Exploratória e Persistência - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%
- **2.1 Análise Descritiva e Correlações**: Estatísticas básicas, outliers e correlações (Pearson, Spearman) foram calculados.
- **2.2 Persistência de Dados**: Implementada persistência em um banco de dados **SQLite** (`projeto_visualizacao.db`) para garantir performance e escalabilidade. O script `src/database/setup_database.py` cria e popula o banco a partir do dataset unificado.

### ✅ FASE 3: Desenvolvimento das Visualizações Avançadas - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### 🎯 Objetivos:
- Desenvolver os três tipos de gráficos relacionais interativos, utilizando dados do banco de dados SQLite, para **todos os anos disponíveis**.

#### ✅ Resultados Obtidos:
- Script `src/visualization/plot_generator.py` criado e funcional.
  - Carrega dados da tabela `analise_unificada` do `projeto_visualizacao.db`.
- Gera e salva as seguintes visualizações interativas (arquivos HTML) em `results/visualizations/` para **cada ano** no dataset:
    - **1. Mapa de Calor Relacional:** Correlações entre IDH e as quatro áreas de gasto.
    - **2. Gráficos de Bolhas Cruzados:** Animação anual mostrando IDH vs. Gasto Per Capita, com tamanho da bolha representando a população.
    - **3. Mapas Coropléticos Relacionais:** Série de mapas para IDH, Gasto por categoria, e a Relação IDH/Gasto.
- **Observação**: A geração é acionada pelo pipeline principal em `main.py`.

### ✅ FASE 4: Dashboard Interativo - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%
**Tecnologia**: `PySide6 (Qt for Python)`

#### 🎯 Objetivos:
- Implementar um dashboard interativo desktop, com uma interface moderna e inspirada no Gemini, que carrega e exibe as visualizações geradas.
- Permitir interação do usuário através de um chatbot integrado a um LLM.

#### ✅ Progresso Atual:
- **Interface Gráfica Funcional**: Dashboard desenvolvido com `PySide6`, apresentando uma UI limpa e responsiva.
- **Carregamento Dinâmico de Gráficos**: O dashboard lê os arquivos HTML do diretório `results/visualizations/` e os exibe em um componente `QWebEngineView`.
- **Seleção de Gráficos**: A interface permite que o usuário navegue e selecione facilmente qual gráfico deseja visualizar.
- **Integração com LLM**: O chatbot na interface está totalmente funcional, permitindo consultas em linguagem natural.

### ✅ FASE 4.5: Integração de LLM - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100% - Lógica de consulta factual, herança de contexto e busca Top N totalmente funcionais e integradas.
**Tecnologia**: `OpenAI (gpt-4o-mini)`

#### ✅ Resultados Obtidos:
- `LLMQueryHandler` (`src/llm/llm_handler.py`) implementado e integrado ao dashboard.
- **Busca Factual Robusta**: O sistema pode responder a perguntas diretas sobre os dados (ex: "Qual o IDH de SP em 2022?", "Quais os 3 estados com menor gasto em saúde em 2021?").
- **Herança de Contexto**: O chatbot mantém o contexto da conversa, permitindo perguntas de acompanhamento.
- **Lógica de Cenários**: O sistema prioriza respostas baseadas nos dados locais antes de consultar o LLM, garantindo precisão.

### ⏳ FASE 5: Análise Final e Insights - **PENDENTE**
**Status**: ⏳ Não iniciada
- **5.1 Resposta às Perguntas de Pesquisa**: Análise sistemática de cada pergunta proposta usando o dashboard e os dados.
- **5.2 Geração de Insights**: Documentação das conclusões e insights obtidos.

## 🛠️ Tecnologias Principais

### 🔧 Stack Tecnológico Implementado:
- **🔄 Coleta e Processamento**: `pandas`, `numpy` ✅
- **📈 Visualização**: `plotly`, `geopandas` (para gerar HTMLs interativos) ✅
- **🖥️ Dashboard**: `PySide6` ✅
- **🤖 LLM**: `openai` ✅
- **📊 Banco de Dados**: `SQLite` ✅
- **📊 Análise**: `scipy`, `statsmodels` ✅

### 📦 Dependências Completas:
```bash
pip install -r requirements.txt
```
**Bibliotecas principais instaladas:**
- `pandas`
- `numpy`
- `plotly`
- `geopandas`
- `PySide6`
- `openai`
- `python-dotenv`
- `scipy`

## 🚀 Como Executar

### 🚀 Execução Completa do Pipeline e do Dashboard
O projeto é orquestrado pelo `main.py`, que executa todas as fases necessárias do pipeline de dados antes de iniciar a aplicação.

```bash
python main.py
```
- **O que este comando faz?**
  1. **Verifica Fases Anteriores**: Checa se os artefatos de cada fase (coleta, limpeza, criação do BD, visualizações) já existem.
  2. **Executa Fases Pendentes**: Se um artefato não for encontrado, o script executa a fase correspondente do pipeline.
  3. **Inicia o Dashboard**: Após a conclusão bem-sucedida do pipeline, a aplicação do dashboard interativo é iniciada.

- **Para forçar a re-execução de todo o pipeline**, limpe os diretórios `data/processed/`, `data/raw/` e `results/`.

## 📁 Estrutura Técnica do Projeto

```
projeto_final/
├── main.py                         # 🚀 SCRIPT PRINCIPAL - Orquestra as fases e inicia o dashboard
├── Chave.env                       # 🔑 Chave da API OpenAI (NÃO COMMITAR)
├── requirements.txt                # 📦 Dependências
├── data/
│   ├── raw/                        # 📊 Dados brutos
│   ├── processed/                  # 📈 Dados processados (dataset_unificado.csv, projeto_visualizacao.db)
│   └── geospatial/                 # 🗺️ Dados geoespaciais (ex: .shp para mapas)
├── src/
│   ├── app/                        # 🖥️ Lógica do Dashboard PySide6
│   │   └── gemini_style_dashboard.py
│   ├── database/                   # 🛠️ Script de configuração do BD
│   │   └── setup_database.py
│   ├── llm/                        # 🤖 Lógica de integração com LLM
│   │   └── llm_handler.py
│   ├── pipeline/                   # 🔧 Scripts de orquestração das fases
│   │   ├── fase1_collect_data.py
│   │   └── ...
│   └── visualization/              # 📈 Scripts de geração de visualizações
│       └── plot_generator.py
└── results/
    ├── exploratory_analysis/       # Resultados da análise exploratória
    ├── advanced_analysis/          # Resultados das análises avançadas
    └── visualizations/             # 📈 Visualizações HTML interativas geradas
```

## 🎯 Próximos Passos Imediatos

### 📋 Prioridades:
1.  **📊 Concluir Fase 5**: Utilizar o dashboard funcional para realizar a análise final e responder sistematicamente às perguntas de pesquisa.
2.  **✍️ Documentar Insights**: Gerar um relatório ou uma seção final no README com as conclusões e os insights obtidos a partir dos dados.
3.  **💅 Refinamento (Opcional)**: Realizar pequenos ajustes de usabilidade ou estéticos no dashboard, se necessário.

---

**🎉 Projeto estruturado para responder perguntas específicas sobre IDH e investimentos públicos!**

**📊 Status de Desenvolvimento**: 
- ✅ **Fase 1**: Concluída (100%) - Coleta e preparação de dados
- ✅ **Fase 2**: Concluída (100%) - Análise e persistência em BD
- ✅ **Fase 3**: Concluída (100%) - Geração de visualizações interativas
- ✅ **Fase 4**: Concluída (100%) - Dashboard interativo com PySide6
- ✅ **Fase 4.5**: Concluída (100%) - Integração de LLM para consultas
- ⏳ **Fase 5**: Pendente (0%) - Análise final e resposta às perguntas de pesquisa

**🏆 Progresso Total**: ~95% concluído | **Dashboard Desktop (PySide6) e Pipeline de Dados totalmente funcionais.** | **LLM com lógica de busca factual, herança de intenção e Top N FUNCIONAL.** ✅