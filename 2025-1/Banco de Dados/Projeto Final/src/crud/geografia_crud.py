"""
CRUD Geografia - Sistema DEC7588
Operações CRUD específicas para entidades geográficas
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.crud.base_crud import BaseCRUD, ValidationException, CRUDException
from src.models.entities import Regiao, Estado, Municipio

# Configurar logger
logger = logging.getLogger(__name__)

class RegiaosCRUD(BaseCRUD[Regiao]):
    """CRUD para Regiões geográficas do Brasil"""
    
    def __init__(self):
        super().__init__(Regiao)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de região"""
        if 'nome_regiao' not in data or not data['nome_regiao']:
            raise ValidationException("Nome da região é obrigatório")
        
        # Validar se é uma das 5 regiões válidas
        regioes_validas = ['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste']
        if data['nome_regiao'] not in regioes_validas:
            raise ValidationException(f"Região deve ser uma das: {', '.join(regioes_validas)}")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se região já existe"""
        existing = session.query(Regiao).filter(
            Regiao.nome_regiao == data['nome_regiao']
        ).first()
        
        if existing:
            raise ValidationException(f"Região '{data['nome_regiao']}' já existe")
    
    def get_by_nome(self, nome_regiao: str) -> Optional[Regiao]:
        """Busca região por nome"""
        return self.search({'nome_regiao': nome_regiao})
    
    def get_with_estados(self, regiao_id: int) -> Dict[str, Any]:
        """Retorna região com seus estados"""
        try:
            with self.db_connection.get_session() as session:
                regiao = session.query(Regiao).filter(Regiao.id == regiao_id).first()
                if not regiao:
                    return {}
                
                estados = session.query(Estado).filter(Estado.regiao_id == regiao_id).all()
                
                return {
                    'regiao': regiao,
                    'estados': estados,
                    'total_estados': len(estados)
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar região com estados: {e}")
            return {}


class EstadosCRUD(BaseCRUD[Estado]):
    """CRUD para Estados e Distrito Federal"""
    
    def __init__(self):
        super().__init__(Estado)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de estado"""
        required_fields = ['nome_estado', 'sigla_uf', 'regiao_id']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar sigla UF (2 caracteres, maiúsculas)
        if len(data['sigla_uf']) != 2:
            raise ValidationException("Sigla UF deve ter exatamente 2 caracteres")
        
        data['sigla_uf'] = data['sigla_uf'].upper()
        
        # Validar se região existe
        regiao_crud = RegiaosCRUD()
        if not regiao_crud.get_by_id(data['regiao_id']):
            raise ValidationException(f"Região com ID {data['regiao_id']} não existe")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se estado já existe"""
        # Verificar por nome
        existing_nome = session.query(Estado).filter(
            Estado.nome_estado == data['nome_estado']
        ).first()
        
        if existing_nome:
            raise ValidationException(f"Estado '{data['nome_estado']}' já existe")
        
        # Verificar por sigla
        existing_sigla = session.query(Estado).filter(
            Estado.sigla_uf == data['sigla_uf']
        ).first()
        
        if existing_sigla:
            raise ValidationException(f"Sigla UF '{data['sigla_uf']}' já existe")
    
    def get_by_sigla(self, sigla_uf: str) -> Optional[Estado]:
        """Busca estado por sigla"""
        results = self.search({'sigla_uf': sigla_uf.upper()})
        return results[0] if results else None
    
    def get_by_regiao(self, regiao_id: int) -> List[Estado]:
        """Busca estados de uma região"""
        return self.search({'regiao_id': regiao_id})
    
    def get_with_regiao(self, estado_id: int) -> Dict[str, Any]:
        """Retorna estado com informações da região"""
        try:
            with self.db_connection.get_session() as session:
                estado = session.query(Estado).filter(Estado.id == estado_id).first()
                if not estado:
                    return {}
                
                regiao = session.query(Regiao).filter(Regiao.id == estado.regiao_id).first()
                
                return {
                    'estado': estado,
                    'regiao': regiao
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar estado com região: {e}")
            return {}
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de estados"""
        try:
            with self.db_connection.get_session() as session:
                # Estados por região
                from sqlalchemy import func
                stats_por_regiao = session.query(
                    Regiao.nome_regiao,
                    func.count(Estado.id).label('total_estados')
                ).join(Estado).group_by(Regiao.nome_regiao).all()
                
                return {
                    'estados_por_regiao': {nome: total for nome, total in stats_por_regiao}
                }
        except Exception:
            return {}
    
    def _get_display_attributes(self) -> List[str]:
        """Atributos para exibição na interface"""
        return ['id', 'nome_estado', 'sigla_uf', 'regiao_nome', 'capital', 'populacao_estimada']
    
    def _format_population(self, value) -> str:
        """Formata população com sufixos (M, Mil, etc)"""
        try:
            if not value:
                return "N/A"
                
            # Converter para float se for string
            if isinstance(value, str):
                value = float(value)
            
            # Definir escalas e sufixos
            if value >= 1_000_000:
                # Milhões
                formatted = value / 1_000_000
                suffix = "M"
            elif value >= 1_000:
                # Milhares
                formatted = value / 1_000
                suffix = "Mil"
            else:
                # Menor que mil
                return f"{value:.0f}"
            
            # Formatar com 2 casas decimais
            return f"{formatted:.2f}{suffix}"
            
        except (ValueError, TypeError):
            return "N/A"
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """
        Lista estados com nome da região em vez do ID
        
        Args:
            limit: Número máximo de registros
            offset: Deslocamento para paginação
            
        Returns:
            List[List[Any]]: Lista com dados formatados
        """
        try:
            with self.db_connection.get_session() as session:
                # Consulta com JOIN para pegar nome da região
                query = session.query(
                    Estado.id,
                    Estado.nome_estado,
                    Estado.sigla_uf,
                    Regiao.nome_regiao,
                    Estado.capital,
                    Estado.populacao_estimada
                ).join(Regiao, Estado.regiao_id == Regiao.id).limit(limit).offset(offset)
                
                resultados = query.all()
                
                # Converter para lista de listas
                dados_formatados = []
                for row in resultados:
                    linha = [
                        row.id,
                        row.nome_estado,
                        row.sigla_uf,
                        row.nome_regiao,  # Nome da região em vez do ID
                        row.capital or "N/A",
                        self._format_population(row.populacao_estimada)
                    ]
                    dados_formatados.append(linha)
                
                return dados_formatados
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar estados: {e}")
            return []


class MunicipiosCRUD(BaseCRUD[Municipio]):
    """CRUD para Municípios (expansão futura)"""
    
    def __init__(self):
        super().__init__(Municipio)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de município"""
        required_fields = ['nome_municipio', 'estado_id']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar se estado existe
        estado_crud = EstadosCRUD()
        if not estado_crud.get_by_id(data['estado_id']):
            raise ValidationException(f"Estado com ID {data['estado_id']} não existe")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se município já existe no mesmo estado"""
        existing = session.query(Municipio).filter(
            Municipio.nome_municipio == data['nome_municipio'],
            Municipio.estado_id == data['estado_id']
        ).first()
        
        if existing:
            raise ValidationException(f"Município '{data['nome_municipio']}' já existe neste estado")
    
    def get_by_estado(self, estado_id: int) -> List[Municipio]:
        """Busca municípios de um estado"""
        return self.search({'estado_id': estado_id})
    
    def get_capitais(self) -> List[Municipio]:
        """Busca apenas as capitais"""
        return self.search({'eh_capital': True})
    
    def set_capital(self, municipio_id: int) -> bool:
        """Define um município como capital"""
        try:
            municipio = self.get_by_id(municipio_id)
            if not municipio:
                return False
            
            with self.db_connection.get_session() as session:
                # Remover capital atual do estado (se existir)
                session.query(Municipio).filter(
                    Municipio.estado_id == municipio.estado_id,
                    Municipio.eh_capital == True
                ).update({'eh_capital': False})
                
                # Definir novo capital
                municipio.eh_capital = True
                session.flush()
                
                return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao definir capital: {e}")
            return False 