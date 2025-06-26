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
                
                # Log da operação
                logger.info(f"✅ {self.model.__name__} criado: ID {obj.id}")
                
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
            # Validar dados
            validated_data = self.validate_update_data(data)
            
            with self.db_connection.get_session() as session:
                obj = session.query(self.model).filter(self.model.id == id).first()
                
                if not obj:
                    raise CRUDException(f"{self.model.__name__} com ID {id} não encontrado")
                
                # Atualizar campos
                for field, value in validated_data.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
                
                session.flush()
                
                logger.info(f"✅ {self.model.__name__} ID {id} atualizado")
                return obj
                
        except CRUDException:
            raise
        except ValidationException:
            raise
        except IntegrityError as e:
            logger.error(f"❌ Erro de integridade ao atualizar {self.model.__name__}: {e}")
            raise CRUDException(f"Violação de integridade: {str(e)}")
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
                    raise CRUDException(f"{self.model.__name__} com ID {id} não encontrado")
                
                # Verificar dependências (se aplicável)
                if hasattr(self, 'check_dependencies'):
                    self.check_dependencies(session, obj)
                
                session.delete(obj)
                session.flush()
                
                logger.info(f"✅ {self.model.__name__} ID {id} removido")
                return True
                
        except CRUDException:
            raise
        except IntegrityError as e:
            logger.error(f"❌ Erro de integridade ao remover {self.model.__name__}: {e}")
            raise CRUDException(f"Não é possível remover: há registros dependentes")
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao remover {self.model.__name__}: {e}")
            raise CRUDException(f"Erro na remoção: {str(e)}")
    
    def delete_multiple(self, ids: List[int]) -> int:
        """
        Remove múltiplos registros por IDs
        
        Args:
            ids: Lista de IDs
            
        Returns:
            int: Número de registros removidos
        """
        removed_count = 0
        errors = []
        
        for id in ids:
            try:
                if self.delete(id):
                    removed_count += 1
            except CRUDException as e:
                errors.append(f"ID {id}: {str(e)}")
        
        if errors:
            logger.warning(f"⚠️ Erros na remoção múltipla: {errors}")
        
        return removed_count
    
    # ==================== VALIDAÇÕES ====================
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados para criação (deve ser sobrescrito pelas subclasses)
        
        Args:
            data: Dados a validar
            
        Returns:
            Dict[str, Any]: Dados validados
        """
        # Implementação base - remover campos None e vazios
        validated = {}
        for key, value in data.items():
            if value is not None and value != '':
                validated[key] = value
        
        return validated
    
    def validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados para atualização (pode ser sobrescrito)
        
        Args:
            data: Dados a validar
            
        Returns:
            Dict[str, Any]: Dados validados
        """
        # Por padrão, usa a mesma validação de criação
        return self.validate_create_data(data)
    
    # ==================== UTILITÁRIOS ====================
    
    def listar(self, limit: int = 1000, offset: int = 0) -> List[List[Any]]:
        """
        Lista registros formatados para exibição em tabela
        
        Args:
            limit: Número máximo de registros
            offset: Deslocamento para paginação
            
        Returns:
            List[List[Any]]: Lista de listas com dados formatados
        """
        try:
            registros = self.get_all(limit=limit, offset=offset)
            dados_formatados = []
            
            for registro in registros:
                # Converter objeto SQLAlchemy para lista de valores
                linha = [getattr(registro, attr) for attr in self._get_display_attributes()]
                dados_formatados.append(linha)
            
            return dados_formatados
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar {self.model.__name__}: {e}")
            return []
    
    def _get_display_attributes(self) -> List[str]:
        """
        Retorna lista de atributos para exibição (deve ser sobrescrito)
        
        Returns:
            List[str]: Lista de nomes de atributos
        """
        # Implementação padrão - todos os atributos exceto created_at, updated_at
        attrs = []
        for column in self.model.__table__.columns:
            if column.name not in ['created_at', 'updated_at']:
                attrs.append(column.name)
        return attrs
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Criação em lote para performance
        
        Args:
            data_list: Lista de dicionários com dados
            
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
                
                logger.info(f"✅ {len(created_objects)} {self.model.__name__} criados em lote")
                return created_objects
                
        except Exception as e:
            logger.error(f"❌ Erro na criação em lote {self.model.__name__}: {e}")
            raise CRUDException(f"Erro na criação em lote: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo estatístico da entidade
        
        Returns:
            Dict[str, Any]: Estatísticas da entidade
        """
        try:
            total = self.count()
            
            summary = {
                'entidade': self.model.__name__,
                'total_registros': total,
                'tem_registros': total > 0
            }
            
            # Adicionar estatísticas específicas se implementadas
            if hasattr(self, 'get_custom_stats'):
                summary.update(self.get_custom_stats())
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo {self.model.__name__}: {e}")
            return {
                'entidade': self.model.__name__,
                'total_registros': 0,
                'erro': str(e)
            } 