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

### ✅ NOVA FASE 4.5: Integração de LLM (2-3 dias) - **CONCLUÍDA**
**Status**: ✅ Finalizada em 100% - Lógica de consulta factual, herança de contexto e busca Top N totalmente funcionais e integradas.
**Tecnologia**: `OpenAI (gpt-4o-mini)`

#### 🎯 Objetivos (Requisito 9 da Faculdade):
- Aplicar e usar um Large Language Model (LLM) de forma prática no projeto.

#### ✅ Progresso Atual:
- `LLMQueryHandler` (`src/llm/llm_handler.py`) implementado e capaz de se conectar à API da OpenAI usando a chave do arquivo `Chave.env`.
- Inicialização do `LLMQueryHandler` no dashboard confirmada como bem-sucedida.
- Estrutura para enviar consultas do usuário e receber respostas do LLM via widgets de chat funcional.
- Lógica robusta para extrair intenções de filtro da resposta do LLM implementada e testada.
- Lógica de busca factual para IDH e gastos, incluindo identificação de UF/ano, tratamento de categorias de despesa, e herança de contexto para perguntas de acompanhamento, foi completamente refatorada, testada e integrada.
- Implementação da funcionalidade "Top N" (ex: "os 3 maiores IDHs") concluída e funcional para todos os cenários relevantes de IDH e Gastos (Brasil e Região).
- O sistema de cenários factuais (`handle_factual_scenarios` e funções auxiliares) está operando corretamente, priorizando dados locais quando aplicável.

#### ⚙️ Plano de Refatoração da Lógica Factual e de Cenários (Concluído e Integrado)
O `LLMQueryHandler` foi refatorado com sucesso para ser mais robusto, modular e preciso na identificação e resposta a consultas factuais.

**Estrutura Geral Implementada e Integrada em `llm_handler.py`:**
- **Funções Auxiliares Dedicadas (Concluídas):**
    - `_extract_year_from_query`: Extração robusta de ano.
    - `_extract_uf_from_query`: Extração robusta de UF.
    - `_extract_top_n`: Extração robusta do número N para consultas "Top N".
    - `_get_relevant_expense_columns`: Identificação de colunas de despesa.
- **Funções de Cenário Específicas e Modulares (Concluídas e com Suporte a Top N):** Funções separadas para cada tipo de consulta factual (ex: `_handle_idh_especifico`, `_handle_idh_maior_brasil`, `_handle_gasto_menor_regiao`, etc.), com capacidade de retornar múltiplos resultados (Top N).
- **Função Principal de Orquestração (`handle_factual_scenarios`) (Concluída):** Orquestra a chamada para as funções de cenário apropriadas.

**Fases do Plano de Implementação da Refatoração (Todas Concluídas):**
1.  **Fase 1: Configuração Inicial e Funções Auxiliares** - ✅ Concluída
2.  **Fase 2: Implementação dos Cenários de IDH (incluindo Top N)** - ✅ Concluída
3.  **Fase 3: Implementação dos Cenários de Gastos (incluindo Top N)** - ✅ Concluída
4.  **Fase 4: Integração e Testes com `llm_handler.py`** - ✅ Concluída
5.  **Fase 5 (Opcional): Refinamento e Cenários de Correlação** - ✅ FUNCIONALIDADE FACTUAL PRIMÁRIA CONCLUÍDA.
Com base nos testes, refinar a lógica das funções auxiliares e dos cenários.
Explorar a implementação de cenários de correlação (Sugestão #2):
Começar com um cenário simples, por exemplo, "Qual a correlação entre IDH e despesa com educação \\\[em SP] \\\[em 2022]?".
Isso exigirá calcular a correlação (Pearson, por exemplo) no subconjunto de dados filtrado.
A text_part poderia descrever a correlação encontrada (ex: "Foi encontrada uma correlação positiva forte (0.75) entre IDH e despesa com educação...").
Este é um cenário mais avançado e pode ser iterativo.
Considerar outros casos não factuais (Sugestão #3): Durante os testes, se identificarmos padrões de perguntas que o LLM consistentemente responde mal e que poderiam ser tratadas com uma lógica semi-factual ou uma resposta padrão melhorada, podemos adicionar.
Fase 6: Limpeza e Migração Final - ✅ CONCLUÍDA
Após a aprovação de que a lógica no arquivo temporário está robusta e correta:
Mover as funções implementadas (_extract_year_from_query, _extract_uf_from_query, as funções _handle_..., e handle_factual_scenarios) para o arquivo src/llm/llm_handler.py (provavelmente como métodos privados ou funções estáticas dentro da classe, ou mantê-las como funções auxiliares no módulo se preferir).
Remover o arquivo temporário.
Revisar e remover logs de depuração excessivos.

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
- 🚧 **Fase 4**: Em Andamento (~65% Concluída) - Dashboard interativo desktop (PySide6)
- 🚧 **Fase 4.5**: Em Andamento (~75% Concluída) - Integração de LLM para consultas em linguagem natural
- ⏳ **Fase 5**: Pendente (0%) - Resposta às perguntas de pesquisa

**🏆 Progresso Total**: ~90% concluído | **Dashboard Desktop (PySide6) em desenvolvimento** | **LLM com lógica de busca factual, herança de intenção e Top N FUNCIONAL.** ✅


PLANO DE INTEGRAÇÃO DO LLM:
Fase 1: Configuração Inicial e Funções Auxiliares (Foco na Sugestão #5) - ✅ CONCLUÍDA
Criar o arquivo src/llm/llm_scenario_handler_temp.py.
Implementar _extract_year_from_query:
Deve tentar converter query_ano_str para int.
Se falhar ou for None, buscar por padrões de ano (ex: "em 2021", "ano de 2020") no prev_response_content (se fornecido).
Se ainda não encontrar e df e uf_context forem fornecidos, buscar o ano mais recente para aquela UF.
Se ainda não encontrar e df for fornecido, buscar o ano mais recente geral no df.
Adicionar logs para cada etapa da tentativa de extração.
Implementar _extract_uf_from_query:
Validar query_uf_str (se é uma sigla de UF conhecida).
Se falhar ou for None, buscar por siglas de UF (ex: "SP", "RJ") ou nomes completos de estados no prev_response_content (se fornecido) e converter para sigla. Usar um mapeamento estado -> sigla.
Adicionar logs.
Implementar a estrutura básica da função handle_factual_scenarios:
Incluir os parâmetros definidos.
Chamar as funções _extract_year_from_query e _extract_uf_from_query.
Incluir os logs de debug iniciais.
Retornar (None, None) por enquanto.
Fase 2: Implementação dos Cenários de IDH (Foco na Sugestão #1 e #4) - ✅ CONCLUÍDA
Para cada cenário de IDH (_handle_idh_especifico, _handle_idh_maior_brasil, etc.):
Definir a lógica de filtragem do DataFrame com base nos parâmetros (UF, ano, região).
Realizar o cálculo ou busca (ex: idxmax(), idxmin(), mean(), seleção direta).
Formatar a text_part da resposta de forma clara e concisa (ex: "O IDH de SP em 2022 foi 0.X.").
Atualizar o dicionário de filters com os valores efetivamente usados (UF, ano, região) e adicionar a chave "tipo_cenario_factual" com um valor descritivo (ex: "idh_especifico_uf_ano", "idh_maior_brasil_ano").
Tratar casos de dados não encontrados ou insuficientes, retornando uma mensagem apropriada na text_part e None para os filtros, ou (None,None) para sinalizar que o cenário não se aplica.
Integrar a chamada da função de cenário dentro da "árvore de decisão" em handle_factual_scenarios.
**Nota: Estes cenários foram aprimorados para suportar a consulta de múltiplos resultados (top N), por exemplo, "os 3 maiores IDHs".** - ✅ CONCLUÍDO
Fase 3: Implementação dos Cenários de Gastos - ✅ CONCLUÍDA
Seguir a mesma abordagem da Fase 2 para os cenários de gastos (específico, maior, menor, por região, etc.).
Prestar atenção especial à coluna de gastos a ser usada (ex: despesa_total_milhoes ou soma de categorias específicas).
**Nota: Estes cenários foram aprimorados para suportar a consulta de múltiplos resultados (top N), por exemplo, "os 5 menores gastos em saúde".** - ✅ CONCLUÍDO
Fase 4: Integração (Inicial e Testes) - ✅ CONCLUÍDA
No arquivo src/llm/llm_handler.py, dentro do método get_response:
Importar handle_factual_scenarios do arquivo temporário.
Após a lógica de final_intent_for_scenarios e antes de retornar a resposta do LLM, chamar handle_factual_scenarios.
Se handle_factual_scenarios retornar um text_part válido, usar esse text_part e os updated_filters como a resposta final. Caso contrário (se retornar (None, None)), prosseguir com a resposta original do LLM.
Realizar testes extensivos com a lista de perguntas que já temos e novas variações, focando em:
Respostas factuais corretas.
Tratamento correto de perguntas de acompanhamento.
Herança e priorização de intenção corretas.
Filtros retornados corretamente.
Fase 5: Refinamento e Cenários de Correlação (Pode ser iterativo com a Fase 4) - ✅ FUNCIONALIDADE FACTUAL PRIMÁRIA CONCLUÍDA.
Com base nos testes, refinar a lógica das funções auxiliares e dos cenários.
Explorar a implementação de cenários de correlação (Sugestão #2):
Começar com um cenário simples, por exemplo, "Qual a correlação entre IDH e despesa com educação \\\[em SP] \\\[em 2022]?".
Isso exigirá calcular a correlação (Pearson, por exemplo) no subconjunto de dados filtrado.
A text_part poderia descrever a correlação encontrada (ex: "Foi encontrada uma correlação positiva forte (0.75) entre IDH e despesa com educação...").
Este é um cenário mais avançado e pode ser iterativo.
Considerar outros casos não factuais (Sugestão #3): Durante os testes, se identificarmos padrões de perguntas que o LLM consistentemente responde mal e que poderiam ser tratadas com uma lógica semi-factual ou uma resposta padrão melhorada, podemos adicionar.
Fase 6: Limpeza e Migração Final - ✅ CONCLUÍDA
Após a aprovação de que a lógica no arquivo temporário está robusta e correta:
Mover as funções implementadas (_extract_year_from_query, _extract_uf_from_query, as funções _handle_..., e handle_factual_scenarios) para o arquivo src/llm/llm_handler.py (provavelmente como métodos privados ou funções estáticas dentro da classe, ou mantê-las como funções auxiliares no módulo se preferir).
Remover o arquivo temporário.
Revisar e remover logs de depuração excessivos.