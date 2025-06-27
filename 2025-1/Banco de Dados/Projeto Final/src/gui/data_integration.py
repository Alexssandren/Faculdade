"""
Integração de Dados para Interface Gráfica
Centraliza acesso aos dados do banco via consultas analíticas
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.queries.analytics_queries import ConsultasAnalíticas
from src.database.connection import get_database_connection

class DataProvider:
    """Provedor centralizado de dados para a interface gráfica"""
    
    def __init__(self):
        """Inicializa o provedor de dados"""
        self.db_connection = get_database_connection()
        self.analytics = None
        self.has_real_data = False
        self.cache = {}
        self.cache_timeout = 300  # 5 minutos
        
        # Tentar inicializar sistema analítico
        self._initialize_analytics()
    
    def _initialize_analytics(self):
        """Inicializa o sistema de consultas analíticas"""
        try:
            self.analytics = ConsultasAnalíticas()
            self.has_real_data = True
            print("✅ Sistema analítico inicializado com sucesso")
        except Exception as e:
            print(f"⚠️ Falha ao inicializar sistema analítico: {e}")
            self.has_real_data = False
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Gera chave única para cache baseada no método e parâmetros"""
        params_str = "_".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return f"{method_name}_{params_str}" if params_str else method_name
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if cache_key not in self.cache:
            return False
        return (time.time() - self.cache[cache_key]['timestamp']) < self.cache_timeout
    
    def _get_from_cache_or_fetch(self, method_name: str, fetch_func, **kwargs):
        """Obtém dados do cache ou executa função de busca"""
        cache_key = self._get_cache_key(method_name, **kwargs)
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # Buscar dados
        data = fetch_func(**kwargs)
        
        # Armazenar no cache
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        return data
    
    def clear_cache(self):
        """Limpa o cache de dados"""
        self.cache.clear()
        print("🧹 Cache de dados limpo")

    # ==================== MÉTRICAS DO DASHBOARD ====================
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Obtém métricas principais para o dashboard"""
        def fetch():
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                # Usar a conexão já configurada
                with self.db_connection.get_session() as session:
                    from src.models.entities import Estado, Periodo, IndicadorIDH, Despesa
                    
                    # Total de estados
                    total_estados = session.query(Estado).count()
                    
                    # Período de dados - com proteção robusta
                    try:
                        periodos_query = session.query(Periodo.ano).distinct().all()
                        anos = []
                        
                        for periodo_result in periodos_query:
                            if periodo_result and periodo_result[0] is not None:
                                ano_valor = periodo_result[0]
                                
                                # Múltiplas tentativas de conversão
                                try:
                                    if isinstance(ano_valor, (int, float)):
                                        anos.append(int(ano_valor))
                                    elif isinstance(ano_valor, str):
                                        anos.append(int(ano_valor))
                                    elif isinstance(ano_valor, bytes):
                                        # Tentar diferentes métodos de conversão de bytes
                                        try:
                                            # Método 1: bytes para int direto (little endian)
                                            if len(ano_valor) >= 4:
                                                anos.append(int.from_bytes(ano_valor[:4], byteorder='little'))
                                            else:
                                                anos.append(int.from_bytes(ano_valor, byteorder='little'))
                                        except:
                                            # Método 2: tentar decodificar como string primeiro
                                            try:
                                                anos.append(int(ano_valor.decode('utf-8')))
                                            except:
                                                # Método 3: usar valor padrão
                                                pass
                                    else:
                                        # Tentar conversão direta
                                        anos.append(int(ano_valor))
                                        
                                except (ValueError, TypeError, OverflowError) as e:
                                    # Log do erro específico para debugging
                                    print(f"⚠️ Erro ao converter ano {ano_valor} (tipo: {type(ano_valor)}): {e}")
                                    continue
                        
                        # Se não conseguiu nenhum ano, usar valores padrão
                        if not anos:
                            anos = [2019, 2020, 2021, 2022, 2023]
                            print("⚠️ Usando anos padrão pois não foi possível ler do banco")
                        
                        periodo_inicio = min(anos)
                        periodo_fim = max(anos)
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao processar períodos: {e}")
                        # Valores padrão em caso de erro
                        periodo_inicio = 2019
                        periodo_fim = 2023
                        anos = [2019, 2020, 2021, 2022, 2023]
                    
                    # Total de registros
                    total_idh = session.query(IndicadorIDH).count()
                    total_despesas = session.query(Despesa).count()
                    total_registros = total_idh + total_despesas
                    
                    print(f"📊 Contagem registros: IDH={total_idh}, Despesas={total_despesas}, Total={total_registros}")
                    
                    # Última atualização
                    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y")
                    
                    return {
                        'total_estados': total_estados or 27,
                        'periodo_anos': periodo_fim - periodo_inicio + 1,
                        'periodo_texto': f"{periodo_inicio}-{periodo_fim}",
                        'total_registros': f"{total_registros:,}".replace(',', '.'),
                        'ultima_atualizacao': ultima_atualizacao
                    }
                    
            except Exception as e:
                print(f"❌ Erro ao buscar métricas do banco: {e}")
                # Retornar estrutura com valores padrão conhecidos
                return {
                    'total_estados': 27,
                    'periodo_anos': 5,
                    'periodo_texto': '2019-2023',
                    'total_registros': '1.131',  # Valor conhecido: 135 IDH + 996 Despesas
                    'ultima_atualizacao': datetime.now().strftime("%d/%m/%Y"),
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('dashboard_metrics', fetch)
        
    def get_dashboard_insights(self) -> List[Dict[str, Any]]:
        """Obtém insights principais para o dashboard"""
        def fetch():
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                # Buscar insights reais das consultas analíticas
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(2023)
                evolucao_data = self.analytics.consulta_2_evolucao_temporal()
                regional_data = self.analytics.consulta_3_analise_regional()
                
                insights = []
                
                # Insight 1: Liderança em IDH
                if ranking_data:
                    top_estado = ranking_data[0]
                    insights.append({
                        'title': 'Liderança em IDH',
                        'insight': f"{top_estado['estado']} mantém o melhor IDH ({top_estado['idh_geral']:.3f})",
                        'trend': 'up',
                        'color': '#10b981'
                    })
                
                # Insight 2: Crescimento regional
                if regional_data and 'ranking_regioes' in regional_data:
                    regioes = regional_data['ranking_regioes']
                    melhor_crescimento = max(regioes, key=lambda x: x.get('crescimento_idh', 0))
                    insights.append({
                        'title': 'Crescimento Regional',
                        'insight': f"Região {melhor_crescimento['regiao']} lidera em crescimento",
                        'trend': 'up',
                        'color': '#06b6d4'
                    })
                
                # Insight 3: Eficiência
                if ranking_data:
                    eficientes = [r for r in ranking_data if r['eficiencia_investimento']['categoria'] == 'Alta']
                    insights.append({
                        'title': 'Eficiência de Gastos',
                        'insight': f"{len(eficientes)} estados demonstram alta eficiência",
                        'trend': 'neutral',
                        'color': '#f59e0b'
                    })
                
                # Insight 4: Desafio
                if ranking_data:
                    baixo_idh = [r for r in ranking_data if r['idh_geral'] < 0.7]
                    insights.append({
                        'title': 'Oportunidades de Melhoria',
                        'insight': f"{len(baixo_idh)} estados necessitam atenção especial",
                        'trend': 'down',
                        'color': '#ef4444'
                    })
                
                return insights[:4]  # Máximo 4 insights
                
            except Exception as e:
                print(f"❌ Erro ao buscar insights do banco: {e}")
                # Retornar insights vazios em caso de erro
                return [{
                    'title': 'Sistema Indisponível',
                    'insight': 'Não foi possível carregar insights do banco de dados',
                    'trend': 'neutral',
                    'color': '#6b7280'
                }]
                
        return self._get_from_cache_or_fetch('dashboard_insights', fetch)

    # ==================== DADOS PARA VISUALIZAÇÕES ====================
    
    def get_correlation_data(self, year: int = 2023, region: str = 'Todas') -> Dict[str, Any]:
        """Obtém dados para gráfico de correlação IDH vs Despesas"""
        def fetch(year, region):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(year)
                
                if not ranking_data or len(ranking_data) < 3:
                    raise Exception(f"Dados insuficientes encontrados ({len(ranking_data) if ranking_data else 0} estados)")
                
                # Filtrar por região se especificado
                if region != 'Todas':
                    ranking_data = [r for r in ranking_data if r['regiao'] == region]
                
                # Preparar dados para scatter plot
                idh_values = [r['idh_geral'] for r in ranking_data]
                despesas_values = [r['investimento_per_capita'] for r in ranking_data]
                estados = [r['uf'] for r in ranking_data]
                regioes = [r['regiao'] for r in ranking_data]
                
                # Calcular correlação
                import numpy as np
                if len(idh_values) > 1 and len(despesas_values) > 1:
                    try:
                        # Verificar se há valores válidos (não NaN)
                        valid_idh = [x for x in idh_values if not np.isnan(x) and x > 0]
                        valid_despesas = [x for x in despesas_values if not np.isnan(x) and x > 0]
                        
                        if len(valid_idh) > 1 and len(valid_despesas) > 1 and len(valid_idh) == len(valid_despesas):
                            correlation = np.corrcoef(valid_idh, valid_despesas)[0, 1]
                            if np.isnan(correlation):
                                correlation = 0
                        else:
                            correlation = 0
                    except:
                        correlation = 0
                else:
                    correlation = 0
                
                return {
                    'idh_values': idh_values,
                    'despesas_values': despesas_values,
                    'estados': estados,
                    'regioes': regioes,
                    'correlation': correlation,
                    'year': year,
                    'region': region,
                    'total_states': len(ranking_data)
                }
                
            except Exception as e:
                print(f"❌ Erro ao buscar dados de correlação do banco: {e}")
                # Retornar estrutura vazia em vez de dados simulados
                return {
                    'idh_values': [],
                    'despesas_values': [],
                    'estados': [],
                    'regioes': [],
                    'correlation': 0,
                    'year': year,
                    'region': region,
                    'total_states': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('correlation_data', fetch, year=year, region=region)
    
    def get_regional_analysis_data(self, year: int = 2023) -> Dict[str, Any]:
        """Obtém dados para análise regional"""
        def fetch(year):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                regional_data = self.analytics.consulta_3_analise_regional()
                
                if not regional_data or 'ranking_regioes' not in regional_data:
                    raise Exception("Dados de análise regional não encontrados no banco")
                
                regioes_data = regional_data['ranking_regioes']
                
                return {
                    'regioes': [r['regiao'] for r in regioes_data],
                    'idh_values': [r.get('idh_medio', r.get('idh_geral', 0.7)) for r in regioes_data],
                    'gastos_values': [r.get('investimento_per_capita', r.get('despesa_per_capita', 2500)) for r in regioes_data],
                    'num_estados': [r.get('total_estados', 5) for r in regioes_data],
                    'year': year,
                    'total_records': len(regioes_data)
                }
                
            except Exception as e:
                print(f"❌ Erro ao buscar dados regionais do banco: {e}")
                return {
                    'regioes': [],
                    'idh_values': [],
                    'gastos_values': [],
                    'num_estados': [],
                    'year': year,
                    'total_records': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('regional_analysis', fetch, year=year)
    
    def get_temporal_trends_data(self, region: str = 'Todas') -> Dict[str, Any]:
        """Obtém dados para análise de tendências temporais"""
        def fetch(region):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                evolucao_data = self.analytics.consulta_2_evolucao_temporal()
                
                if not evolucao_data:
                    raise Exception("Dados de evolução temporal não encontrados no banco")
                
                # Verificar se tem a estrutura esperada
                if 'series_temporais' not in evolucao_data:
                    # Usar dados diretos da consulta se não tem a estrutura esperada
                    evolucao_data = {
                        'series_temporais': evolucao_data if isinstance(evolucao_data, list) else [],
                        'crescimento_medio_anual': 0.01
                    }
                
                series_data = evolucao_data['series_temporais']
                
                # Organizar dados por região do banco
                anos = list(range(2019, 2024))
                regioes_tendencias = {}
                
                # Processar dados reais do banco por região
                for item in series_data:
                    regiao = item.get('regiao', 'Desconhecida')
                    ano = item.get('ano')
                    idh_medio = item.get('idh_medio', 0)
                    
                    if regiao not in regioes_tendencias:
                        regioes_tendencias[regiao] = {}
                    
                    regioes_tendencias[regiao][ano] = idh_medio
                
                # Garantir que todas as regiões tenham dados para todos os anos
                for regiao in regioes_tendencias:
                    valores_ordenados = []
                    for ano in anos:
                        valor = regioes_tendencias[regiao].get(ano, 0)
                        valores_ordenados.append(valor)
                    regioes_tendencias[regiao] = valores_ordenados
                
                return {
                    'anos': anos,
                    'regioes_data': regioes_tendencias,
                    'region_filter': region,
                    'growth_rate': evolucao_data.get('crescimento_medio_anual', 0)
                }
                
            except Exception as e:
                print(f"❌ Erro ao buscar dados temporais do banco: {e}")
                # Retornar estrutura vazia em vez de dados simulados
                return {
                    'anos': list(range(2019, 2024)),
                    'regioes_data': {},
                    'region_filter': region,
                    'growth_rate': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('temporal_trends', fetch, region=region)
    
    def get_state_efficiency_data(self, year: int = 2023) -> Dict[str, Any]:
        """Obtém dados de eficiência por estado"""
        def fetch(year):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(year)
                
                if not ranking_data or len(ranking_data) < 10:
                    raise Exception(f"Dados de eficiência insuficientes ({len(ranking_data) if ranking_data else 0} estados)")
                
                # Selecionar top 10 estados por eficiência
                efficient_states = sorted(ranking_data, 
                                        key=lambda x: x['eficiencia_investimento']['score'], 
                                        reverse=True)[:10]
                
                estados = [s['uf'] for s in efficient_states]
                efficiency_values = [s['eficiencia_investimento']['score'] for s in efficient_states]
                categorias = [s['eficiencia_investimento']['categoria'] for s in efficient_states]
                
                return {
                    'estados': estados,
                    'efficiency_values': efficiency_values,
                    'categorias': categorias,
                    'year': year,
                    'media_nacional': sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0
                }
                
            except Exception as e:
                print(f"❌ Erro ao buscar dados de eficiência do banco: {e}")
                return {
                    'estados': [],
                    'efficiency_values': [],
                    'categorias': [],
                    'year': year,
                    'media_nacional': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('state_efficiency', fetch, year=year)
    
    def get_sectoral_distribution_data(self, year: int = 2023) -> Dict[str, Any]:
        """Obtém dados de distribuição setorial"""
        def fetch(year):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                # Buscar dados de distribuição por categoria
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(year)
                
                if not ranking_data or len(ranking_data) < 5:
                    raise Exception(f"Dados setoriais insuficientes ({len(ranking_data) if ranking_data else 0} estados)")
                
                # Agregar investimentos por setor
                total_saude = sum(r['investimento_saude'] for r in ranking_data)
                total_educacao = sum(r['investimento_educacao'] for r in ranking_data)
                total_assistencia = sum(r['investimento_assistencia'] for r in ranking_data)
                total_geral = sum(r['total_investimento_milhoes'] for r in ranking_data)
                
                # Calcular outros setores
                total_outros = max(0, total_geral - total_saude - total_educacao - total_assistencia)
                
                if total_geral > 0:
                    return {
                        'setores': ['Educação', 'Saúde', 'Assistência Social', 'Outros'],
                        'valores': [
                            (total_educacao / total_geral) * 100,
                            (total_saude / total_geral) * 100,
                            (total_assistencia / total_geral) * 100,
                            (total_outros / total_geral) * 100
                        ],
                        'year': year,
                        'total_investimento': total_geral
                    }
                else:
                    raise Exception("Total de investimentos é zero")
                    
            except Exception as e:
                print(f"❌ Erro ao buscar dados setoriais do banco: {e}")
                return {
                    'setores': [],
                    'valores': [],
                    'year': year,
                    'total_investimento': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('sectoral_distribution', fetch, year=year)
    
    def get_comparative_analysis_data(self, year: int = 2023) -> Dict[str, Any]:
        """Obtém dados para análise comparativa de estados"""
        def fetch(year):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(year)
                
                if not ranking_data or len(ranking_data) < 20:
                    raise Exception(f"Dados comparativos insuficientes ({len(ranking_data) if ranking_data else 0} estados)")
                
                # Top 10 e Bottom 10
                top_10 = ranking_data[:10]
                bottom_10 = ranking_data[-10:]
                
                return {
                    'top_states': {
                        'estados': [s['uf'] for s in top_10],
                        'idh_values': [s['idh_geral'] for s in top_10],
                        'label': 'Melhores IDH'
                    },
                    'bottom_states': {
                        'estados': [s['uf'] for s in bottom_10],
                        'idh_values': [s['idh_geral'] for s in bottom_10],
                        'label': 'Menores IDH'
                    },
                    'year': year,
                    'gap_idh': top_10[0]['idh_geral'] - bottom_10[-1]['idh_geral'] if top_10 and bottom_10 else 0
                }
                
            except Exception as e:
                print(f"❌ Erro ao buscar dados comparativos do banco: {e}")
                return {
                    'top_states': {'estados': [], 'idh_values': [], 'label': 'Melhores IDH'},
                    'bottom_states': {'estados': [], 'idh_values': [], 'label': 'Menores IDH'},
                    'year': year,
                    'gap_idh': 0,
                    'error': str(e)
                }
                
        return self._get_from_cache_or_fetch('comparative_analysis', fetch, year=year)


# Instância global do provedor de dados
data_provider = DataProvider()