"""
Base CRUD - Sistema DEC7588
Classe base com operações CRUD genéricas para todas as entidades
"""

import sys
import os
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func, and_, or_
import logging

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database_connection
from src.models.entities import Base

# Type variable para genericidade
ModelType = TypeVar("ModelType", bound=Base)

logger = logging.getLogger(__name__)

class CRUDException(Exception):
    """Exceção personalizada para operações CRUD"""
    pass

class ValidationException(CRUDException):
    """Exceção para erros de validação"""
    pass

class BaseCRUD(Generic[ModelType]):
    """
    Classe base para operações CRUD genéricas
    
    Fornece operações básicas de Create, Read, Update, Delete
    que podem ser herdadas e especializadas por cada entidade.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializa o CRUD base
        
        Args:
            model: Classe do modelo SQLAlchemy
        """
        self.model = model
        self.db_connection = get_database_connection()
        
    # ==================== CREATE ====================
    
    def create(self, **data) -> ModelType:
        """
        Cria um novo registro
        
        Args:
            **data: Dados para criar o registro
            
        Returns:
            ModelType: Objeto criado
            
        Raises:
            ValidationException: Se os dados são inválidos
            CRUDException: Se houver erro na criação
        """
        try:
            # Validar dados antes de criar
            validated_data = self.validate_create_data(data)
            
            with self.db_connection.get_session() as session:
                # Verificar se já existe (se aplicável)
                if hasattr(self, 'check_duplicates'):
                    self.check_duplicates(session, validated_data)
                
                # Criar novo objeto
                obj = self.model(**validated_data)
                session.add(obj)
                session.flush()  # Para obter o ID
                
                return obj
                
        except IntegrityError as e:
            logger.error(f"❌ Erro de integridade ao criar {self.model.__name__}: {e}")
            raise CRUDException(f"Violação de integridade: {str(e)}")
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao criar {self.model.__name__}: {e}")
            raise CRUDException(f"Erro na criação: {str(e)}")
    
    # ==================== READ ====================
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Busca um registro por ID
        
        Args:
            id: ID do registro
            
        Returns:
            ModelType ou None: Objeto encontrado ou None
        """
        try:
            with self.db_connection.get_session() as session:
                return session.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"❌ Erro ao buscar {self.model.__name__} por ID {id}: {e}")
            return None
    
    def get_all(self, limit: int = 1000, offset: int = 0) -> List[ModelType]:
        """
        Busca todos os registros com paginação
        
        Args:
            limit: Limite de registros
            offset: Offset para paginação
            
        Returns:
            List[ModelType]: Lista de objetos
        """
        try:
            with self.db_connection.get_session() as session:
                return session.query(self.model).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todos {self.model.__name__}: {e}")
            return []
    
    def search(self, filters: Dict[str, Any]) -> List[ModelType]:
        """
        Busca registros com filtros
        
        Args:
            filters: Dicionário com filtros {campo: valor}
            
        Returns:
            List[ModelType]: Lista de objetos filtrados
        """
        try:
            with self.db_connection.get_session() as session:
                query = session.query(self.model)
                
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, str) and '%' in value:
                            # Busca com LIKE
                            query = query.filter(getattr(self.model, field).like(value))
                        else:
                            # Busca exata
                            query = query.filter(getattr(self.model, field) == value)
                
                return query.all()
        except Exception as e:
            logger.error(f"❌ Erro ao pesquisar {self.model.__name__}: {e}")
            return []
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Conta registros total ou com filtros
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            int: Número de registros
        """
        try:
            with self.db_connection.get_session() as session:
                query = session.query(func.count(self.model.id))
                
                if filters:
                    for field, value in filters.items():
                        if hasattr(self.model, field):
                            query = query.filter(getattr(self.model, field) == value)
                
                return query.scalar() or 0
        except Exception as e:
            logger.error(f"❌ Erro ao contar {self.model.__name__}: {e}")
            return 0
    
    # ==================== UPDATE ====================
    
    def update(self, id: int, **data) -> Optional[ModelType]:
        """
        Atualiza um registro por ID
        
        Args:
            id: ID do registro
            **data: Dados para atualizar
            
        Returns:
            ModelType ou None: Objeto atualizado ou None
            
        Raises:
            ValidationException: Se os dados são inválidos
            CRUDException: Se houver erro na atualização
        """
        try:
            # Validar dados antes de atualizar
            validated_data = self.validate_update_data(data)
            
            with self.db_connection.get_session() as session:
                obj = session.query(self.model).filter(self.model.id == id).first()
                
                if not obj:
                    return None
                
                # Atualizar campos
                for key, value in validated_data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                
                session.flush()
                
                return obj
                
        except IntegrityError as e:
            logger.error(f"❌ Erro de integridade ao atualizar {self.model.__name__}: {e}")
            raise CRUDException(f"Violação de integridade: {str(e)}")
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao atualizar {self.model.__name__}: {e}")
            raise CRUDException(f"Erro na atualização: {str(e)}")
    
    # ==================== DELETE ====================
    
    def delete(self, id: int) -> bool:
        """
        Remove um registro por ID
        
        Args:
            id: ID do registro
            
        Returns:
            bool: True se removido com sucesso
            
        Raises:
            CRUDException: Se houver erro na remoção
        """
        try:
            with self.db_connection.get_session() as session:
                obj = session.query(self.model).filter(self.model.id == id).first()
                
                if not obj:
                    return False
                
                session.delete(obj)
                session.flush()
                
                return True
                
        except IntegrityError as e:
            logger.error(f"❌ Erro de integridade ao remover {self.model.__name__}: {e}")
            raise CRUDException(f"Violação de integridade: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao remover {self.model.__name__}: {e}")
            raise CRUDException(f"Erro na remoção: {str(e)}")
    
    def delete_multiple(self, ids: List[int]) -> int:
        """
        Remove múltiplos registros
        
        Args:
            ids: Lista de IDs para remover
            
        Returns:
            int: Número de registros removidos
        """
        removed_count = 0
        errors = []
        
        for id in ids:
            try:
                if self.delete(id):
                    removed_count += 1
            except Exception as e:
                errors.append(f"ID {id}: {str(e)}")
        
        if errors:
            logger.warning(f"⚠️ Erros na remoção múltipla: {errors}")
        
        return removed_count
    
    # ==================== VALIDATION ====================
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados para criação
        
        Args:
            data: Dados a serem validados
            
        Returns:
            Dict: Dados validados
            
        Raises:
            ValidationException: Se dados inválidos
        """
        # Implementação base - pode ser sobrescrita pelas classes filhas
        return data
    
    def validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados para atualização
        
        Args:
            data: Dados a serem validados
            
        Returns:
            Dict: Dados validados
            
        Raises:
            ValidationException: Se dados inválidos
        """
        # Implementação base - pode ser sobrescrita pelas classes filhas
        return data
    
    # ==================== UTILITY METHODS ====================
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """
        Lista registros em formato tabular
        
        Args:
            limit: Limite de registros
            offset: Offset para paginação
            
        Returns:
            List[List]: Dados em formato tabular
        """
        try:
            objetos = self.get_all(limit=limit, offset=offset)
            
            if not objetos:
                return []
            
            # Obter atributos para exibição
            display_attrs = self._get_display_attributes()
            
            # Converter para lista de listas
            data = []
            for obj in objetos:
                row = []
                for attr in display_attrs:
                    value = getattr(obj, attr, '')
                    row.append(str(value) if value is not None else '')
                data.append(row)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar {self.model.__name__}: {e}")
            return []
    
    def _get_display_attributes(self) -> List[str]:
        """
        Obtém atributos para exibição
        
        Returns:
            List[str]: Lista de atributos
        """
        # Implementação base - retorna alguns campos comuns
        common_attrs = ['id', 'nome', 'nome_estado', 'nome_regiao', 'titulo', 'valor_milhoes']
        
        actual_attrs = []
        for attr in common_attrs:
            if hasattr(self.model, attr):
                actual_attrs.append(attr)
        
        return actual_attrs[:5]  # Limitar a 5 campos
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Cria múltiplos registros em lote
        
        Args:
            data_list: Lista de dados para criar
            
        Returns:
            List[ModelType]: Lista de objetos criados
        """
        created_objects = []
        
        try:
            with self.db_connection.get_session() as session:
                for data in data_list:
                    validated_data = self.validate_create_data(data)
                    obj = self.model(**validated_data)
                    session.add(obj)
                    created_objects.append(obj)
                
                session.flush()
                
                return created_objects
                
        except Exception as e:
            logger.error(f"❌ Erro na criação em lote {self.model.__name__}: {e}")
            return []
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo dos dados
        
        Returns:
            Dict: Resumo com estatísticas
        """
        try:
            total = self.count()
            
            # Estatísticas básicas
            summary = {
                'model_name': self.model.__name__,
                'total_records': total,
                'table_name': getattr(self.model, '__tablename__', 'unknown')
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo {self.model.__name__}: {e}")
            return {} 