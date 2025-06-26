"""
Módulo de IA Analítica - Fase 4
Sistema avançado de análise com IA integrada às consultas da Fase 3
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import pandas as pd
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class AIAnalyticsEngine:
    """
    Motor de IA para análises socioeconômicas avançadas.
    Integra com as consultas analíticas da Fase 3.
    """
    
    def __init__(self):
        """Inicializa o motor de IA analítica."""
        self._setup_gemini()
        self._load_data()
        self.conversation_history = []
        self.analysis_cache = {}
        
    def _setup_gemini(self):
        """Configura a API do Google Gemini."""
        try:
            # Encontrar arquivo .env
            current_dir = Path(__file__).parent
            while current_dir != current_dir.parent:
                dotenv_path = current_dir / "Chave.env"
                if dotenv_path.exists():
                    load_dotenv(dotenv_path=dotenv_path)
                    break
                current_dir = current_dir.parent
            
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini configurado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Gemini: {e}")
            raise
    
    def _load_data(self):
        """Carrega dados do banco via consultas analíticas."""
        try:
            from src.queries.analytics_queries import ConsultasAnalíticas
            from src.database.connection import get_database_connection
            
            # Inicializar sistema analítico
            self.analytics = ConsultasAnalíticas()
            self.db_connection = get_database_connection()
            
            # Verificar se há dados disponíveis
            with self.db_connection.get_session() as session:
                from src.models.entities import IndicadorIDH, Despesa
                
                total_idh = session.query(IndicadorIDH).count()
                total_despesas = session.query(Despesa).count()
                
                if total_idh == 0 or total_despesas == 0:
                    logger.warning(f"⚠️ Dados insuficientes no banco: {total_idh} IDH, {total_despesas} despesas")
                    self.data_available = False
                else:
                    logger.info(f"✅ Dados carregados do banco: {total_idh} registros IDH, {total_despesas} registros despesas")
                    self.data_available = True
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados do banco: {e}")
            self.analytics = None
            self.db_connection = None
            self.data_available = False
    
    def analyze_with_ai(self, query: str, context_data: Dict = None) -> Dict:
        """
        Análise principal com IA integrada.
        
        Args:
            query: Pergunta do usuário
            context_data: Dados de contexto das consultas da Fase 3
            
        Returns:
            Dict com análise completa
        """
        try:
            # Preparar contexto analítico
            enriched_prompt = self._create_analytical_prompt(query, context_data)
            
            # Gerar resposta com Gemini
            response = self.model.generate_content(
                enriched_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            # Processar resposta
            analysis = self._process_ai_response(response.text, query, context_data)
            
            # Adicionar ao histórico
            self._add_to_history(query, analysis)
            
            return analysis
            
        except Exception as e:
            error_msg = str(e) if str(e) else "Erro desconhecido na análise"
            # Evitar erro vazio ("0")
            if not error_msg or error_msg.strip() == "0":
                error_msg = "Erro inesperado durante a análise. Verifique os dados de entrada."
            logger.error(f"❌ Erro na análise: {error_msg}")
            return self._create_error_response(error_msg)
    
    def _create_analytical_prompt(self, query: str, context_data: Dict = None) -> str:
        """Cria prompt analítico enriquecido."""
        
        base_prompt = f"""
        Você é um ANALISTA SÊNIOR especializado em dados socioeconômicos brasileiros.
        
        🎯 ESPECIALIDADES:
        - Análise de IDH (Índice de Desenvolvimento Humano)
        - Despesas públicas federais
        - Comparações regionais e estaduais
        - Eficiência de investimentos
        - Tendências e projeções
        
        📊 CONSULTA DO USUÁRIO: {query}
        
        """
        
        # Adicionar contexto das consultas analíticas do banco
        if context_data and self.data_available:
            base_prompt += "\n🔍 CONTEXTO ANALÍTICO DO BANCO DE DADOS:\n"
            
            if 'consulta_1' in context_data:
                ranking_data = context_data['consulta_1']
                base_prompt += f"📈 RANKING IDH vs INVESTIMENTO (Consulta Analítica 1):\n"
                
                # Verificar se há dados válidos
                correlation = ranking_data.get('correlation', 0)
                if correlation and not (isinstance(correlation, float) and str(correlation) == 'nan'):
                    base_prompt += f"- Correlação IDH vs Despesas: {correlation:.3f}\n"
                else:
                    base_prompt += f"- Correlação IDH vs Despesas: dados insuficientes\n"
                
                total_states = ranking_data.get('total_states', 0)
                base_prompt += f"- {total_states} estados analisados\n"
                
                # Adicionar dados específicos se disponíveis
                if 'estados' in ranking_data and ranking_data['estados']:
                    base_prompt += f"- Estados com dados: {', '.join(ranking_data['estados'][:5])}\n"
            
            if 'consulta_2' in context_data:
                temporal_data = context_data['consulta_2']
                base_prompt += f"📅 EVOLUÇÃO TEMPORAL (Consulta Analítica 2):\n"
                
                years = temporal_data.get('years', [])
                if years:
                    base_prompt += f"- Período analisado: {min(years)}-{max(years)}\n"
                
                growth_rate = temporal_data.get('growth_rate', 0)
                if growth_rate:
                    base_prompt += f"- Taxa de crescimento médio: {growth_rate:.2f}%\n"
                
                total_records = temporal_data.get('total_records', 0)
                base_prompt += f"- {total_records} registros temporais\n"
            
            if 'consulta_3' in context_data:
                regional_data = context_data['consulta_3']
                base_prompt += f"🗺️ ANÁLISE REGIONAL (Consulta Analítica 3):\n"
                
                if 'regioes' in regional_data and regional_data['regioes']:
                    base_prompt += f"- Regiões: {', '.join(regional_data['regioes'])}\n"
                
                if 'idh_values' in regional_data and regional_data['idh_values']:
                    idh_values = regional_data['idh_values']
                    if idh_values:
                        base_prompt += f"- IDH médio nacional: {sum(idh_values)/len(idh_values):.3f}\n"
                        base_prompt += f"- Variação IDH: {min(idh_values):.3f} - {max(idh_values):.3f}\n"
                
                total_records = regional_data.get('total_records', 0)
                base_prompt += f"- {total_records} registros regionais\n"
        
        elif not self.data_available:
            base_prompt += "\n⚠️ AVISO: Dados do banco não disponíveis. Análise limitada.\n"
        
        base_prompt += """
        
        📋 INSTRUÇÕES PARA RESPOSTA:
        1. Forneça insights baseados nos dados reais disponíveis
        2. Use linguagem técnica mas acessível
        3. Inclua recomendações práticas e específicas
        4. Cite métricas concretas quando possível
        5. Identifique padrões, tendências e anomalias
        6. Sugira próximos passos ou análises complementares
        
        📊 ESTRUTURA DA RESPOSTA:
        - Análise principal (2-3 parágrafos)
        - Insights específicos (3-5 pontos)
        - Recomendações práticas (2-3 ações)
        - Métricas de destaque
        
        IMPORTANTE: Seja específico, prático e baseado em dados.
        """
        
        return base_prompt
    
    def _process_ai_response(self, response_text: str, query: str, context_data: Dict) -> Dict:
        """Processa a resposta da IA."""
        
        # Extrair insights estruturados
        insights = self._extract_insights(response_text)
        
        # Extrair recomendações
        recommendations = self._extract_recommendations(response_text)
        
        # Determinar tipo de análise
        analysis_type = self._determine_analysis_type(query)
        
        # Extrair métricas mencionadas
        metrics = self._extract_metrics(response_text)
        
        # Calcular score de confiança
        confidence_score = self._calculate_confidence(response_text, context_data)
        
        # Sugerir visualizações
        viz_suggestions = self._suggest_visualizations(analysis_type, query)
        
        return {
            'response_text': response_text,
            'insights': insights,
            'recommendations': recommendations,
            'analysis_type': analysis_type,
            'metrics_mentioned': metrics,
            'confidence_score': confidence_score,
            'visualization_suggestions': viz_suggestions,
            'timestamp': datetime.now().isoformat(),
            'query_original': query,
            'has_context_data': bool(context_data)
        }
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extrai insights principais do texto."""
        insights = []
        
        # Padrões para identificar insights
        patterns = [
            r'[Ii]nsight[:\s]+([^.]+)',
            r'[Dd]escobri[:\s]+([^.]+)',
            r'[Oo]bservamos?\s+que\s+([^.]+)',
            r'É\s+importante\s+notar\s+que\s+([^.]+)',
            r'[Dd]estaca-se\s+([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            insights.extend([match.strip() for match in matches])
        
        # Limitar a 5 insights principais
        return insights[:5]
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extrai recomendações do texto."""
        recommendations = []
        
        patterns = [
            r'[Rr]ecomend[ao]\s+([^.]+)',
            r'[Ss]ugiro\s+([^.]+)',
            r'[Dd]everia[m]?\s+([^.]+)',
            r'É\s+aconselhável\s+([^.]+)',
            r'[Pp]róximos?\s+passos?\s*:\s*([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            recommendations.extend([match.strip() for match in matches])
        
        return recommendations[:3]  # Top 3 recomendações
    
    def _determine_analysis_type(self, query: str) -> str:
        """Determina o tipo de análise baseado na query."""
        query_lower = query.lower()
        
        type_patterns = {
            'ranking': ['ranking', 'melhor', 'pior', 'maior', 'menor', 'comparar', 'top'],
            'temporal': ['evolução', 'temporal', 'ao longo', 'tendência', 'crescimento', 'declínio'],
            'regional': ['região', 'regional', 'norte', 'sul', 'nordeste', 'sudeste', 'centro-oeste'],
            'eficiencia': ['eficiência', 'eficiente', 'retorno', 'roi', 'custo-benefício'],
            'politica': ['política', 'estratégia', 'governamental', 'público', 'investimento'],
            'projecao': ['futuro', 'projeção', 'previsão', 'cenário', 'estimativa']
        }
        
        for analysis_type, keywords in type_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return analysis_type
        
        return 'geral'
    
    def _extract_metrics(self, text: str) -> List[str]:
        """Extrai métricas mencionadas no texto."""
        metrics = []
        
        # Padrões para métricas
        metric_patterns = [
            r'IDH[:\s]+([0-9.,]+)',
            r'R\$\s*([0-9.,]+)',
            r'([0-9.,]+)%',
            r'([0-9.,]+)\s*milhões?',
            r'([0-9.,]+)\s*bilhões?'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text)
            metrics.extend(matches)
        
        return metrics[:10]  # Limitar métricas
    
    def _calculate_confidence(self, text: str, context_data: Dict) -> float:
        """Calcula score de confiança da análise."""
        confidence = 0.5  # Base
        
        # Aumentar se há dados de contexto
        if context_data:
            confidence += 0.2
        
        # Aumentar se há métricas específicas
        if re.search(r'\d+[.,]\d+', text):
            confidence += 0.15
        
        # Aumentar se há recomendações
        if any(word in text.lower() for word in ['recomendo', 'sugiro', 'deveria']):
            confidence += 0.1
        
        # Diminuir se há incertezas
        uncertainty_words = ['talvez', 'possivelmente', 'pode ser', 'incerto']
        for word in uncertainty_words:
            if word in text.lower():
                confidence -= 0.05
        
        return min(max(confidence, 0.0), 1.0)
    
    def _suggest_visualizations(self, analysis_type: str, query: str) -> List[Dict]:
        """Sugere visualizações apropriadas."""
        
        viz_suggestions = {
            'ranking': [
                {'type': 'bar_chart', 'title': 'Ranking de Estados', 'priority': 'high'},
                {'type': 'heatmap', 'title': 'Mapa de Calor', 'priority': 'medium'},
                {'type': 'scatter_plot', 'title': 'Dispersão IDH vs Investimento', 'priority': 'medium'}
            ],
            'temporal': [
                {'type': 'line_chart', 'title': 'Evolução Temporal', 'priority': 'high'},
                {'type': 'area_chart', 'title': 'Tendências Acumuladas', 'priority': 'medium'},
                {'type': 'trend_analysis', 'title': 'Análise de Tendências', 'priority': 'high'}
            ],
            'regional': [
                {'type': 'choropleth_map', 'title': 'Mapa do Brasil', 'priority': 'high'},
                {'type': 'box_plot', 'title': 'Distribuição Regional', 'priority': 'medium'},
                {'type': 'radar_chart', 'title': 'Perfil Regional', 'priority': 'medium'}
            ],
            'eficiencia': [
                {'type': 'bubble_chart', 'title': 'Eficiência vs Tamanho', 'priority': 'high'},
                {'type': 'scatter_matrix', 'title': 'Matriz de Correlação', 'priority': 'medium'}
            ]
        }
        
        return viz_suggestions.get(analysis_type, [
            {'type': 'generic_chart', 'title': 'Visualização Geral', 'priority': 'low'}
        ])
    
    def _create_error_response(self, error_msg: str) -> Dict:
        """Cria resposta de erro estruturada."""
        return {
            'response_text': f"Erro na análise: {error_msg}",
            'insights': [],
            'recommendations': [],
            'analysis_type': 'error',
            'metrics_mentioned': [],
            'confidence_score': 0.0,
            'visualization_suggestions': [],
            'timestamp': datetime.now().isoformat(),
            'error': True
        }
    
    def _add_to_history(self, query: str, analysis: Dict):
        """Adiciona análise ao histórico."""
        self.conversation_history.append({
            'query': query,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
        # Manter apenas últimas 10 análises
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def generate_executive_summary(self, analyses: List[Dict]) -> str:
        """Gera resumo executivo baseado em múltiplas análises."""
        if not analyses:
            return "Nenhuma análise disponível para resumo."
        
        summary_prompt = f"""
        Com base nas seguintes análises socioeconômicas, gere um RESUMO EXECUTIVO:
        
        ANÁLISES REALIZADAS:
        {json.dumps([a.get('response_text', '')[:500] for a in analyses], ensure_ascii=False)}
        
        RESUMO DEVE CONTER:
        1. 📊 Principais descobertas (3-4 pontos)
        2. 🎯 Recomendações estratégicas (2-3 ações)
        3. ⚠️ Pontos de atenção (riscos/limitações)
        4. 📈 Próximos passos sugeridos
        
        Seja conciso, objetivo e focado em insights acionáveis.
        """
        
        try:
            response = self.model.generate_content(summary_prompt)
            return response.text
        except Exception as e:
            return f"Erro ao gerar resumo: {str(e)}"
    
    def get_conversation_context(self) -> str:
        """Retorna contexto da conversa atual."""
        if not self.conversation_history:
            return "Nenhuma conversa ativa."
        
        recent_queries = [item['query'] for item in self.conversation_history[-3:]]
        return f"Últimas consultas: {', '.join(recent_queries)}"
    
    def clear_history(self):
        """Limpa histórico de conversas."""
        self.conversation_history = []
        self.analysis_cache = {}
        logger.info("🧹 Histórico de conversas limpo")


# ==================== INTEGRAÇÃO COM CONSULTAS DA FASE 3 ====================

class Phase3Integration:
    """Classe para integrar IA com consultas da Fase 3."""
    
    def __init__(self, ai_engine: AIAnalyticsEngine):
        self.ai_engine = ai_engine
    
    def analyze_ranking_results(self, ranking_data: List[Dict], user_query: str = None) -> Dict:
        """Analisa resultados da Consulta 1 com IA."""
        context = {'consulta_1': ranking_data}
        
        if not user_query:
            user_query = "Analise os resultados do ranking IDH vs investimento e forneça insights estratégicos."
        
        return self.ai_engine.analyze_with_ai(user_query, context)
    
    def analyze_temporal_results(self, temporal_data: Dict, user_query: str = None) -> Dict:
        """Analisa resultados da Consulta 2 com IA."""
        context = {'consulta_2': temporal_data}
        
        if not user_query:
            user_query = "Analise a evolução temporal dos indicadores e identifique tendências importantes."
        
        return self.ai_engine.analyze_with_ai(user_query, context)
    
    def analyze_regional_results(self, regional_data: List[Dict], user_query: str = None) -> Dict:
        """Analisa resultados da Consulta 3 com IA."""
        context = {'consulta_3': regional_data}
        
        if not user_query:
            user_query = "Analise as diferenças regionais e sugira estratégias de desenvolvimento."
        
        return self.ai_engine.analyze_with_ai(user_query, context)
    
    def comprehensive_analysis(self, all_results: Dict, user_query: str = None) -> Dict:
        """Análise abrangente com todos os resultados das consultas."""
        if not user_query:
            user_query = "Faça uma análise abrangente de todos os dados disponíveis e forneça recomendações estratégicas para políticas públicas."
        
        return self.ai_engine.analyze_with_ai(user_query, all_results)


# ==================== FUNÇÃO DE CONVENIÊNCIA ====================

def create_ai_analytics_system() -> Tuple[AIAnalyticsEngine, Phase3Integration]:
    """Cria sistema completo de IA analítica."""
    try:
        ai_engine = AIAnalyticsEngine()
        phase3_integration = Phase3Integration(ai_engine)
        
        logger.info("🤖 Sistema de IA Analítica criado com sucesso")
        return ai_engine, phase3_integration
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar sistema de IA: {e}")
        raise 