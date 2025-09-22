# 🤖 Chatbot Educacional com Google Gemini

Este projeto implementa um **chatbot educacional completo em um único arquivo** que utiliza o Google Gemini 2.5 Pro para responder perguntas de forma clara e didática.

## 📁 Estrutura Limpa

```
📂 Projeto
├── 📄 chatbot_educacional.py  # 🏆 Arquivo único com tudo!
├── 📄 web_app.py             # 🌐 Inicialização direta da web
├── 📄 README.md               # 📖 Documentação
├── 📄 INSTRUCOES_RAPIDAS.md   # 🚀 Guia rápido
├── 📄 requirements.txt        # 📦 Dependências
└── 📄 .env                    # 🔑 Configuração da API (opcional)
```

## 🚀 Instalação Rápida

```bash
# Instale as dependências
pip install google-generativeai python-dotenv streamlit

# Configure sua chave da API (opcional - funciona no modo simulado)
echo "GOOGLE_API_KEY=sua_chave_do_google_ai_aqui" > .env
```

## 🎯 Uso Simples (Arquivo Único)

### 🌐 Interface Web (Recomendado!)
```bash
# 🚀 MAIS SIMPLES - apenas execute!
python web_app.py

# Ou via streamlit
python -m streamlit run web_app.py

# Ou arquivo completo
python -m streamlit run chatbot_educacional.py
```

**💡 Dica:** Execute `python chatbot_educacional.py` para ver todas as opções disponíveis!

### 🔌 Configuração de Porta
- **Porta Fixa:** 8501
- **Motivo:** Evita conflitos quando múltiplas instâncias rodam
- **Acesso:** Sempre em `http://localhost:8501`

### 💻 Modo Terminal (Avançado)
```bash
# Modo terminal explícito
python chatbot_educacional.py --terminal

# Modo simulado (funciona sem chave da API)
python chatbot_educacional.py --terminal --simulado

# Com tema específico
python chatbot_educacional.py --terminal --simulado fisica
```

## 📚 Temas Disponíveis

- **🧬 Biologia**: Células, DNA, evolução, ecossistemas
- **🔢 Matemática**: Equações, geometria, cálculo, álgebra
- **⚡ Física**: Gravidade, energia, movimento, leis físicas
- **📚 História**: Eventos históricos, civilizações, revoluções

## 🎨 Características

### Interface Web
- ✅ Design moderno e responsivo
- ✅ Seleção intuitiva de temas
- ✅ Histórico visual de conversa
- ✅ Funciona em qualquer navegador

### Terminal
- ✅ Respostas rápidas e diretas
- ✅ Suporte completo a todos os temas
- ✅ Modo simulado para testes

### IA
- ✅ Google Gemini 2.5 Pro
- ✅ Contexto especializado por tema
- ✅ Respostas didáticas e explicativas
- ✅ Histórico de conversa mantido

## 📋 Como Funciona

### Modo Simulado
- Funciona sem configuração de API
- Respostas pré-programadas baseadas em temas
- Ideal para testes e demonstrações

### Modo Gemini
- Requer chave da API do Google AI
- Respostas geradas por IA avançada
- Contexto educacional personalizado

## 🔧 Configuração da API (Opcional)

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crie uma chave de API
3. Adicione no arquivo `.env`:
```
GOOGLE_API_KEY=sua_chave_aqui
```

## 📖 Exemplos de Uso

```bash
# 🌟 Interface web (recomendado - mais fácil!)
python chatbot_educacional.py

# Interface web com tema específico
python chatbot_educacional.py matematica

# 💻 Modo terminal (avançado)
python chatbot_educacional.py --terminal --simulado biologia

# Teste rápido sem API
python chatbot_educacional.py --terminal fisica
```

## 🏗️ Arquitetura

O arquivo `chatbot_educacional.py` contém:
- ✅ Configurações e constantes
- ✅ Classe do chatbot educacional
- ✅ Interface web (Streamlit)
- ✅ Modo terminal
- ✅ Modo simulado
- ✅ Tratamento de erros

## 🎓 Casos de Uso

- **Estudantes**: Aprendizado interativo
- **Professores**: Exemplos e explicações
- **Desenvolvedores**: Demonstrações de IA
- **Educadores**: Ferramenta de apoio ao ensino

---

**Arquivo único:** `chatbot_educacional.py` - Tudo que você precisa em um só lugar! 🎯

## 🧹 Projeto Limpo e Organizado

Este projeto foi **consolidado em um único arquivo** para máxima simplicidade:

### ✅ Arquivos Mantidos
- `chatbot_educacional.py` - **🏆 Arquivo único com tudo!**
- `web_app.py` - **🌐 Inicialização direta da interface web**
- `README.md` - Documentação completa
- `INSTRUCOES_RAPIDAS.md` - Guia rápido
- `requirements.txt` - Dependências
- `.env` - Configuração da API

### 🗑️ Arquivos Removidos
- `main.py` → Consolidado no arquivo único
- `app.py` → Interface integrada
- `config.py` → Configurações no arquivo único
- `teste_simulado.py` → Modo simulado integrado
- `env.example` → `.env` serve como exemplo
- `INSTRUCOES_CONFIGURACAO.md` → Instruções no README
- `__pycache__/` → Arquivos temporários removidos

### 🎯 Benefícios da Estrutura Limpa
- **Simplicidade**: Apenas 1 arquivo principal
- **Portabilidade**: Fácil de compartilhar
- **Manutenção**: Menos arquivos para gerenciar
- **Clareza**: Estrutura organizada e intuitiva