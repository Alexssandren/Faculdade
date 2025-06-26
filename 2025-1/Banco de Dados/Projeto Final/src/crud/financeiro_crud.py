"""
CRUD Financeiro - Sistema DEC7588
Operações CRUD para entidades financeiras principais
"""

import sys
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date
import logging

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.crud.base_crud import BaseCRUD, ValidationException, CRUDException
from src.models.entities import CategoriaDespesa, Periodo, Orcamento, Despesa

class CategoriasDespesasCRUD(BaseCRUD[CategoriaDespesa]):
    """CRUD para Categorias de Despesas"""
    
    def __init__(self):
        super().__init__(CategoriaDespesa)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de categoria"""
        required_fields = ['nome_categoria']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Normalizar nome
        data['nome_categoria'] = data['nome_categoria'].strip().title()
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se categoria já existe"""
        existing = session.query(CategoriaDespesa).filter(
            CategoriaDespesa.nome_categoria == data['nome_categoria']
        ).first()
        
        if existing:
            raise ValidationException(f"Categoria '{data['nome_categoria']}' já existe")
    
    def get_by_tipo(self, tipo: str) -> List[CategoriaDespesa]:
        """Busca categorias por nome (substituindo tipo)"""
        return self.search({'nome_categoria': f'%{tipo}%'})
    
    def get_pessoal(self) -> List[CategoriaDespesa]:
        """Busca categorias de pessoal"""
        return self.get_by_tipo('Pessoal e Encargos')
    
    def get_custeio(self) -> List[CategoriaDespesa]:
        """Busca categorias de custeio"""
        return self.get_by_tipo('Custeio')
    
    def get_investimentos(self) -> List[CategoriaDespesa]:
        """Busca categorias de investimentos"""
        return self.get_by_tipo('Investimentos')


class PeriodosCRUD(BaseCRUD[Periodo]):
    """CRUD para Períodos"""
    
    def __init__(self):
        super().__init__(Periodo)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de período"""
        required_fields = ['ano']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar ano
        if not isinstance(data['ano'], int) or data['ano'] < 2000 or data['ano'] > 2030:
            raise ValidationException("Ano deve estar entre 2000 e 2030")
        
        # Validar mês (se fornecido)
        if 'mes' in data and data['mes']:
            if data['mes'] < 1 or data['mes'] > 12:
                raise ValidationException("Mês deve estar entre 1 e 12")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se período já existe"""
        existing = session.query(Periodo).filter(
            Periodo.ano == data['ano']
        )
        
        if 'mes' in data and data['mes']:
            existing = existing.filter(Periodo.mes == data['mes'])
        
        if existing.first():
            periodo_desc = f"{data['ano']}"
            if 'mes' in data and data['mes']:
                periodo_desc += f"/{data['mes']:02d}"
            raise ValidationException(f"Período {periodo_desc} já existe")
    
    def get_by_ano(self, ano: int) -> List[Periodo]:
        """Busca períodos por ano"""
        return self.search({'ano': ano})
    
    def get_anuais(self) -> List[Periodo]:
        """Busca apenas períodos anuais (sem mês especificado)"""
        with self.db_connection.get_session() as session:
            return session.query(Periodo).filter(Periodo.mes.is_(None)).all()
    
    def get_mensais(self, ano: int = None) -> List[Periodo]:
        """Busca períodos mensais"""
        with self.db_connection.get_session() as session:
            query = session.query(Periodo).filter(Periodo.mes.isnot(None))
            if ano:
                query = query.filter(Periodo.ano == ano)
            return query.all()
    
    def get_periodo_atual(self) -> Optional[Periodo]:
        """Busca período do ano atual"""
        ano_atual = datetime.now().year
        results = self.search({'ano': ano_atual})
        return results[0] if results else None


class OrcamentosCRUD(BaseCRUD[Orcamento]):
    """CRUD para Orçamentos"""
    
    def __init__(self):
        super().__init__(Orcamento)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de orçamento"""
        required_fields = ['orgao_id', 'fonte_recurso_id', 'categoria_despesa_id', 
                          'periodo_id', 'valor_orcado']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar valor orçado
        if not isinstance(data['valor_orcado'], (int, float, Decimal)):
            raise ValidationException("Valor orçado deve ser numérico")
        
        valor = Decimal(str(data['valor_orcado']))
        if valor <= 0:
            raise ValidationException("Valor orçado deve ser maior que zero")
        
        data['valor_orcado'] = valor
        
        # Validar existência de entidades relacionadas
        from src.crud.organizacional_crud import OrgaosPublicosCRUD, FontesRecursosCRUD
        from src.crud.financeiro_crud import CategoriasDespesasCRUD, PeriodosCRUD
        
        orgao_crud = OrgaosPublicosCRUD()
        if not orgao_crud.get_by_id(data['orgao_id']):
            raise ValidationException(f"Órgão com ID {data['orgao_id']} não existe")
        
        fonte_crud = FontesRecursosCRUD()
        if not fonte_crud.get_by_id(data['fonte_recurso_id']):
            raise ValidationException(f"Fonte de recurso com ID {data['fonte_recurso_id']} não existe")
        
        categoria_crud = CategoriasDespesasCRUD()
        if not categoria_crud.get_by_id(data['categoria_despesa_id']):
            raise ValidationException(f"Categoria de despesa com ID {data['categoria_despesa_id']} não existe")
        
        periodo_crud = PeriodosCRUD()
        if not periodo_crud.get_by_id(data['periodo_id']):
            raise ValidationException(f"Período com ID {data['periodo_id']} não existe")
        
        return super().validate_create_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se orçamento já existe para a mesma combinação"""
        existing = session.query(Orcamento).filter(
            Orcamento.orgao_id == data['orgao_id'],
            Orcamento.fonte_recurso_id == data['fonte_recurso_id'],
            Orcamento.categoria_despesa_id == data['categoria_despesa_id'],
            Orcamento.periodo_id == data['periodo_id']
        ).first()
        
        if existing:
            raise ValidationException("Orçamento já existe para esta combinação")
    
    def get_by_orgao(self, orgao_id: int) -> List[Orcamento]:
        """Busca orçamentos por órgão"""
        return self.search({'orgao_id': orgao_id})
    
    def get_by_periodo(self, periodo_id: int) -> List[Orcamento]:
        """Busca orçamentos por período"""
        return self.search({'periodo_id': periodo_id})
    
    def get_total_orcado(self, periodo_id: int = None) -> Decimal:
        """Calcula total orçado por período"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                query = session.query(func.sum(Orcamento.valor_orcado))
                
                if periodo_id:
                    query = query.filter(Orcamento.periodo_id == periodo_id)
                
                total = query.scalar()
                return total or Decimal('0.00')
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular total orçado: {e}")
            return Decimal('0.00')


class DespesasCRUD(BaseCRUD[Despesa]):
    """CRUD para Despesas (entidade principal)"""
    
    def __init__(self):
        super().__init__(Despesa)
        self.logger = logging.getLogger(__name__)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de despesa"""
        required_fields = ['orgao_publico_id', 'fonte_recurso_id', 'categoria_despesa_id', 
                          'periodo_id', 'estado_id', 'valor_milhoes']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar valores monetários
        for field in ['valor_milhoes', 'valor_per_capita']:
            if field in data and data[field] is not None:
                if not isinstance(data[field], (int, float, Decimal)):
                    raise ValidationException(f"{field} deve ser numérico")
                
                valor = Decimal(str(data[field]))
                if valor < 0:
                    raise ValidationException(f"{field} não pode ser negativo")
                
                data[field] = valor
        
        # Validar se valor em milhões > 0
        if data['valor_milhoes'] <= 0:
            raise ValidationException("Valor em milhões deve ser maior que zero")
        
        # Validar existência de entidades relacionadas
        from src.crud.organizacional_crud import OrgaosPublicosCRUD, FontesRecursosCRUD
        from src.crud.geografia_crud import EstadosCRUD
        
        orgao_crud = OrgaosPublicosCRUD()
        if not orgao_crud.get_by_id(data['orgao_publico_id']):
            raise ValidationException(f"Órgão com ID {data['orgao_publico_id']} não existe")
        
        fonte_crud = FontesRecursosCRUD()
        if not fonte_crud.get_by_id(data['fonte_recurso_id']):
            raise ValidationException(f"Fonte de recurso com ID {data['fonte_recurso_id']} não existe")
        
        categoria_crud = CategoriasDespesasCRUD()
        if not categoria_crud.get_by_id(data['categoria_despesa_id']):
            raise ValidationException(f"Categoria de despesa com ID {data['categoria_despesa_id']} não existe")
        
        periodo_crud = PeriodosCRUD()
        if not periodo_crud.get_by_id(data['periodo_id']):
            raise ValidationException(f"Período com ID {data['periodo_id']} não existe")
        
        estado_crud = EstadosCRUD()
        if not estado_crud.get_by_id(data['estado_id']):
            raise ValidationException(f"Estado com ID {data['estado_id']} não existe")
        
        return super().validate_create_data(data)
    
    def get_by_orgao(self, orgao_id: int) -> List[Despesa]:
        """Busca despesas por órgão"""
        return self.search({'orgao_publico_id': orgao_id})
    
    def get_by_periodo(self, periodo_id: int) -> List[Despesa]:
        """Busca despesas por período"""
        return self.search({'periodo_id': periodo_id})
    
    def get_by_categoria(self, categoria_id: int) -> List[Despesa]:
        """Busca despesas por categoria"""
        return self.search({'categoria_despesa_id': categoria_id})
    
    def get_totais_por_periodo(self, periodo_id: int) -> Dict[str, Decimal]:
        """Calcula totais por período"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                result = session.query(
                    func.sum(Despesa.valor_milhoes).label('total_milhoes'),
                    func.count(Despesa.id).label('total_despesas')
                ).filter(Despesa.periodo_id == periodo_id).first()
                
                return {
                    'total_milhoes': result.total_milhoes or Decimal('0.00'),
                    'total_despesas': result.total_despesas or 0
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular totais: {e}")
            return {
                'total_milhoes': Decimal('0.00'),
                'total_despesas': 0
            }
    
    def get_despesas_por_orgao(self, periodo_id: int) -> List[Dict[str, Any]]:
        """Agrupa despesas por órgão"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                from src.models.entities import OrgaoPublico
                
                result = session.query(
                    OrgaoPublico.nome_orgao,
                    func.sum(Despesa.valor_milhoes).label('total_milhoes'),
                    func.count(Despesa.id).label('total_despesas')
                ).join(Despesa).filter(
                    Despesa.periodo_id == periodo_id
                ).group_by(OrgaoPublico.nome_orgao).all()
                
                return [
                    {
                        'orgao': row.nome_orgao,
                        'total_milhoes': row.total_milhoes or Decimal('0.00'),
                        'total_despesas': row.total_despesas or 0
                    }
                    for row in result
                ]
        except Exception as e:
            self.logger.error(f"❌ Erro ao agrupar despesas por órgão: {e}")
            return []
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de despesas"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Totais gerais
                totais = session.query(
                    func.sum(Despesa.valor_milhoes).label('total_milhoes'),
                    func.avg(Despesa.valor_per_capita).label('media_per_capita'),
                    func.count(Despesa.id).label('total_despesas')
                ).first()
                
                return {
                    'total_milhoes': totais.total_milhoes or Decimal('0.00'),
                    'media_per_capita': totais.media_per_capita or Decimal('0.00'),
                    'total_despesas': totais.total_despesas or 0
                }
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {}
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """Lista despesas com informações relacionadas"""
        try:
            with self.db_connection.get_session() as session:
                from src.models.entities import Estado, Periodo, OrgaoPublico, CategoriaDespesa
                
                # Query com JOINs para obter informações relacionadas
                query = session.query(
                    Despesa.id,
                    Estado.nome_estado,
                    Periodo.ano,
                    CategoriaDespesa.nome_categoria,
                    Despesa.valor_milhoes,
                    Despesa.valor_per_capita,
                    OrgaoPublico.nome_orgao
                ).join(Estado, Despesa.estado_id == Estado.id) \
                 .join(Periodo, Despesa.periodo_id == Periodo.id) \
                 .join(OrgaoPublico, Despesa.orgao_publico_id == OrgaoPublico.id) \
                 .join(CategoriaDespesa, Despesa.categoria_despesa_id == CategoriaDespesa.id) \
                 .order_by(Estado.nome_estado, Periodo.ano) \
                 .limit(limit).offset(offset)
                
                result = query.all()
                
                # Converter para lista de listas
                data = []
                for row in result:
                    data.append([
                        row[0],  # id
                        row[1],  # nome_estado
                        row[2],  # ano
                        row[3],  # nome_categoria (função)
                        f"R$ {float(row[4]):,.2f}M" if row[4] else "R$ 0,00M",  # valor_milhoes
                        f"R$ {float(row[5]):,.2f}" if row[5] else "R$ 0,00",     # valor_per_capita
                        row[6]   # nome_orgao
                    ])
                
                self.logger.info(f"✅ Listadas {len(data)} despesas")
                return data
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar despesas: {e}")
            return []
    
    def listar_agregado(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """Lista despesas agregadas por categoria e ano (total Brasil)"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                from src.models.entities import Periodo, CategoriaDespesa
                
                # Query agregada por categoria e ano
                query = session.query(
                    CategoriaDespesa.nome_categoria,
                    Periodo.ano,
                    func.sum(Despesa.valor_milhoes).label('valor_total')
                ).join(CategoriaDespesa, Despesa.categoria_despesa_id == CategoriaDespesa.id) \
                 .join(Periodo, Despesa.periodo_id == Periodo.id) \
                 .group_by(CategoriaDespesa.nome_categoria, Periodo.ano) \
                 .order_by(Periodo.ano, CategoriaDespesa.nome_categoria) \
                 .limit(limit).offset(offset)
                
                result = query.all()
                
                # Converter para lista de listas
                data = []
                for i, row in enumerate(result, 1):
                    data.append([
                        i,  # id sequencial
                        row[0],  # nome_categoria
                        row[1],  # ano
                        f"R$ {float(row[2]):,.2f}M" if row[2] else "R$ 0,00M"  # valor_total
                    ])
                
                self.logger.info(f"✅ Listadas {len(data)} despesas agregadas")
                return data
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar despesas agregadas: {e}")
            return [] 