"""
Configurações gerais do projeto IA Classificadora de Gatos e Cachorros
"""

import os
from pathlib import Path

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# Configurações do modelo
MODEL_CONFIG = {
    'image_size': (128, 128),  # Aumentado para capturar mais detalhes
    'test_size': 0.2,       # Proporção para teste
    'random_state': 42,     # Seed para reprodutibilidade
}

# Configurações do dataset Kaggle
KAGGLE_DATASET = {
    'dataset_name': 'tongpython/cat-and-dog',
    'unzip_dir': str(RAW_DATA_DIR),
}

# Configurações da aplicação Streamlit
STREAMLIT_CONFIG = {
    'page_title': '🐱🐶 Classificador de Gatos e Cachorros',
    'page_icon': '🐾',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Classes de predição
CLASSES = {
    0: 'Gato',
    1: 'Cachorro'
}

# Configurações de treinamento
TRAINING_CONFIG = {
    'n_estimators': 100,    # Para Random Forest
    'random_state': 42,
    'n_jobs': -1,           # Usar todos os cores da CPU
}

# Configurações de logging
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
