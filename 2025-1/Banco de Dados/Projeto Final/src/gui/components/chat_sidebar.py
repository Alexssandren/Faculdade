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
                print("✅ Sistema de IA Gemini inicializado")
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
            print("🚀 Expansão automática da sidebar na inicialização")
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
                if self.ai_mode == "real" and self.ai_engine:
                    # Usar IA real com dados contextuais
                    response = self._generate_real_ai_response(user_message)
                else:
                    # Usar sistema simulado com dados reais do data_provider
                    response = self._generate_enhanced_simulated_response(user_message)
                
                # Atualizar UI na thread principal
                self.main_window.root.after(0, lambda: self._show_ai_response(response))
                
            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
                self.main_window.root.after(0, lambda: self._show_ai_response(error_msg))
                
        self.main_window.thread_manager.run_thread(ai_task)
        
    def _generate_real_ai_response(self, user_message):
        """Gera resposta usando IA real Gemini com dados contextuais"""
        try:
            # Buscar dados contextuais das consultas analíticas
            context_data = self._gather_context_data(user_message)
            
            # Usar IA real
            analysis = self.ai_engine.analyze_with_ai(user_message, context_data)
            
            # Verificar se houve erro na análise
            if analysis.get('error', False):
                print(f"Erro na análise IA: {analysis.get('response_text', 'Erro desconhecido')}")
                return self._generate_enhanced_simulated_response(user_message)
            
            # Verificar se há resposta válida
            response_text = analysis.get('response_text', '')
            if not response_text or response_text.strip() == '':
                print("Resposta vazia da IA, usando fallback")
                return self._generate_enhanced_simulated_response(user_message)
            
            return response_text
            
        except Exception as e:
            print(f"Erro na IA real: {e}")
            return self._generate_enhanced_simulated_response(user_message)
    
    def _generate_enhanced_simulated_response(self, user_message):
        """Gera resposta simulada mas usando dados reais do sistema"""
        message_lower = user_message.lower()
        
        try:
            # Buscar dados reais do sistema
            metrics = data_provider.get_dashboard_metrics()
            correlation_data = data_provider.get_correlation_data(2023, 'Todas')
            regional_data = data_provider.get_regional_analysis_data(2023)
            efficiency_data = data_provider.get_state_efficiency_data(2023)
            
            # Respostas baseadas em dados reais
            if any(word in message_lower for word in ['resumo', 'geral', 'visão', 'panorama']):
                return f"""📊 **Resumo Geral dos Dados (Atualizado)**

Com base na análise dos dados disponíveis:

• **Período**: {metrics['periodo_texto']} ({metrics['periodo_anos']} anos)
• **Cobertura**: {metrics['total_estados']} estados + DF
• **Registros**: {metrics['total_registros']} registros ativos
• **Última Atualização**: {metrics['ultima_atualizacao']}

**Principais Insights:**
• Correlação IDH vs Despesas: {correlation_data['correlation']:.3f} (moderada a forte)
• Melhor região em IDH: {regional_data['melhor_regiao']}
• Total de estados analisados: {correlation_data['total_states']}
• Eficiência média nacional: {efficiency_data['media_nacional']:.3f}

**Status**: Dados atualizados e sincronizados ✅"""

            elif any(word in message_lower for word in ['correlação', 'correlações', 'relação']):
                return f"""📈 **Análise de Correlações (Dados Reais)**

**IDH vs Despesas Públicas (2023):**
• **Correlação Geral**: {correlation_data['correlation']:.3f}
• **Estados Analisados**: {correlation_data['total_states']}
• **Interpretação**: {'Correlação forte' if abs(correlation_data['correlation']) > 0.7 else 'Correlação moderada' if abs(correlation_data['correlation']) > 0.4 else 'Correlação fraca'}

**Análise Regional:**
• **Melhor Região**: {regional_data['melhor_regiao']} 
• **Total de Regiões**: {regional_data['total_regions']}

**Insight Chave:** 
Estados com maiores investimentos per capita tendem a apresentar IDH superior, confirmando a efetividade dos gastos públicos direcionados."""

            elif any(word in message_lower for word in ['top', 'melhores', 'maiores', 'ranking', 'líderes']):
                top_states = efficiency_data['estados'][:5]
                top_values = efficiency_data['efficiency_values'][:5]
                
                ranking_text = "\n".join([f"{i+1}. **{state}**: {value:.3f}" 
                                        for i, (state, value) in enumerate(zip(top_states, top_values))])
                
                return f"""🏆 **Top Estados por Eficiência (2023)**

**Ranking de Eficiência (IDH/Gasto per capita):**
{ranking_text}

**Média Nacional**: {efficiency_data['media_nacional']:.3f}

**Análise**: Os estados listados demonstram melhor relação custo-benefício entre investimentos e resultados no IDH."""

            elif any(word in message_lower for word in ['eficien', 'gasto', 'investimento']):
                efficient_count = len([e for e in efficiency_data['efficiency_values'] if e > efficiency_data['media_nacional']])
                
                return f"""💰 **Análise de Eficiência dos Gastos (Dados Atuais)**

**Estados Analisados**: {len(efficiency_data['estados'])}
**Média Nacional**: {efficiency_data['media_nacional']:.3f}
**Estados Acima da Média**: {efficient_count}/{len(efficiency_data['estados'])}

**Estados Mais Eficientes:**
{', '.join(efficiency_data['estados'][:3])}

**Recomendação**: Estados com alta eficiência podem servir como benchmark para otimização de recursos públicos."""

            elif any(word in message_lower for word in ['tendência', 'temporal', 'evolução', 'tempo']):
                temporal_data = data_provider.get_temporal_trends_data('Todas')
                
                return f"""📉 **Tendências Temporais ({temporal_data['anos'][0]}-{temporal_data['anos'][-1]})**

**Período Analisado**: {len(temporal_data['anos'])} anos
**Taxa de Crescimento Estimada**: {temporal_data['growth_rate']:.1f}% ao ano

**Evolução por Região** (IDH médio {temporal_data['anos'][-1]}):
• **Sudeste**: {temporal_data['regioes_data']['Sudeste'][-1]:.3f}
• **Sul**: {temporal_data['regioes_data']['Sul'][-1]:.3f}
• **Centro-Oeste**: {temporal_data['regioes_data']['Centro-Oeste'][-1]:.3f}
• **Norte**: {temporal_data['regioes_data']['Norte'][-1]:.3f}
• **Nordeste**: {temporal_data['regioes_data']['Nordeste'][-1]:.3f}

**Projeção**: Mantendo tendências atuais, convergência regional esperada para próxima década."""

            elif any(word in message_lower for word in ['recomendação', 'sugestão', 'estratégia', 'conselho']):
                return f"""🎯 **Recomendações Estratégicas (Baseado em Dados Reais)**

**Para Gestores Públicos:**
• Foco na correlação positiva: cada R$ investido adequadamente gera retorno mensurável no IDH
• Benchmark com estados eficientes: {', '.join(efficiency_data['estados'][:2])}
• Monitoramento contínuo da relação custo-benefício

**Para Regiões Específicas:**
• **{regional_data['melhor_regiao']}**: Manter liderança e servir como modelo
• **Demais regiões**: Estudar casos de sucesso e adaptar boas práticas

**Métricas de Acompanhamento:**
• Taxa de correlação IDH vs investimento (atual: {correlation_data['correlation']:.3f})
• Eficiência relativa por estado (meta: > {efficiency_data['media_nacional']:.3f})
• Convergência regional temporal

**Próximos Passos**: Análise detalhada por subíndices e setores específicos."""

            else:
                return f"""Recebi sua pergunta: "{user_message}"

Como sua assistente de IA conectada aos **dados reais** do sistema DEC7588, posso ajudar com análises específicas.

**Dados Disponíveis** (atualizado {metrics['ultima_atualizacao']}):
• {metrics['total_estados']} estados analisados
• {metrics['total_registros']} registros ativos
• Correlação IDH vs Despesas: {correlation_data['correlation']:.3f}

**Exemplos de perguntas:**
- "Como está a evolução do IDH no período atual?"
- "Qual a correlação entre gastos em saúde e IDH?"
- "Que estados são mais eficientes nos investimentos?"

Como posso ajudar especificamente? 😊"""
                
        except Exception as e:
            print(f"Erro ao gerar resposta com dados reais: {e}")
            return self._generate_fallback_response(user_message)
    
    def _generate_fallback_response(self, user_message):
        """Resposta de fallback básica"""
        return f"""Recebi sua pergunta: "{user_message}"

Atualmente estou com dificuldades para acessar os dados em tempo real, mas posso ajudar com:

• Análises gerais sobre IDH e despesas públicas
• Comparações regionais do Brasil
• Tendências socioeconômicas
• Recomendações baseadas em padrões conhecidos

Por favor, reformule sua pergunta ou use uma das **Análises Rápidas** disponíveis. 🤖"""
    
    def _gather_context_data(self, user_message):
        """Reúne dados contextuais das consultas analíticas do banco para a IA"""
        try:
            # Buscar dados das 3 consultas principais do banco
            correlation_data = data_provider.get_correlation_data(2023, 'Todas')
            regional_data = data_provider.get_regional_analysis_data(2023)
            temporal_data = data_provider.get_temporal_trends_data('Todas')
            efficiency_data = data_provider.get_state_efficiency_data(2023)
            
            # Verificar se há dados válidos antes de montar o contexto
            context = {}
            
            # Consulta 1: Correlação IDH vs Despesas
            if correlation_data and not correlation_data.get('error'):
                # Calcular correlação corrigida se necessário
                correlation = correlation_data.get('correlation', 0)
                if correlation == 0 and correlation_data.get('idh_values') and correlation_data.get('despesas_values'):
                    try:
                        import numpy as np
                        idh_vals = correlation_data.get('idh_values', [])
                        desp_vals = correlation_data.get('despesas_values', [])
                        if len(idh_vals) > 1 and len(desp_vals) > 1:
                            valid_pairs = [(i, d) for i, d in zip(idh_vals, desp_vals) if not np.isnan(i) and not np.isnan(d) and i > 0 and d > 0]
                            if len(valid_pairs) > 1:
                                valid_idh, valid_desp = zip(*valid_pairs)
                                correlation = np.corrcoef(valid_idh, valid_desp)[0, 1]
                                if np.isnan(correlation):
                                    correlation = 0
                    except:
                        correlation = 0
                
                context['consulta_1'] = {
                    'correlation': correlation,
                    'total_states': correlation_data.get('total_states', 0),
                    'estados': correlation_data.get('estados', []),
                    'idh_values': correlation_data.get('idh_values', []),
                    'despesas_values': correlation_data.get('despesas_values', []),
                    'year': correlation_data.get('year', 2023)
                }
                print(f"✅ Contexto Consulta 1: {correlation_data.get('total_states', 0)} estados")
            else:
                print(f"⚠️ Consulta 1 sem dados válidos: {correlation_data.get('error', 'erro desconhecido')}")
            
            # Consulta 2: Evolução Temporal
            if temporal_data and not temporal_data.get('error'):
                anos = temporal_data.get('anos', [])
                context['consulta_2'] = {
                    'years': anos,
                    'periodo_analise': f"{min(anos)}-{max(anos)}" if anos else "N/A",
                    'growth_rate': temporal_data.get('growth_rate', 0),
                    'total_records': temporal_data.get('total_records', 0),
                    'regioes_data': temporal_data.get('regioes_data', {})
                }
                print(f"✅ Contexto Consulta 2: {len(anos)} anos de dados")
            else:
                print(f"⚠️ Consulta 2 sem dados válidos: {temporal_data.get('error', 'erro desconhecido')}")
            
            # Consulta 3: Análise Regional
            if regional_data and not regional_data.get('error'):
                regioes = regional_data.get('regioes', [])
                context['consulta_3'] = {
                    'regioes': regioes,
                    'idh_values': regional_data.get('idh_values', []),
                    'gastos_values': regional_data.get('gastos_values', []),
                    'total_records': regional_data.get('total_records', 0),
                    'year': regional_data.get('year', 2023)
                }
                print(f"✅ Contexto Consulta 3: {len(regioes)} regiões")
            else:
                print(f"⚠️ Consulta 3 sem dados válidos: {regional_data.get('error', 'erro desconhecido')}")
            
            # Dados de Eficiência (adicional)
            if efficiency_data and not efficiency_data.get('error'):
                context['eficiencia'] = {
                    'media_nacional': efficiency_data.get('media_nacional', 0),
                    'estados': efficiency_data.get('estados', []),
                    'efficiency_values': efficiency_data.get('efficiency_values', []),
                    'year': efficiency_data.get('year', 2023)
                }
                print(f"✅ Contexto Eficiência: {len(efficiency_data.get('estados', []))} estados")
            else:
                print(f"⚠️ Dados de eficiência sem dados válidos: {efficiency_data.get('error', 'erro desconhecido')}")
            
            return context
            
        except Exception as e:
            print(f"❌ Erro ao reunir contexto do banco: {e}")
            return {}
        
    def _show_thinking(self):
        """Mostra indicador de que a IA está pensando"""
        self.is_thinking = True
        ai_type = "Gemini" if self.ai_mode == "real" else "Simulado"
        self.status_indicator.config(
            text=f"{self.styling.icons['loading']} IA {ai_type} Pensando...",
            foreground=self.styling.colors['warning']
        )
        self.send_btn.config(state=DISABLED)
        
    def _show_ai_response(self, response):
        """Mostra resposta da IA"""
        self.is_thinking = False
        ai_type = "Gemini" if self.ai_mode == "real" else "Simulado"
        status_color = self.styling.colors['success'] if self.ai_mode == "real" else self.styling.colors['info']
        
        self.status_indicator.config(
            text=f"{self.styling.icons['check']} IA {ai_type} Online",
            foreground=status_color
        )
        self.send_btn.config(state=NORMAL)
        
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
        print("🎯 Configurando eventos de hover da sidebar...")
        
        def on_enter(event):
            print(f"🖱️ Mouse ENTROU na sidebar (widget: {event.widget})")
            self.mouse_in_sidebar = True
            self._cancel_contract_timer()
            
            # Garantir sincronização de estado antes de expandir
            self._sync_expansion_state()
            
            if not self.is_expanded:
                print("➡️ Expandindo sidebar via hover...")
                self.expand_sidebar()
            else:
                print("ℹ️ Sidebar já expandida")
            
        def on_leave(event):
            print(f"🖱️ Mouse SAIU da sidebar (widget: {event.widget})")
            
            # Verificar se o mouse realmente saiu da sidebar (não apenas mudou de widget filho)
            try:
                x, y = self.parent.winfo_pointerxy()
                widget_under_mouse = self.parent.winfo_containing(x, y)
                
                if widget_under_mouse and (widget_under_mouse == self.parent or 
                                         str(widget_under_mouse).startswith(str(self.parent))):
                    # Mouse ainda está sobre a sidebar ou seus filhos
                    print("ℹ️ Mouse ainda na sidebar (widget filho)")
                    return
            except Exception as e:
                print(f"⚠️ Erro ao verificar posição do mouse: {e}")
                
            self.mouse_in_sidebar = False
            print("⏱️ Agendando contração da sidebar...")
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
                
                print("✅ Eventos de hover configurados com sucesso")
                
            except Exception as e:
                print(f"⚠️ Erro ao configurar eventos de hover: {e}")
        
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
                    
                print("🔧 Sidebar reconfigurada via _ensure_sidebar_visible")
        except Exception as e:
            print(f"⚠️ Erro ao reconfigurar sidebar: {e}")
        
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
                print("🔄 [TIMER] Contraindo sidebar via timer...")
                self.contract_sidebar()
            else:
                if not self.is_expanded:
                    print("ℹ️ [TIMER] Sidebar já contraída")
                else:
                    print("ℹ️ [TIMER] Mouse ainda na sidebar - cancelando contração")
            self.hover_timer = None
        except Exception as e:
            print(f"❌ [TIMER] Erro na contração: {e}")
            self.hover_timer = None
        
    # Método recursivo removido - não é mais necessário
            
    def expand_sidebar(self):
        """Expande a sidebar"""
        if not self.is_expanded:
            print(f"➡️ [EXPAND] Iniciando expansão da sidebar...")
            
            try:
                # Verificar se o frame ainda existe
                if not hasattr(self.main_window, 'sidebar_frame'):
                    print(f"❌ [EXPAND] ERRO: sidebar_frame não existe (hasattr)")
                    return
                
                if not self.main_window.sidebar_frame.winfo_exists():
                    print(f"❌ [EXPAND] ERRO: sidebar_frame não existe (winfo_exists)")
                    return
                
                frame_id = id(self.main_window.sidebar_frame)
                print(f"➡️ [EXPAND] Frame válido: {frame_id}")
                
                # Verificar geometria antes
                try:
                    pre_width = self.main_window.sidebar_frame.winfo_width()
                    pre_viewable = self.main_window.sidebar_frame.winfo_viewable()
                    print(f"➡️ [EXPAND] Geometria antes: width={pre_width}, viewable={pre_viewable}")
                except Exception as geo_e:
                    print(f"⚠️ [EXPAND] Erro ao obter geometria antes: {geo_e}")
                
                # Atualizar estados
                self.is_expanded = True
                self.main_window.sidebar_expanded = True
                print(f"➡️ [EXPAND] Estados atualizados: sidebar={self.is_expanded}, main={self.main_window.sidebar_expanded}")
                
                # Configurar largura do frame COM FORÇA
                target_width = self.main_window.sidebar_expanded_width
                print(f"➡️ [EXPAND] Configurando largura: {target_width}px")
                
                # FORÇAR LAYOUT PRESERVANDO PLACE OVERRIDE
                # Tentativa 1: Config direto (preserva place se existir)
                self.main_window.sidebar_frame.config(width=target_width)
                
                # Tentativa 2: Verificar se precisa de place override
                self.main_window.root.update_idletasks()
                check_width = self.main_window.sidebar_frame.winfo_width()
                
                if check_width < target_width * 0.8:
                    print(f"➡️ [EXPAND] Config insuficiente ({check_width}px) - aplicando place override")
                    
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
                            print(f"➡️ [EXPAND] Place override para expansão aplicado: {target_width}px")
                        
                    except Exception as place_error:
                        print(f"➡️ [EXPAND] Erro no place override: {place_error}")
                else:
                    print(f"➡️ [EXPAND] Config adequado ({check_width}px)")
                
                # Mostrar conteúdo expandido
                print(f"➡️ [EXPAND] Aplicando modo expandido...")
                self._set_expanded_mode()
                
                # Forçar atualização visual múltipla
                self.parent.update_idletasks()
                self.main_window.root.update_idletasks()
                
                # Verificação e correção final robusta
                def final_layout_check():
                    try:
                        current_width = self.main_window.sidebar_frame.winfo_width()
                        current_viewable = self.main_window.sidebar_frame.winfo_viewable()
                        
                        print(f"➡️ [EXPAND] Verificação final: {current_width}px, viewable={current_viewable}")
                        
                        # Se largura insuficiente OU não visível, aplicar place override definitivo
                        if current_width < target_width * 0.8 or not current_viewable:
                            print(f"➡️ [EXPAND] Correção final necessária: {current_width}px → {target_width}px")
                            
                            # Place override definitivo
                            container_width = self.main_window.content_container.winfo_width()
                            container_height = self.main_window.content_container.winfo_height()
                            
                            if container_width > target_width and container_height > 100:
                                sidebar_x = container_width - target_width
                                self.main_window.sidebar_frame.place(
                                    x=sidebar_x, 
                                    y=0, 
                                    width=target_width, 
                                    height=container_height
                                )
                                
                                # Forçar update e verificação
                                self.main_window.root.update_idletasks()
                                final_width = self.main_window.sidebar_frame.winfo_width()
                                final_viewable = self.main_window.sidebar_frame.winfo_viewable()
                                
                                print(f"➡️ [EXPAND] Resultado final: {final_width}px, viewable={final_viewable}")
                            else:
                                print(f"➡️ [EXPAND] Container muito pequeno para place: {container_width}x{container_height}")
                        else:
                            print(f"➡️ [EXPAND] Layout final adequado")
                            
                    except Exception as e:
                        print(f"➡️ [EXPAND] Erro na verificação final: {e}")
                
                # Programar verificação após 100ms
                self.main_window.root.after(100, final_layout_check)
                
                # Verificar geometria depois
                try:
                    post_width = self.main_window.sidebar_frame.winfo_width()
                    post_viewable = self.main_window.sidebar_frame.winfo_viewable()
                    print(f"➡️ [EXPAND] Geometria depois: width={post_width}, viewable={post_viewable}")
                    
                    if post_width < 50:
                        print(f"⚠️ [EXPAND] AVISO: Largura muito pequena após expansão!")
                    
                    if not post_viewable:
                        print(f"⚠️ [EXPAND] AVISO: Frame não visível após expansão!")
                        
                except Exception as geo_e:
                    print(f"⚠️ [EXPAND] Erro ao obter geometria depois: {geo_e}")
                
                print("✅ [EXPAND] Sidebar expandida com sucesso")
                
            except Exception as e:
                print(f"❌ [EXPAND] Erro ao expandir sidebar: {e}")
                # Tentar recuperar estado
                self.is_expanded = False
                self.main_window.sidebar_expanded = False
        else:
            print(f"ℹ️ [EXPAND] Sidebar já expandida - nenhuma ação necessária")
                    
    def contract_sidebar(self):
        """Contrai a sidebar removendo place override se necessário"""
        if self.is_expanded:
            print(f"⬅️ [CONTRACT] Iniciando contração da sidebar...")
            
            try:
                # Atualizar estados primeiro
                self.is_expanded = False
                self.main_window.sidebar_expanded = False
                print(f"⬅️ [CONTRACT] Estados atualizados: sidebar={self.is_expanded}, main={self.main_window.sidebar_expanded}")
                
                # REMOVER PLACE OVERRIDE se existir
                place_info = self.main_window.sidebar_frame.place_info()
                if place_info:
                    print(f"⬅️ [CONTRACT] Removendo place override: {place_info}")
                    self.main_window.sidebar_frame.place_forget()
                    print(f"⬅️ [CONTRACT] Place override removido")
                
                # Voltar para pack normal com largura contraída
                target_width = self.main_window.sidebar_contracted_width
                print(f"⬅️ [CONTRACT] Aplicando largura contraída: {target_width}px")
                
                # Repack com largura contraída
                self.main_window.sidebar_frame.pack_forget()
                self.main_window.sidebar_frame.config(width=target_width)
                self.main_window.sidebar_frame.pack(side='right', fill='y')
                
                # Mostrar apenas ícone
                self._set_collapsed_mode()
                
                # Forçar atualização visual
                self.parent.update_idletasks()
                self.main_window.root.update_idletasks()
                
                # Verificação final e correção se necessário
                try:
                    final_width = self.main_window.sidebar_frame.winfo_width()
                    final_viewable = self.main_window.sidebar_frame.winfo_viewable()
                    print(f"⬅️ [CONTRACT] Resultado final: {final_width}px, viewable={final_viewable}")
                    
                    # Se pack falhou (largura incorreta OU não visível), aplicar place override
                    if final_width > target_width * 1.5 or not final_viewable:
                        print(f"🚀 [CONTRACT] Pack falhou ({final_width}px, viewable={final_viewable}) - aplicando place override")
                        
                        try:
                            # Aplicar place override para contração
                            container_width = self.main_window.content_container.winfo_width()
                            container_height = self.main_window.content_container.winfo_height()
                            
                            if container_width > target_width and container_height > 100:
                                sidebar_x = container_width - target_width
                                self.main_window.sidebar_frame.place(
                                    x=sidebar_x, 
                                    y=0, 
                                    width=target_width, 
                                    height=container_height
                                )
                                print(f"🚀 [CONTRACT] Place override aplicado: {target_width}px na posição x={sidebar_x}")
                                
                                # Verificar resultado final
                                self.main_window.root.update_idletasks()
                                final_width_place = self.main_window.sidebar_frame.winfo_width()
                                final_viewable_place = self.main_window.sidebar_frame.winfo_viewable()
                                print(f"🚀 [CONTRACT] Resultado com place: {final_width_place}px, viewable={final_viewable_place}")
                                
                            else:
                                print(f"⚠️ [CONTRACT] Container muito pequeno para place: {container_width}x{container_height}")
                                
                        except Exception as place_error:
                            print(f"❌ [CONTRACT] Erro no place override: {place_error}")
                        
                        print(f"✅ [CONTRACT] Contração corrigida com place override")
                    else:
                        print(f"✅ [CONTRACT] Contração bem-sucedida com pack")
                        
                except Exception as geo_e:
                    print(f"⚠️ [CONTRACT] Erro ao verificar geometria final: {geo_e}")
                
            except Exception as e:
                print(f"❌ [CONTRACT] Erro ao contrair sidebar: {e}")
                # Tentar recuperar estado
                self.is_expanded = True
                self.main_window.sidebar_expanded = True
        else:
            print(f"ℹ️ [CONTRACT] Sidebar já contraída - nenhuma ação necessária")
            
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
                    
                print(f"✅ Estado sincronizado: {self.is_expanded}")
                
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
        print("🔄 Monitor persistente da sidebar configurado")