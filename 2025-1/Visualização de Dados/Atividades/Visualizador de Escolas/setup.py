import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def instalar_dependencias():
    """Instala as dependências necessárias"""
    try:
        logger.info("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar dependências: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao instalar dependências: {e}")
        raise

if __name__ == "__main__":
    instalar_dependencias() 