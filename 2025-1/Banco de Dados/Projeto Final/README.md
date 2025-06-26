# 🎯 Projeto Final - Banco de Dados DEC7588

## 📊 Sistema Analítico IDH vs Despesas Públicas Federais (2019-2023)

**Sistema completo de análise de dados socioeconômicos** com **interface gráfica moderna**, **consultas analíticas avançadas**, **visualizações interativas** e **chat IA integrado** para análise de correlação entre **Índice de Desenvolvimento Humano (IDH)** e **despesas públicas federais** dos estados brasileiros.

---

## 🎯 Objetivos do Sistema

Este sistema oferece uma plataforma robusta e moderna para:
- **Análise Correlacional**: IDH vs Despesas Públicas por estado (2019-2023)
- **Visualizações Interativas**: 6 tipos de gráficos analíticos
- **Dashboard Executivo**: Métricas principais e insights automáticos
- **Sistema CRUD Completo**: Gerenciamento de todas as entidades
- **Chat IA Integrado**: Análise inteligente com Google Gemini
- **Dados Centralizados**: Fonte única de verdade no banco de dados

---

## 🏆 Status de Implementação

### ✅ **PROJETO 100% CONCLUÍDO E FUNCIONAL**

#### 🚀 **Fase 1: Modelagem Completa** - ✅ CONCLUÍDA
- **12 entidades relacionais** com integridade referencial
- **Normalização 3ª Forma Normal** aplicada
- **Scripts DDL automáticos** para PostgreSQL/SQLite
- **Relacionamentos complexos** 1:N e N:N

#### 🚀 **Fase 2: Sistema CRUD Completo** - ✅ CONCLUÍDA  
- **Operações CRUD** para todas as 12 entidades
- **Interface gráfica moderna** com ttkbootstrap
- **Validações robustas** e tratamento de erros
- **Sistema de importação CSV** automático

#### 🚀 **Fase 3: Consultas Analíticas** - ✅ CONCLUÍDA
- **3 consultas analíticas principais** implementadas
- **Consultas complexas** com 7+ joins e agregações
- **Métricas automatizadas**: eficiência, correlação, tendências
- **Relatórios executivos** com insights inteligentes

#### 🚀 **Fase 4: Integração com IA** - ✅ CONCLUÍDA
- **Chat Inteligente** com Google Gemini
- **Análise Contextual** integrada com dados reais
- **Recomendações Personalizadas** baseadas em consultas
- **Relatórios IA** automáticos e contextualizados

#### 🚀 **Fase 5: Interface Gráfica Moderna** - ✅ CONCLUÍDA
- **Dashboard interativo** com métricas principais
- **6 visualizações analíticas** diferentes
- **Sistema de filtros** por ano e região
- **Sidebar IA persistente** entre mudanças de aba

---

## 🛠️ Tecnologias Utilizadas

### 🗄️ **Banco de Dados**
- **PostgreSQL** (produção) + **SQLite** (desenvolvimento)
- **SQLAlchemy ORM** com session management
- **Fallback automático** PostgreSQL → SQLite

### 🐍 **Backend Python**
- **Python 3.8+** com type hints
- **Pandas & NumPy** para análise de dados
- **Threading** para operações assíncronas

### 🎨 **Interface Gráfica**
- **Tkinter + ttkbootstrap** (interface moderna)
- **Matplotlib** (gráficos estáticos)
- **Plotly** (gráficos interativos)
- **Design responsivo** e profissional

### 🤖 **Inteligência Artificial**
- **Google Gemini API** para análise de dados
- **Processamento contextual** com dados reais
- **Insights automáticos** e recomendações

---

## 📁 Estrutura do Projeto

```
Projeto Final/
├── 🚀 main.py                     # Aplicação principal
├── 📋 requirements.txt            # Dependências
├── 📖 README.md                   # Esta documentação
│
├── 📊 data/                       # Dados do sistema
│   ├── processed/                 # Dados processados
│   │   ├── dados_socioeconomicos.db  # SQLite database
│   │   └── dataset_unificado.csv     # Dataset principal
│   └── geospatial/               # Shapefiles dos estados
│       ├── BR_UF_2024.shp        # Geometrias dos estados
│       └── ...                   # Arquivos complementares
│
├── 🔧 src/                        # Código fonte
│   ├── 🗄️ database/               # Sistema de banco
│   │   ├── connection.py         # Conexão PostgreSQL/SQLite
│   │   ├── config.py             # Configurações
│   │   ├── schema.sql            # DDL scripts
│   │   ├── csv_importer.py       # Importador CSV → DB
│   │   └── seed_data.py          # Dados iniciais
│   │
│   ├── 🏗️ models/                 # Modelos de dados
│   │   └── entities.py           # 12 entidades SQLAlchemy
│   │
│   ├── 📝 crud/                   # Operações CRUD
│   │   ├── base_crud.py          # CRUD base genérico
│   │   ├── geografia_crud.py     # Estados/Regiões
│   │   ├── indicadores_crud.py   # IDH
│   │   ├── financeiro_crud.py    # Despesas
│   │   ├── organizacional_crud.py # Órgãos
│   │   └── sistema_crud.py       # Usuários/Relatórios
│   │
│   ├── 🔍 queries/                # Consultas analíticas
│   │   └── analytics_queries.py  # 3 consultas principais
│   │
│   ├── 📈 visualization/          # Sistema de gráficos
│   │   └── plot_generator.py     # Gerador de visualizações
│   │
│   ├── 🤖 llm/                    # Integração IA
│   │   └── ai_analytics.py       # Google Gemini handler
│   │
│   └── 🖥️ gui/                    # Interface gráfica
│       ├── main_window.py        # Janela principal
│       ├── data_integration.py   # Provedor de dados
│       ├── components/           # Componentes da UI
│   │   ├── dashboard_tab.py      # Aba dashboard
│   │   ├── visualizations_tab.py # Aba visualizações
│   │   ├── crud_tab.py           # Aba CRUD
│   │   └── chat_sidebar.py       # Sidebar IA
│   │
│   └── utils/                    # Utilitários UI
│       ├── styling.py            # Estilos e temas
DEC7588-Projeto-BD/
├── main.py                     # Aplicação principal
├── requirements.txt            # Dependências
├── README.md                   # Documentação
│
├── data/                       # Dados do sistema
│   ├── raw/                    # Dados brutos originais
│   ├── processed/              # Dados processados
│   └── geospatial/             # Dados geográficos
│
├── src/                        # Código fonte
│   ├── database/               # Conexão e configuração BD
│   │   ├── connection.py       # Conexão PostgreSQL/MySQL
│   │   ├── models.py           # Modelos SQLAlchemy
│   │   └── ddl_scripts.sql     # Scripts de criação
│   │
│   ├── crud/                   # Operações CRUD
│   │   ├── create.py           # Inserções
│   │   ├── read.py             # Consultas
│   │   ├── update.py           # Atualizações
│   │   └── delete.py           # Exclusões
│   │
│   ├── queries/                # Consultas analíticas
│   │   ├── consulta1.py        # Gastos por região/categoria
│   │   ├── consulta2.py        # IDH vs Investimentos
│   │   └── consulta3.py        # Evolução temporal
│   │
│   ├── visualization/          # Geração de gráficos
│   │   └── plot_generator.py   # Gráficos das consultas
│   │
│   ├── llm/                    # Integração com IA
│   │   └── llm_handler.py      # Handler do Gemini
│   │
│   └── interface/              # Interface do usuário
│       ├── menu_principal.py   # Menu principal
│       └── crud_interface.py   # Interface CRUD
│
└── docs/                       # Documentação
    ├── modelo_conceitual.png   # Diagrama ER
    ├── modelo_logico.png       # Modelo lógico
    └── relatorio_final.pdf     # Relatório completo
```

---

## Como Executar

### 1. Configuração do Ambiente
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
# Edite o arquivo Chave.env com:
# - GEMINI_API_KEY (chave do Google Gemini)
# - DATABASE_URL (URL do PostgreSQL/MySQL)
```

### 2. Configuração do Banco
```bash
# O sistema criará automaticamente as tabelas
# e carregará dados iniciais na primeira execução
python main.py --setup-database
```

### 3. Execução Principal
```bash
# Executar aplicação completa
python main.py
```

---

## 🚀 Status de Implementação

### ✅ Fase 1: Modelagem Completa (CONCLUÍDA)
- **12 entidades relacionais** modeladas e implementadas
- **Relacionamentos 1:N e N:N** com integridade referencial
- **Normalização 3ª Forma Normal** aplicada
- **Validações e constraints** robustas

### ✅ Fase 2: Sistema CRUD Completo (CONCLUÍDA)  
- **Operações CRUD** para todas as 12 entidades
- **Interface interativa** e profissional
- **Sistema de seed data** automático com 106 registros
- **Validações robustas** e tratamento de erros

### ✅ Fase 3: Consultas Analíticas (CONCLUÍDA)
- **3 consultas analíticas principais** implementadas
- **Consultas complexas** com 7+ joins e agregações avançadas
- **Métricas automatizadas**: eficiência, homogeneidade, tendências
- **Relatórios executivos** com insights inteligentes
- **Interface profissional** para análises especializadas

### ✅ Fase 4: Integração com IA (CONCLUÍDA)
- **Chat Inteligente**: 9 funcionalidades com Google Gemini
- **Análise Contextual**: IA integrada com consultas da Fase 3
- **Recomendações Personalizadas**: 5 perfis profissionais
- **Relatórios IA**: Documentos executivos automáticos
- **Exploração Guiada**: Sistema didático para usuários

---

## Funcionalidades Principais

### 1. Operações CRUD Completas
- **12 Entidades**: Estados, Regiões, Despesas, IDH, Órgãos, etc.
- **Interface Profissional**: Menus interativos e validações
- **Seed Data**: 106 registros de exemplo automáticos
- **Validação Robusta**: Integridade referencial garantida

### 2. Consultas Analíticas Especializadas

#### 🏆 Consulta 1: Ranking IDH vs Investimento Público
**Complexidade**: 7 tabelas, múltiplas agregações, métricas compostas
```sql
SELECT e.nome_estado, r.nome_regiao,
       AVG(i.idh_geral) as idh_medio,
       SUM(d.valor_milhoes) as total_investimento,
       -- Métricas de eficiência calculadas
       (AVG(i.idh_geral) * 1000) / SUM(d.valor_milhoes) as eficiencia
FROM Estado e
JOIN Regiao r ON e.regiao_id = r.id
JOIN IndicadorIDH i ON e.id = i.estado_id
JOIN Despesa d ON e.id = d.estado_id
JOIN CategoriaDespesa c ON d.categoria_despesa_id = c.id
JOIN Periodo p ON i.periodo_id = p.id AND d.periodo_id = p.id
GROUP BY e.id, e.nome_estado, r.nome_regiao
ORDER BY AVG(i.idh_geral) DESC;
```

#### 📈 Consulta 2: Evolução Temporal de Indicadores
**Complexidade**: Análise temporal, tendências, projeções
```sql
SELECT p.ano,
       AVG(i.idh_geral) as idh_medio_ano,
       SUM(d.valor_milhoes) as investimento_total_ano,
       COUNT(DISTINCT d.orgao_publico_id) as orgaos_ativos
FROM Periodo p
JOIN IndicadorIDH i ON p.id = i.periodo_id
JOIN Despesa d ON p.id = d.periodo_id
GROUP BY p.ano
ORDER BY p.ano;
```

#### 🗺️ Consulta 3: Análise Comparativa Regional
**Complexidade**: Agregações regionais, homogeneidade, eficiência
```sql
SELECT r.nome_regiao,
       COUNT(DISTINCT e.id) as total_estados,
       AVG(i.idh_geral) as idh_regional_medio,
       SUM(d.valor_milhoes) as investimento_regional_total,
       -- Cálculos de homogeneidade e eficiência
FROM Regiao r
JOIN Estado e ON r.id = e.regiao_id
JOIN IndicadorIDH i ON e.id = i.estado_id
JOIN Despesa d ON e.id = d.estado_id
GROUP BY r.id, r.nome_regiao
ORDER BY AVG(i.idh_geral) DESC;
```

### 3. Métricas Avançadas Implementadas
- **Eficiência de Investimento**: IDH/Investimento ratio
- **Homogeneidade Regional**: Coeficiente de variação
- **Tendências Temporais**: Crescimento médio anual
- **Projeções**: Estimativas baseadas em séries históricas
- **Categorização Automática**: Classificação de desempenho

### 3. Integração com IA
- **Análise Automática**: Identificação de padrões
- **Insights Inteligentes**: Correlações e tendências
- **Recomendações**: Sugestões de investimentos
- **Chat Analítico**: Consultas em linguagem natural

---

## Modelo de Dados

### Entidades Principais (10+)
1. **Estado** - Unidades federativas
2. **Regiao** - Regiões geográficas
3. **Municipio** - Municípios por estado
4. **Orgao_Publico** - Órgãos responsáveis
5. **Categoria_Despesa** - Tipos de gastos
6. **Despesa** - Registros de gastos
7. **Orcamento** - Orçamentos anuais
8. **Fonte_Recurso** - Origens dos recursos
9. **Periodo** - Períodos temporais
10. **Indicador_IDH** - Índices de desenvolvimento
11. **Usuario** - Usuários do sistema
12. **Relatorio** - Relatórios gerados

---

## Dados Utilizados

### Período de Análise
- **2019-2023** (5 anos)
- **27 Estados + DF**
- **4 Categorias** principais de despesa

### Fontes Oficiais
- **IDH**: Atlas Brasil - PNUD
- **Despesas**: Portal da Transparência - Governo Federal
- **Geografia**: IBGE

### Volume de Dados
- **135 registros** de IDH
- **10.800 registros** de despesas
- **R$ 1,11+ trilhão** investido

---

## Apresentação e Entrega

### Cronograma
- **Entrega**: 29/06/2025
- **Apresentação**: 01-09/07/2025
- **Duração**: 15 minutos + 5 minutos perguntas

### Artefatos
- ✅ **Relatório Completo** (itens 1-6 dos requisitos)
- ✅ **Código Fonte** (aplicação funcional)
- ✅ **Scripts DDL** (criação de tabelas)
- ✅ **Consultas e Gráficos** (3 consultas obrigatórias)
- ✅ **Integração IA** (funcionalidade com LLM)

---

## Equipe de Desenvolvimento

**Disciplina**: Banco de Dados (DEC7588) - 2025.1  
**Professor**: Alexandre Leopoldo Gonçalves  
**Campus**: UFSC Araranguá  

---

## Suporte

### Execução por Módulos
```bash
# Apenas operações CRUD
python -m src.interface.menu_principal

# Apenas consultas analíticas
python -m src.queries.consulta1

# Apenas integração com IA
python -m src.llm.llm_handler
```

### Requisitos Técnicos
- Python 3.8+
- PostgreSQL 12+ ou MySQL 8+
- 2GB RAM mínimo
- Conexão com internet (para IA)

---

**Sistema Completo de Banco de Dados com IA Integrada**

Análise abrangente de dados socioeconômicos brasileiros com funcionalidades CRUD completas, consultas analíticas e insights gerados por Inteligência Artificial.