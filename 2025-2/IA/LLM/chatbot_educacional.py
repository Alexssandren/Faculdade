#!/usr/bin/env python3
"""
Chatbot Educacional Completo - Arquivo Único

Este arquivo contém tudo necessário para executar o chatbot educacional:
- Configurações e constantes
- Classe do chatbot
- Interface web (se executado com --web)
- Modo terminal (execução padrão)

Uso:
- Terminal: python chatbot_educacional.py [tema]
- Web: python chatbot_educacional.py --web [tema]
- Simulado: python chatbot_educacional.py --simulado [tema]
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

# Configurações gerais
CONFIGURACAO = {
    "modelo": "gemini-2.0-flash-exp",  # Modelo Gemini a ser usado
    "generation_config": {
        "max_output_tokens": 500,    # Máximo de tokens na resposta
        "temperature": 0.7,          # Criatividade vs precisão (0.0-2.0)
        "top_p": 0.8,                # Nucleus sampling
        "top_k": 10,                 # Top-k sampling
    },
    "comando_sair": ["sair", "exit", "quit"]  # Comandos para encerrar
}

# Contextos educacionais disponíveis
CONTEXTOS_EDUCACIONAIS = {
    "biologia": """
    Você é um chatbot educacional especializado em Biologia.
    Suas respostas devem ser:
    - Claras e objetivas, adequadas para estudantes de nível médio
    - Didáticas e explicativas, com exemplos quando relevante
    - Limitadas a até 3 parágrafos quando possível
    - Sempre verdadeiras e baseadas em conhecimento científico atual
    - Inclua analogias simples quando explicar conceitos complexos
    """,

    "matematica": """
    Você é um chatbot educacional especializado em Matemática.
    Suas respostas devem ser:
    - Claras e objetivas, adequadas para estudantes de nível médio
    - Didáticas com resolução passo-a-passo quando necessário
    - Limitadas a até 3 parágrafos quando possível
    - Sempre corretas matematicamente
    - Inclua exemplos numéricos práticos
    """,

    "fisica": """
    Você é um chatbot educacional especializado em Física.
    Suas respostas devem ser:
    - Claras e objetivas, adequadas para estudantes de nível médio
    - Didáticas com explicações conceituais e fórmulas quando relevante
    - Limitadas a até 3 parágrafos quando possível
    - Sempre baseadas em princípios físicos corretos
    - Inclua analogias do dia-a-dia quando possível
    """,

    "historia": """
    Você é um chatbot educacional especializado em História.
    Suas respostas devem ser:
    - Claras e objetivas, adequadas para estudantes de nível médio
    - Didáticas com contexto histórico e cronologia quando relevante
    - Limitadas a até 3 parágrafos quando possível
    - Sempre baseadas em fatos históricos verificados
    - Inclua conexões com o presente quando apropriado
    """
}

# Tema padrão
TEMA_PADRAO = "biologia"

# =============================================================================
# CLASSE DO CHATBOT
# =============================================================================

class ChatbotEducacional:
    """
    Classe principal do chatbot educacional.
    Gerencia a interação com o usuário e a comunicação com o LLM.
    """

    def __init__(self, tema=None, modo_simulado=False):
        """
        Inicializa o chatbot com as configurações necessárias.

        Args:
            tema (str): Tema educacional desejado
            modo_simulado (bool): Se True, usa respostas pré-programadas
        """
        self.modo_simulado = modo_simulado

        # Define o tema educacional
        self.tema = tema or TEMA_PADRAO
        if self.tema not in CONTEXTOS_EDUCACIONAIS:
            print(f"Tema '{self.tema}' não encontrado. Usando tema padrão: {TEMA_PADRAO}")
            self.tema = TEMA_PADRAO

        # Configurações do modelo
        self.config = CONFIGURACAO

        if not modo_simulado:
            # Modo real com API
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                print("Erro: Chave da API não encontrada. Configure GOOGLE_API_KEY no arquivo .env")
                print("Para usar modo simulado: python chatbot_educacional.py --simulado")
                sys.exit(1)

            try:
                import google.generativeai as genai

                # Configura a API do Google Gemini
                genai.configure(api_key=self.api_key)

                # Inicializa o modelo Gemini
                self.model = genai.GenerativeModel(
                    model_name=self.config["modelo"],
                    generation_config=self.config["generation_config"]
                )

                # Inicia o chat com o contexto educacional
                self.chat = self.model.start_chat(history=[])

                # Envia a instrução inicial do contexto educacional
                self.chat.send_message(CONTEXTOS_EDUCACIONAIS[self.tema])

            except ImportError:
                print("Erro: Biblioteca google-generativeai não instalada.")
                print("Instale com: pip install google-generativeai")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao conectar com Gemini: {e}")
                print("Usando modo simulado...")
                self.modo_simulado = True

        # Contador de perguntas (para modo simulado)
        self.perguntas_respondidas = 0

        print(f"Chatbot Educacional - Tema: {self.tema.capitalize()}")
        if self.modo_simulado:
            print("Modo simulado - respostas pré-programadas")
        else:
            print("Gemini 2.5 Pro ativado")
        print("Digite 'sair' para encerrar a conversa")
        print("-" * 50)

    def obter_resposta_simulada(self, pergunta):
        """
        Retorna respostas simuladas baseadas em palavras-chave.
        """
        pergunta_lower = pergunta.lower()
        self.perguntas_respondidas += 1

        # Respostas simuladas baseadas em temas
        if self.tema == "biologia":
            if "celula" in pergunta_lower:
                return "Uma célula é a unidade básica da vida. Existem células procariotas (sem núcleo definido, como bactérias) e eucariotas (com núcleo, como células animais e vegetais). As células realizam todas as funções necessárias para manter a vida."
            elif "dna" in pergunta_lower:
                return "O DNA (ácido desoxirribonucleico) é a molécula que contém as instruções genéticas para o desenvolvimento e funcionamento de todos os seres vivos. É formado por nucleotídeos e tem formato de dupla hélice."
            elif "evolucao" in pergunta_lower:
                return "A evolução biológica é o processo pelo qual as espécies mudam ao longo do tempo através de mecanismos como seleção natural, mutação e deriva genética, conforme proposto por Charles Darwin."
            else:
                return "Esta é uma pergunta interessante sobre Biologia! Em um ambiente real, eu consultaria minha base de conhecimento atualizada para dar a resposta mais precisa e didática possível."

        elif self.tema == "matematica":
            if "equacao" in pergunta_lower or "2x" in pergunta_lower:
                return "Para resolver uma equação linear como 2x + 3 = 7: subtraia 3 dos dois lados: 2x = 4. Divida por 2: x = 2. Verificação: 2×2 + 3 = 7"
            elif "derivada" in pergunta_lower:
                return "A derivada representa a taxa de variação instantânea de uma função. Para f(x) = x², a derivada é f'(x) = 2x. Isso indica quão rápido a função está crescendo em cada ponto."
            else:
                return "Esta é uma questão matemática interessante! Eu ajudaria passo a passo, com exemplos numéricos e explicações conceituais claras."

        elif self.tema == "fisica":
            if "gravidade" in pergunta_lower:
                return "A gravidade é a força que atrai objetos com massa um para o outro. Na Terra, a aceleração da gravidade é aproximadamente 9,8 m/s². Quanto maior a massa, maior a força gravitacional."
            elif "energia" in pergunta_lower:
                return "A energia é a capacidade de realizar trabalho. Existem vários tipos: cinética (movimento), potencial (posição), térmica (calor), elétrica, etc. A primeira lei da termodinâmica diz que energia não se cria nem se destrói, apenas se transforma."
            else:
                return "Questão física interessante! Eu explicaria com princípios fundamentais, fórmulas relevantes e exemplos práticos do dia a dia."

        elif self.tema == "historia":
            if "segunda guerra" in pergunta_lower:
                return "A Segunda Guerra Mundial (1939-1945) foi o conflito mais devastador da história, envolvendo a maioria dos países do mundo. Foi travada entre os Aliados (EUA, Reino Unido, URSS, etc.) e o Eixo (Alemanha, Itália, Japão)."
            elif "revolucao" in pergunta_lower and "francesa" in pergunta_lower:
                return "A Revolução Francesa (1789-1799) foi um período de mudanças radicais que aboliu a monarquia absoluta e estabeleceu princípios democráticos. Influenciou movimentos revolucionários em todo o mundo."
            else:
                return "Esta é uma pergunta histórica fascinante! Eu contextualizaria com datas importantes, causas, consequências e conexões com o presente."

        return "Sua pergunta é muito interessante! Em um ambiente real, eu forneceria uma resposta completa e didática baseada no conhecimento mais atualizado disponível."

    def obter_resposta_llm(self, pergunta):
        """
        Envia a pergunta para o modelo LLM e retorna a resposta.

        Args:
            pergunta (str): Pergunta do usuário

        Returns:
            str: Resposta do modelo LLM
        """
        if self.modo_simulado:
            return self.obter_resposta_simulada(pergunta)

        try:
            # Envia a pergunta para o chat do Gemini
            resposta = self.chat.send_message(pergunta)

            # Extrai o texto da resposta
            resposta_texto = resposta.text

            return resposta_texto

        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {e}"

    def iniciar_conversa_terminal(self):
        """
        Inicia o loop principal de conversa no terminal.
        """
        while True:
            try:
                # Recebe a entrada do usuário
                entrada = input("Voce: ").strip()

                # Verifica se o usuário quer encerrar
                if entrada.lower() in self.config["comando_sair"]:
                    print("Ate logo! Foi um prazer ajudar nos seus estudos!")
                    break

                # Verifica se a entrada não está vazia
                if not entrada:
                    print(f"Por favor, digite uma pergunta sobre {self.tema.capitalize()}.")
                    continue

                # Mostra que está processando
                print("Pensando...")

                # Obtém resposta do LLM
                resposta = self.obter_resposta_llm(entrada)

                # Exibe a resposta
                print(f"Chatbot: {resposta}")
                print("-" * 50)

            except KeyboardInterrupt:
                print("\nConversa interrompida. Ate logo!")
                break
            except Exception as e:
                print(f"Erro inesperado: {str(e)}")
                continue

# =============================================================================
# INTERFACE WEB (STREAMLIT)
# =============================================================================

def criar_interface_web(tema_inicial=None):
    """
    Cria e executa a interface web usando Streamlit.
    """
    try:
        import streamlit as st
    except ImportError:
        print("Erro: Streamlit não instalado. Instale com: pip install streamlit")
        return

    # Configuração da página
    st.set_page_config(
        page_title="Chatbot Educacional",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )

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
                    mensagem_boas_vindas = f"Olá! Sou seu assistente educacional especializado em {tema.capitalize()}.{status}"
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

    # Título e descrição
    st.markdown('<h1 class="main-header">Chatbot Educacional</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Aprenda de forma interativa com IA especializada em diferentes temas educacionais</p>', unsafe_allow_html=True)

    # Sidebar para configurações
    with st.sidebar:
        st.header("Configuracoes")

        # Seleção de tema
        tema_options = {
            "biologia": "Biologia",
            "matematica": "Matematica",
            "fisica": "Fisica",
            "historia": "Historia"
        }

        tema_selecionado = st.selectbox(
            "Selecione o tema educacional:",
            options=list(tema_options.keys()),
            format_func=lambda x: tema_options[x],
            index=list(tema_options.keys()).index(tema_inicial) if tema_inicial and tema_inicial in tema_options else 0,
            key="tema_selector"
        )

        # Inicializar chatbot com tema selecionado
        if not inicializar_chatbot(tema_selecionado):
            st.error("Falha ao inicializar o chatbot.")
            return

        st.divider()

        # Informações do tema
        st.subheader(f"Sobre {tema_options[tema_selecionado]}")
        tema_descricao = {
            "biologia": "Explore o mundo dos seres vivos, células, ecossistemas e evolução.",
            "matematica": "Aprenda cálculos, geometria, álgebra e resolução de problemas.",
            "fisica": "Entenda leis físicas, movimento, energia e fenômenos naturais.",
            "historia": "Descubra eventos históricos, civilizações e contextos temporais."
        }
        st.write(tema_descricao[tema_selecionado])

        # Status da API
        api_status = "Gemini 2.5 Pro" if os.getenv('GOOGLE_API_KEY') else "Modo Simulado"
        st.info(f"**Status:** {api_status}")

        st.divider()

        # Botão para limpar conversa
        if st.button("Limpar Conversa", use_container_width=True):
            limpar_conversa()
            st.rerun()

        st.divider()

        # Informações técnicas
        with st.expander("Sobre"):
            st.write("**Arquivo único:** chatbot_educacional.py")
            st.write("**Interface:** Streamlit")
            st.write("**IA:** Google Gemini 2.5 Pro")

    # Área principal - Chat
    st.subheader("Conversa")

    # Container do chat
    chat_container = st.container()

    with chat_container:
        if 'mensagens' in st.session_state:
            for mensagem in st.session_state.mensagens:
                if mensagem["role"] == "user":
                    # Mensagem do usuário (alinhada à direita)
                    col1, col2 = st.columns([1, 3])
                    with col2:
                        st.markdown(f"**Voce:** {mensagem['content']}")
                        st.markdown("---")
                else:
                    # Mensagem do bot (alinhada à esquerda)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Chatbot:** {mensagem['content']}")
                        st.markdown("---")
        else:
            st.info("Selecione um tema na barra lateral e comece a conversar!")

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
        if st.button("Enviar", use_container_width=True):
            enviar_mensagem()
            st.rerun()

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """
    Função principal - Inicializa interface web por padrão.
    """
    parser = argparse.ArgumentParser(description='Chatbot Educacional')
    parser.add_argument('--terminal', action='store_true', help='Executa modo terminal')
    parser.add_argument('--simulado', action='store_true', help='Força modo simulado (terminal)')
    parser.add_argument('tema', nargs='?', default=TEMA_PADRAO,
                       choices=list(CONTEXTOS_EDUCACIONAIS.keys()),
                       help='Tema educacional')

    args = parser.parse_args()

    if args.terminal:
        # Modo terminal explícito
        try:
            modo_simulado = args.simulado or not bool(os.getenv('GOOGLE_API_KEY'))
            chatbot = ChatbotEducacional(args.tema, modo_simulado)
            chatbot.iniciar_conversa_terminal()

        except KeyboardInterrupt:
            print("\nAte logo!")
        except Exception as e:
            print(f"Erro ao iniciar chatbot: {e}")
            sys.exit(1)
    else:
        # Modo interface web (padrão)
        print("Iniciando Interface Web...")
        print("")
        print("Para usar a interface web, execute um dos comandos abaixo:")
        print("")
        print("   Opcao 1 (Recomendada - Python module):")
        print(f"      python -m streamlit run {__file__}")
        print("")
        print("   Opcao 2 (Arquivo direto):")
        print("      python web_app.py")
        print("")
        print("   Opcao 3 (Com tema especifico):")
        print(f"      python -m streamlit run {__file__} matematica")
        print("")
        print("A interface web abrira em: http://localhost:8501 (porta fixa)")
        print("")
        print("Para usar o modo terminal:")
        print("      python chatbot_educacional.py --terminal")
        print("")
        sys.exit(0)

# =============================================================================
# DETECÇÃO DE EXECUÇÃO PELO STREAMLIT
# =============================================================================

def detectar_streamlit():
    """
    Detecta se o arquivo está sendo executado pelo Streamlit.
    """
    import sys
    import os

    # Verificar se há argumentos do streamlit
    if len(sys.argv) > 1 and sys.argv[1] in ['run', 'hello']:
        return True

    # Verificar variáveis de ambiente do Streamlit
    if 'STREAMLIT_SERVER_PORT' in os.environ:
        return True

    # Verificar se foi chamado por streamlit (não diretamente por python)
    if hasattr(sys, '_getframe'):
        frame = sys._getframe(1)
        if frame and 'streamlit' in str(frame.f_code.co_filename).lower():
            return True

    return False

if __name__ == "__main__":
    # Verificar se está sendo executado pelo Streamlit ou se deve executar interface web
    # Se não há argumentos específicos de terminal, executar interface web
    if detectar_streamlit() or (len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] not in ['--terminal', '--simulado'])):
        # Executar interface web diretamente usando o código do web_app.py
        try:
            import streamlit as st
            import os
            import sys

            # Adiciona o diretório atual ao path (mesmo que web_app.py faz)
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            # Configuração da página (igual ao web_app.py)
            st.set_page_config(
                page_title="Chatbot Educacional",
                page_icon=None,
                layout="wide",
                initial_sidebar_state="expanded"
            )

            # Configurar porta fixa para evitar conflitos
            os.environ['STREAMLIT_SERVER_PORT'] = '8501'
            os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

            # Estilos CSS personalizados (igual ao web_app.py)
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

            # Funções auxiliares (copiadas do web_app.py)
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
                            mensagem_boas_vindas = f"Olá! Sou seu assistente educacional especializado em {tema.capitalize()}.{status}"
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

            # Interface principal (igual ao web_app.py)
            # Título e descrição
            st.markdown('<h1 class="main-header">Chatbot Educacional</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Aprenda de forma interativa com IA especializada em diferentes temas educacionais</p>', unsafe_allow_html=True)

            # Sidebar para configurações
            with st.sidebar:
                st.header("Configuracoes")

                # Seleção de tema
                tema_options = {
                    "biologia": "Biologia",
                    "matematica": "Matematica",
                    "fisica": "Fisica",
                    "historia": "Historia"
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
                    st.stop()

                st.divider()

                # Informações do tema
                st.subheader(f"Sobre {tema_options[tema_selecionado]}")
                tema_descricao = {
                    "biologia": "Explore o mundo dos seres vivos, células, ecossistemas e evolução.",
                    "matematica": "Aprenda cálculos, geometria, álgebra e resolução de problemas.",
                    "fisica": "Entenda leis físicas, movimento, energia e fenômenos naturais.",
                    "historia": "Descubra eventos históricos, civilizações e contextos temporais."
                }
                st.write(tema_descricao[tema_selecionado])

                # Status da API
                api_status = "Gemini 2.5 Pro" if os.getenv('GOOGLE_API_KEY') else "Modo Simulado"
                st.info(f"**Status:** {api_status}")

                st.divider()

                # Botão para limpar conversa
                if st.button("Limpar Conversa", use_container_width=True):
                    limpar_conversa()
                    st.rerun()

                st.divider()

                # Informações técnicas
                with st.expander("Sobre"):
                    st.write("**Arquivo único:** chatbot_educacional.py")
                    st.write("**Interface:** Streamlit")
                    st.write("**IA:** Google Gemini 2.5 Pro")

            # Área principal - Chat
            st.subheader("Conversa")

            # Container do chat
            chat_container = st.container()

            with chat_container:
                if 'mensagens' in st.session_state:
                    for mensagem in st.session_state.mensagens:
                        if mensagem["role"] == "user":
                            # Mensagem do usuário (alinhada à direita)
                            col1, col2 = st.columns([1, 3])
                            with col2:
                                st.markdown(f"**Voce:** {mensagem['content']}")
                                st.markdown("---")
                        else:
                            # Mensagem do bot (alinhada à esquerda)
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Chatbot:** {mensagem['content']}")
                                st.markdown("---")
                else:
                    st.info("Selecione um tema na barra lateral e comece a conversar!")

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
                if st.button("Enviar", use_container_width=True):
                    enviar_mensagem()
                    st.rerun()

        except ImportError:
            print("Erro: Streamlit não encontrado. Instale com: pip install streamlit")
            sys.exit(1)
    else:
        # Executar lógica normal (terminal ou instruções)
        main()
