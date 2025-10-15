#!/usr/bin/env python3
"""
Interface Web do Chatbot Educacional - Arquivo Executável

Execute com: python -m streamlit run web_app.py
"""

import streamlit as st
import os
import sys

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa componentes do chatbot
from chatbot_educacional import (
    ChatbotEducacional, CONTEXTOS_EDUCACIONAIS,
    TEMA_PADRAO
)

# Configuração da página
st.set_page_config(
    page_title="🤖 Chatbot Educacional",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar porta fixa para evitar conflitos
import os
os.environ['STREAMLIT_SERVER_PORT'] = '8501'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 1em;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
</style>
""", unsafe_allow_html=True)

def inicializar_chatbot(tema):
    """Inicializa ou reinicializa o chatbot com o tema selecionado."""
    if 'chatbot' not in st.session_state or st.session_state.get('tema_atual') != tema:
        with st.spinner(f"Inicializando chatbot para {tema.capitalize()}..."):
            try:
                modo_simulado = not bool(os.getenv('GOOGLE_API_KEY'))
                st.session_state.chatbot = ChatbotEducacional(tema, modo_simulado)
                st.session_state.tema_atual = tema
                st.session_state.mensagens = []

                # Mensagem de boas-vindas
                status = " (MODO SIMULADO)" if modo_simulado else " (Gemini 2.5 Pro)"
                mensagem_boas_vindas = f"Olá! Sou seu assistente educacional especializado em {tema.capitalize()}.{status} 💡"
                st.session_state.mensagens.append({"role": "assistant", "content": mensagem_boas_vindas})

            except Exception as e:
                st.error(f"Erro ao inicializar chatbot: {e}")
                return False
    return True

def enviar_mensagem():
    """Processa o envio de uma mensagem pelo usuário."""
    if st.session_state.user_input and st.session_state.user_input.strip():
        pergunta = st.session_state.user_input.strip()

        # Adiciona pergunta do usuário ao histórico
        st.session_state.mensagens.append({"role": "user", "content": pergunta})

        # Processa resposta do chatbot
        with st.spinner("🤔 Pensando..."):
            try:
                resposta = st.session_state.chatbot.obter_resposta_llm(pergunta)
                st.session_state.mensagens.append({"role": "assistant", "content": resposta})
            except Exception as e:
                resposta_erro = f"Desculpe, ocorreu um erro: {e}"
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_erro})

        # Limpa o campo de entrada
        st.session_state.user_input = ""

def limpar_conversa():
    """Limpa o histórico de conversa."""
    if 'mensagens' in st.session_state:
        # Mantém apenas a mensagem de boas-vindas
        if st.session_state.mensagens:
            boas_vindas = st.session_state.mensagens[0]
            st.session_state.mensagens = [boas_vindas]
        else:
            st.session_state.mensagens = []

def main():
    """
    Função principal da interface web.
    """

    # Título e descrição
    st.markdown('<h1 class="main-header">🎓 Chatbot Educacional</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Aprenda de forma interativa com IA especializada em diferentes temas educacionais</p>', unsafe_allow_html=True)

    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")

        # Seleção de tema
        tema_options = {
            "biologia": "🧬 Biologia",
            "matematica": "🔢 Matemática",
            "fisica": "⚡ Física",
            "historia": "📚 História"
        }

        tema_selecionado = st.selectbox(
            "Selecione o tema educacional:",
            options=list(tema_options.keys()),
            format_func=lambda x: tema_options[x],
            key="tema_selector"
        )

        # Inicializar chatbot com tema selecionado
        if not inicializar_chatbot(tema_selecionado):
            st.error("Falha ao inicializar o chatbot.")
            return

        st.divider()

        # Informações do tema
        st.subheader(f"📖 Sobre {tema_options[tema_selecionado].split()[1]}")
        tema_descricao = {
            "biologia": "Explore o mundo dos seres vivos, células, ecossistemas e evolução.",
            "matematica": "Aprenda cálculos, geometria, álgebra e resolução de problemas.",
            "fisica": "Entenda leis físicas, movimento, energia e fenômenos naturais.",
            "historia": "Descubra eventos históricos, civilizações e contextos temporais."
        }
        st.write(tema_descricao[tema_selecionado])

        # Status da API
        api_status = "✅ Gemini 2.5 Pro" if os.getenv('GOOGLE_API_KEY') else "⚠️ Modo Simulado"
        st.info(f"**Status:** {api_status}")

        st.divider()

        # Botão para limpar conversa
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            limpar_conversa()
            st.rerun()

        st.divider()

        # Informações técnicas
        with st.expander("ℹ️ Sobre"):
            st.write("**Interface:** web_app.py")
            st.write("**Framework:** Streamlit")
            st.write("**IA:** Google Gemini 2.5 Pro")

    # Área principal - Chat
    st.subheader("💬 Conversa")

    # Container do chat
    chat_container = st.container()

    with chat_container:
        if 'mensagens' in st.session_state:
            for mensagem in st.session_state.mensagens:
                if mensagem["role"] == "user":
                    # Mensagem do usuário (alinhada à direita)
                    col1, col2 = st.columns([1, 3])
                    with col2:
                        st.markdown(f"**👤 Você:** {mensagem['content']}")
                        st.markdown("---")
                else:
                    # Mensagem do bot (alinhada à esquerda)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**🤖 Chatbot:** {mensagem['content']}")
                        st.markdown("---")
        else:
            st.info("💡 Selecione um tema na barra lateral e comece a conversar!")

    # Campo de entrada
    st.markdown("---")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.text_input(
            "Digite sua pergunta:",
            key="user_input",
            placeholder="Ex: O que é uma célula? (biologia) ou Como calcular área de um círculo? (matemática)",
            on_change=enviar_mensagem,
            label_visibility="collapsed"
        )

    with col2:
        if st.button("📤 Enviar", use_container_width=True):
            enviar_mensagem()
            st.rerun()

if __name__ == "__main__":
    main()
