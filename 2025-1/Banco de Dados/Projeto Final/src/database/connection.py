"""
Gerenciador de Conexão com Banco PostgreSQL - DEC7588
Configuração SQLAlchemy para sistema de dados socioeconômicos
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Optional, Generator

# Adicionar o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.entities import Base

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Gerenciador de conexão com PostgreSQL (com fallback para SQLite)
    """
    
    def __init__(self, database_url: Optional[str] = None, use_sqlite_fallback: bool = True):
        """
        Inicializa a conexão com o banco
        
        Args:
            database_url: URL de conexão completa (opcional)
            use_sqlite_fallback: Se deve usar SQLite quando PostgreSQL não disponível
        """
        self.use_sqlite_fallback = use_sqlite_fallback
        self.is_sqlite = False
        self.force_sqlite = False  # Flag para forçar SQLite
        
        if database_url:
            self.database_url = database_url
        else:
            # Configuração padrão do PostgreSQL
            self.host = os.getenv('DB_HOST', 'localhost')
            self.port = os.getenv('DB_PORT', '5432')
            self.database = os.getenv('DB_NAME', 'dados_socioeconomicos_db')
            self.username = os.getenv('DB_USER', 'postgres')
            self.password = os.getenv('DB_PASSWORD', 'postgres')
            
            self.database_url = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        # Tentar conectar com PostgreSQL primeiro
        self.engine = self._create_engine()
        self._test_connection()
    
    def _create_engine(self):
        """Cria engine SQLAlchemy com fallback"""
        # Se force_sqlite está ativado, pular PostgreSQL
        if self.force_sqlite or not self.use_sqlite_fallback:
            logger.info("🔄 Forçando uso do SQLite...")
            sqlite_url = f"sqlite:///data/processed/dados_socioeconomicos.db"
            self.is_sqlite = True
            
            # Criar diretório se não existir
            os.makedirs("data/processed", exist_ok=True)
            
            engine = create_engine(
                sqlite_url,
                echo=False,
                pool_pre_ping=True
            )
            
            logger.info("✅ Usando SQLite (forçado)")
            return engine
        
        try:
            # Tentar PostgreSQL primeiro
            engine = create_engine(
                self.database_url,
                echo=False,  # True para debug SQL
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Testar conexão rapidamente
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Usando PostgreSQL")
            return engine
            
        except Exception as e:
            if self.use_sqlite_fallback:
                logger.warning(f"⚠️ PostgreSQL não disponível: {e}")
                logger.info("🔄 Usando SQLite como fallback...")
                
                # Usar SQLite como fallback
                sqlite_url = f"sqlite:///data/processed/dados_socioeconomicos.db"
                self.is_sqlite = True
                
                # Criar diretório se não existir
                os.makedirs("data/processed", exist_ok=True)
                
                engine = create_engine(
                    sqlite_url,
                    echo=False,
                    pool_pre_ping=True
                )
                
                logger.info("✅ Usando SQLite (modo desenvolvimento)")
                return engine
            else:
                raise e
    
    def _test_connection(self) -> bool:
        """
        Testa se a conexão com o banco está funcionando
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                if self.is_sqlite:
                    logger.info("✅ Conexão com SQLite estabelecida com sucesso!")
                else:
                    logger.info("✅ Conexão com PostgreSQL estabelecida com sucesso!")
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """
        Cria o banco de dados se não existir (apenas para PostgreSQL)
        
        Returns:
            bool: True se criação bem-sucedida ou já existe
        """
        if self.is_sqlite:
            logger.info("ℹ️ SQLite: banco será criado automaticamente.")
            return True
            
        try:
            # URL de conexão temporária para o postgres padrão
            temp_url = self.database_url.rsplit('/', 1)[0] + '/postgres'
            temp_engine = create_engine(temp_url)
            
            with temp_engine.connect() as connection:
                # Verificar se o banco existe
                result = connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": self.database}
                )
                
                if not result.fetchone():
                    # Criar o banco
                    connection.execute(text("COMMIT"))
                    connection.execute(text(f"CREATE DATABASE {self.database}"))
                    logger.info(f"✅ Banco de dados '{self.database}' criado com sucesso!")
                else:
                    logger.info(f"ℹ️ Banco de dados '{self.database}' já existe.")
            
            temp_engine.dispose()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao criar banco de dados: {e}")
            return False
    
    def create_all_tables(self) -> bool:
        """
        Cria todas as tabelas do modelo
        
        Returns:
            bool: True se criação bem-sucedida
        """
        try:
            # Importar todos os modelos para garantir que estão registrados
            from src.models.entities import (
                Regiao, Estado, Municipio, OrgaoPublico, FonteRecurso,
                CategoriaDespesa, Periodo, Orcamento, Despesa, 
                IndicadorIDH, Usuario, Relatorio
            )
            
            Base.metadata.create_all(bind=self.engine)
            db_type = "SQLite" if self.is_sqlite else "PostgreSQL"
            logger.info(f"✅ Todas as tabelas foram criadas com sucesso no {db_type}!")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def drop_all_tables(self) -> bool:
        """
        Remove todas as tabelas (CUIDADO!)
        
        Returns:
            bool: True se remoção bem-sucedida
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("⚠️ Todas as tabelas foram removidas!")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao remover tabelas: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager para sessões do banco
        
        Yields:
            Session: Sessão SQLAlchemy
        """
        # Configuração da sessão
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    def get_new_session(self) -> Session:
        """
        Retorna uma nova sessão (lembre-se de fechar!)
        
        Returns:
            Session: Nova sessão SQLAlchemy
        """
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        return SessionLocal()
    
    def execute_raw_sql(self, sql: str, params: dict = None) -> list:
        """
        Executa SQL raw e retorna resultados
        
        Args:
            sql: Query SQL
            params: Parâmetros para a query
            
        Returns:
            list: Resultados da query
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao executar SQL: {e}")
            raise
    
    def get_table_info(self) -> dict:
        """
        Retorna informações sobre as tabelas
        
        Returns:
            dict: Informações das tabelas
        """
        info = {}
        try:
            with self.get_session() as session:
                if self.is_sqlite:
                    # Consulta específica para SQLite
                    sql = """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                    """
                    
                    result = session.execute(text(sql))
                    tables = [row[0] for row in result]
                    
                    for table_name in tables:
                        info[table_name] = {'columns': [], 'count': 0}
                        
                        # Contar registros
                        try:
                            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                            info[table_name]['count'] = count_result.scalar()
                        except:
                            info[table_name]['count'] = 0
                else:
                    # Consulta para PostgreSQL
                    sql = """
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                    """
                    
                    result = session.execute(text(sql))
                    
                    for row in result:
                        table_name = row[0]
                        if table_name not in info:
                            info[table_name] = {'columns': [], 'count': 0}
                        
                        info[table_name]['columns'].append({
                            'name': row[1],
                            'type': row[2],
                            'nullable': row[3] == 'YES',
                            'default': row[4]
                        })
                    
                    # Contar registros em cada tabela
                    for table_name in info.keys():
                        try:
                            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                            info[table_name]['count'] = count_result.scalar()
                        except:
                            info[table_name]['count'] = 0
                        
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao obter informações das tabelas: {e}")
        
        return info
    
    def close(self):
        """
        Fecha todas as conexões
        """
        self.engine.dispose()
        db_type = "SQLite" if self.is_sqlite else "PostgreSQL"
        logger.info(f"🔌 Conexões com {db_type} fechadas.")


# Instância global (singleton)
_db_connection = None

def get_database_connection() -> DatabaseConnection:
    """
    Retorna instância singleton da conexão com o banco
    
    Returns:
        DatabaseConnection: Instância da conexão
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection

def init_database(create_db: bool = True, create_tables: bool = True) -> bool:
    """
    Inicializa o banco de dados completo
    
    Args:
        create_db: Se deve criar o banco
        create_tables: Se deve criar as tabelas
        
    Returns:
        bool: True se inicialização bem-sucedida
    """
    try:
        db = get_database_connection()
        
        if create_db and not db.is_sqlite:
            if not db.create_database_if_not_exists():
                return False
        
        if create_tables:
            if not db.create_all_tables():
                return False
        
        db_type = "SQLite" if db.is_sqlite else "PostgreSQL"
        logger.info(f"🎉 Banco de dados {db_type} inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        return False

# Exemplo de uso
if __name__ == "__main__":
    # Teste da conexão
    db = DatabaseConnection()
    
    # Inicializar banco completo
    if init_database():
        print("✅ Sistema de banco inicializado!")
        
        # Mostrar informações das tabelas
        info = db.get_table_info()
        print(f"\n📊 Tabelas criadas: {len(info)}")
        for table, details in info.items():
            print(f"  - {table}: {details['count']} registros, {len(details.get('columns', []))} colunas")
    else:
        print("❌ Falha na inicialização do banco!") 