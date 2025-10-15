# IA Classificadora de Gatos e Cachorros 🐱🐶

Projeto para desenvolvimento de uma Inteligência Artificial que classifica imagens entre gatos e cachorros usando Machine Learning tradicional.

## 📋 Visão Geral do Projeto

### **Arquitetura da Solução**
- **Abordagem**: Machine Learning tradicional com scikit-learn
- **Modelo**: Usa features extraídas de imagens (cores, texturas, formas)
- **Framework Web**: Streamlit para interface simples e interativa
- **Dados**: Dataset "Cats and Dogs" do Kaggle (aprox. 25k imagens)

### **Status do Projeto**
✅ **Concluído e Funcional!**

O projeto está totalmente implementado e pronto para uso com todas as funcionalidades planejadas:

- ✅ Sistema de treinamento completo
- ✅ Modelo de classificação funcional
- ✅ Interface web Streamlit
- ✅ Processamento de imagens
- ✅ Sistema de predição com confiança

### **Estrutura do Projeto**
```
classificador_imagens/
├── data/                          # Dados e datasets
│   ├── raw/                      # Dataset bruto do Kaggle
│   ├── processed/                # Dados processados
│   └── models/                   # Modelos treinados salvos
├── models/                       # Lógica do modelo
│   ├── __init__.py
│   ├── feature_extractor.py      # Extração de características das imagens
│   ├── trainer.py                # Treinamento do modelo
│   └── predictor.py              # Classe para fazer predições
├── app/                          # Interface web
│   ├── __init__.py
│   ├── main.py                   # Aplicação principal Streamlit
│   └── utils.py                  # Funções auxiliares para a interface
├── training/                     # Scripts de treinamento
│   ├── __init__.py
│   ├── download_data.py          # Download do dataset Kaggle
│   ├── preprocess_data.py        # Pré-processamento das imagens
│   └── train_model.py            # Script principal de treinamento
└── utils/                        # Utilitários gerais
    ├── __init__.py
    ├── image_utils.py            # Funções para processamento de imagens
    └── config.py                 # Configurações gerais
```

### **Etapas de Implementação**

#### **Fase 1: Configuração e Dados**
1. ✅ Configurar ambiente (instalar dependências necessárias)
2. 📋 Baixar e preparar dataset do Kaggle
3. 📋 Extrair features básicas das imagens (cores, texturas, bordas)

#### **Fase 2: Modelo de Machine Learning**
1. 📋 Implementar extrator de características
2. 📋 Treinar modelo inicial com algoritmos simples (Random Forest, SVM)
3. 📋 Avaliar performance básica e salvar modelo

#### **Fase 3: Interface Web**
1. 📋 Criar aplicação Streamlit básica
2. 📋 Implementar upload de imagens
3. 📋 Adicionar funcionalidade de classificação
4. 📋 Mostrar resultado com confiança da predição

#### **Fase 4: Testes e Validação**
1. 📋 Testar com imagens diversas
2. 📋 Validar performance do modelo
3. 📋 Preparar para melhorias futuras

### **Tecnologias Utilizadas**
- **scikit-learn**: Para algoritmos de ML
- **OpenCV/Pillow**: Para processamento de imagens
- **Streamlit**: Para interface web
- **Kaggle API**: Para download do dataset
- **Joblib/Pickle**: Para salvar/carregar modelos

### **Estimativa de Tempo**
- **Fase 1**: 2-3 horas (configuração + dados)
- **Fase 2**: 3-4 horas (modelo + treinamento)
- **Fase 3**: 2-3 horas (interface)
- **Fase 4**: 1-2 horas (testes)

**Total estimado: 8-12 horas**

## 🚀 Como Usar

### ⚡ Início Ultra-Rápido (Arquivo Único)
```bash
# Execute apenas este comando - ele faz tudo automaticamente!
python main.py
```

**O que o `main.py` faz:**
- ✅ Verifica dependências e instala se necessário
- ✅ Baixa o dataset do Kaggle automaticamente
- ✅ Processa as imagens e extrai features
- ✅ Treina o modelo de IA
- ✅ Inicia a interface web Streamlit

### 📋 Outras Opções

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

### 📋 Instalação Manual
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar Kaggle (opcional para download automático)
# Ver instruções em: https://www.kaggle.com/docs/api
```

### 🏃‍♂️ Treinamento do Modelo
```bash
cd training

# 1. Baixar dados do Kaggle (requer API key)
python download_data.py

# 2. Pré-processar imagens e extrair features
python preprocess_data.py

# 3. Treinar modelo (Random Forest + SVM)
python train_model.py
```

### 🌐 Interface Web
```bash
cd app
streamlit run main.py
```
Acesse: http://localhost:8501

## 📊 Funcionalidades

- ✅ Classificação básica gato/cachorro
- ✅ Interface web intuitiva
- ✅ Upload de imagens
- ✅ Mostra confiança da predição
- 🚧 Suporte para múltiplas imagens (futuro)
- 🚧 Histórico de classificações (futuro)
- 🚧 Explicabilidade visual (futuro)

## 🔧 Melhorias Futuras

1. **Modelo avançado**: Implementar CNNs com TensorFlow/Keras
2. **Mais funcionalidades**: Múltiplas imagens, histórico, explicabilidade
3. **Otimização**: Melhorar performance e precisão
4. **Deploy**: Hospedar em cloud (Heroku, AWS, etc.)

---

*Projeto iniciado em: Outubro 2025*
*Status: 🚧 Em desenvolvimento*
