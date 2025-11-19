# Sistema de Controle de Velocidade de Ventoinha Fuzzy

Um sistema inteligente de controle de ventoinha de computador que utiliza lógica Fuzzy para determinar a velocidade ideal baseada na temperatura da CPU e carga de processamento.

## Descrição

Este projeto implementa um controlador Fuzzy para sistema de resfriamento de computadores. O sistema analisa a **temperatura da CPU** e **carga de processamento** simultaneamente para determinar a velocidade adequada da ventoinha, usando conjuntos fuzzy para cada variável de entrada: **baixa**, **média** e **alta**.

### Como Funciona

1. **Entradas**:
   - Temperatura da CPU (30°C a 100°C)
   - Carga de processamento (0% a 100%)

2. **Análise Simultânea**: Avalia ambas as entradas em conjunto

3. **Processamento Fuzzy**:
   - Calcula graus de pertinência para temperatura (baixa/média/alta)
   - Calcula graus de pertinência para carga (baixa/média/alta)
   - Aplica 9 regras de inferência baseadas em combinações
   - Realiza defuzzificação

4. **Saída**: Velocidade da ventoinha recomendada (0% a 100%)

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

## Lógica Fuzzy Implementada

### Variáveis Linguísticas

#### Temperatura da CPU (Entrada)
- **Baixa**: triangular [30, 30, 50]°C (CPU fria)
- **Média**: triangular [40, 55, 70]°C (temperatura normal)
- **Alta**: triangular [60, 100, 100]°C (CPU quente)

#### Carga de Processamento (Entrada)
- **Baixa**: triangular [0, 0, 30]% (CPU pouco utilizada)
- **Média**: triangular [20, 45, 70]% (CPU moderadamente utilizada)
- **Alta**: triangular [60, 100, 100]% (CPU intensamente utilizada)

#### Velocidade da Ventoinha (Saída)
- **Baixa**: triangular [0, 0, 25]% (ventoinha lenta)
- **Média**: triangular [15, 30, 50]% (ventoinha moderada)
- **Alta**: triangular [40, 60, 75]% (ventoinha rápida)
- **Muito Alta**: triangular [70, 100, 100]% (ventoinha máxima)

### Regras Fuzzy

O sistema utiliza **9 regras** baseadas em todas as combinações possíveis de temperatura e carga:

1. **Se** temperatura **Baixa** E carga **Baixa** → velocidade **Baixa**
2. **Se** temperatura **Baixa** E carga **Média** → velocidade **Média**
3. **Se** temperatura **Baixa** E carga **Alta** → velocidade **Alta**
4. **Se** temperatura **Média** E carga **Baixa** → velocidade **Baixa**
5. **Se** temperatura **Média** E carga **Média** → velocidade **Média**
6. **Se** temperatura **Média** E carga **Alta** → velocidade **Alta**
7. **Se** temperatura **Alta** E carga **Baixa** → velocidade **Alta**
8. **Se** temperatura **Alta** E carga **Média** → velocidade **Muito Alta**
9. **Se** temperatura **Alta** E carga **Alta** → velocidade **Muito Alta**

### Exemplos de Funcionamento

```
Cenário: Computador ocioso (CPU 35°C, carga 10%)
├── Temp Baixa: 0.75, Média: 0.00, Alta: 0.00
├── Carga Baixa: 0.67, Média: 0.00, Alta: 0.00
└── Velocidade Recomendada: 9.0% (baixa, sistema frio e pouco usado)

Cenário: Trabalho office (CPU 55°C, carga 50%)
├── Temp Baixa: 0.00, Média: 1.00, Alta: 0.00
├── Carga Baixa: 0.00, Média: 0.80, Alta: 0.00
└── Velocidade Recomendada: 31.7% (média, condições normais)

Cenário: Gaming intenso (CPU 80°C, carga 90%)
├── Temp Baixa: 0.00, Média: 0.00, Alta: 1.00
├── Carga Baixa: 0.00, Média: 0.00, Alta: 0.50
└── Velocidade Recomendada: 88.3% (muito alta, situação crítica)
```

## 📁 Estrutura do Projeto

```
fan_control_fuzzy/
├── fuzzy_logic.py          # Lógica Fuzzy principal (FanController)
├── app.py                  # Aplicação Flask com API REST
├── test_fuzzy.py           # Testes unitários completos
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
├── docs/
│   └── Apresentação.md     # Documentação técnica detalhada
├── templates/
│   └── index.html         # Interface web responsiva
└── static/
    ├── css/
    │   └── style.css      # Estilos com tema hardware
    └── js/
        └── script.js      # JavaScript interativo
```

## Testes

O projeto inclui **11 testes unitários** abrangentes que validam:

- ✅ Funções de pertinência para temperatura CPU e carga
- ✅ Cálculos de velocidade da ventoinha
- ✅ Sistema de controle Fuzzy com 2 entradas
- ✅ 9 regras de inferência Fuzzy
- ✅ Valores extremos e limites
- ✅ Consistência entre classe e função
- ✅ Cenários realistas de uso

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
Calcula velocidade da ventoinha baseada na temperatura CPU e carga de processamento.

**Request:**
```json
{
  "cpu_temperature": 70.0,
  "cpu_load": 80.0
}
```

**Response:**
```json
{
  "success": true,
  "cpu_temperature": 70.0,
  "cpu_load": 80.0,
  "fan_speed": 76.5,
  "membership": {
    "cpu_temp_baixa": 0.0,
    "cpu_temp_media": 0.5,
    "cpu_temp_alta": 0.0,
    "cpu_load_baixa": 0.0,
    "cpu_load_media": 0.0,
    "cpu_load_alta": 1.0
  }
}
```

### GET /plot
Retorna gráfico das funções de pertinência em base64.

## Casos de Uso

- **🖥️ Controle de Ventoinhas**: Sistemas de resfriamento inteligentes para PCs
- **🎮 Gaming**: Ajuste automático durante jogos intensos
- **💼 Workstations**: Otimização para tarefas de produção
- **🔧 Overclocking**: Controle térmico para sistemas modificados
- **📚 Educação**: Demonstração prática de lógica Fuzzy com 2 entradas
- **🤖 IoT**: Integração com sensores de hardware
- **🛠️ Manutenção**: Prevenção de overheating em servidores

## Personalização

Para modificar o sistema:

1. **Ajustar conjuntos fuzzy**: Edite as funções em `FanController`
   - `_define_cpu_temp_membership()`: modificar faixas de temperatura
   - `_define_cpu_load_membership()`: modificar faixas de carga
   - `_define_fan_speed_membership()`: modificar velocidades da ventoinha

2. **Modificar regras**: Edite `_define_rules()` para ajustar lógica de controle

3. **Alterar interface**: Personalize `templates/index.html` e `static/css/style.css`

4. **Adaptar para outros hardwares**: GPU, HDD, etc. (similar à CPU)

## Possíveis Melhorias

- [ ] **Múltiplas ventoinhas**: Controle independente para CPU/GPU case
- [ ] **Sensores adicionais**: Temperatura GPU, HDD, motherboard
- [ ] **Perfis de uso**: Automático (gaming, work, idle)
- [ ] **Machine Learning**: Otimização adaptativa das regras
- [ ] **Integração real**: APIs de motherboard (ASUS, MSI, Gigabyte)
- [ ] **Interface avançada**: Gráficos em tempo real, alertas
- [ ] **Modo silencioso**: Priorizar baixo ruído vs performance
- [ ] **Histórico e análise**: Logs de temperatura e carga

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

**Nota**: Este é um sistema educacional que demonstra conceitos avançados de lógica Fuzzy com múltiplas entradas. Para aplicações reais em hardware, considere integração com drivers específicos e validação em diversos cenários de uso.
