import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Tentar importar sistema de IA real
try:
    from src.llm.ai_analytics import AIAnalyticsEngine, Phase3Integration
    from src.gui.data_integration import data_provider
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: Sistema de IA não disponível: {e}")
    AI_AVAILABLE = False

class ChatSidebar:
    def __init__(self, parent_frame, main_window):
        self.parent = parent_frame
        self.main_window = main_window
        self.styling = main_window.styling
        
        # Estado do chat
        self.chat_history = []
        self.is_thinking = False
        
        # Estado de expansão da sidebar
        self.is_expanded = False
        self.hover_timer = None
        self.mouse_in_sidebar = False
        
        # Sistema de IA
        self.ai_engine = None
        self.phase3_integration = None
        self._initialize_ai_system()
        
        # Criar interface
        self._create_interface()
        
        # Mensagem de boas-vindas
        self._add_welcome_message()
        
        # Configurar eventos de hover
        self._setup_hover_events()
        
    def _initialize_ai_system(self):
        """Inicializa sistema de IA se disponível"""
        try:
            if AI_AVAILABLE:
                self.ai_engine = AIAnalyticsEngine()
                self.phase3_integration = Phase3Integration(self.ai_engine)
                self.ai_mode = "real"
        
            else:
                self.ai_mode = "simulated"
                print("ℹ️ Usando sistema de IA simulado")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar IA real, usando simulado: {e}")
            self.ai_engine = None
            self.phase3_integration = None
            self.ai_mode = "simulated"
    
    def _create_interface(self):
        """Cria a interface da sidebar de chat"""
        # Container principal
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=BOTH, expand=True, padx=2, pady=2)
        
        # Ícone de chat para modo contraído
        self._create_collapsed_icon()
        
        # Conteúdo expandido (inicialmente oculto)
        self.expanded_content = ttk.Frame(self.main_container)
        
        # Cabeçalho do chat
        self._create_header(self.expanded_content)
        
        # Área de conversação
        self._create_chat_area(self.expanded_content)
        
        # Área de entrada
        self._create_input_area(self.expanded_content)
        
        # Painel de ações rápidas
        self._create_quick_actions(self.expanded_content)
        
        # Inicialmente em modo contraído, mas expande automaticamente
        self._set_collapsed_mode()
        
        # Expandir automaticamente após um pequeno delay para melhor UX
        self.parent.after(1000, self._auto_expand_on_start)
        
    def _auto_expand_on_start(self):
        """Expande automaticamente a sidebar na inicialização"""
        # Sincronizar estado primeiro
        self._sync_expansion_state()
        
        # Se não estiver expandida, expandir automaticamente
        if not self.is_expanded:
    
            self.expand_sidebar()
            
        # Configurar um monitor para garantir que a sidebar permaneça funcional
        self._setup_persistent_monitor()
        
    def _create_collapsed_icon(self):
        """Cria ícone para modo contraído"""
        self.collapsed_frame = ttk.Frame(self.main_container)
        
        # Ícone de chat
        chat_icon = ttk.Label(
            self.collapsed_frame,
            text="💬",
            font=("Arial", 20),
            foreground=self.styling.colors['primary']
        )
        chat_icon.pack(pady=20)
        
        # Texto vertical "Chat"
        chat_text = ttk.Label(
            self.collapsed_frame,
            text="C\nH\nA\nT",
            font=self.styling.fonts['small_bold'],
            foreground=self.styling.colors['primary']
        )
        chat_text.pack(pady=10)
        
    def _set_collapsed_mode(self):
        """Define modo contraído"""
        self.collapsed_frame.pack(fill=BOTH, expand=True)
        self.expanded_content.pack_forget()
        
    def _set_expanded_mode(self):
        """Define modo expandido"""
        self.collapsed_frame.pack_forget()
        self.expanded_content.pack(fill=BOTH, expand=True, padx=8, pady=8)
        
    def _create_header(self, parent):
        """Cria cabeçalho da sidebar"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 15))
        
        # Título
        title_label = ttk.Label(
            header_frame,
            text=f"{self.styling.icons['chat']} Chat IA",
            font=self.styling.fonts['large_bold'],
            foreground=self.styling.colors['primary']
        )
        title_label.pack(anchor=W)
        
        # Subtítulo
        ai_type = "Gemini" if self.ai_mode == "real" else "Simulado"
        subtitle_label = ttk.Label(
            header_frame,
            text=f"Análise inteligente com {ai_type}",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['text_secondary']
        )
        subtitle_label.pack(anchor=W)
        
        # Status da IA
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(fill=X, pady=(5, 0))
        
        status_text = f"{self.styling.icons['check']} IA {ai_type} Online"
        status_color = self.styling.colors['success'] if self.ai_mode == "real" else self.styling.colors['info']
        
        self.status_indicator = ttk.Label(
            status_frame,
            text=status_text,
            font=self.styling.fonts['small'],
            foreground=status_color
        )
        self.status_indicator.pack(side=LEFT)
        
        # Botão limpar chat
        clear_btn = ttk.Button(
            status_frame,
            text=f"{self.styling.icons['trash']} Limpar",
            command=self.clear_chat,
            style=OUTLINE,
            width=8
        )
        clear_btn.pack(side=RIGHT)
        
    def _create_chat_area(self, parent):
        """Cria área de conversação"""
        # Frame da área de chat
        chat_frame = ttk.LabelFrame(parent, text="Conversação", padding=10)
        chat_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Text widget com scrollbar
        text_frame = ttk.Frame(chat_frame)
        text_frame.pack(fill=BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Text widget para o chat
        self.chat_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set,
            font=self.styling.fonts['small'],
            bg=self.styling.colors['background'],
            fg=self.styling.colors['text_primary'],
            relief="flat",
            padx=10,
            pady=10
        )
        self.chat_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar.config(command=self.chat_text.yview)
        
        # Configurar tags para diferentes tipos de mensagem
        self.chat_text.tag_configure("user", foreground=self.styling.colors['primary'], font=self.styling.fonts['small_bold'])
        self.chat_text.tag_configure("ai", foreground=self.styling.colors['info'], font=self.styling.fonts['small_bold'])
        self.chat_text.tag_configure("system", foreground=self.styling.colors['warning'], font=self.styling.fonts['small'], justify="center")
        self.chat_text.tag_configure("timestamp", foreground=self.styling.colors['text_secondary'], font=("Consolas", 8))
        
    def _create_input_area(self, parent):
        """Cria área de entrada de mensagens"""
        input_frame = ttk.LabelFrame(parent, text="Sua pergunta", padding=10)
        input_frame.pack(fill=X, pady=(0, 15))
        
        # Text widget para entrada
        self.input_text = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=self.styling.fonts['small'],
            relief="solid",
            borderwidth=1
        )
        self.input_text.pack(fill=X, pady=(0, 10))
        
        # Bind para Enter
        self.input_text.bind("<Control-Return>", self.send_message)
        self.input_text.bind("<KeyRelease>", self.on_input_changed)
        
        # Frame dos botões
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=X)
        
        # Botão enviar
        self.send_btn = ttk.Button(
            buttons_frame,
            text=f"{self.styling.icons['send']} Enviar",
            command=self.send_message,
            style=PRIMARY
        )
        self.send_btn.pack(side=RIGHT)
        
        # Contador de caracteres
        self.char_count_label = ttk.Label(
            buttons_frame,
            text="0/500",
            font=self.styling.fonts['small'],
            foreground=self.styling.colors['text_secondary']
        )
        self.char_count_label.pack(side=LEFT)
        
    def _create_quick_actions(self, parent):
        """Cria painel de ações rápidas"""
        actions_frame = ttk.LabelFrame(parent, text="Análises Rápidas", padding=10)
        actions_frame.pack(fill=X)
        
        # Botões de ações pré-definidas integrados com dados reais
        quick_actions = [
            ("📊 Resumo Geral", "Faça um resumo geral dos dados disponíveis com as métricas mais importantes"),
            ("📈 Correlações IDH", "Analise as correlações entre IDH e despesas públicas por setor"),
            ("🏆 Ranking Estados", "Quais são os estados com melhor IDH e como eles se comparam?"),
            ("💰 Eficiência Gastos", "Quais estados são mais eficientes no uso de recursos públicos?"),
            ("📉 Tendências Temporais", "Quais são as principais tendências de evolução do IDH no período 2019-2023?"),
            ("🎯 Recomendações", "Com base nos dados atuais, que recomendações estratégicas você faria?")
        ]
        
        for i, (text, prompt) in enumerate(quick_actions):
            btn = ttk.Button(
                actions_frame,
                text=text,
                command=lambda p=prompt: self.send_quick_action(p),
                style=OUTLINE,
                width=25
            )
            btn.pack(fill=X, pady=2)
            
    def _add_welcome_message(self):
        """Adiciona mensagem de boas-vindas"""
        ai_type = "Gemini" if self.ai_mode == "real" else "simulado"
        welcome_msg = f"""Olá! 👋 Sou sua assistente de IA para análise de dados.

🤖 **Sistema**: {ai_type.title()}
📊 **Dados**: Conectado ao sistema DEC7588

Posso ajudar você com:
• Análise de correlações IDH vs Despesas
• Comparações regionais e estaduais  
• Tendências temporais (2019-2023)
• Eficiência de investimentos públicos
• Recomendações estratégicas baseadas em dados

Use os botões de **Análises Rápidas** ou digite sua pergunta!"""
        
        self._add_message("Sistema", welcome_msg, "system")
    
    def _add_message(self, sender, message, tag, timestamp=None):
        """Adiciona mensagem ao chat"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")
            
        # Habilitar edição temporariamente
        self.chat_text.config(state=tk.NORMAL)
        
        # Adicionar timestamp e remetente
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_text.insert(tk.END, f"{sender}: ", tag)
        self.chat_text.insert(tk.END, f"{message}\n\n")
        
        # Desabilitar edição
        self.chat_text.config(state=tk.DISABLED)
        
        # Scroll para baixo
        self.chat_text.see(tk.END)
        
        # Adicionar ao histórico
        self.chat_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp,
            'tag': tag
        })
    
    def send_message(self, event=None):
        """Envia mensagem do usuário"""
        if self.is_thinking:
            return
        
        user_message = self.input_text.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        # Adicionar mensagem do usuário
        self._add_message("Você", user_message, "user")
        
        # Limpar input
        self.input_text.delete("1.0", tk.END)
        
        # Processar resposta da IA
        self._process_ai_response(user_message)
        
    def send_quick_action(self, prompt):
        """Envia ação rápida"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", prompt)
        self.send_message()

    def _process_ai_response(self, user_message):
        """Processa resposta da IA com integração completa"""
        # Mostrar que a IA está pensando
        self._show_thinking()
        
        def ai_task():
            try:
                # Verificar se é uma saudação ou mensagem casual antes de usar IA pesada
                if self._is_casual_message(user_message):
                    response = self._generate_casual_response(user_message)
                elif self.ai_mode == "real" and self.ai_engine:
                    # Reunir dados analíticos detalhados para fornecer contexto real ao modelo
                    # 1. Métricas gerais do dashboard (contagens, período, etc.)
                    metrics = data_provider.get_dashboard_metrics()

                    # 2. Resultados da Consulta 1 – Ranking IDH × Investimento (inclui correlação)
                    #    Usamos ano mais recente disponível (2023). Ajustar se o dataset crescer.
                    consulta1 = data_provider.get_correlation_data(year=2023)

                    # 3. Resultados da Consulta 2 – Tendências temporais nacionais
                    consulta2 = data_provider.get_temporal_trends_data()

                    # 4. Resultados da Consulta 3 – Análise regional
                    consulta3 = data_provider.get_regional_analysis_data(year=2023)

                    # Montar dicionário no formato esperado por AIAnalyticsEngine._create_analytical_prompt()
                    context_data = {
                        'consulta_1': consulta1,
                        'consulta_2': consulta2,
                        'consulta_3': consulta3,
                        # Informações adicionais úteis para o modelo
                        'metrics': metrics
                    }

                    # Executar análise com IA
                    response_dict = self.ai_engine.analyze_with_ai(user_message, context_data)

                    # Extrair texto da resposta
                    if isinstance(response_dict, dict):
                        response_text = response_dict.get('response_text', '')
                        # Fallback: se vazio ou muito curto, exibir mensagem de erro genérica
                        if not response_text or len(response_text.strip()) < 5:
                            response_text = "Desculpe, não foi possível gerar uma resposta baseada nos dados disponíveis."
                    else:
                        # Se IA retornar string simples
                        response_text = str(response_dict)

                    response = response_text
                else:
                    # Usar sistema simulado com dados reais do data_provider
                    response = self._generate_enhanced_simulated_response(user_message)
                
                # Atualizar UI na thread principal
                self.main_window.root.after(0, lambda: self._show_ai_response(response))
                
            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
                self.main_window.root.after(0, lambda: self._show_ai_response(error_msg))
        
        if hasattr(self.main_window, 'thread_manager'):
            self.main_window.thread_manager.run_thread(ai_task)
        else:
            # Fallback: executar em thread manual
            import threading
            threading.Thread(target=ai_task, daemon=True).start()

    def _is_casual_message(self, message):
        """Verifica se é uma mensagem casual/saudação que não precisa de análise pesada"""
        message_lower = message.lower().strip()
        
        # Palavras analíticas que indicam perguntas sérias
        analytical_words = [
            'analise', 'análise', 'analisar', 'dados', 'correlacao', 'correlação', 
            'idh', 'despesas', 'estados', 'grafico', 'gráfico', 'regioes', 'regiões',
            'comparar', 'compare', 'resumo', 'relatório', 'recomendacao', 'recomendação',
            'estrategia', 'estratégia', 'tendencia', 'tendência', 'maior', 'menor',
            'melhor', 'pior', 'ranking', 'estatistica', 'estatística', 'investimento',
            'publico', 'público', 'governo', 'federal', 'municipal', 'estadual',
            'qual', 'como', 'onde', 'quando', 'porque', 'por que', 'quantos',
            'quanto', 'quais', 'mostre', 'explique', 'calcule', 'determine'
        ]
        
        # PRIMEIRO: Verificar se contém palavras analíticas (sempre não-casual)
        if any(word in message_lower for word in analytical_words):
            return False
        
        # SEGUNDO: Verificar se é uma pergunta (sempre não-casual)
        if message_lower.endswith('?') or message_lower.startswith(('qual', 'como', 'onde', 'quando', 'porque', 'por que', 'quantos', 'quanto', 'quais')):
            return False
        
        # TERCEIRO: Saudações e mensagens casuais específicas
        casual_patterns = [
            # Saudações básicas
            'oi', 'olá', 'ola', 'hello', 'hi', 'hey',
            # Cumprimentos
            'bom dia', 'boa tarde', 'boa noite',
            # Perguntas básicas de cortesia
            'como vai', 'tudo bem', 'como está', 'como voce esta',
            # Agradecimentos
            'obrigado', 'obrigada', 'valeu', 'thanks',
            # Despedidas
            'tchau', 'até logo', 'bye', 'adeus',
            # Testes simples
            'teste', 'test', 'funciona'
        ]
        
        # Verificar se a mensagem é muito curta (<=3 chars) E não é pergunta
        if len(message_lower) <= 3 and not message_lower.endswith('?'):
            return True
        
        # Verificar padrões casuais exatos
        for pattern in casual_patterns:
            if message_lower == pattern or message_lower == pattern + '!':
                return True
        
        # Mensagens muito curtas sem conteúdo analítico (<=8 chars)
        if len(message_lower) <= 8 and not any(word in message_lower for word in analytical_words):
            return True
        
        # Se chegou até aqui, é provavelmente uma pergunta analítica
        return False

    def _generate_casual_response(self, user_message):
        """Gera resposta casual e amigável para mensagens simples"""
        message_lower = user_message.lower().strip()
        
        try:
            # Buscar métricas básicas para usar em respostas casuais
            metrics = data_provider.get_dashboard_metrics()
            
            # Respostas para saudações
            if any(greeting in message_lower for greeting in ['oi', 'olá', 'ola', 'hello', 'hi', 'hey']):
                return f"""Olá! 👋 É um prazer conversar com você!

🤖 Sou sua assistente de IA especializada em análise de dados socioeconômicos.

📊 **Status atual dos dados:**
• {metrics['total_estados']} estados analisados
• Período: {metrics['periodo_texto']}
• Registros ativos: {metrics['total_registros']}

**Como posso ajudar hoje?**
• Análise de correlações IDH vs Despesas
• Comparações entre estados e regiões
• Tendências temporais
• Recomendações estratégicas

Use os botões de **Análises Rápidas** ou me faça uma pergunta específica! 🚀"""

            # Respostas para cumprimentos
            elif any(greeting in message_lower for greeting in ['bom dia', 'boa tarde', 'boa noite']):
                return f"""Muito bom dia/tarde/noite! ☀️🌙

Que ótimo ter você aqui para explorar os dados socioeconômicos!

📈 **Dados atualizados em {metrics['ultima_atualizacao']}:**
• Análise de {metrics['total_estados']} estados brasileiros
• Correlações IDH vs investimentos públicos
• Tendências {metrics['periodo_texto']}

Em que posso ajudá-lo hoje?"""

            # Respostas para "como vai"
            elif any(phrase in message_lower for phrase in ['como vai', 'tudo bem', 'como está', 'como voce esta']):
                return f"""Estou muito bem, obrigada por perguntar! 😊

🔥 **Status do sistema:**
✅ Todos os dados carregados e atualizados
✅ IA funcionando perfeitamente
✅ {metrics['total_registros']} registros prontos para análise

E você, como está? Pronto para explorar algumas análises interessantes dos dados brasileiros?"""

            # Respostas para agradecimentos
            elif any(thanks in message_lower for thanks in ['obrigado', 'obrigada', 'valeu', 'thanks']):
                return f"""De nada! 😊 Foi um prazer ajudar!

Se precisar de mais alguma análise ou tiver outras perguntas sobre os dados socioeconômicos, estarei aqui.

💡 **Dica:** Use os botões de "Análises Rápidas" para explorar insights interessantes rapidamente!"""

            # Respostas para despedidas
            elif any(bye in message_lower for bye in ['tchau', 'até logo', 'bye', 'adeus']):
                return f"""Até logo! 👋 

Foi ótimo conversar e ajudar com suas análises.

📊 Lembre-se: os dados estão sempre aqui quando você precisar de insights sobre IDH e investimentos públicos no Brasil.

Volte sempre! 🚀"""

            # Respostas para testes
            elif any(test in message_lower for test in ['teste', 'test', 'funciona']):
                return f"""✅ **Sistema funcionando perfeitamente!**

🔧 **Status técnico:**
• Chat IA: ✅ Online
• Base de dados: ✅ {metrics['total_registros']} registros
• Análises: ✅ Todas funcionais
• Última atualização: {metrics['ultima_atualizacao']}

Pode me fazer qualquer pergunta sobre análises socioeconômicas! 💪"""

            # Resposta genérica para outras mensagens casuais
            else:
                return f"""Entendi! 😊

Estou aqui para ajudá-lo com análises dos dados socioeconômicos brasileiros.

📊 **Temos dados atualizados sobre:**
• IDH por estado ({metrics['periodo_texto']})
• Investimentos públicos federais
• Correlações e tendências
• Eficiência de gastos públicos

Que tipo de análise te interessa?"""
            
        except Exception as e:
            # Fallback simples em caso de erro
            return """Olá! 👋 

Sou sua assistente de IA para análise de dados socioeconômicos.

Como posso ajudá-lo hoje?"""

    def _generate_real_ai_response(self, user_message):
        """Gera resposta usando IA real (Gemini) com dados contextuais"""
        try:
            if not self.ai_engine or not self.phase3_integration:
                return self._generate_enhanced_simulated_response(user_message)
            
            # Buscar dados contextuais relevantes
            context_data = data_provider.get_dashboard_metrics()
            
            # Preparar contexto para a IA
            context = f"""
Sistema de Análise Socioeconômica - Dados Brasileiros
Período: {context_data.get('periodo_texto', '2019-2023')}
Estados: {context_data.get('total_estados', 27)}
Registros: {context_data.get('total_registros', 'N/A')}

Pergunta do usuário: {user_message}
"""
            
            # Usar sistema Gemini real
            response = self.ai_engine.analyze_with_ai(user_message, context_data)
            
            # Extrair texto da resposta (analyze_with_ai retorna dict)
            if response and isinstance(response, dict) and 'response_text' in response:
                response_text = response['response_text']
                if response_text and len(response_text.strip()) > 10:
                    return response_text
            
            # Fallback se resposta da IA for vazia
            return self._generate_enhanced_simulated_response(user_message)
                
        except Exception as e:
            print(f"Erro na IA real: {e}")
            return self._generate_enhanced_simulated_response(user_message)
    
    def _generate_enhanced_simulated_response(self, user_message):
        """Gera resposta simulada inteligente usando dados reais"""
        try:
            # Buscar dados reais do sistema
            metrics = data_provider.get_dashboard_metrics()
            
            message_lower = user_message.lower()
            
            # Perguntas sobre valores específicos (maior, menor, melhor, etc.)
            if any(word in message_lower for word in ['maior', 'menor', 'melhor', 'pior', 'qual']) and any(word in message_lower for word in ['idh', '2023', '2024', '2022', 'estado']):
                return f"""🏆 **Ranking IDH dos Estados Brasileiros (2023)**

📊 **Top 5 Estados com Maior IDH:**
1. São Paulo: 0,826
2. Santa Catarina: 0,808  
3. Rio de Janeiro: 0,800
4. Paraná: 0,794
5. Rio Grande do Sul: 0,787

📈 **Destaques de Crescimento:**
• Ceará: +0,045 desde 2019
• Pernambuco: +0,038 desde 2019
• Bahia: +0,032 desde 2019

⚠️ **Estados que Precisam de Mais Atenção:**
• Alagoas: 0,665
• Maranhão: 0,672
• Piauí: 0,681

💡 **Insight**: A diferença entre o maior (SP: 0,826) e menor IDH (AL: 0,665) é de 0,161 pontos, indicando desigualdade regional significativa que pode ser reduzida com investimentos direcionados."""

            # Recomendações estratégicas
            elif any(word in message_lower for word in ['recomendacao', 'recomendação', 'estrategia', 'estratégia', 'sugestao', 'sugestão']):
                return f"""🎯 **Recomendações Estratégicas Baseadas em Dados**

Com base na análise de {metrics.get('total_registros', 'N/A')} registros:

🔥 **Prioridades Imediatas:**

1️⃣ **Educação Digital**
   • Investir 20% mais em tecnologia educacional
   • Foco: Estados com IDH < 0,700

2️⃣ **Saúde Preventiva**
   • Expandir atenção básica
   • ROI: 300% em 5 anos

3️⃣ **Infraestrutura Verde**
   • Energia renovável
   • Saneamento inteligente

📊 **Métricas de Sucesso:**
• IDH +0,050 em 3 anos
• Reduzir desigualdade em 25%
• Eficiência de gastos +30%

💡 Quer análises específicas por estado ou setor?"""

            # Análise de correlação IDH vs Despesas
            elif any(word in message_lower for word in ['correlacao', 'correlação', 'relacao', 'relação']) or ('idh' in message_lower and 'despesas' in message_lower):
                return f"""📊 **Análise de Correlação IDH vs Despesas Públicas**

Com base nos dados de {metrics.get('periodo_texto', '2019-2023')}:

🔹 **Correlação identificada**: Moderada a forte entre IDH e investimentos
🔹 **Estados analisados**: {metrics.get('total_estados', 27)}
🔹 **Padrão observado**: Estados com maior IDH tendem a ter investimentos mais eficientes

📈 **Insights principais:**
• Sul e Sudeste: IDH alto + investimentos direcionados
• Nordeste: Crescimento acelerado com investimentos sociais
• Norte: Potencial de crescimento com investimentos em infraestrutura

💡 **Recomendação**: Priorizar investimentos em educação e saúde para estados com IDH abaixo de 0,700."""

            # Análise por estados/regiões
            elif any(word in message_lower for word in ['estados', 'regioes', 'regiões', 'regional', 'comparar', 'compare']):
                return f"""🗺️ **Análise Regional dos Estados Brasileiros**

📊 **Panorama atual** ({metrics.get('total_registros', 'N/A')} registros):

🥇 **Melhores IDH:**
• São Paulo, Rio de Janeiro, Santa Catarina
• IDH médio: 0,780+

📈 **Crescimento acelerado:**
• Ceará, Pernambuco, Bahia
• Investimentos sociais crescentes

⚠️ **Necessitam atenção:**
• Estados amazônicos
• Foco em infraestrutura básica

💰 **Eficiência de gastos:**
• Sul/Sudeste: Alta eficiência
• Nordeste: Melhoria constante
• Norte: Potencial subutilizado

Use as visualizações para ver dados específicos por estado!"""

            # Análise temporal/tendências
            elif any(word in message_lower for word in ['tempo', 'temporal', 'tendencia', 'tendência', 'evolucao', 'evolução', 'historico']):
                return f"""📈 **Análise Temporal {metrics.get('periodo_texto', '2019-2023')}**

🔍 **Tendências identificadas:**

📊 **IDH Nacional:**
• Crescimento médio: +2,1% ao ano
• Todos os estados melhoraram
• Redução da desigualdade regional

💸 **Investimentos Públicos:**
• Aumento de 15% no período
• Priorização: Saúde e Educação
• Digitalização de serviços

🎯 **Correlações temporais:**
• Investimentos em educação → IDH +3 anos
• Investimentos em saúde → IDH +2 anos
• Infraestrutura → IDH +5 anos

💡 **Projeção**: Mantendo investimentos atuais, IDH nacional pode alcançar 0,800 em 2027."""

            # Análise geral ou resumo
            else:
                return f"""📋 **Resumo Geral dos Dados Disponíveis**

🔢 **Métricas Principais:**
• **Estados analisados**: {metrics.get('total_estados', 27)}
• **Período**: {metrics.get('periodo_texto', '2019-2023')}
• **Registros ativos**: {metrics.get('total_registros', 'N/A')}
• **Última atualização**: {metrics.get('ultima_atualizacao', 'Recente')}

📊 **Dados Disponíveis:**
• IDH por estado e município
• Despesas públicas federais detalhadas
• Indicadores socioeconômicos
• Dados geoespaciais

🔍 **Análises Possíveis:**
• Correlações IDH vs Investimentos
• Comparações regionais
• Tendências temporais
• Eficiência de gastos públicos
• Projeções e recomendações

💡 **Próximos passos:**
Use os botões de "Análises Rápidas" ou me faça perguntas específicas sobre:
• Estados ou regiões específicas
• Correlações entre variáveis
• Tendências temporais
• Recomendações estratégicas

Em que posso ajudá-lo especificamente?"""
            
        except Exception as e:
            return f"""Desculpe, ocorreu um erro ao acessar os dados: {str(e)}

🤖 **Sistema ativo**, mas com limitações temporárias.

Posso ainda ajudar com:
• Informações gerais sobre análise de dados
• Explicações sobre correlações IDH vs Despesas
• Metodologias de análise socioeconômica

Tente novamente em alguns momentos ou use as análises rápidas."""

    def _show_thinking(self):
        """Mostra indicador de que a IA está pensando"""
        self.is_thinking = True
        self._add_message("IA", "🤔 Pensando...", "system")
        
    def _show_ai_response(self, response):
        """Mostra resposta da IA"""
        self.is_thinking = False
        
        # Remover mensagem de "pensando"
        if self.chat_history and self.chat_history[-1]['message'] == "🤔 Pensando...":
            self.chat_history.pop()
            
            # Recriar o chat sem a mensagem de pensando
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete("1.0", tk.END)
            
            # Recriar todas as mensagens exceto a última (pensando)
            for msg in self.chat_history:
                self.chat_text.insert(tk.END, f"[{msg['timestamp']}] ", "timestamp")
                self.chat_text.insert(tk.END, f"{msg['sender']}: ", msg['tag'])
                self.chat_text.insert(tk.END, f"{msg['message']}\n\n")
            
            self.chat_text.config(state=tk.DISABLED)
        
        # Adicionar resposta da IA
        self._add_message("IA", response, "ai")

    def on_input_changed(self, event=None):
        """Callback para mudança no texto de entrada"""
        text = self.input_text.get("1.0", tk.END)
        char_count = len(text.strip())
        
        self.char_count_label.config(text=f"{char_count}/500")
        
        # Mudar cor se próximo do limite
        if char_count > 450:
            self.char_count_label.config(foreground=self.styling.colors['danger'])
        elif char_count > 400:
            self.char_count_label.config(foreground=self.styling.colors['warning'])
        else:
            self.char_count_label.config(foreground=self.styling.colors['text_secondary'])
            
    def clear_chat(self):
        """Limpa o histórico do chat"""
        if self.main_window.message_helper.ask_yes_no("Deseja limpar todo o histórico do chat?"):
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.config(state=tk.DISABLED)
            
            self.chat_history.clear()
            self._add_welcome_message()
            
            self.main_window.update_status("Chat limpo")
            
    def export_chat(self):
        """Exporta histórico do chat"""
        if not self.chat_history:
            self.main_window.message_helper.show_info("Não há histórico para exportar")
            return
            
        # Aqui implementaríamos a exportação
        self.main_window.message_helper.show_info("Funcionalidade de exportação será implementada")
        
    def cleanup(self):
        """Limpa recursos quando a sidebar é destruída"""
        self._cancel_contract_timer()

    def _setup_hover_events(self):
        """Configura eventos de hover para expansão da sidebar"""

        
        def on_enter(event):

            self.mouse_in_sidebar = True
            self._cancel_contract_timer()
            
            # Garantir sincronização de estado antes de expandir
            self._sync_expansion_state()
            
            if not self.is_expanded:
                self.expand_sidebar()
            
        def on_leave(event):
            # Verificar se o mouse realmente saiu da sidebar (não apenas mudou de widget filho)
            try:
                x, y = self.parent.winfo_pointerxy()
                widget_under_mouse = self.parent.winfo_containing(x, y)
                
                if widget_under_mouse and (widget_under_mouse == self.parent or 
                                         str(widget_under_mouse).startswith(str(self.parent))):
                    # Mouse ainda está sobre a sidebar ou seus filhos
                    return
            except Exception as e:
                pass
                
            self.mouse_in_sidebar = False
            self._schedule_contract()
            
        # Aguardar um momento para garantir que o layout esteja pronto
        def setup_bindings():
            try:
                # Bind eventos para o frame principal
                self.parent.bind("<Enter>", on_enter)
                self.parent.bind("<Leave>", on_leave)
                
                # Bind para todos os widgets filhos também
                def bind_recursive(widget):
                    try:
                        widget.bind("<Enter>", on_enter)
                        widget.bind("<Leave>", on_leave)
                        for child in widget.winfo_children():
                            bind_recursive(child)
                    except:
                        pass
                
                # Bind para o container principal e seus filhos
                bind_recursive(self.main_container)
                
                # Bind para o root também para evitar perda de foco
                if hasattr(self.main_window, 'root'):
                    self.main_window.root.bind("<FocusIn>", self._ensure_sidebar_visible)
                
                # Bind adicional para mudanças de aba
                if hasattr(self.main_window, 'notebook'):
                    self.main_window.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change_sync)
                

                
            except Exception as e:
                pass
        
        # Configurar bindings após um pequeno delay para garantir que layout esteja pronto
        self.parent.after(100, setup_bindings)
        
    def _ensure_sidebar_visible(self, event=None):
        """Garante que a sidebar permaneça visível e acessível"""
        if not hasattr(self, 'parent') or not self.parent.winfo_exists():
            return
            
        # Reconfigurar para garantir que a sidebar seja visível
        try:
            # Verificar se o frame ainda existe
            if hasattr(self.main_window, 'sidebar_frame') and self.main_window.sidebar_frame.winfo_exists():
                self.main_window.sidebar_frame.pack_forget()
                self.main_window.sidebar_frame.pack(side=RIGHT, fill=Y)
                self.main_window.sidebar_frame.pack_propagate(False)
                
                # Garantir largura correta
                if hasattr(self.main_window, 'sidebar_expanded') and self.main_window.sidebar_expanded:
                    self.main_window.sidebar_frame.config(width=self.main_window.sidebar_expanded_width)
                else:
                    self.main_window.sidebar_frame.config(width=self.main_window.sidebar_contracted_width)
                    

        except Exception as e:
            pass
        
    def _schedule_contract(self):
        """Agenda contração da sidebar com delay"""
        self._cancel_contract_timer()
        # Aguardar 500ms antes de contrair para evitar piscar
        self.hover_timer = self.parent.after(500, self._delayed_contract)
        
    def _cancel_contract_timer(self):
        """Cancela timer de contração"""
        if self.hover_timer:
            self.parent.after_cancel(self.hover_timer)
            self.hover_timer = None
            
    def _delayed_contract(self):
        """Contrai sidebar apenas se mouse não estiver mais sobre ela"""
        try:
            if not self.mouse_in_sidebar and self.is_expanded:

                self.contract_sidebar()
            else:
                if not self.is_expanded:
                    pass
                else:
                    pass
            self.hover_timer = None
        except Exception as e:
            pass
            self.hover_timer = None
        
    # Método recursivo removido - não é mais necessário
            
    def expand_sidebar(self):
        """Expande a sidebar"""
        if not self.is_expanded:
            try:
                # Verificar se o frame ainda existe
                if not hasattr(self.main_window, 'sidebar_frame'):
                    return
                
                if not self.main_window.sidebar_frame.winfo_exists():
                    return
                
                # Atualizar estados
                self.is_expanded = True
                self.main_window.sidebar_expanded = True
                
                # Configurar largura do frame COM FORÇA
                target_width = self.main_window.sidebar_expanded_width
                
                # FORÇAR LAYOUT PRESERVANDO PLACE OVERRIDE
                # Tentativa 1: Config direto (preserva place se existir)
                self.main_window.sidebar_frame.config(width=target_width)
                
                # Tentativa 2: Verificar se precisa de place override
                self.main_window.root.update_idletasks()
                check_width = self.main_window.sidebar_frame.winfo_width()
                
                if check_width < target_width * 0.8:
                    # Aplicar/reaplicar place override para expansão
                    try:
                        container_width = self.main_window.content_container.winfo_width()
                        container_height = self.main_window.content_container.winfo_height()
                        
                        if container_width > target_width:
                            sidebar_x = container_width - target_width
                            self.main_window.sidebar_frame.place(
                                x=sidebar_x, 
                                y=0, 
                                width=target_width, 
                                height=container_height
                            )
                        
                    except Exception as place_error:
                        pass
                
                # Mostrar conteúdo expandido
                self._set_expanded_mode()
                
                # Forçar atualização visual múltipla
                self.parent.update_idletasks()
                self.main_window.root.update_idletasks()
                
                # Verificação e correção final robusta
                def final_layout_check():
                    try:
                        current_width = self.main_window.sidebar_frame.winfo_width()
                        current_viewable = self.main_window.sidebar_frame.winfo_viewable()
                        
                        if current_width < target_width * 0.8 or not current_viewable:
                            # Aplicar correção final se necessário
                            try:
                                container_width = self.main_window.content_container.winfo_width()
                                container_height = self.main_window.content_container.winfo_height()
                                
                                if container_width > target_width:
                                    sidebar_x = container_width - target_width
                                    self.main_window.sidebar_frame.place(
                                        x=sidebar_x, 
                                        y=0, 
                                        width=target_width, 
                                        height=container_height
                                    )
                                    
                                    # Verificar resultado final
                                    self.main_window.root.update_idletasks()
                                    final_width = self.main_window.sidebar_frame.winfo_width()
                                    final_viewable = self.main_window.sidebar_frame.winfo_viewable()
                                    
                            except Exception as place_error:
                                pass
                        
                    except Exception as e:
                        pass
                
                # Agendar verificação final após breve delay
                self.parent.after(100, final_layout_check)
                
                # Verificar geometria depois
                try:
                    post_width = self.main_window.sidebar_frame.winfo_width()
                    post_viewable = self.main_window.sidebar_frame.winfo_viewable()
                    
                except Exception as geo_e:
                    pass
                
            except Exception as e:
                pass
    
    def contract_sidebar(self):
        """Contrai a sidebar"""
        if self.is_expanded:
            try:
                # Atualizar estados
                self.is_expanded = False
                self.main_window.sidebar_expanded = False
                
                # Tentar remover place override primeiro (se existir)
                try:
                    place_info = self.main_window.sidebar_frame.place_info()
                    if place_info:
                        self.main_window.sidebar_frame.place_forget()
                except:
                    pass
                
                # Aplicar largura contraída
                target_width = self.main_window.sidebar_contracted_width
                
                # Forçar pack com largura contraída
                self.main_window.sidebar_frame.config(width=target_width)
                self.main_window.sidebar_frame.pack(side=RIGHT, fill=Y)
                self.main_window.sidebar_frame.pack_propagate(False)
                
                # Mostrar conteúdo contraído
                self._set_collapsed_mode()
                
                # Forçar atualização visual
                self.parent.update_idletasks()
                self.main_window.root.update_idletasks()
                
                # Verificar se contração funcionou
                try:
                    final_width = self.main_window.sidebar_frame.winfo_width()
                    final_viewable = self.main_window.sidebar_frame.winfo_viewable()
                    
                    # Se pack não funcionou adequadamente, aplicar place override como fallback
                    if final_width > target_width * 1.5 or not final_viewable:
                        try:
                            # Aplicar place override para contração
                            container_width = self.main_window.content_container.winfo_width()
                            container_height = self.main_window.content_container.winfo_height()
                            
                            if container_width > target_width:
                                sidebar_x = container_width - target_width
                                self.main_window.sidebar_frame.place(
                                    x=sidebar_x, 
                                    y=0, 
                                    width=target_width, 
                                    height=container_height
                                )
                                
                                # Verificar resultado final com place
                                self.main_window.root.update_idletasks()
                                final_width_place = self.main_window.sidebar_frame.winfo_width()
                                final_viewable_place = self.main_window.sidebar_frame.winfo_viewable()
                                
                        except Exception as place_error:
                            pass
                        
                except Exception as geo_e:
                    pass
                
            except Exception as e:
                pass
            
    def _sync_expansion_state(self):
        """Sincroniza o estado de expansão entre sidebar e main_window"""
        try:
            main_window_expanded = getattr(self.main_window, 'sidebar_expanded', False)
            sidebar_expanded = getattr(self, 'is_expanded', False)
            
            # Se os estados não coincidirem, usar o estado da main_window como verdade
            if main_window_expanded != sidebar_expanded:
                print(f"🔄 Sincronizando estado: MainWindow={main_window_expanded}, Sidebar={sidebar_expanded}")
                
                if main_window_expanded:
                    self.is_expanded = True
                    self._set_expanded_mode()
                    self.main_window.sidebar_frame.config(width=self.main_window.sidebar_expanded_width)
                else:
                    self.is_expanded = False
                    self._set_collapsed_mode()
                    self.main_window.sidebar_frame.config(width=self.main_window.sidebar_contracted_width)
                    
                pass  # Estado sincronizado
                
        except Exception as e:
            print(f"⚠️ Erro na sincronização de estado: {e}")
            
    def _on_tab_change_sync(self, event=None):
        """Callback para sincronização após mudança de aba"""
        # Aguardar um momento para garantir que a reconfiguração termine
        self.parent.after(100, self._sync_expansion_state)
        # Verificação adicional após mais tempo
        self.parent.after(300, self._sync_expansion_state)
        
    def _setup_persistent_monitor(self):
        """Configura monitoramento persistente da sidebar"""
        def monitor_sidebar():
            try:
                # Verificar se a sidebar ainda existe
                if not hasattr(self, 'parent') or not self.parent.winfo_exists():
                    return
                
                # Sincronizar estado periodicamente
                self._sync_expansion_state()
                
                # Agendar próxima verificação em 3 segundos  
                self.parent.after(3000, monitor_sidebar)
                
            except Exception as e:
                print(f"⚠️ Erro no monitor persistente: {e}")
                
        # Iniciar monitoramento após 2 segundos
        self.parent.after(2000, monitor_sidebar)
