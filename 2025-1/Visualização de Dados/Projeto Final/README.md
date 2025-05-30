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
- ✅ **Interface gráfica interativa**: Dashboard com Streamlit

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

## 🚀 Progresso do Projeto - Plano de Ação Abrangente

### ✅ FASE 1: Coleta e Preparação dos Dados (2-3 dias) - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### 1.1 ✅ Coleta do Dataset de Despesas Públicas Federais
- Portal da Transparência (gov.br) acessado e dados extraídos
- Execução orçamentária por estado (2019-2023) coletada
- Categorias focadas: Saúde, Educação, Assistência Social, Infraestrutura

#### 1.2 ✅ Coleta do Dataset de IDH
- Atlas Brasil - PNUD acessado e dados extraídos
- IDH por estado para período 2019-2023 coletado
- Dados demográficos complementares incluídos

#### 1.3 ✅ Limpeza e Estruturação dos Dados
- Nomenclaturas de estados padronizadas
- Valores ausentes e inconsistências tratados
- Estrutura unificada de dados criada

### ✅ FASE 2: Análise Exploratória e Correlações (2-3 dias) - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### 2.1 ✅ Análise Descritiva
- Estatísticas básicas de ambos os datasets calculadas
- Outliers identificados e documentados
- Padrões regionais mapeados

#### 2.2 ✅ Análise de Correlações
- Correlações entre categorias de gastos e IDH calculadas (Pearson e Spearman)
- Categorias com maior correlação identificadas
- Análise temporal da evolução implementada
- **Arquivos gerados**: correlações por categoria, ano, estado e região

#### 2.3 ✅ Preparação para Visualizações
- Dados agregados por região criados
- Métricas derivadas calculadas (per capita, variações anuais)
- **15+ arquivos CSV** processados para análises

### 🔄 FASE 3: Desenvolvimento das Visualizações (3-4 dias) - **EM DESENVOLVIMENTO**
**Status**: 🔄 Parcialmente implementada (50%)

#### 3.1 ✅ Mapa de Calor Relacional
- **Objetivo**: Correlação entre categorias de gastos e IDH por estado
- **Tecnologia**: seaborn/matplotlib
- **Status**: ✅ Versão básica implementada (PNG)

#### 3.2 ⚠️ Gráfico de Bolhas Cruzado
- **Objetivo**: Gastos vs IDH com tamanho das bolhas representando população
- **Recurso**: Animação temporal (2019-2023)
- **Status**: ⚠️ Código implementado, pendente execução completa

#### 3.3 ✅ Mapa Coroplético Relacional
- **Objetivo**: Distribuição geográfica dos gastos e IDH
- **Tecnologia**: geopandas e plotly
- **Status**: ✅ GeoJSON dos estados brasileiros obtido

#### 📋 Pendências Fase 3:
- [ ] Executar geração completa das visualizações interativas (HTML)
- [ ] Finalizar mapas coropléticos relacionais avançados
- [ ] Integrar dados reais de população nos gráficos de bolhas
- [ ] Validar visualizações para integração no dashboard

### ⏳ FASE 4: Dashboard Interativo (2-3 dias) - **PENDENTE**
**Status**: ⏳ Não iniciada

#### 4.1 ⏳ Estrutura do Dashboard
- Interface com Streamlit
- Filtros por ano, região, categoria de gasto

#### 4.2 ⏳ Integração das Visualizações
- Implementação dos três tipos de gráficos
- Interatividade entre componentes

#### 4.3 ⏳ Análises Estatísticas Integradas
- Coeficientes de correlação dinâmicos
- Testes de significância básicos

### ⏳ FASE 5: Análise Final e Insights (1-2 dias) - **PENDENTE**
**Status**: ⏳ Não iniciada

#### 5.1 ⏳ Resposta às Perguntas de Pesquisa
- Análise sistemática de cada pergunta proposta
- Geração de insights baseados nos dados

#### 5.2 ⏳ Validação e Refinamento
- Verificação da consistência dos resultados
- Ajustes finais nas visualizações

## 🛠️ Tecnologias Principais

### 🔧 Stack Tecnológico Implementado:
- **🔄 Coleta**: `requests`, `BeautifulSoup`, `pandas` ✅
- **📊 Processamento**: `pandas`, `numpy` ✅
- **📈 Visualização**: `matplotlib`, `seaborn`, `plotly`, `geopandas` ✅
- **🖥️ Dashboard**: `streamlit` (Fase 4)
- **📊 Análise**: `scipy`, `statsmodels` ✅

### 📦 Dependências Completas:
```bash
pip install -r requirements.txt
```

**Bibliotecas principais instaladas:**
- `pandas>=2.0.0` - Manipulação de dados ✅
- `numpy>=1.24.0` - Computação numérica ✅
- `matplotlib>=3.7.0` - Visualizações ✅
- `seaborn>=0.12.0` - Visualizações estatísticas ✅
- `plotly>=5.0.0` - Visualizações interativas ✅
- `geopandas>=0.10.0` - Mapas geográficos ✅
- `streamlit>=1.25.0` - Dashboard interativo
- `scipy>=1.11.0` - Análises estatísticas ✅
- `beautifulsoup4>=4.12.0` - Web scraping ✅
- `requests>=2.31.0` - Requisições HTTP ✅

## 🚀 Como Executar

### ✅ Fase 1: Coleta de Dados Oficiais 
```bash
python fase1_coleta_oficial.py
```

### ✅ Fase 2: Análise Exploratória 
```bash
python fase2_analise_exploratoria.py
```

### 🔍 Verificação dos Dados
```bash
python verificar_dados.py
```

## 📁 Estrutura Técnica do Projeto

```
projeto_final/
├── fase1_coleta_oficial.py         # 🚀 SCRIPT PRINCIPAL - Coleta dados oficiais ✅
├── fase2_analise_exploratoria.py   # 📊 Análise exploratória e correlações ✅
├── verificar_dados.py              # 🔍 Verificação dos dados coletados ✅
├── data/
│   ├── raw/                        # 📊 Dados brutos ✅
│   │   ├── idh_oficial_real.csv                    # IDH por estado (136 registros)
│   │   ├── despesas_publicas_oficiais_real.csv     # Despesas federais (10.800+ registros)
│   │   └── relatorio_compatibilidade_oficial.csv   # Relatório de compatibilidade
│   ├── processed/                  # 📈 Dados processados ✅
│   │   ├── brazil_states.geojson                   # ✅ GeoJSON dos estados brasileiros
│   │   ├── dataset_unificado.csv                   # Dataset pronto para análises
│   │   ├── estatisticas_*.csv                      # Estatísticas descritivas
│   │   ├── correlacoes_*.csv                       # Análises de correlação
│   │   ├── *_por_regiao.csv                        # Dados agregados por região
│   │   ├── variacao_anual_*.csv                    # Variações anuais
│   │   ├── outliers_*.csv                          # Outliers identificados
│   │   ├── *.png                                   # 12+ gráficos exploratórios
│   │   └── *.html                                  # Visualizações interativas (pendente)
│   └── external/                   # 🗺️ Dados auxiliares
├── src/
│   ├── data_collection/            # 🔧 Scripts de coleta ✅
│   │   ├── __init__.py
│   │   ├── idh_oficial_collector.py        # Coletor IDH oficial
│   │   └── despesas_oficiais_collector.py  # Coletor despesas oficial
│   ├── data_processing/            # 🔄 Limpeza e transformação
│   ├── analysis/                   # 📊 Análises estatísticas
│   └── visualization/              # 📈 Gráficos e dashboard
├── notebooks/                      # 📓 Jupyter notebooks exploratórios
├── dashboard/                      # 🖥️ Aplicação Streamlit (Fase 4)
├── docs/                          # 📖 Documentação
├── requirements.txt               # 📦 Dependências ✅
└── README.md                      # 📖 Este arquivo
```

## 📊 Resultados Obtidos

### 💰 Resumo por Categoria de Despesa:
- **Saúde**: R$ 345,4+ bilhões (34,1%)
- **Educação**: R$ 264,4+ bilhões (26,1%)
- **Infraestrutura**: R$ 224,3+ bilhões (22,1%)
- **Assistência Social**: R$ 178,8+ bilhões (17,7%)

### 📈 Visualizações Geradas:
- **📊 Gráficos estáticos (PNG)**: 12+ visualizações exploratórias
  - Boxplots de distribuição por região
  - Scatterplots de correlação IDH vs gastos
  - Heatmap de correlação entre variáveis
  - Séries temporais por categoria de gasto
- **📋 Análises estatísticas**: 15+ arquivos CSV processados
- **🗺️ Dados geográficos**: Estados brasileiros preparados

### 🔗 Correlações Identificadas:
- **Métodos**: Pearson e Spearman implementados
- **Granularidade**: Por categoria, ano, estado e região
- **Outliers**: Identificados e documentados

## 🎯 Próximos Passos Imediatos

### 📋 Prioridades:
1. **🔄 Finalizar Fase 3**: Executar geração completa das visualizações interativas
2. **🚀 Iniciar Fase 4**: Desenvolver dashboard Streamlit com filtros dinâmicos
3. **📊 Implementar Fase 5**: Responder sistematicamente às perguntas de pesquisa

### 🛠️ Tarefas Técnicas:
- [ ] Executar `fase2_analise_exploratoria.py` para gerar visualizações HTML
- [ ] Criar interface Streamlit com os três tipos de gráficos especificados
- [ ] Implementar filtros por ano, região e categoria de gasto
- [ ] Desenvolver análises para responder às perguntas de pesquisa
- [ ] Gerar relatório final com insights e conclusões

## 🛡️ Garantias de Qualidade

- ✅ **Dados 100% Reais**: Todas as fontes são oficiais e governamentais
- ✅ **Verificação de Integridade**: Scripts de validação automática
- ✅ **Documentação Completa**: Código bem documentado e comentado
- ✅ **Rastreabilidade**: Todas as fontes são identificadas e verificáveis
- ✅ **Análises Robustas**: Correlações múltiplas e detecção de outliers
- ✅ **Estrutura Modular**: Código organizado e escalável
- ✅ **Metodologia Científica**: Abordagem sistemática e reproduzível

## 📞 Informações Técnicas

### 🔬 Metodologia de Análise:
- **Coleta**: Dados oficiais extraídos via APIs e web scraping
- **Processamento**: Limpeza, padronização e agregação de dados
- **Correlação**: Análises de Pearson e Spearman implementadas
- **Visualização**: Três tipos específicos de gráficos relacionais
- **Validação**: Verificação automática de integridade e consistência

### 🖥️ Ambiente Técnico:
- **Backend**: Python 3.8+
- **Interface**: Dashboard interativo com Streamlit
- **Análise**: Correlações temporais e espaciais
- **Visualização**: Mapas coropléticos, bolhas cruzadas, heatmaps relacionais

---

**🎉 Projeto estruturado para responder perguntas específicas sobre IDH e investimentos públicos!**

**📊 Status de Desenvolvimento**: 
- ✅ **Fase 1**: Concluída (100%) - Coleta e preparação de dados oficiais
- ✅ **Fase 2**: Concluída (100%) - Análise exploratória e correlações
- 🔄 **Fase 3**: Em desenvolvimento (50%) - Visualizações relacionais específicas
- ⏳ **Fase 4**: Pendente (0%) - Dashboard interativo com Streamlit
- ⏳ **Fase 5**: Pendente (0%) - Resposta às perguntas de pesquisa

**🏆 Progresso Total**: 50% concluído | **Base sólida estabelecida** | **Pronto para visualizações e dashboard** ✅ 