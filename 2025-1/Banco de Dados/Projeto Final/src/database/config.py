"""
Configurações do Banco de Dados - DEC7588
Configurações centralizadas para PostgreSQL e SQLite
"""

import os
from pathlib import Path
from typing import Dict, Any

class DatabaseConfig:
    """Configurações do banco de dados (somente SQLite)"""
    
    # Caminho do arquivo SQLite (pode ser sobrescrito via variável de ambiente)
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'data/processed/dados_socioeconomicos.db')
    
    # Pool de conexões (mantido para compatibilidade com SQLAlchemy)
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    
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
        'database_url': f"sqlite:///{Path(db_config.SQLITE_PATH).resolve()}?check_same_thread=False",
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