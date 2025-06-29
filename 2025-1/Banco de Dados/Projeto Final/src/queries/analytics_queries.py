"""
Consultas Analíticas Avançadas - Sistema DEC7588
Fase 3: Análises socioeconômicas especializadas
"""

import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, text
from decimal import Decimal
from datetime import datetime, date
import logging

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database_connection
from src.models.entities import (
    Regiao, Estado, Municipio, OrgaoPublico, FonteRecurso,
    CategoriaDespesa, Periodo, Orcamento, Despesa, 
    IndicadorIDH, Usuario, Relatorio
)

logger = logging.getLogger(__name__)

class ConsultasAnalíticas:
    """
    Classe principal para consultas analíticas especializadas
    """
    
    def __init__(self):
        self.db_connection = get_database_connection()
        self.logger = logger
    
    # ==================== CONSULTA 1: RANKING IDH vs INVESTIMENTO ====================
    
    def consulta_1_ranking_idh_investimento(self, ano: int = 2023) -> List[Dict[str, Any]]:
        """
        CONSULTA 1: Ranking de Estados por IDH vs Investimento Público
        
        Análise comparativa entre desenvolvimento humano e investimentos públicos
        por estado, revelando correlações e oportunidades de melhoria.
        
        Args:
            ano: Ano de referência para análise
            
        Returns:
            List[Dict]: Ranking completo com métricas analíticas
        """
        try:
            with self.db_connection.get_session() as session:
                
                # Query complexa com múltiplas agregações e joins
                query = session.query(
                    Estado.id,
                    Estado.nome_estado,
                    Estado.sigla_uf,
                    Regiao.nome_regiao,
                    
                    # Métricas IDH
                    func.avg(IndicadorIDH.idh_geral).label('idh_medio'),
                    func.avg(IndicadorIDH.idh_educacao).label('idh_educacao'),
                    func.avg(IndicadorIDH.idh_longevidade).label('idh_longevidade'),
                    func.avg(IndicadorIDH.idh_renda).label('idh_renda'),
                    func.avg(IndicadorIDH.ranking_nacional).label('ranking_medio'),
                    
                    # Métricas de Investimento
                    func.sum(Despesa.valor_milhoes).label('total_investimento'),
                    func.avg(Despesa.valor_per_capita).label('investimento_per_capita'),
                    func.count(Despesa.id).label('total_projetos'),
                    
                    # Métricas por Categoria
                    func.sum(
                        case(
                            (CategoriaDespesa.nome_categoria.like('%Saúde%'), Despesa.valor_milhoes),
                            else_=0
                        )
                    ).label('investimento_saude'),
                    
                    func.sum(
                        case(
                            (CategoriaDespesa.nome_categoria.like('%Educação%'), Despesa.valor_milhoes),
                            else_=0
                        )
                    ).label('investimento_educacao'),
                    
                    func.sum(
                        case(
                            (CategoriaDespesa.nome_categoria.like('%Assistência%'), Despesa.valor_milhoes),
                            else_=0
                        )
                    ).label('investimento_assistencia'),
                    
                ).select_from(
                    Estado
                ).join(
                    Regiao, Estado.regiao_id == Regiao.id
                ).join(
                    IndicadorIDH, Estado.id == IndicadorIDH.estado_id
                ).join(
                    Despesa, Estado.id == Despesa.estado_id
                ).join(
                    CategoriaDespesa, Despesa.categoria_despesa_id == CategoriaDespesa.id
                ).join(
                    Periodo, Despesa.periodo_id == Periodo.id
                ).filter(
                    and_(
                        Periodo.ano == ano,
                        IndicadorIDH.periodo_id.in_(
                            session.query(Periodo.id).filter(Periodo.ano == ano)
                        )
                    )
                ).group_by(
                    Estado.id,
                    Estado.nome_estado,
                    Estado.sigla_uf,
                    Regiao.nome_regiao
                ).order_by(
                    func.avg(IndicadorIDH.idh_geral).desc()
                )
                
                # Tentar executar query e capturar informações detalhadas
                try:
                    resultados = query.all()
                    
                    if len(resultados) == 0:
                        # Verificar dados das tabelas principais em caso de resultado vazio
                        count_estados = session.query(Estado).count()
                        count_idh = session.query(IndicadorIDH).count()
                        count_despesas = session.query(Despesa).count()
                        count_periodos = session.query(Periodo).count()
                        
                        # Verificar se existe o ano específico
                        periodo_ano = session.query(Periodo).filter(Periodo.ano == ano).first()
                        if not periodo_ano:
                            # Listar anos disponíveis para debugging
                            anos_disponiveis = session.query(Periodo.ano).distinct().all()
                            print(f"❌ Período {ano} não encontrado. Anos disponíveis: {[a[0] for a in anos_disponiveis]}")
                    
                except Exception as query_error:
                    print(f"❌ Erro ao executar query SQL: {query_error}")
                    return []
                
                # Processar e enriquecer resultados
                ranking = []
                for i, row in enumerate(resultados, 1):
                    
                    # Calcular índices analíticos
                    eficiencia_investimento = self._calcular_eficiencia_investimento(
                        row.idh_medio, row.total_investimento
                    )
                    
                    categoria_desempenho = self._categorizar_desempenho(
                        row.idh_medio, row.ranking_medio
                    )
                    
                    distribuicao_investimento = self._analisar_distribuicao_investimento(
                        row.investimento_saude,
                        row.investimento_educacao, 
                        row.investimento_assistencia,
                        row.total_investimento
                    )
                    
                    item_ranking = {
                        'posicao_ranking': i,
                        'estado_id': row.id,
                        'estado': row.nome_estado,
                        'uf': row.sigla_uf,
                        'regiao': row.nome_regiao,
                        
                        # Métricas IDH
                        'idh_geral': float(row.idh_medio or 0),
                        'idh_educacao': float(row.idh_educacao or 0),
                        'idh_longevidade': float(row.idh_longevidade or 0),
                        'idh_renda': float(row.idh_renda or 0),
                        'ranking_nacional': int(row.ranking_medio or 0),
                        
                        # Métricas Investimento
                        'total_investimento_milhoes': float(row.total_investimento or 0),
                        'investimento_per_capita': float(row.investimento_per_capita or 0),
                        'total_projetos': int(row.total_projetos or 0),
                        
                        # Investimento por Área
                        'investimento_saude': float(row.investimento_saude or 0),
                        'investimento_educacao': float(row.investimento_educacao or 0),
                        'investimento_assistencia': float(row.investimento_assistencia or 0),
                        
                        # Análises Calculadas
                        'eficiencia_investimento': eficiencia_investimento,
                        'categoria_desempenho': categoria_desempenho,
                        'distribuicao_investimento': distribuicao_investimento,
                        
                        # Insights
                        'principal_area_investimento': self._identificar_principal_area(
                            row.investimento_saude,
                            row.investimento_educacao,
                            row.investimento_assistencia
                        ),
                        
                        'potencial_melhoria': self._avaliar_potencial_melhoria(
                            row.idh_medio, row.total_investimento
                        )
                    }
                    
                    ranking.append(item_ranking)

                return ranking
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro na Consulta 1: {error_msg}")
            return []
    
    # ==================== CONSULTA 2: EVOLUÇÃO TEMPORAL ====================
    
    def consulta_2_evolucao_temporal(self, estado_id: int = None) -> Dict[str, Any]:
        """
        CONSULTA 2: Evolução Temporal de IDH e Investimentos
        
        Análise da evolução histórica de indicadores socioeconômicos,
        identificando tendências, sazonalidades e pontos de inflexão.
        
        Args:
            estado_id: ID do estado específico (None para análise nacional)
            
        Returns:
            Dict: Análise temporal completa com projeções
        """
        try:
            with self.db_connection.get_session() as session:
                
                # Query base para evolução temporal
                query = session.query(
                    Periodo.ano,
                    
                    # Agregações IDH
                    func.avg(IndicadorIDH.idh_geral).label('idh_medio_ano'),
                    func.avg(IndicadorIDH.idh_educacao).label('idh_educacao_ano'),
                    func.avg(IndicadorIDH.idh_longevidade).label('idh_longevidade_ano'),
                    func.avg(IndicadorIDH.idh_renda).label('idh_renda_ano'),
                    
                    # Agregações Investimento
                    func.sum(Despesa.valor_milhoes).label('investimento_total_ano'),
                    func.avg(Despesa.valor_per_capita).label('investimento_per_capita_ano'),
                    func.count(Despesa.id).label('projetos_total_ano'),
                    
                    # Análises por órgão
                    func.count(func.distinct(Despesa.orgao_publico_id)).label('orgaos_ativos'),
                    
                ).select_from(
                    Periodo
                ).join(
                    IndicadorIDH, Periodo.id == IndicadorIDH.periodo_id
                ).join(
                    Despesa, Periodo.id == Despesa.periodo_id
                )
                
                # Filtro por estado se especificado
                if estado_id:
                    query = query.filter(
                        and_(
                            IndicadorIDH.estado_id == estado_id,
                            Despesa.estado_id == estado_id
                        )
                    )
                
                query = query.group_by(Periodo.ano).order_by(Periodo.ano)
                
                dados_temporais = query.all()
                
                # Calcular tendências e projeções
                analise_temporal = {
                    'periodo_analise': {
                        'ano_inicial': dados_temporais[0].ano if dados_temporais else None,
                        'ano_final': dados_temporais[-1].ano if dados_temporais else None,
                        'total_anos': len(dados_temporais)
                    },
                    'evolucao_anual': [],
                    'tendencias': {},
                    'projecoes': {},
                    'insights': []
                }
                
                # Processar dados anuais
                for i, ano_data in enumerate(dados_temporais):
                    
                    # Calcular variações ano anterior
                    variacao_idh = 0
                    variacao_investimento = 0
                    
                    if i > 0:
                        ano_anterior = dados_temporais[i-1]
                        variacao_idh = ((ano_data.idh_medio_ano - ano_anterior.idh_medio_ano) / ano_anterior.idh_medio_ano) * 100
                        variacao_investimento = ((ano_data.investimento_total_ano - ano_anterior.investimento_total_ano) / ano_anterior.investimento_total_ano) * 100
                    
                    analise_temporal['evolucao_anual'].append({
                        'ano': ano_data.ano,
                        'idh_geral': float(ano_data.idh_medio_ano or 0),
                        'idh_educacao': float(ano_data.idh_educacao_ano or 0),
                        'idh_longevidade': float(ano_data.idh_longevidade_ano or 0),
                        'idh_renda': float(ano_data.idh_renda_ano or 0),
                        'investimento_total': float(ano_data.investimento_total_ano or 0),
                        'investimento_per_capita': float(ano_data.investimento_per_capita_ano or 0),
                        'total_projetos': int(ano_data.projetos_total_ano or 0),
                        'orgaos_ativos': int(ano_data.orgaos_ativos or 0),
                        'variacao_idh_percent': round(variacao_idh, 2),
                        'variacao_investimento_percent': round(variacao_investimento, 2)
                    })
                
                # Calcular tendências gerais
                if len(dados_temporais) >= 2:
                    analise_temporal['tendencias'] = self._calcular_tendencias(dados_temporais)
                    analise_temporal['projecoes'] = self._gerar_projecoes(dados_temporais)
                    analise_temporal['insights'] = self._gerar_insights_temporais(dados_temporais)
                

                return analise_temporal
                
        except Exception as e:
            self.logger.error(f"❌ Erro na Consulta 2: {e}")
            return {}
    
    # ==================== CONSULTA 3: ANÁLISE REGIONAL ====================
    
    def consulta_3_analise_regional(self) -> Dict[str, Any]:
        """
        CONSULTA 3: Análise Comparativa Regional
        
        Comparação detalhada entre as 5 regiões brasileiras, identificando
        disparidades, padrões regionais e oportunidades de desenvolvimento.
        
        Returns:
            Dict: Análise regional completa com rankings e recomendações
        """
        try:
            with self.db_connection.get_session() as session:
                
                # Query para análise regional
                query = session.query(
                    Regiao.id,
                    Regiao.nome_regiao,
                    
                    # Contadores
                    func.count(func.distinct(Estado.id)).label('total_estados'),
                    
                    # Métricas IDH Regionais
                    func.avg(IndicadorIDH.idh_geral).label('idh_regional_medio'),
                    func.min(IndicadorIDH.idh_geral).label('idh_regional_min'),
                    func.max(IndicadorIDH.idh_geral).label('idh_regional_max'),
                    # SQLite não tem STDDEV, vamos calcular manualmente depois
                    func.count(IndicadorIDH.idh_geral).label('idh_count'),
                    
                    # Métricas Investimento Regionais
                    func.sum(Despesa.valor_milhoes).label('investimento_regional_total'),
                    func.avg(Despesa.valor_milhoes).label('investimento_medio_projeto'),
                    func.avg(Despesa.valor_per_capita).label('investimento_per_capita_regional'),
                    func.count(Despesa.id).label('total_projetos_regional'),
                    
                    # Distribuição por categorias
                    func.sum(
                        case(
                            (CategoriaDespesa.nome_categoria.like('%Saúde%'), Despesa.valor_milhoes),
                            else_=0
                        )
                    ).label('investimento_saude_regional'),
                    
                    func.sum(
                        case(
                            (CategoriaDespesa.nome_categoria.like('%Educação%'), Despesa.valor_milhoes),
                            else_=0
                        )
                    ).label('investimento_educacao_regional'),
                    
                    # Diversidade de órgãos
                    func.count(func.distinct(Despesa.orgao_publico_id)).label('diversidade_orgaos'),
                    
                ).select_from(
                    Regiao
                ).join(
                    Estado, Regiao.id == Estado.regiao_id
                ).join(
                    IndicadorIDH, Estado.id == IndicadorIDH.estado_id
                ).join(
                    Despesa, Estado.id == Despesa.estado_id
                ).join(
                    CategoriaDespesa, Despesa.categoria_despesa_id == CategoriaDespesa.id
                ).group_by(
                    Regiao.id,
                    Regiao.nome_regiao
                ).order_by(
                    func.avg(IndicadorIDH.idh_geral).desc()
                )
                
                dados_regionais = query.all()
                
                # Processar análise regional
                analise_regional = {
                    'resumo_geral': {
                        'total_regioes_analisadas': len(dados_regionais),
                        'melhor_regiao_idh': None,
                        'melhor_regiao_investimento': None,
                        'maior_disparidade': None
                    },
                    'ranking_regioes': [],
                    'comparativo_detalhado': {},
                    'recomendacoes': []
                }
                
                # Calcular métricas para ranking
                melhor_idh = None
                melhor_investimento = None
                maior_disparidade = 0
                regiao_maior_disparidade = None
                
                for i, regiao_data in enumerate(dados_regionais, 1):
                    
                    # Calcular índices analíticos regionais
                    eficiencia_regional = self._calcular_eficiencia_regional(
                        regiao_data.idh_regional_medio,
                        regiao_data.investimento_regional_total,
                        regiao_data.total_estados
                    )
                    
                    # Calcular homogeneidade baseada na diferença min-max (aproximação)
                    homogeneidade = self._calcular_homogeneidade_regional_simples(
                        regiao_data.idh_regional_min,
                        regiao_data.idh_regional_max,
                        regiao_data.idh_regional_medio
                    )
                    
                    # Identificar melhor região por IDH
                    if not melhor_idh or regiao_data.idh_regional_medio > melhor_idh[1]:
                        melhor_idh = (regiao_data.nome_regiao, regiao_data.idh_regional_medio)
                    
                    # Identificar melhor região por investimento
                    if not melhor_investimento or regiao_data.investimento_regional_total > melhor_investimento[1]:
                        melhor_investimento = (regiao_data.nome_regiao, regiao_data.investimento_regional_total)
                    
                    # Calcular disparidade interna
                    disparidade = float(regiao_data.idh_regional_max or 0) - float(regiao_data.idh_regional_min or 0)
                    if disparidade > maior_disparidade:
                        maior_disparidade = disparidade
                        regiao_maior_disparidade = regiao_data.nome_regiao
                    
                    analise_regional['ranking_regioes'].append({
                        'posicao': i,
                        'regiao': regiao_data.nome_regiao,
                        'total_estados': int(regiao_data.total_estados or 0),
                        
                        # IDH Regional
                        'idh_regional_medio': float(regiao_data.idh_regional_medio or 0),
                        'idh_regional_min': float(regiao_data.idh_regional_min or 0),
                        'idh_regional_max': float(regiao_data.idh_regional_max or 0),
                        'homogeneidade_idh': homogeneidade,
                        
                        # Investimento Regional
                        'investimento_total_milhoes': float(regiao_data.investimento_regional_total or 0),
                        'investimento_medio_projeto': float(regiao_data.investimento_medio_projeto or 0),
                        'investimento_per_capita': float(regiao_data.investimento_per_capita_regional or 0),
                        'total_projetos': int(regiao_data.total_projetos_regional or 0),
                        
                        # Distribuição por área
                        'foco_saude': float(regiao_data.investimento_saude_regional or 0),
                        'foco_educacao': float(regiao_data.investimento_educacao_regional or 0),
                        
                        # Métricas analíticas
                        'eficiencia_regional': eficiencia_regional,
                        'diversidade_orgaos': int(regiao_data.diversidade_orgaos or 0),
                        
                        # Classificação
                        'nivel_desenvolvimento': self._classificar_desenvolvimento_regional(
                            regiao_data.idh_regional_medio
                        ),
                        'prioridade_investimento': self._avaliar_prioridade_investimento(
                            regiao_data.idh_regional_medio,
                            regiao_data.investimento_per_capita_regional
                        )
                    })
                
                # Atualizar resumo geral
                analise_regional['resumo_geral'].update({
                    'melhor_regiao_idh': melhor_idh[0] if melhor_idh else None,
                    'melhor_regiao_investimento': melhor_investimento[0] if melhor_investimento else None,
                    'maior_disparidade': regiao_maior_disparidade
                })
                
                # Gerar comparativo detalhado
                analise_regional['comparativo_detalhado'] = self._gerar_comparativo_regional(dados_regionais)
                
                # Gerar recomendações
                analise_regional['recomendacoes'] = self._gerar_recomendacoes_regionais(analise_regional['ranking_regioes'])
                

                return analise_regional
                
        except Exception as e:
            self.logger.error(f"❌ Erro na Consulta 3: {e}")
            return {}
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _calcular_eficiencia_investimento(self, idh: float, investimento: float) -> Dict[str, Any]:
        """Calcula eficiência do investimento em relação ao IDH"""
        if not idh or not investimento or investimento == 0:
            return {'score': 0, 'categoria': 'Insuficiente'}
        
        # Converter para float para evitar problemas com Decimal
        idh = float(idh) if idh else 0
        investimento = float(investimento) if investimento else 0
        
        if investimento == 0:
            return {'score': 0, 'categoria': 'Insuficiente'}
        
        # Fórmula: IDH / (Investimento/1000) - maior IDH com menor investimento é mais eficiente
        eficiencia = (idh * 1000) / investimento
        
        if eficiencia >= 0.1:
            categoria = 'Excelente'
        elif eficiencia >= 0.05:
            categoria = 'Boa'
        elif eficiencia >= 0.02:
            categoria = 'Regular'
        else:
            categoria = 'Baixa'
        
        return {
            'score': round(eficiencia, 4),
            'categoria': categoria
        }
    
    def _categorizar_desempenho(self, idh: float, ranking: int) -> str:
        """Categoriza o desempenho geral do estado"""
        if idh >= 0.8 and ranking <= 5:
            return 'Excelente'
        elif idh >= 0.7 and ranking <= 10:
            return 'Muito Bom'
        elif idh >= 0.6 and ranking <= 15:
            return 'Bom'
        elif idh >= 0.5:
            return 'Regular'
        else:
            return 'Necessita Atenção'
    
    def _analisar_distribuicao_investimento(self, saude: float, educacao: float, assistencia: float, total: float) -> Dict[str, Any]:
        """Analisa a distribuição percentual dos investimentos"""
        # Converter para float para evitar problemas com Decimal
        saude = float(saude) if saude else 0
        educacao = float(educacao) if educacao else 0
        assistencia = float(assistencia) if assistencia else 0
        total = float(total) if total else 0
        
        if total == 0:
            return {'saude_percent': 0, 'educacao_percent': 0, 'assistencia_percent': 0, 'outros_percent': 100}
        
        saude_pct = (saude / total) * 100
        educacao_pct = (educacao / total) * 100
        assistencia_pct = (assistencia / total) * 100
        outros_pct = 100 - (saude_pct + educacao_pct + assistencia_pct)
        
        return {
            'saude_percent': round(saude_pct, 1),
            'educacao_percent': round(educacao_pct, 1),
            'assistencia_percent': round(assistencia_pct, 1),
            'outros_percent': round(outros_pct, 1)
        }
    
    def _identificar_principal_area(self, saude: float, educacao: float, assistencia: float) -> str:
        """Identifica a área com maior investimento"""
        areas = {
            'Saúde': saude or 0,
            'Educação': educacao or 0,
            'Assistência Social': assistencia or 0
        }
        return max(areas, key=areas.get)
    
    def _avaliar_potencial_melhoria(self, idh: float, investimento: float) -> Dict[str, Any]:
        """Avalia o potencial de melhoria baseado em IDH e investimento"""
        if idh >= 0.8:
            return {'nivel': 'Baixo', 'recomendacao': 'Manter padrão de excelência'}
        elif idh >= 0.7:
            return {'nivel': 'Médio', 'recomendacao': 'Otimizar investimentos existentes'}
        else:
            return {'nivel': 'Alto', 'recomendacao': 'Aumentar investimentos focados'}
    
    def _calcular_tendencias(self, dados_temporais) -> Dict[str, float]:
        """Calcula tendências de crescimento/decrescimento"""
        if len(dados_temporais) < 2:
            return {}
        
        # Tendência IDH (crescimento médio anual)
        idh_inicial = float(dados_temporais[0].idh_medio_ano) if dados_temporais[0].idh_medio_ano else 0
        idh_final = float(dados_temporais[-1].idh_medio_ano) if dados_temporais[-1].idh_medio_ano else 0
        anos = len(dados_temporais) - 1
        
        tendencia_idh = ((idh_final / idh_inicial) ** (1/anos) - 1) * 100 if idh_inicial > 0 else 0
        
        # Tendência Investimento
        inv_inicial = float(dados_temporais[0].investimento_total_ano) if dados_temporais[0].investimento_total_ano else 0
        inv_final = float(dados_temporais[-1].investimento_total_ano) if dados_temporais[-1].investimento_total_ano else 0
        
        tendencia_inv = ((inv_final / inv_inicial) ** (1/anos) - 1) * 100 if inv_inicial > 0 else 0
        
        return {
            'idh_crescimento_anual_percent': round(tendencia_idh, 2),
            'investimento_crescimento_anual_percent': round(tendencia_inv, 2)
        }
    
    def _gerar_projecoes(self, dados_temporais) -> Dict[str, float]:
        """Gera projeções simples para próximo ano"""
        if len(dados_temporais) < 2:
            return {}
        
        ultimo_ano = dados_temporais[-1]
        tendencias = self._calcular_tendencias(dados_temporais)
        
        # Converter para float para evitar problemas com Decimal
        idh_ultimo = float(ultimo_ano.idh_medio_ano) if ultimo_ano.idh_medio_ano else 0
        inv_ultimo = float(ultimo_ano.investimento_total_ano) if ultimo_ano.investimento_total_ano else 0
        
        projecao_idh = idh_ultimo * (1 + tendencias['idh_crescimento_anual_percent']/100)
        projecao_inv = inv_ultimo * (1 + tendencias['investimento_crescimento_anual_percent']/100)
        
        return {
            'projecao_idh_2024': round(projecao_idh, 3),
            'projecao_investimento_2024': round(projecao_inv, 2)
        }
    
    def _gerar_insights_temporais(self, dados_temporais) -> List[str]:
        """Gera insights baseados na análise temporal"""
        insights = []
        
        if len(dados_temporais) >= 3:
            # Verificar aceleração/desaceleração
            crescimentos = []
            for i in range(1, len(dados_temporais)):
                crescimento = dados_temporais[i].idh_medio_ano - dados_temporais[i-1].idh_medio_ano
                crescimentos.append(crescimento)
            
            if len(crescimentos) >= 2:
                if crescimentos[-1] > crescimentos[-2]:
                    insights.append("📈 Aceleração positiva no desenvolvimento humano detectada")
                elif crescimentos[-1] < crescimentos[-2]:
                    insights.append("📉 Desaceleração no crescimento do IDH observada")
        
        return insights
    
    def _calcular_eficiencia_regional(self, idh_medio: float, investimento_total: float, num_estados: int) -> float:
        """Calcula eficiência regional considerando número de estados"""
        if not all([idh_medio, investimento_total, num_estados]) or investimento_total == 0:
            return 0
        
        # Converter para float para evitar problemas com Decimal
        idh_medio = float(idh_medio) if idh_medio else 0
        investimento_total = float(investimento_total) if investimento_total else 0
        
        if investimento_total == 0 or num_estados == 0:
            return 0
        
        # Eficiência = IDH médio / (Investimento per estado)
        investimento_per_estado = investimento_total / num_estados
        eficiencia = (idh_medio * 1000) / investimento_per_estado
        
        return round(eficiencia, 4)
    
    def _calcular_homogeneidade_regional(self, desvio_padrao: float, media: float) -> Dict[str, Any]:
        """Calcula homogeneidade regional (menor CV = mais homogêneo)"""
        if not media or media == 0:
            return {'coeficiente_variacao': 0, 'categoria': 'Indeterminado'}
        
        cv = (desvio_padrao / media) * 100 if desvio_padrao else 0
        
        if cv <= 5:
            categoria = 'Muito Homogêneo'
        elif cv <= 10:
            categoria = 'Homogêneo'
        elif cv <= 15:
            categoria = 'Moderadamente Heterogêneo'
        else:
            categoria = 'Muito Heterogêneo'
        
        return {
            'coeficiente_variacao': round(cv, 2),
            'categoria': categoria
        }
    
    def _calcular_homogeneidade_regional_simples(self, idh_min: float, idh_max: float, idh_medio: float) -> Dict[str, Any]:
        """Calcula homogeneidade regional usando diferença min-max como aproximação"""
        if not idh_medio or idh_medio == 0:
            return {'coeficiente_variacao': 0, 'categoria': 'Indeterminado'}
        
        # Usar amplitude como aproximação do desvio padrão
        amplitude = float(idh_max or 0) - float(idh_min or 0)
        # Aproximação: desvio_padrao ≈ amplitude/4 (regra empírica)
        desvio_aproximado = amplitude / 4
        
        cv = (desvio_aproximado / float(idh_medio)) * 100 if idh_medio else 0
        
        if cv <= 5:
            categoria = 'Muito Homogêneo'
        elif cv <= 10:
            categoria = 'Homogêneo'
        elif cv <= 15:
            categoria = 'Moderadamente Heterogêneo'
        else:
            categoria = 'Muito Heterogêneo'
        
        return {
            'coeficiente_variacao': round(cv, 2),
            'categoria': categoria
        }
    
    def _classificar_desenvolvimento_regional(self, idh_medio: float) -> str:
        """Classifica nível de desenvolvimento regional"""
        if idh_medio >= 0.8:
            return 'Muito Alto'
        elif idh_medio >= 0.7:
            return 'Alto'
        elif idh_medio >= 0.6:
            return 'Médio'
        elif idh_medio >= 0.5:
            return 'Baixo'
        else:
            return 'Muito Baixo'
    
    def _avaliar_prioridade_investimento(self, idh_medio: float, investimento_per_capita: float) -> str:
        """Avalia prioridade de investimento regional"""
        if idh_medio < 0.6 and investimento_per_capita < 1000:
            return 'Crítica'
        elif idh_medio < 0.7:
            return 'Alta'
        elif idh_medio < 0.8:
            return 'Média'
        else:
            return 'Baixa'
    
    def _gerar_comparativo_regional(self, dados_regionais) -> Dict[str, Any]:
        """Gera comparativo detalhado entre regiões"""
        # Implementação detalhada seria aqui
        return {
            'nota': 'Comparativo detalhado implementado na versão completa'
        }
    
    def _gerar_recomendacoes_regionais(self, ranking_regioes) -> List[str]:
        """Gera recomendações baseadas no ranking regional"""
        recomendacoes = []
        
        for regiao in ranking_regioes:
            if regiao['prioridade_investimento'] == 'Crítica':
                recomendacoes.append(f"🚨 {regiao['regiao']}: Necessita investimento emergencial")
            elif regiao['homogeneidade_idh']['categoria'] == 'Muito Heterogêneo':
                recomendacoes.append(f"⚖️ {regiao['regiao']}: Reduzir disparidades internas")
        
        return recomendacoes


# ==================== CLASSE RELATÓRIOS ESTATÍSTICOS ====================

class RelatoriosEstatisticos:
    """
    Geração de relatórios estatísticos avançados
    """
    
    def __init__(self):
        self.db_connection = get_database_connection()
        self.consultas = ConsultasAnalíticas()
    
    def gerar_relatorio_executivo(self) -> Dict[str, Any]:
        """Gera relatório executivo completo"""
        try:
            relatorio = {
                'data_geracao': datetime.now().isoformat(),
                'tipo': 'Relatório Executivo',
                'resumo_executivo': {},
                'analises_principais': {},
                'recomendacoes_estrategicas': [],
                'metricas_chave': {}
            }
            
            # Executar consultas principais
            ranking_estados = self.consultas.consulta_1_ranking_idh_investimento()
            evolucao_temporal = self.consultas.consulta_2_evolucao_temporal()
            analise_regional = self.consultas.consulta_3_analise_regional()
            
            # Compilar resumo executivo
            relatorio['resumo_executivo'] = {
                'total_estados_analisados': len(ranking_estados),
                'melhor_estado_idh': ranking_estados[0]['estado'] if ranking_estados else None,
                'total_investimento_nacional': sum(e['total_investimento_milhoes'] for e in ranking_estados),
                'idh_medio_nacional': sum(e['idh_geral'] for e in ranking_estados) / len(ranking_estados) if ranking_estados else 0
            }
            
            relatorio['analises_principais'] = {
                'ranking_estados': ranking_estados[:10],  # Top 10
                'evolucao_temporal': evolucao_temporal,
                'analise_regional': analise_regional
            }
            
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório executivo: {e}")
            return {}


# ==================== CLASSE ANÁLISE COMPARATIVA ====================

class AnaliseComparativa:
    """
    Análises comparativas especializadas
    """
    
    def __init__(self):
        self.db_connection = get_database_connection()
    
    def comparar_estados(self, estado_id_1: int, estado_id_2: int) -> Dict[str, Any]:
        """Compara dois estados específicos"""
        # Implementação de comparação detalhada
        return {'nota': 'Comparação detalhada entre estados'}
    
    def benchmark_regional(self, regiao_id: int) -> Dict[str, Any]:
        """Benchmark de uma região específica"""
        # Implementação de benchmark regional
        return {'nota': 'Benchmark regional detalhado'}


# ==================== CLASSE MÉTRICAS AVANÇADAS ====================

class MetricasAvancadas:
    """
    Cálculo de métricas avançadas e indicadores compostos
    """
    
    def __init__(self):
        self.db_connection = get_database_connection()
    
    def calcular_indice_desenvolvimento_integrado(self) -> Dict[str, Any]:
        """Calcula índice personalizado de desenvolvimento"""
        # Implementação de índice composto personalizado
        return {'nota': 'Índice de desenvolvimento integrado'}
    
    def analise_correlacao_avancada(self) -> Dict[str, Any]:
        """Análise de correlação entre variáveis"""
        # Implementação de análise de correlação
        return {'nota': 'Análise de correlação avançada'} 