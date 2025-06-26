"""
CRUD Organizacional - Sistema DEC7588
Operações CRUD para entidades organizacionais (Órgãos Públicos e Fontes de Recursos)
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
from src.models.entities import OrgaoPublico, FonteRecurso

class OrgaosPublicosCRUD(BaseCRUD[OrgaoPublico]):
    """CRUD para Órgãos Públicos"""
    
    def __init__(self):
        super().__init__(OrgaoPublico)
        self.logger = logging.getLogger(__name__)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de órgão público"""
        required_fields = ['nome_orgao', 'tipo_orgao']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar tipo de órgão
        tipos_validos = ['Federal', 'Estadual', 'Municipal', 'Ministério', 'Secretaria', 'Autarquia', 'Fundação', 'Empresa Pública', 'Outros']
        if data['tipo_orgao'] not in tipos_validos:
            raise ValidationException(f"Tipo de órgão deve ser um dos: {', '.join(tipos_validos)}")
        
        # Normalizar campos
        data['nome_orgao'] = data['nome_orgao'].strip().title()
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se órgão já existe"""
        existing = session.query(OrgaoPublico).filter(
            OrgaoPublico.nome_orgao == data['nome_orgao'],
            OrgaoPublico.tipo_orgao == data['tipo_orgao']
        ).first()
        
        if existing:
            raise ValidationException(f"Órgão '{data['nome_orgao']}' já existe como {data['tipo_orgao']}")
    
    def get_by_esfera(self, esfera: str) -> List[OrgaoPublico]:
        """Busca órgãos por esfera de governo"""
        return self.search({'tipo_orgao': esfera})
    
    def get_by_tipo(self, tipo: str) -> List[OrgaoPublico]:
        """Busca órgãos por tipo"""
        return self.search({'tipo_orgao': tipo})
    
    def get_federais(self) -> List[OrgaoPublico]:
        """Busca apenas órgãos federais"""
        return self.get_by_esfera('Federal')
    
    def get_estaduais(self) -> List[OrgaoPublico]:
        """Busca apenas órgãos estaduais"""
        return self.get_by_esfera('Estadual')
    
    def get_municipais(self) -> List[OrgaoPublico]:
        """Busca apenas órgãos municipais"""
        return self.get_by_esfera('Municipal')
    
    def get_ministerios(self) -> List[OrgaoPublico]:
        """Busca apenas ministérios"""
        return self.get_by_tipo('Ministério')
    
    def ativar_orgao(self, orgao_id: int) -> bool:
        """Ativa um órgão público"""
        return self.update(orgao_id, ativo=True) is not None
    
    def desativar_orgao(self, orgao_id: int) -> bool:
        """Desativa um órgão público"""
        return self.update(orgao_id, ativo=False) is not None
    
    def get_ativos(self) -> List[OrgaoPublico]:
        """Busca apenas órgãos ativos"""
        return self.search({'ativo': True})
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de órgãos públicos"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Órgãos por esfera
                stats_esfera = session.query(
                    OrgaoPublico.tipo_orgao,
                    func.count(OrgaoPublico.id).label('total')
                ).group_by(OrgaoPublico.tipo_orgao).all()
                
                # Órgãos por tipo
                stats_tipo = session.query(
                    OrgaoPublico.tipo_orgao,
                    func.count(OrgaoPublico.id).label('total')
                ).group_by(OrgaoPublico.tipo_orgao).all()
                
                # Órgãos ativos vs inativos
                total_ativos = session.query(func.count(OrgaoPublico.id)).filter(
                    OrgaoPublico.ativo == True
                ).scalar()
                total_inativos = session.query(func.count(OrgaoPublico.id)).filter(
                    OrgaoPublico.ativo == False
                ).scalar()
                
                return {
                    'por_esfera': {esfera: total for esfera, total in stats_esfera},
                    'por_tipo': {tipo: total for tipo, total in stats_tipo},
                    'ativos': total_ativos,
                    'inativos': total_inativos
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas de órgãos: {e}")
            return {}
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """Lista órgãos públicos"""
        try:
            with self.db_connection.get_session() as session:
                # Query simples para órgãos públicos
                query = session.query(
                    OrgaoPublico.id,
                    OrgaoPublico.nome_orgao,
                    OrgaoPublico.tipo_orgao,
                    OrgaoPublico.sigla_orgao,
                    OrgaoPublico.ativo
                ).order_by(OrgaoPublico.nome_orgao) \
                 .limit(limit).offset(offset)
                
                result = query.all()
                
                # Converter para lista de listas
                data = []
                for row in result:
                    data.append([
                        row[0],  # id
                        row[1],  # nome_orgao
                        row[2] if row[2] else "N/A",  # tipo_orgao
                        row[3] if row[3] else "N/A",  # sigla_orgao
                        "Ativo" if row[4] else "Inativo"  # ativo
                    ])
                
                self.logger.info(f"✅ Listados {len(data)} órgãos públicos")
                return data
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar órgãos públicos: {e}")
            return []


class FontesRecursosCRUD(BaseCRUD[FonteRecurso]):
    """CRUD para Fontes de Recursos"""
    
    def __init__(self):
        super().__init__(FonteRecurso)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de fonte de recurso"""
        required_fields = ['nome_fonte', 'tipo_fonte']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar tipos de fonte
        tipos_validos = [
            'Tesouro Nacional', 'Receitas Próprias', 'Transferências',
            'Financiamentos', 'Convênios', 'Operações de Crédito', 'Outros'
        ]
        if data['tipo_fonte'] not in tipos_validos:
            raise ValidationException(f"Tipo de fonte deve ser um dos: {', '.join(tipos_validos)}")
        
        # Validar código da fonte (se fornecido)
        if 'codigo_fonte' in data and data['codigo_fonte']:
            if not str(data['codigo_fonte']).isdigit():
                raise ValidationException("Código da fonte deve ser numérico")
        
        # Normalizar campos
        data['nome_fonte'] = data['nome_fonte'].strip().title()
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se fonte já existe"""
        # Verificar por nome
        existing_nome = session.query(FonteRecurso).filter(
            FonteRecurso.nome_fonte == data['nome_fonte']
        ).first()
        
        if existing_nome:
            raise ValidationException(f"Fonte '{data['nome_fonte']}' já existe")
        
        # Verificar por código (se fornecido)
        if 'codigo_fonte' in data and data['codigo_fonte']:
            existing_codigo = session.query(FonteRecurso).filter(
                FonteRecurso.codigo_fonte == data['codigo_fonte']
            ).first()
            
            if existing_codigo:
                raise ValidationException(f"Código de fonte '{data['codigo_fonte']}' já existe")
    
    def get_by_tipo(self, tipo: str) -> List[FonteRecurso]:
        """Busca fontes por tipo"""
        return self.search({'tipo_fonte': tipo})
    
    def get_by_codigo(self, codigo: str) -> Optional[FonteRecurso]:
        """Busca fonte por código"""
        results = self.search({'codigo_fonte': codigo})
        return results[0] if results else None
    
    def get_tesouro_nacional(self) -> List[FonteRecurso]:
        """Busca fontes do Tesouro Nacional"""
        return self.get_by_tipo('Tesouro Nacional')
    
    def get_receitas_proprias(self) -> List[FonteRecurso]:
        """Busca fontes de receitas próprias"""
        return self.get_by_tipo('Receitas Próprias')
    
    def get_transferencias(self) -> List[FonteRecurso]:
        """Busca fontes de transferências"""
        return self.get_by_tipo('Transferências')
    
    def get_ativas(self) -> List[FonteRecurso]:
        """Busca apenas fontes ativas"""
        return self.search({'ativa': True})
    
    def ativar_fonte(self, fonte_id: int) -> bool:
        """Ativa uma fonte de recurso"""
        return self.update(fonte_id, ativa=True) is not None
    
    def desativar_fonte(self, fonte_id: int) -> bool:
        """Desativa uma fonte de recurso"""
        return self.update(fonte_id, ativa=False) is not None
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de fontes de recursos"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Fontes por tipo
                stats_tipo = session.query(
                    FonteRecurso.tipo_fonte,
                    func.count(FonteRecurso.id).label('total')
                ).group_by(FonteRecurso.tipo_fonte).all()
                
                # Fontes ativas vs inativas
                total_ativas = session.query(func.count(FonteRecurso.id)).filter(
                    FonteRecurso.ativa == True
                ).scalar()
                total_inativas = session.query(func.count(FonteRecurso.id)).filter(
                    FonteRecurso.ativa == False
                ).scalar()
                
                return {
                    'por_tipo': {tipo: total for tipo, total in stats_tipo},
                    'ativas': total_ativas,
                    'inativas': total_inativas
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas de fontes: {e}")
            return {} 