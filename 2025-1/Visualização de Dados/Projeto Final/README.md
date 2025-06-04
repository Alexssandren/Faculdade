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
- **✅ Dataset Unificado `data/processed/dataset_unificado.csv` gerado, servindo como base para o BD.**

### ✅ NOVA FASE 2.5: Persistência de Dados em Banco de Dados (1-2 dias) - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100% (Depurada e Funcional)

#### 🎯 Objetivos (Requisito 7 da Faculdade):
- Implementar persistência dos dados processados em um banco de dados relacional.

#### ✅ Resultados Obtidos:
- **Escolha do Banco de Dados**: SQLite utilizado pela simplicidade.
- **Criação do Banco de Dados**: Script `src/database_setup.py` criado.
  - Cria o arquivo `data/processed/projeto_visualizacao.db`.
  - Define esquema e cria a tabela `analise_unificada` dinamicamente a partir do `dataset_unificado.csv`.
- **Carga de Dados**: O script `src/database_setup.py` carrega os dados do `dataset_unificado.csv` para a tabela `analise_unificada`.
- **Segurança**: Evita duplicação de dados em execuções subsequentes.

#### 🛠️ Como Configurar o Banco de Dados:
```bash
python src/database_setup.py
```
- Este comando irá criar o arquivo `projeto_visualizacao.db` e popular as tabelas.

### 🔄 FASE 3: Desenvolvimento das Visualizações Avançadas (3-4 dias) - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100%

#### 🎯 Objetivos:
- Desenvolver os três tipos de gráficos relacionais interativos especificados, utilizando dados do banco de dados SQLite.

#### ✅ Resultados Obtidos:
- Script `src/fase3_visualizacoes_avancadas.py` criado e funcional.
  - Carrega dados da tabela `analise_unificada` do `projeto_visualizacao.db`.
  - Gera e salva as seguintes visualizações interativas (arquivos HTML) em `results/visualizations/`:
    - **1. Mapa de Calor Relacional:** `fase3_mapa_calor_interativo.html` mostrando correlações entre IDH e gastos.
    - **2. Gráficos de Bolhas Cruzados:** Múltiplos arquivos `fase3_grafico_bolhas_<categoria>.html` (um para cada categoria de despesa), mostrando IDH vs. Gasto Per Capita, com tamanho da bolha pela população e animação por ano.
    - **3. Mapas Coropléticos Relacionais:** Múltiplos arquivos para o ano mais recente (ex: 2023):
      - `fase3_mapa_coropletico_idh_<ano>.html` (IDH por estado).
      - `fase3_mapa_coropletico_gasto_<categoria>_<ano>.html` (Gasto per capita por categoria e estado).
      - `fase3_mapa_coropletico_relacao_<categoria>_<ano>.html` (Relação IDH/Gasto por categoria e estado).
- **Aviso:** Utiliza `choropleth_mapbox` que está depreciado em Plotly, mas funcional.

#### 🛠️ Como Gerar as Visualizações Avançadas:
```bash
python src/visualization/static_visualizer.py
```
- Certifique-se de que as Fases 2 e 2.5 foram executadas anteriormente.
- Os arquivos HTML serão salvos em `results/final_visualizations/`.
- **Nota**: Estas são visualizações estáticas. O dashboard interativo (Fase 4) renderiza gráficos diretamente.

### ⏳ FASE 4: Dashboard Interativo (3-5 dias) - **EM ANDAMENTO**
**Status**: 🚧 Em Andamento (~65% Concluída)
**Tecnologia**: `CustomTkinter (Tkinter)`

#### 🎯 Objetivos:
- Implementar um dashboard interativo desktop com CustomTkinter que lê dados do `dataset_unificado.csv` (e futuramente do banco de dados SQLite).
- Exibir visualizações dinâmicas (mapa de calor, gráfico de bolhas, mapas coropléticos) usando Matplotlib.
- Permitir interação do usuário através de filtros e consultas ao LLM.

#### ✅ Progresso Atual:
- Interface gráfica básica da janela principal renderizada com CustomTkinter.
- Erro crítico de inicialização (`bad screen distance`) resolvido.
- Carregamento de dados do `dataset_unificado.csv` implementado.
- Filtro de ano funcional para atualizar visualizações.
- Gráficos (mapa de calor, bolhas, coropléticos) são gerados com Matplotlib e exibidos dentro da UI.
- Widgets para a funcionalidade de chat com LLM (histórico, campo de entrada, botão) estão instanciados e visíveis na UI.

#### ⚠️ Problemas Conhecidos e Próximos Passos:
- **Entrada de texto no chat:** Atualmente não está funcional ou o texto digitado não é visível.
- **Comportamento do filtro de ano:** Ao alterar o ano, o campo de entrada do chat é apagado.
- **Erros no console:** Mensagens de `invalid command name "..."` persistem e precisam ser investigadas.
- Melhorar a usabilidade geral e a estética do dashboard.
- Integrar completamente a leitura de dados do banco de dados SQLite.

#### 4.1 🏗️ Estrutura do Dashboard
- Interface com CustomTkinter (`src/app/dashboard_ui.py`).
- Filtros por ano (implementado), região, categoria de gasto (a serem aprimorados).
- **Fonte de Dados Primária Atual**: `dataset_unificado.csv`.

#### 4.2 📊 Integração das Visualizações
- Implementação dos três tipos de gráficos usando Matplotlib, renderizados em canvases Tkinter.
- Interatividade básica com filtros (ano).

#### 4.3 💬 Análises Estatísticas Integradas / LLM
- Funcionalidade delegada à integração com LLM (Fase 4.5).

### ⏳ NOVA FASE 4.5: Integração de LLM (2-3 dias) - **EM ANDAMENTO**
**Status**: 🚧 Em Andamento (~70% Concluída)
**Tecnologia**: `OpenAI (gpt-4o-mini)`

#### 🎯 Objetivos (Requisito 9 da Faculdade):
- Aplicar e usar um Large Language Model (LLM) de forma prática no projeto.

#### ✅ Progresso Atual:
- `LLMQueryHandler` (`src/llm/llm_handler.py`) implementado e capaz de se conectar à API da OpenAI usando a chave do arquivo `Chave.env`.
- Inicialização do `LLMQueryHandler` no dashboard confirmada como bem-sucedida.
- Estrutura básica para enviar consultas do usuário e receber respostas do LLM via widgets de chat está no lugar.
- Lógica para extrair intenções de filtro da resposta do LLM parcialmente implementada.

#### ⚠️ Problemas Conhecidos e Próximos Passos:
- **Testes de interação com LLM bloqueados:** Problemas com a entrada de texto no chat do dashboard impedem testes completos da funcionalidade do LLM.
- Validar e refinar a aplicação dos filtros (ano, UF, região, categoria) sugeridos pelo LLM na interface do dashboard.
- Melhorar o prompt do sistema e a robustez da extração de JSON da resposta do LLM.

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
- **📈 Visualização**: `matplotlib`, `seaborn`, `plotly`, `geopandas` ✅ (Plotly para estáticos, Matplotlib/Seaborn para dashboard)
- **🖥️ Dashboard**: `CustomTkinter` ✅
- **🤖 LLM**: `openai` ✅
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
- `plotly>=5.0.0` - Visualizações interativas (para HTMLs estáticos) ✅
- `geopandas>=0.10.0` - Mapas geográficos ✅
- `customtkinter>=5.0.0` - Dashboard interativo desktop ✅
- `openai>=1.0.0` - Integração com LLM ✅
- `python-dotenv>=1.0.0` - Carregamento de variáveis de ambiente ✅
- `scipy>=1.11.0` - Análises estatísticas ✅
- `beautifulsoup4>=4.12.0` - Web scraping ✅
- `requests>=2.31.0` - Requisições HTTP ✅

## 🚀 Como Executar

### ✅ Fase 1: Coleta de Dados Oficiais 
```bash
python fase1_coleta_oficial.py
```

### ✅ Fase 2: Análise Exploratória e Criação do Dataset Unificado
```bash
python fase2_analise_exploratoria.py
```
- Este script agora também gera o `data/processed/dataset_unificado.csv`.

### ✅ Fase 2.5: Configuração do Banco de Dados
```bash
python src/database/database_manager.py
```
- Este comando cria o banco de dados `projeto_visualizacao.db` e o popula com os dados do `dataset_unificado.csv`.

### ✅ Fase 3: Geração das Visualizações Avançadas (Estáticas HTML)
```bash
python src/visualization/static_visualizer.py
```
- Gera os arquivos HTML interativos em `results/final_visualizations/`.

### 🚀 Execução Completa do Pipeline (incluindo Dashboard Interativo)
```bash
python main.py
```
- Este é o comando principal para executar todas as fases configuradas no `main.py`, incluindo a inicialização do dashboard interativo.

### 🔍 Verificação dos Dados
```bash
python verificar_dados.py
```

## 📁 Estrutura Técnica do Projeto

```
projeto_final/
├── main.py                         # 🚀 SCRIPT PRINCIPAL - Orquestra as fases e inicia o dashboard ✅
├── Chave.env                       # 🔑 Arquivo para a chave da API OpenAI (NÃO COMMITAR)
├── fase1_coleta_oficial.py         # Script legado da Fase 1 (funcionalidade agora em src/)
├── fase2_analise_exploratoria.py   # Script legado da Fase 2 (funcionalidade agora em src/)
├── verificar_dados.py              # 🔍 Verificação dos dados coletados (pode precisar de ajuste)
├── data/
│   ├── raw/                        # 📊 Dados brutos ✅
│   ├── processed/                  # 📈 Dados processados ✅
│   │   ├── dataset_unificado.csv   # ✅ Dataset consolidado
│   │   └── projeto_visualizacao.db # ✅ Banco de dados SQLite
│   └── geospatial/                 # ✅ Dados geoespaciais (ex: .shp para mapas)
│       └── BR_UF_2024.shp
├── src/
│   ├── app/                        # 🖥️ Lógica do Dashboard CustomTkinter ✅
│   │   └── dashboard_ui.py
│   ├── llm/                        # 🤖 Lógica de integração com LLM ✅
│   │   └── llm_handler.py
│   ├── data_collection/            # 🔧 Scripts de coleta ✅
│   │   ├── __init__.py
│   │   ├── idh_oficial_collector.py
│   │   └── despesas_oficiais_collector.py
│   ├── data_processing/            # 🔄 Limpeza e transformação ✅
│   │   └── data_processor.py
│   ├── analysis/                   # 📊 Análises estatísticas ✅
│   │   ├── __init__.py
│   │   ├── exploratory_analyzer.py
│   │   └── advanced_analyzer.py
│   ├── visualization/              # 📈 Scripts de visualização ✅
│   │   └── static_visualizer.py    # Para HTMLs estáticos
│   └── database/                   # 🛠️ Script de configuração do BD ✅
│       └── database_manager.py
├── results/
│   ├── exploratory_analysis/       # Resultados da análise exploratória ✅
│   ├── advanced_analysis/          # Resultados das análises avançadas ✅
│   └── final_visualizations/       # Visualizações HTML estáticas geradas pela Fase 3 ✅
├── notebooks/                      # 📓 Jupyter notebooks exploratórios (se houver)
├── docs/                           # 📖 Documentação adicional
├── requirements.txt                # 📦 Dependências ✅
└── README.md                       # 📖 Este arquivo
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
1.  **🐞 Corrigir Dashboard CustomTkinter**:
    *   Resolver problema de entrada de texto não funcional/invisível no chat.
    *   Corrigir comportamento do filtro de ano que apaga o campo de chat.
    *   Investigar e resolver erros `invalid command name "..."` no console.
2.  **🤖 Testar Funcionalidade LLM**: Após correção da UI do chat, testar completamente a interação com o LLM, incluindo a aplicação de filtros.
3.  **💅 Refinar Dashboard**: Melhorar usabilidade, estética e responsividade.
4.  **⚙️ Integração BD**: Migrar dashboard para ler dados diretamente do SQLite.
5.  **📊 Concluir Fase 5**: Responder sistematicamente às perguntas de pesquisa usando o dashboard funcional.

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
- ✅ **Fase 2**: Concluída (100%) - Análise exploratória e dataset unificado
- ✅ **Fase 2.5**: Concluída (100%) - Persistência de dados em Banco de Dados SQLite
- ✅ **Fase 3**: Concluída (100%) - Visualizações relacionais específicas geradas
- 🚧 **Fase 4**: Em Andamento (~65% Concluída) - Dashboard interativo desktop
- 🚧 **Fase 4.5**: Em Andamento (~70% Concluída) - Integração de LLM para consultas em linguagem natural
- ⏳ **Fase 5**: Pendente (0%) - Resposta às perguntas de pesquisa

**🏆 Progresso Total**: ~75% concluído | **Dashboard Desktop funcional com ressalvas** | **LLM integrado, pendente de UI do chat** ✅ 