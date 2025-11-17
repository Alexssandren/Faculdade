# Sistema de Controle de Temperatura Fuzzy

Um sistema inteligente de controle de ar-condicionado que utiliza logica Fuzzy para determinar a potencia ideal baseada na diferenca entre a temperatura ambiente atual e a desejada.

## Descricao

Este projeto implementa um controlador Fuzzy para sistema de ar-condicionado. O sistema calcula o **erro** (diferença entre temperatura desejada e atual) e determina a potência adequada do aparelho usando cinco conjuntos fuzzy para o erro: **muito frio**, **frio**, **ideal**, **quente** e **muito quente**.

### Como Funciona

1. **Entradas**:
   - Temperatura ambiente atual (0°C a 40°C)
   - Temperatura desejada (15°C a 30°C)

2. **Cálculo do Erro**: `erro = temperatura_desejada - temperatura_atual`

3. **Processamento Fuzzy**:
   - Calcula graus de pertinência do erro para cada conjunto fuzzy
   - Aplica regras de inferência baseadas no erro
   - Realiza defuzzificação

4. **Saída**: Potência recomendada (0% a 100%)

## Como Executar

### Pré-requisitos

- Python 3.8 ou superior (compatível com Python 3.13)
- pip (gerenciador de pacotes)

### Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Execução

#### Interface Web (Recomendado)
```bash
python app.py
```
Acesse: http://localhost:5000

#### Teste via Terminal
```bash
python fuzzy_logic.py
```

#### Executar Testes
```bash
python test_fuzzy.py
```

## Logica Fuzzy Implementada

### Variáveis Linguísticas

#### Erro (Entrada)
Diferença entre temperatura desejada e atual: `erro = temp_desejada - temp_atual`

- **Muito Frio**: triangular [-20, -20, -12]°C (ambiente muito abaixo do desejado)
- **Frio**: triangular [-16, -10, -4]°C (ambiente abaixo do desejado)
- **Ideal**: triangular [-6, 0, 6]°C (temperatura próxima do desejado - manutenção)
- **Quente**: triangular [4, 10, 16]°C (ambiente acima do desejado)
- **Muito Quente**: triangular [12, 20, 20]°C (ambiente muito acima do desejado)

#### Potência (Saída)
- **Muito Baixa**: triangular [0, 0, 20]%
- **Baixa**: triangular [10, 20, 40]%
- **Média**: triangular [30, 50, 70]%
- **Alta**: triangular [60, 80, 90]%
- **Muito Alta**: triangular [80, 100, 100]%

### Regras Fuzzy

1. **Se** erro indica **Muito Frio** → potência é **Muito Baixa**
2. **Se** erro indica **Frio** → potência é **Baixa**
3. **Se** erro é **Ideal** → potência é **Muito Baixa** (manutenção mínima)
4. **Se** erro indica **Quente** → potência é **Alta**
5. **Se** erro indica **Muito Quente** → potência é **Muito Alta**

### Exemplos de Funcionamento

```
Cenário: Ambiente 32°C, Desejado 22°C (Erro = -10°C)
├── Pertinência "Muito Frio": 0.00
├── Pertinência "Frio": 0.33
├── Pertinência "Ideal": 0.00
├── Pertinência "Quente": 0.00
├── Pertinência "Muito Quente": 0.00
└── Potência Recomendada: 16.7% (baixa, pois está quente)

Cenário: Ambiente 22°C, Desejado 22°C (Erro = 0°C)
├── Pertinência "Muito Frio": 0.00
├── Pertinência "Frio": 0.00
├── Pertinência "Ideal": 1.00
├── Pertinência "Quente": 0.00
├── Pertinência "Muito Quente": 0.00
└── Potência Recomendada: 6.7% (muito baixa, manutenção mínima)

Cenário: Ambiente 17°C, Desejado 22°C (Erro = +5°C)
├── Pertinência "Muito Frio": 0.00
├── Pertinência "Frio": 0.00
├── Pertinência "Ideal": 0.17
├── Pertinência "Quente": 0.50
├── Pertinência "Muito Quente": 0.00
└── Potência Recomendada: 48.9% (média, transição para aquecimento)
```

## 📁 Estrutura do Projeto

```
fuzzy_temp_control/
├── fuzzy_logic.py          # Lógica Fuzzy principal
├── app.py                  # Aplicação Flask
├── test_fuzzy.py           # Testes unitários
├── requirements.txt        # Dependências
├── README.md              # Esta documentação
├── templates/
│   └── index.html         # Interface web
└── static/
    ├── css/
    │   └── style.css      # Estilos da interface
    └── js/
        └── script.js      # JavaScript interativo
```

## Testes

O projeto inclui 11 testes unitarios que validam:

- Funcoes de pertinencia
- Calculos de potencia
- Sistema de controle
- Regras Fuzzy
- Valores extremos
- Consistencia dos resultados

Execute os testes:
```bash
python test_fuzzy.py
```

## Tecnologias Utilizadas

- **Python 3.8+** (compatível com Python 3.13): Linguagem principal
- **scikit-fuzzy >=0.5.0**: Biblioteca para lógica Fuzzy
- **Flask >=3.0.3**: Framework web
- **Matplotlib >=3.10.3**: Geração de gráficos
- **NumPy >=2.2.6**: Computação numérica
- **HTML/CSS/JavaScript**: Interface web

## API Endpoints

### POST /calculate
Calcula potência baseada nas temperaturas atual e desejada.

**Request:**
```json
{
  "current_temperature": 25.0,
  "desired_temperature": 22.0
}
```

**Response:**
```json
{
  "success": true,
  "current_temperature": 25.0,
  "desired_temperature": 22.0,
  "error": -3.0,
  "power": 50.0,
  "membership": {
    "muito_frio": 0.0,
    "frio": 0.0,
    "ideal": 0.4,
    "quente": 0.0,
    "muito_quente": 0.0
  }
}
```

### GET /plot
Retorna gráfico das funções de pertinência em base64.

## Casos de Uso

- **Controle de Ar-Condicionado**: Ajuste automático da potência
- **Educação**: Demonstração prática de lógica Fuzzy
- **IoT**: Integração com sensores de temperatura
- **Automação Residencial**: Controle inteligente de climatização

## Personalizacao

Para modificar o sistema:

1. **Ajustar conjuntos fuzzy**: Edite `fuzzy_logic.py`
2. **Adicionar regras**: Modifique o método `_define_rules()`
3. **Alterar interface**: Edite `templates/index.html` e `static/css/style.css`

## Possiveis Melhorias

- [ ] Adicionar mais variáveis (umidade, ocupação)
- [ ] Implementar aprendizado de máquina para otimizar regras
- [ ] Integração com dispositivos IoT reais
- [ ] Interface móvel responsiva
- [ ] Múltiplos idiomas
- [ ] Histórico de leituras

## Contribuicao

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licenca

Este projeto é open source e está disponível sob a [Licença MIT](LICENSE).

## Autor

Desenvolvido como projeto acadêmico de Inteligência Artificial.

---

**Nota**: Este é um sistema educacional que demonstra conceitos de lógica Fuzzy. Para aplicações reais, considere validação adicional e testes extensivos.
