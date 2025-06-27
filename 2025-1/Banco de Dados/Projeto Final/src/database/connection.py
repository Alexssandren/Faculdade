"""
Módulo de conexão e configuração do banco de dados
Suporte para PostgreSQL com fallback automático para SQLite
"""

import os
import logging
from typing import Optional, Any, Dict, List
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError

from .config import DatabaseConfig

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Gerenciador de conexão com banco de dados
    """
    
    def __init__(self, force_sqlite: bool = False):
        """
        Inicializa o gerenciador de conexão
        
        Args:
            force_sqlite: Força uso do SQLite independente da configuração
        """
        self.config = DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self.database_type: str = ""
        self.database_url: str = ""
        self.database: str = ""
        
        # Determinar qual banco usar
        if force_sqlite or self.config.FORCE_SQLITE:
            self._setup_sqlite()
        else:
            self._setup_database()
    
    def _setup_database(self):
        """Configura a conexão com o banco de dados"""
        
        # Tentar PostgreSQL apenas se todas as configurações estiverem presentes
        postgres_available = all([
            self.config.POSTGRES_HOST,
            self.config.POSTGRES_PORT,
            self.config.POSTGRES_DB,
            self.config.POSTGRES_USER,
            self.config.POSTGRES_PASSWORD
        ])
        
        if postgres_available and self.config.POSTGRES_URL:
            try:
                self._setup_postgresql()
                return
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL não disponível: {e}")
                logger.info("🔄 Usando SQLite como fallback...")
        
        # Fallback para SQLite
        self._setup_sqlite()
    
    def _setup_postgresql(self):
        """Configura conexão com PostgreSQL"""
        self.database_type = "PostgreSQL"
        self.database_url = self.config.POSTGRES_URL
        self.database = self.config.POSTGRES_DB
        
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False)
        logger.info("✅ Usando PostgreSQL")
    
    def _setup_sqlite(self):
        """Configura conexão SQLite"""
        try:
            # Caminho absoluto para o banco SQLite
            db_path = Path(self.config.SQLITE_PATH).resolve()
            
            if not db_path.exists():
                logger.error(f"❌ Banco SQLite não encontrado: {db_path}")
                raise FileNotFoundError(f"Banco SQLite não encontrado: {db_path}")
            
            # URL de conexão com configurações específicas
            database_url = f"sqlite:///{db_path}?check_same_thread=False"
            
            # Configurações específicas para SQLite
            sqlite_config = {
                'echo': False,
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 30
                }
            }
            
            # Criar engine com configurações otimizadas
            self.engine = create_engine(database_url, **sqlite_config)
            
            # Configurar event listeners para garantir tipos corretos
            from sqlalchemy import event
            
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """Configurar pragmas do SQLite para melhor performance e tipos"""
                cursor = dbapi_connection.cursor()
                # Garantir integridade referencial
                cursor.execute("PRAGMA foreign_keys=ON")
                # Melhorar performance
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.close()
            
            # Criar sessão
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            logger.info(f"✅ SQLite conectado: {db_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar SQLite: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                
            if self.database_type == "SQLite":
                logger.info("✅ Conexão com SQLite estabelecida com sucesso!")
            else:
                logger.info("✅ Conexão com PostgreSQL estabelecida com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
            return False
    
    def create_database(self) -> bool:
        """
        Cria o banco de dados se necessário
        
        Returns:
            bool: True se criação bem-sucedida
        """
        if self.database_type == "SQLite":
            # SQLite cria automaticamente
            logger.info("ℹ️ SQLite: banco será criado automaticamente.")
            return True
        
        # Para PostgreSQL, tentar criar banco
        try:
            from sqlalchemy import create_engine
            
            # Conectar ao postgres padrão para criar o banco
            base_url = self.database_url.rsplit('/', 1)[0]
            admin_url = f"{base_url}/postgres"
            
            admin_engine = create_engine(admin_url, isolation_level='AUTOCOMMIT')
            
            with admin_engine.connect() as conn:
                # Verificar se banco existe
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": self.database}
                )
                
                if not result.fetchone():
                    # Criar banco
                    conn.execute(text(f'CREATE DATABASE "{self.database}"'))
                    logger.info(f"✅ Banco de dados '{self.database}' criado com sucesso!")
                else:
                    logger.info(f"ℹ️ Banco de dados '{self.database}' já existe.")
            
            admin_engine.dispose()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar banco de dados: {e}")
            return False
    
    def create_tables(self) -> bool:
        """
        Cria as tabelas do banco de dados
        
        Returns:
            bool: True se criação bem-sucedida
        """
        try:
            from src.models.entities import Base
            
            # Criar todas as tabelas
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"✅ Todas as tabelas foram criadas com sucesso no {self.database_type}!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def drop_all_tables(self) -> bool:
        """Remove todas as tabelas (cuidado!)"""
        try:
            from src.models.entities import Base
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("⚠️ Todas as tabelas foram removidas!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover tabelas: {e}")
            return False
    
    @contextmanager
    def get_session(self):
        """
        Context manager para sessões do banco
        
        Yields:
            Session: Sessão SQLAlchemy
        """
        if not self.SessionLocal:
            raise RuntimeError("Banco de dados não inicializado")
        
        session = self.SessionLocal()
        
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
        Obtém uma nova sessão do banco (sem context manager)
        
        Returns:
            Session: Sessão do SQLAlchemy
        """
        if not self.SessionLocal:
            raise RuntimeError("Banco de dados não inicializado")
        
        return self.SessionLocal()
    
    @contextmanager
    def get_session_context(self):
        """
        Context manager para sessões do banco
        
        Yields:
            Session: Sessão SQLAlchemy
        """
        if not self.SessionLocal:
            raise RuntimeError("Banco de dados não inicializado")
        
        session = self.SessionLocal()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    def execute_sql(self, sql: str, params: Dict = None) -> List[Dict]:
        """
        Executa SQL customizado
        
        Args:
            sql: Query SQL
            params: Parâmetros da query
            
        Returns:
            List[Dict]: Resultados da query
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(sql), params or {})
                
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar SQL: {e}")
            return []
    
    def get_table_info(self) -> Dict[str, List[str]]:
        """
        Obtém informações sobre as tabelas
        
        Returns:
            Dict: Informações das tabelas
        """
        try:
            inspector = inspect(self.engine)
            tables_info = {}
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                column_names = [col['name'] for col in columns]
                tables_info[table_name] = column_names
            
            return tables_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações das tabelas: {e}")
            return {}
    
    def close_connections(self):
        """Fecha todas as conexões"""
        if self.engine:
            self.engine.dispose()
            logger.info(f"🔌 Conexões com {self.database_type} fechadas.")

# Instância global
_db_connection: Optional[DatabaseConnection] = None

def get_database_connection(force_sqlite: bool = True) -> DatabaseConnection:
    """
    Obtém a instância global da conexão com banco
    
    Args:
        force_sqlite: Força uso do SQLite (padrão: True para evitar erros)
        
    Returns:
        DatabaseConnection: Instância da conexão
    """
    global _db_connection
    
    if _db_connection is None or force_sqlite:
        _db_connection = DatabaseConnection(force_sqlite=force_sqlite)
    
    return _db_connection

def init_database(create_db: bool = True, create_tables: bool = True, force_sqlite: bool = False) -> bool:
    """
    Inicializa o sistema de banco de dados
    
    Args:
        create_db: Criar banco se não existir
        create_tables: Criar tabelas se não existirem
        force_sqlite: Forçar uso do SQLite
        
    Returns:
        bool: True se inicialização bem-sucedida
    """
    try:
        db = get_database_connection(force_sqlite=force_sqlite)
        
        # Criar banco se necessário
        if create_db and not db.create_database():
            return False
        
        # Testar conexão
        if not db.test_connection():
            return False
        
        # Criar tabelas se necessário
        if create_tables and not db.create_tables():
            return False
        
        logger.info(f"🎉 Banco de dados {db.database_type} inicializado com sucesso!")
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
        for table, columns in info.items():
            print(f"  - {table}: {columns}")
    else:
        print("❌ Falha na inicialização do banco!") 