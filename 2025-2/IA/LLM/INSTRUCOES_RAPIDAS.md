# 🚀 Instruções Rápidas - Chatbot Educacional

## 📁 Arquivo Único: `chatbot_educacional.py`

### 🎯 Instalação (1 minuto)
```bash
pip install google-generativeai python-dotenv streamlit
```

### 🎮 Como Usar

#### Modo Simulado (Funciona Imediatamente)
```bash
python chatbot_educacional.py --simulado
```

#### Interface Web (Recomendado)
```bash
# 🚀 MAIS SIMPLES - apenas execute!
python web_app.py

# Ou via streamlit
python -m streamlit run web_app.py
```
Acesse: **http://localhost:8501** (porta fixa configurada)

#### Terminal com API
```bash
# Configure primeiro: GOOGLE_API_KEY=chave_no_arquivo_.env
python chatbot_educacional.py biologia
```

### 📚 Temas Disponíveis
- `biologia` - 🧬 Células, DNA, evolução
- `matematica` - 🔢 Cálculos, geometria, álgebra
- `fisica` - ⚡ Gravidade, energia, movimento
- `historia` - 📚 Eventos históricos, civilizações

### 💡 Exemplos Práticos
```bash
# Biologia no terminal
python chatbot_educacional.py --simulado biologia

# Matemática na web
python chatbot_educacional.py --web matematica

# Física com API real
python chatbot_educacional.py fisica
```

### 🔑 API (Opcional)
Para usar com Google Gemini:
1. [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Pegue sua chave
3. Edite `.env`: `GOOGLE_API_KEY=sua_chave`

### 🎉 Pronto!
Execute `python chatbot_educacional.py --web` e comece a aprender! 🤖📚
