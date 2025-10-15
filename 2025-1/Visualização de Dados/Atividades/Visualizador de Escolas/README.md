# Sistema de Gestão de Escolas

Sistema para gerenciamento e visualização de dados escolares.

## Estrutura do Projeto

```
projeto/
├── src/                    # Código fonte principal
│   ├── main.py            # Ponto de entrada da aplicação
│   ├── app/               # Lógica da aplicação
│   ├── database/          # Gerenciamento de banco de dados
│   ├── gui/               # Componentes da interface gráfica
│   └── utils/             # Utilitários e funções auxiliares
├── data/                  # Arquivos de dados
│   ├── raw/               # Dados brutos
│   └── processed/         # Dados processados
├── scripts/               # Scripts de utilidade
├── cache/                 # Cache de dados temporários
├── requirements.txt       # Dependências do projeto
└── setup.py              # Script de configuração
```

## Requisitos

- Python 3.8+
- Bibliotecas listadas em requirements.txt

## Instalação

1. Clone o repositório
2. Execute `pip install -r requirements.txt`
3. Execute `python src/main.py`

## Funcionalidades

- Consulta de escolas com paginação
- Visualização de dados em diferentes formatos de gráficos:
  - Gráfico de Barras
  - Gráfico de Pizza
  - Gráfico de Linha
- Gerenciamento eficiente de janelas e recursos 