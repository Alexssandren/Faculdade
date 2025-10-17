# [COMPLETED] IA Classificadora de Gatos e Cachorros

**Sistema completo e funcional** para classificação automática de imagens entre gatos e cachorros usando Machine Learning tradicional com alta precisão e interface web intuitiva.

## Visão Geral do Projeto

### **Arquitetura da Solução**

- **Abordagem**: Machine Learning tradicional com scikit-learn
- **Modelo**: Usa features extraídas de imagens (cores, texturas, formas)
- **Framework Web**: Streamlit para interface simples e interativa
- **Dados**: Dataset "Cats and Dogs" do Kaggle (aprox. 25k imagens)

### **Estrutura do Projeto**

```
classificador_imagens/
├── run_app.py                    # [NOVO] Script orquestrador principal (faz tudo automaticamente)
├── data/                         # Dados e datasets
│   ├── raw/                      # Dataset bruto do Kaggle
│   ├── processed/                # Dados processados (features.npy, labels.npy)
│   └── models/                   # Modelos treinados salvos (.joblib)
├── models/                       # Lógica do modelo
│   ├── __init__.py
│   ├── feature_extractor.py      # Extração de características das imagens
│   ├── predictor.py              # Classe para fazer predições
├── app/                          # Interface web
│   ├── __init__.py
│   ├── main.py                   # Aplicação principal Streamlit
│   └── utils.py                  # Funções auxiliares para a interface
├── training/                     # Scripts de treinamento
│   ├── __init__.py
│   ├── download_data.py          # Download do dataset Kaggle
│   ├── preprocess_data.py        # Pré-processamento das imagens
│   └── model_selection.py        # [ATUALIZADO] Comparação de algoritmos via GridSearchCV
├── utils/                        # Utilitários gerais
   ├── __init__.py
   ├── image_utils.py             # Funções para processamento de imagens
   └── config.py                  # Configurações gerais
```

### **Funcionalidades Implementadas**

#### **Sistema Completo de Machine Learning**

- [OK] **Extração de Características Avançada**: Histogramas RGB/HSV, HOG, LBP
- [OK] **Pré-processamento Inteligente**: Redimensionamento, normalização automática
- [OK] **Comparação de Algoritmos**: Random Forest, SVM-RBF, Gradient Boosting, KNN
- [OK] **Otimização Automática**: GridSearchCV com validação cruzada
- [OK] **Redução de Dimensionalidade**: PCA para melhor performance
- [OK] **Persistência de Modelos**: Salvar/carregar modelos treinados

#### **Interface Web Streamlit**

- [OK] **Upload de Imagens**: Suporte a PNG, JPG, JPEG
- [OK] **Classificação em Tempo Real**: Predição instantânea com confiança
- [OK] **Visualização de Resultados**: Gráficos de probabilidade e barras de progresso
- [OK] **Interface Responsiva**: Design adaptável para diferentes dispositivos
- [OK] **Seleção de Modelos**: Escolha entre modelos treinados disponíveis

#### **Automação e Facilidade de Uso**

- [OK] **Script Orquestrador**: `run_app.py` faz tudo automaticamente
- [OK] **Verificação de Dependências**: Instalação automática de pacotes
- [OK] **Download Automático**: Dataset baixado diretamente do Kaggle
- [OK] **Processamento Batch**: Tratamento eficiente de grandes volumes de imagens
- [OK] **Logs Informativos**: Acompanhamento detalhado do processo

### **Tecnologias Utilizadas**

- **scikit-learn**: Para algoritmos de ML
- **OpenCV/Pillow**: Para processamento de imagens
- **Streamlit**: Para interface web
- **Kaggle API**: Para download do dataset
- **Joblib/Pickle**: Para salvar/carregar modelos

## Como Usar

### [START] Início Ultra-Rápido (Script Orquestrador)

```bash
# Execute apenas este comando - ele faz TUDO automaticamente!
python run_app.py
```

**O que o `run_app.py` faz:**

- [OK] Verifica versão do Python (requer 3.8+)
- [OK] Verifica e instala dependências automaticamente
- [OK] Verifica se há dataset processado disponível
- [OK] Baixa e processa imagens do Kaggle (se necessário)
- [OK] Treina modelo com algoritmo ótimo automaticamente
- [OK] Inicia interface web Streamlit na porta 8501

**Interface acessível em:** http://localhost:8501

### [INFO] Características Especiais do Sistema

- **Sem Deep Learning**: Usa técnicas clássicas de ML (Random Forest, SVM) com alta eficiência
- **Features Artesanais**: Extração manual de características visuais (não redes neurais)
- **Interface Limpa**: Sistema purgado de elementos gráficos desnecessários
- **Automação Total**: Script orquestrador que gerencia todo o pipeline
- **Código Legível**: Estrutura organizada e bem documentada
- **Performance Otimizada**: PCA e validação cruzada para máxima eficiência

### Outras Opções

#### Configuração Manual

```bash
# 1. Instalar dependências
python setup.py

# 2. Processo passo a passo
cd training
python download_data.py    # Baixar dataset
python preprocess_data.py  # Processar imagens
python train_model.py     # Treinar modelo

# 3. Interface web
cd app
streamlit run main.py
```

### Instalação Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar Kaggle (opcional para download automático)
# Ver instruções em: https://www.kaggle.com/docs/api
```

### Treinamento do Modelo

```bash
cd training

# 1. Baixar dados do Kaggle (requer API key)
python download_data.py

# 2. Pré-processar imagens e extrair features
python preprocess_data.py

# 3. Treinar modelo (Random Forest + SVM)
python train_model.py
```

### Interface Web

```bash
cd app
streamlit run main.py
```

Acesse: http://localhost:8501

## Funcionalidades Atuais

### **Classificação de Imagens**

- [OK] **Classificação Automática**: Gato, Cachorro ou Outro com alta precisão
- [OK] **Confiança da Predição**: Mostra probabilidade percentual da classificação
- [OK] **Suporte a Múltiplos Formatos**: PNG, JPG, JPEG
- [OK] **Processamento em Tempo Real**: Classificação instantânea após upload

### **Interface Web Avançada**

- [OK] **Design Responsivo**: Interface adaptável para desktop e mobile
- [OK] **Upload Intuitivo**: Arraste e solte ou seleção de arquivo
- [OK] **Visualização de Resultados**: Gráficos de barras e métricas visuais
- [OK] **Seleção de Modelo**: Escolha entre diferentes modelos treinados
- [OK] **Indicadores de Status**: Sistema de logs com códigos textuais

### **Características Técnicas**

- [OK] **Features Avançadas**: RGB, HSV, HOG, LBP para máxima precisão
- [OK] **Otimização PCA**: Redução de dimensionalidade para melhor performance
- [OK] **Validação Cruzada**: Garantia de robustez do modelo
- [OK] **Processamento Batch**: Tratamento eficiente de grandes volumes
- [OK] **Persistência**: Modelos salvos automaticamente para reutilização

## Melhorias Futuras

1. **Modelo avançado**: Implementar CNNs com TensorFlow/Keras para maior precisão
2. **Funcionalidades expandidas**: Upload múltiplo, histórico de classificações
3. **Explicabilidade visual**: Heatmaps mostrando áreas de decisão do modelo
4. **Otimização avançada**: Quantização e poda de modelos para deploy mobile
5. **Deploy em produção**: Hospedagem em cloud (Heroku, AWS, GCP)
6. **API REST**: Interface programática para integração com outros sistemas
7. **Aplicativo mobile**: App nativo para iOS/Android usando o modelo treinado
