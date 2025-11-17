"""Sistema de logging estruturado"""
import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/sma_system.log")


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configura um logger com handlers para arquivo e console"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Evitar duplicação de handlers
    if logger.handlers:
        return logger

    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo
    file_handler = logging.FileHandler(
        log_file or LOG_FILE,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Loggers específicos para cada agente
wallet_logger = setup_logger("WalletManager", "logs/wallet_manager.log")
market_logger = setup_logger("MarketAnalyst", "logs/market_analyst.log")
portfolio_logger = setup_logger("PortfolioManager", "logs/portfolio_manager.log")
system_logger = setup_logger("SMA_System", "logs/sma_system.log")

