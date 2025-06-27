"""
Configurações do Banco de Dados - DEC7588
Configurações centralizadas para PostgreSQL e SQLite
"""

import os
from pathlib import Path
from typing import Dict, Any

class DatabaseConfig:
    """Configurações do banco de dados"""
    
    # Configurações do PostgreSQL
    POSTGRES_HOST = os.getenv('DB_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('DB_PORT', '5432'))
    POSTGRES_DB = os.getenv('DB_NAME', 'dados_socioeconomicos_db')
    POSTGRES_USER = os.getenv('DB_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Configurações do SQLite
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'data/processed/dados_socioeconomicos.db')
    
    # Controle de banco
    FORCE_SQLITE = os.getenv('FORCE_SQLITE', 'False').lower() == 'true'
    
    # Pool de conexões
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    
    # URL de conexão PostgreSQL
    @property
    def POSTGRES_URL(self) -> str:
        """Retorna URL de conexão do PostgreSQL"""
        if not all([self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB, 
                   self.POSTGRES_USER, self.POSTGRES_PASSWORD]):
            return None
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Configurações de teste
    TEST_DATABASE = os.getenv('TEST_DB_NAME', 'dados_socioeconomicos_test_db')
    
    @classmethod
    def get_test_database_url(cls) -> str:
        """Retorna URL de conexão para testes"""
        return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.TEST_DATABASE}"
    
    # Configurações SQLAlchemy
    SQLALCHEMY_CONFIG = {
        'echo': os.getenv('DB_ECHO', 'False').lower() == 'true',
        'pool_size': POOL_SIZE,
        'max_overflow': MAX_OVERFLOW,
        'pool_pre_ping': True,
        'pool_recycle': POOL_RECYCLE,
    }

class SystemConfig:
    """Configurações gerais do sistema"""
    
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/sistema.log')
    
    # Google Gemini API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    
    # Segurança
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-desenvolvimento')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'salt-padrao')

# Configurações específicas por ambiente
ENVIRONMENT_CONFIGS = {
    'development': {
        'DB_ECHO': True,
        'DEBUG': True,
        'LOG_LEVEL': 'DEBUG'
    },
    'testing': {
        'DB_ECHO': False,
        'DEBUG': False,
        'LOG_LEVEL': 'WARNING'
    },
    'production': {
        'DB_ECHO': False,
        'DEBUG': False,
        'LOG_LEVEL': 'ERROR'
    }
}

def get_config() -> Dict[str, Any]:
    """
    Retorna configurações baseadas no ambiente atual
    """
    env = SystemConfig.ENVIRONMENT
    db_config = DatabaseConfig()
    
    base_config = {
        'database_url': db_config.POSTGRES_URL,
        'sqlalchemy_config': DatabaseConfig.SQLALCHEMY_CONFIG,
        'environment': env,
        'debug': SystemConfig.DEBUG,
        'log_level': SystemConfig.LOG_LEVEL,
        'google_api_key': SystemConfig.GOOGLE_API_KEY,
    }
    
    # Aplicar configurações específicas do ambiente
    if env in ENVIRONMENT_CONFIGS:
        base_config.update(ENVIRONMENT_CONFIGS[env])
    
    return base_config 