#!/usr/bin/env python3
"""
IA Classificadora de Gatos e Cachorros - Arquivo Principal
=======================================================

Este arquivo único verifica dependências, baixa dados, treina modelo e inicia a interface.
"""

import os
import sys
import subprocess
import importlib
import shutil
from pathlib import Path
import time

# Cores para output no terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
ENDC = '\033[0m'

def print_header():
    """Exibe cabeçalho do programa"""
    print(f"{BOLD}{BLUE}")
    print("🐱🐶 IA CLASSIFICADORA DE GATOS E CACHORROS 🐱🐶")
    print("=" * 60)
    print(f"{ENDC}")

def print_step(step_num, description, status=""):
    """Exibe um passo do processo"""
    status_icon = {
        "✅": GREEN,
        "⚠️": YELLOW,
        "❌": RED,
        "🔄": BLUE,
        "⏳": YELLOW
    }.get(status[:2] if status else "🔄", BLUE)

    print(f"{status_icon}{step_num}. {description}{ENDC}")
    if status:
        print(f"   Status: {status}")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print_step(1, "Verificando versão do Python...")

    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_step(1, "Verificando versão do Python", "✅ Python 3.8+ encontrado")
        return True
    else:
        print_step(1, "Verificando versão do Python", f"❌ Python {version.major}.{version.minor} - requer Python 3.8+")
        return False

def install_requirements():
    """Instala as dependências necessárias"""
    print_step(2, "Verificando e instalando dependências...")

    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_step(2, "Verificando e instalando dependências", "❌ Arquivo requirements.txt não encontrado")
        return False

    try:
        # Verificar se as principais bibliotecas estão instaladas
        required_packages = [
            'scikit-learn', 'numpy', 'pandas', 'opencv-python',
            'pillow', 'streamlit', 'joblib', 'scikit-image'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"   📦 Instalando {len(missing_packages)} pacotes: {', '.join(missing_packages)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                         check=True, capture_output=True)
            print_step(2, "Verificando e instalando dependências", f"✅ {len(missing_packages)} pacotes instalados")
        else:
            print_step(2, "Verificando e instalando dependências", "✅ Todas as dependências já instaladas")

        return True

    except subprocess.CalledProcessError as e:
        print_step(2, "Verificando e instalando dependências", f"❌ Erro na instalação: {e}")
        return False
    except Exception as e:
        print_step(2, "Verificando e instalando dependências", f"❌ Erro inesperado: {e}")
        return False

def check_kaggle_credentials():
    """Verifica se as credenciais do Kaggle estão configuradas"""
    print_step(3, "Verificando credenciais do Kaggle...")

    return True  # Ignorado

def check_dataset():
    """Verifica se o dataset está baixado"""
    print_step(4, "Verificando dataset...")

    raw_data_dir = Path("data/raw")
    processed_data_dir = Path("data/processed")

    # Verificar se há dados processados
    if processed_data_dir.exists():
        features_file = processed_data_dir / "features.npy"
        labels_file = processed_data_dir / "labels.npy"

        if features_file.exists() and labels_file.exists():
            print_step(4, "Verificando dataset", "✅ Dataset processado encontrado")
            return True

    # Verificar se há dados brutos
    if raw_data_dir.exists():
        image_files = list(raw_data_dir.rglob("*.jpg")) + list(raw_data_dir.rglob("*.png"))
        if len(image_files) > 0:
            print_step(4, "Verificando dataset", f"✅ {len(image_files)} imagens encontradas")
            return True

    print_step(4, "Verificando dataset", "❌ Dataset não encontrado")
    return False

def download_and_process_data():
    """Baixa e processa o dataset"""
    print_step(5, "Baixando e processando dataset...")
    print("❌ Função desativada - baixe/processe manualmente")
    return False

def train_model():
    """Treina o modelo de IA"""
    print_step(6, "Treinando modelo de IA...")

    try:
        result = subprocess.run([sys.executable, "training/train_model.py"],
                              capture_output=True, text=True, timeout=1200)

        if result.returncode != 0:
            print(f"   ❌ Erro no treinamento: {result.stderr}")
            return False

        print("   ✅ Treinamento concluído")
        print_step(6, "Treinando modelo de IA", "✅ Modelo treinado")
        return True

    except subprocess.TimeoutExpired:
        print_step(6, "Treinando modelo de IA", "⏳ Timeout - treinamento pode estar em andamento")
        return True
    except Exception as e:
        print_step(6, "Treinando modelo de IA", f"❌ Erro: {e}")
        return False

def start_streamlit():
    """Inicia a interface Streamlit"""
    print_step(7, "Iniciando interface web...")

    try:
        print(f"{GREEN}🚀 Iniciando Streamlit...{ENDC}")
        print(f"{BLUE}Acesse: http://localhost:8501{ENDC}")
        print(f"{YELLOW}Pressione Ctrl+C para parar{ENDC}")

        # Executar Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py",
                       "--server.port", "8501", "--server.address", "localhost"])

    except KeyboardInterrupt:
        print(f"\n{YELLOW}🛑 Interface parada pelo usuário{ENDC}")
    except Exception as e:
        print_step(7, "Iniciando interface web", f"❌ Erro: {e}")

def main():
    """Função principal"""
    print_header()

    # Passo 1: Verificar Python
    if not check_python_version():
        print(f"\n{RED}❌ Versão do Python incompatível. Abortando.{ENDC}")
        sys.exit(1)

    # Passo 2: Instalar dependências
    if not install_requirements():
        print(f"\n{RED}❌ Falha na instalação das dependências. Abortando.{ENDC}")
        sys.exit(1)

    # Passo 3: Verificar Kaggle (desativado)
    check_kaggle_credentials()

    # Passo 4: Verificar dataset
    if not check_dataset():
        print(f"\n{RED}❌ Dataset não encontrado. Execute `training/preprocess_data.py` primeiro.{ENDC}")
        sys.exit(1)

    # Passo 5: Verificar se modelo existe
    models_dir = Path("data/models")
    model_files = list(models_dir.glob("*.joblib")) if models_dir.exists() else []

    if not model_files:
        print(f"\n{YELLOW}🤖 Modelo não encontrado. Treinando...{ENDC}")
        if not train_model():
            print(f"\n{RED}❌ Falha no treinamento do modelo.{ENDC}")
            sys.exit(1)

    # Passo 6: Iniciar Streamlit
    print(f"\n{GREEN}🎉 Tudo pronto! Iniciando interface...{ENDC}")
    start_streamlit()

if __name__ == "__main__":
    main()
