"""
CRUD Indicadores - Sistema DEC7588
Operações CRUD para Indicadores IDH
"""

import sys
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.crud.base_crud import BaseCRUD, ValidationException, CRUDException
from src.models.entities import IndicadorIDH

class IndicadoresIDHCRUD(BaseCRUD[IndicadorIDH]):
    """CRUD para Indicadores IDH"""
    
    def __init__(self):
        super().__init__(IndicadorIDH)
        self.logger = logging.getLogger(__name__)
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """Lista indicadores IDH com informações relacionadas"""
        try:
            with self.db_connection.get_session() as session:
                from src.models.entities import Estado, Periodo
                
                # Query com JOIN para obter nome do estado e ano
                # Ordenar por ano DESC e depois por estado para mostrar dados recentes primeiro
                query = session.query(
                    IndicadorIDH.id,
                    Estado.nome_estado,
                    Periodo.ano,
                    IndicadorIDH.idh_geral,
                    IndicadorIDH.idh_educacao,
                    IndicadorIDH.idh_longevidade,
                    IndicadorIDH.idh_renda
                ).join(Estado, IndicadorIDH.estado_id == Estado.id) \
                 .join(Periodo, IndicadorIDH.periodo_id == Periodo.id) \
                 .order_by(Periodo.ano.desc(), Estado.nome_estado) \
                 .limit(limit).offset(offset)
                
                result = query.all()
                
                # Converter para lista de listas
                data = []
                for row in result:
                    data.append([
                        row[0],  # id
                        row[1],  # nome_estado
                        row[2],  # ano
                        f"{float(row[3]):.3f}" if row[3] else "N/A",  # idh_geral
                        f"{float(row[4]):.3f}" if row[4] else "N/A",  # idh_educacao
                        f"{float(row[5]):.3f}" if row[5] else "N/A",  # idh_longevidade
                        f"{float(row[6]):.3f}" if row[6] else "N/A"   # idh_renda
                    ])
                
                self.logger.info(f"✅ Listados {len(data)} indicadores IDH")
                return data
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar indicadores IDH: {e}")
            return []
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de indicador IDH"""
        required_fields = ['estado_id', 'periodo_id', 'idh_geral']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar valores IDH (devem estar entre 0 e 1)
        idh_fields = ['idh_geral', 'idh_educacao', 'idh_longevidade', 'idh_renda']
        
        for field in idh_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], (int, float, Decimal)):
                    raise ValidationException(f"{field} deve ser numérico")
                
                valor = Decimal(str(data[field]))
                if valor < 0 or valor > 1:
                    raise ValidationException(f"{field} deve estar entre 0 e 1")
                
                data[field] = valor
        
        # Validar ranking (se fornecido)
        if 'ranking_nacional' in data and data['ranking_nacional'] is not None:
            if not isinstance(data['ranking_nacional'], int) or data['ranking_nacional'] < 1:
                raise ValidationException("Ranking nacional deve ser um inteiro positivo")
        
        # Validar população (se fornecida)
        if 'populacao' in data and data['populacao'] is not None:
            if not isinstance(data['populacao'], int) or data['populacao'] < 0:
                raise ValidationException("População deve ser um inteiro não negativo")
        
        # Validar existência de entidades relacionadas
        from src.crud.geografia_crud import EstadosCRUD
        from src.crud.financeiro_crud import PeriodosCRUD
        
        estado_crud = EstadosCRUD()
        if not estado_crud.get_by_id(data['estado_id']):
            raise ValidationException(f"Estado com ID {data['estado_id']} não existe")
        
        periodo_crud = PeriodosCRUD()
        if not periodo_crud.get_by_id(data['periodo_id']):
            raise ValidationException(f"Período com ID {data['periodo_id']} não existe")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se indicador já existe para o mesmo estado e período"""
        existing = session.query(IndicadorIDH).filter(
            IndicadorIDH.estado_id == data['estado_id'],
            IndicadorIDH.periodo_id == data['periodo_id']
        ).first()
        
        if existing:
            raise ValidationException("Indicador IDH já existe para este estado e período")
    
    def get_by_estado(self, estado_id: int) -> List[IndicadorIDH]:
        """Busca indicadores por estado"""
        return self.search({'estado_id': estado_id})
    
    def get_by_periodo(self, periodo_id: int) -> List[IndicadorIDH]:
        """Busca indicadores por período"""
        return self.search({'periodo_id': periodo_id})
    
    def get_ranking_nacional(self, periodo_id: int) -> List[Dict[str, Any]]:
        """Retorna ranking nacional por período"""
        try:
            with self.db_connection.get_session() as session:
                from src.models.entities import Estado
                
                result = session.query(
                    IndicadorIDH,
                    Estado.nome_estado,
                    Estado.sigla_uf
                ).join(Estado).filter(
                    IndicadorIDH.periodo_id == periodo_id
                ).order_by(IndicadorIDH.idh_geral.desc()).all()
                
                ranking = []
                for i, (indicador, nome_estado, sigla_uf) in enumerate(result, 1):
                    ranking.append({
                        'posicao': i,
                        'estado': nome_estado,
                        'sigla': sigla_uf,
                        'idh_geral': indicador.idh_geral,
                        'idh_educacao': indicador.idh_educacao,
                        'idh_longevidade': indicador.idh_longevidade,
                        'idh_renda': indicador.idh_renda,
                        'populacao': indicador.populacao
                    })
                
                return ranking
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar ranking nacional: {e}")
            return []
    
    def get_melhores_idh(self, periodo_id: int, limit: int = 10) -> List[IndicadorIDH]:
        """Busca estados com melhor IDH"""
        try:
            with self.db_connection.get_session() as session:
                return session.query(IndicadorIDH).filter(
                    IndicadorIDH.periodo_id == periodo_id
                ).order_by(IndicadorIDH.idh_geral.desc()).limit(limit).all()
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar melhores IDH: {e}")
            return []
    
    def get_piores_idh(self, periodo_id: int, limit: int = 10) -> List[IndicadorIDH]:
        """Busca estados com pior IDH"""
        try:
            with self.db_connection.get_session() as session:
                return session.query(IndicadorIDH).filter(
                    IndicadorIDH.periodo_id == periodo_id
                ).order_by(IndicadorIDH.idh_geral.asc()).limit(limit).all()
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar piores IDH: {e}")
            return []
    
    def get_estatisticas_periodo(self, periodo_id: int) -> Dict[str, Any]:
        """Calcula estatísticas do IDH por período"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                stats = session.query(
                    func.avg(IndicadorIDH.idh_geral).label('media_idh'),
                    func.max(IndicadorIDH.idh_geral).label('maior_idh'),
                    func.min(IndicadorIDH.idh_geral).label('menor_idh'),
                    func.count(IndicadorIDH.id).label('total_estados')
                ).filter(IndicadorIDH.periodo_id == periodo_id).first()
                
                # Calcular mediana (aproximação)
                mediana_query = session.query(IndicadorIDH.idh_geral).filter(
                    IndicadorIDH.periodo_id == periodo_id
                ).order_by(IndicadorIDH.idh_geral)
                
                total = stats.total_estados or 0
                if total > 0:
                    meio = total // 2
                    mediana_result = mediana_query.offset(meio).limit(1).first()
                    mediana = mediana_result[0] if mediana_result else Decimal('0')
                else:
                    mediana = Decimal('0')
                
                return {
                    'media_idh': stats.media_idh or Decimal('0'),
                    'maior_idh': stats.maior_idh or Decimal('0'),
                    'menor_idh': stats.menor_idh or Decimal('0'),
                    'mediana_idh': mediana,
                    'total_estados': total
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_comparativo_dimensoes(self, periodo_id: int) -> List[Dict[str, Any]]:
        """Compara as dimensões do IDH por estado"""
        try:
            with self.db_connection.get_session() as session:
                from src.models.entities import Estado
                
                result = session.query(
                    Estado.nome_estado,
                    Estado.sigla_uf,
                    IndicadorIDH.idh_educacao,
                    IndicadorIDH.idh_longevidade,
                    IndicadorIDH.idh_renda
                ).join(IndicadorIDH).filter(
                    IndicadorIDH.periodo_id == periodo_id
                ).order_by(Estado.nome_estado).all()
                
                comparativo = []
                for estado, sigla, educacao, longevidade, renda in result:
                    comparativo.append({
                        'estado': estado,
                        'sigla': sigla,
                        'educacao': educacao or Decimal('0'),
                        'longevidade': longevidade or Decimal('0'),
                        'renda': renda or Decimal('0'),
                        'melhor_dimensao': self._get_melhor_dimensao(educacao, longevidade, renda),
                        'pior_dimensao': self._get_pior_dimensao(educacao, longevidade, renda)
                    })
                
                return comparativo
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar comparativo: {e}")
            return []
    
    def _get_melhor_dimensao(self, educacao, longevidade, renda) -> str:
        """Identifica a melhor dimensão do IDH"""
        if not educacao or not longevidade or not renda:
            return "N/A"
        
        dimensoes = {
            'Educação': educacao,
            'Longevidade': longevidade,
            'Renda': renda
        }
        
        return max(dimensoes, key=dimensoes.get)
    
    def _get_pior_dimensao(self, educacao, longevidade, renda) -> str:
        """Identifica a pior dimensão do IDH"""
        if not educacao or not longevidade or not renda:
            return "N/A"
        
        dimensoes = {
            'Educação': educacao,
            'Longevidade': longevidade,
            'Renda': renda
        }
        
        return min(dimensoes, key=dimensoes.get)
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de indicadores IDH"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Total de indicadores por ano
                from src.models.entities import Periodo
                stats_por_ano = session.query(
                    Periodo.ano,
                    func.count(IndicadorIDH.id).label('total')
                ).join(IndicadorIDH).group_by(Periodo.ano).all()
                
                # Estatísticas gerais
                stats_gerais = session.query(
                    func.avg(IndicadorIDH.idh_geral).label('media_nacional'),
                    func.max(IndicadorIDH.idh_geral).label('maior_idh_historico'),
                    func.min(IndicadorIDH.idh_geral).label('menor_idh_historico'),
                    func.count(IndicadorIDH.id).label('total_registros')
                ).first()
                
                return {
                    'media_nacional': stats_gerais.media_nacional or Decimal('0'),
                    'maior_idh_historico': stats_gerais.maior_idh_historico or Decimal('0'),
                    'menor_idh_historico': stats_gerais.menor_idh_historico or Decimal('0'),
                    'total_registros': stats_gerais.total_registros or 0
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas gerais: {e}")
            return {} 