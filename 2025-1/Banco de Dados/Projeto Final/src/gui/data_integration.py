"""
Integração de Dados para Interface Gráfica
Centraliza acesso aos dados do banco via consultas analíticas
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
from sqlalchemy import func

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.queries.analytics_queries import ConsultasAnalíticas
from src.database.connection import get_database_connection, init_database

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

    def reload_database(self):
        """Reconecta DataProvider ao banco após importação/limpeza."""
        try:
            # Forçar nova conexão
            get_database_connection(force_sqlite=True)
            init_database(create_db=False, create_tables=False, force_sqlite=True)
            # Recarregar analytics
            self.analytics = ConsultasAnalíticas()
            self.has_real_data = True
            self.clear_cache()
            print("✅ DataProvider reconectado.")
        except Exception as e:
            print(f"❌ Falha ao reconectar DataProvider: {e}")

    # Compatibilidade
    reset_database = reload_database

    # ==================== MÉTRICAS DO DASHBOARD ====================
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Obtém métricas principais para o dashboard"""
        def fetch():
            try:
                if not self.has_real_data or not self.analytics:
                    # Se não há dados reais disponíveis, retornar métricas vazias
                    return {
                        'total_estados': 0,
                        'periodo_anos': 0,
                        'periodo_texto': '-',
                        'total_registros': '0',
                        'ultima_atualizacao': '',
                        'warning': 'Sistema analítico indisponível ou sem dados.'
                    }

                # Usar a conexão já configurada
                with self.db_connection.get_session() as session:
                    from src.models.entities import Estado, Periodo, IndicadorIDH, Despesa

                    # Total de estados
                    total_estados = session.query(Estado).count() or 0

                    # Período de dados – proteger contra tabelas vazias
                    anos_raw = session.query(Periodo.ano).distinct().all()
                    anos_extraidos = [int(a[0]) for a in anos_raw if a and a[0] is not None]

                    if anos_extraidos:
                        periodo_inicio = min(anos_extraidos)
                        periodo_fim = max(anos_extraidos)
                        periodo_anos = periodo_fim - periodo_inicio + 1
                        periodo_texto = f"{periodo_inicio}-{periodo_fim}"
                    else:
                        periodo_anos = 0
                        periodo_texto = '-'

                    # Total de registros
                    total_idh = session.query(IndicadorIDH).count()
                    total_despesas = session.query(Despesa).count()
                    total_registros = total_idh + total_despesas

                    # Última atualização – somente se houver registros
                    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y") if total_registros else ''

                    return {
                        'total_estados': total_estados,
                        'periodo_anos': periodo_anos,
                        'periodo_texto': periodo_texto,
                        'total_registros': f"{total_registros:,}".replace(',', '.') if total_registros else '0',
                        'ultima_atualizacao': ultima_atualizacao
                    }

            except Exception as e:
                print(f"❌ Erro ao buscar métricas do banco: {e}")
                # Em caso de erro inesperado, retornar zeros para evitar dados obsoletos na interface
                return {
                    'total_estados': 0,
                    'periodo_anos': 0,
                    'periodo_texto': '-',
                    'total_registros': '0',
                    'ultima_atualizacao': '',
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
                    error_msg = f"Sistema analítico não disponível - has_real_data: {self.has_real_data}, analytics: {self.analytics is not None}"
                    raise Exception(error_msg)
                
                ranking_data = self.analytics.consulta_1_ranking_idh_investimento(year)
                
                if not ranking_data or len(ranking_data) < 3:
                    error_msg = f"Dados insuficientes encontrados ({len(ranking_data) if ranking_data else 0} estados)"
                    raise Exception(error_msg)
                
                # Filtrar por região se especificado
                if region != 'Todas':
                    ranking_data = [r for r in ranking_data if r['regiao'] == region]
                
                # Preparar dados para scatter plot
                idh_values = [r['idh_geral'] for r in ranking_data]
                despesas_values = [r['investimento_per_capita'] for r in ranking_data]
                estados = [r['uf'] for r in ranking_data]
                regioes = [r['regiao'] for r in ranking_data]
                
                # Calcular correlação
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
                    except Exception as corr_error:
                        correlation = 0
                else:
                    correlation = 0
                
                result = {
                    'idh_values': idh_values,
                    'despesas_values': despesas_values,
                    'idh': idh_values,  # Alias para compatibilidade com VisualizationsTab
                    'investimento': despesas_values,  # Alias para compatibilidade
                    'estados': estados,
                    'regioes': regioes,
                    'correlation': correlation,
                    'year': year,
                    'region': region,
                    'total_states': len(ranking_data)
                }
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Erro ao buscar dados de correlação do banco: {error_msg}")
                
                # Retornar estrutura vazia em vez de dados simulados
                result = {
                    'idh_values': [],
                    'despesas_values': [],
                    'idh': [],
                    'investimento': [],
                    'estados': [],
                    'regioes': [],
                    'correlation': 0,
                    'year': year,
                    'region': region,
                    'total_states': 0,
                    'error': error_msg
                }
                return result
                
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
                
                # CORREÇÃO: Usar os campos corretos dos dados retornados
                return {
                    'regioes': [r['regiao'] for r in regioes_data],
                    'idh_values': [r.get('idh_regional_medio', r.get('idh_geral', 0.7)) for r in regioes_data],
                    'gastos_values': [r.get('investimento_total_milhoes', r.get('investimento_per_capita', 2500)) / 1000 for r in regioes_data],  # Converter para milhares
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
                anos = [2019, 2020, 2021, 2022, 2023]
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
                    'anos': [2019, 2020, 2021, 2022, 2023],
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

    def get_temporal_data(self) -> Dict[str, Any]:
        """Compatibilidade: dados simples para tendências temporais (anos, idh, investimento)."""
        def fetch():
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")
                evolucao = self.analytics.consulta_2_evolucao_temporal()
                series = evolucao.get('evolucao_anual', []) if isinstance(evolucao, dict) else []
                if not series:
                    raise Exception("Dados de evolução temporal vazios")
                anos = [item.get('ano') for item in series]
                idh_medio = [item.get('idh_geral') for item in series]
                investimento_medio = [item.get('investimento_total') for item in series]
                return {
                    'anos': anos,
                    'idh_medio': idh_medio,
                    'investimento_medio': investimento_medio
                }
            except Exception as e:
                print(f"⚠️ Erro ao obter dados temporais simples: {e}")
                # Retornar dados simulados em caso de falha
                return {
                    'anos': [],
                    'idh_medio': [],
                    'investimento_medio': [],
                    'error': str(e)
                }
        return self._get_from_cache_or_fetch('temporal_simple', fetch)

    # === Wrappers de compatibilidade ===
    def get_efficiency_data(self, year: int = 2023):
        """Wrapper para compatibilidade antiga"""
        raw = self.get_state_efficiency_data(year=year)
        # Adaptar para estrutura esperada (idh, investimento)
        if raw and raw.get('estados'):
            # Usar média nacional para normalizar investimento se necessário
            estados = raw['estados']
            # Recuperar ranking original para IDH e investimento
            try:
                ranking = self.analytics.consulta_1_ranking_idh_investimento(year)
                idh_map = {r['uf']: r['idh_geral'] for r in ranking}
                inv_map = {r['uf']: r['total_investimento_milhoes'] for r in ranking}
                idh_vals = [idh_map.get(uf, 0) for uf in estados]
                inv_vals = [inv_map.get(uf, 1) for uf in estados]
            except Exception:
                # Fallback simples
                idh_vals = [0]*len(estados)
                inv_vals = [1]*len(estados)
            raw.update({'idh': np.array(idh_vals), 'investimento': np.array(inv_vals)})
        return raw

    def get_sectoral_data(self, year: int = 2023):
        """Wrapper para compatibilidade antiga"""
        return self.get_sectoral_distribution_data(year=year)

    def get_comparative_data(self, year: int = 2023):
        """Wrapper para compatibilidade antiga"""
        raw = self.get_comparative_analysis_data(year=year)
        # Ajustar estrutura esperada: estados, idh, investimento_norm
        try:
            ranking = self.analytics.consulta_1_ranking_idh_investimento(year)
            estados = [r['uf'] for r in ranking]
            idh_vals = np.array([r['idh_geral'] for r in ranking])
            inv_vals = np.array([r['total_investimento_milhoes'] for r in ranking])
            inv_norm = inv_vals / np.max(inv_vals) if len(inv_vals)>0 else inv_vals
            return {
                'estados': estados,
                'idh': idh_vals,
                'investimento_norm': inv_norm
            }
        except Exception as e:
            print(f"⚠️ Erro ao adaptar dados comparativos: {e}")
            return {}

    # ==================== NOVO MÉTODO: Evolução IDH por Região ====================
    def get_idh_evolution_by_region(self, anos: list = None) -> Dict[str, Any]:
        """Retorna evolução do IDH por região para os anos solicitados.

        Args:
            anos: Lista de anos inteiros. Se None, detecta anos disponíveis no banco.
        Returns:
            Dict com chaves: anos (list[int]), regioes_data (dict[str, list[float]])
        """
        def fetch(anos_key="auto"):
            try:
                if not self.has_real_data or not self.analytics:
                    raise Exception("Sistema analítico não disponível")

                with self.db_connection.get_session() as session:
                    from src.models.entities import Regiao, Estado, IndicadorIDH, Periodo
                    # Detectar anos se não fornecido
                    if anos is None or len(anos) == 0:
                        anos_query = session.query(Periodo.ano).distinct().order_by(Periodo.ano).all()
                        anos_detectados = [int(a[0]) for a in anos_query if a and a[0] is not None]
                        anos_lista = sorted(anos_detectados)
                    else:
                        anos_lista = sorted(list(set(anos)))

                    if not anos_lista:
                        raise Exception("Nenhum ano disponível para evolucao por região")

                    # Obter lista de regiões
                    regioes = session.query(Regiao.nome_regiao).all()
                    regioes_nomes = [r[0] for r in regioes]
                    regioes_data = {r: [0]*len(anos_lista) for r in regioes_nomes}

                    # Fazer query para média IDH por ano e região
                    q = session.query(
                        Regiao.nome_regiao.label("regiao"),
                        Periodo.ano.label("ano"),
                        func.avg(IndicadorIDH.idh_geral).label("idh_medio")
                    ).select_from(IndicadorIDH)
                    q = q.join(Estado, Estado.id == IndicadorIDH.estado_id)
                    q = q.join(Regiao, Estado.regiao_id == Regiao.id)
                    q = q.join(Periodo, Periodo.id == IndicadorIDH.periodo_id)
                    q = q.filter(Periodo.ano.in_(anos_lista))
                    q = q.group_by(Regiao.nome_regiao, Periodo.ano)

                    resultados = q.all()
                    for row in resultados:
                        regiao = row.regiao
                        ano = row.ano
                        idh_val = float(row.idh_medio or 0)
                        if regiao in regioes_data and ano in anos_lista:
                            idx = anos_lista.index(ano)
                            regioes_data[regiao][idx] = idh_val

                    return {
                        'anos': anos_lista,
                        'regioes_data': regioes_data
                    }

            except Exception as e:
                print(f"❌ Erro ao buscar evolução IDH por região: {e}")
                return {
                    'anos': anos if anos else [],
                    'regioes_data': {},
                    'error': str(e)
                }

        cache_key_anos = "-".join(map(str, anos)) if anos else "auto"
        return self._get_from_cache_or_fetch('idh_evolucao_regiao', fetch, anos_key=cache_key_anos)


# Instância global do provedor de dados
data_provider = DataProvider()