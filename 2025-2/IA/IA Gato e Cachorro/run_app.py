#!/usr/bin/env python3
"""
IA Classificadora de Gatos e Cachorros - Script Orquestrador
===========================================================

Este arquivo verifica dependências, prepara dados, treina modelo (se necessário)
e inicia a interface Streamlit localizada em app/main.py.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

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
    print("IA CLASSIFICADORA DE GATOS E CACHORROS")
    print("=" * 60)
    print(f"{ENDC}")


def print_step(step_num: int, description: str, status: str = ""):
    """Exibe um passo do processo"""
    status_icon = {
        "[OK]": GREEN,
        "[WARN]": YELLOW,
        "[ERROR]": RED,
        "[SYNC]": BLUE,
        "[WAIT]": YELLOW,
    }.get(status[:2] if status else "[SYNC]", BLUE)

    print(f"{status_icon}{step_num}. {description}{ENDC}")
    if status:
        print(f"   Status: {status}")


def check_python_version() -> bool:
    """Verifica se a versão do Python é compatível"""
    print_step(1, "Verificando versão do Python...")

    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_step(1, "Verificando versão do Python", "[OK] Python 3.8+ encontrado")
        return True
    print_step(1, "Verificando versão do Python", f"[ERROR] Python {version.major}.{version.minor} - requer Python 3.8+")
    return False


def install_requirements() -> bool:
    """Instala as dependências necessárias"""
    print_step(2, "Verificando e instalando dependências...")

    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_step(2, "Verificando e instalando dependências", "[ERROR] Arquivo requirements.txt não encontrado")
        return False

    try:
        required_packages = [
            "scikit-learn",
            "numpy",
            "pandas",
            "opencv-python",
            "pillow",
            "streamlit",
            "joblib",
            "scikit-image",
        ]
        missing_packages = []
        for pkg in required_packages:
            try:
                importlib.import_module(pkg.replace('-', '_'))
            except ImportError:
                missing_packages.append(pkg)

        if missing_packages:
            print(f"    Instalando {len(missing_packages)} pacotes: {', '.join(missing_packages)}")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print_step(2, "Verificando e instalando dependências", f"[OK] {len(missing_packages)} pacotes instalados")
        else:
            print_step(2, "Verificando e instalando dependências", "[OK] Todas as dependências já instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print_step(2, "Verificando e instalando dependências", f"[ERROR] Erro na instalação: {e}")
        return False
    except Exception as e:
        print_step(2, "Verificando e instalando dependências", f"[ERROR] Erro inesperado: {e}")
        return False


def check_dataset() -> bool:
    """Verifica se o dataset processado existe"""
    print_step(3, "Verificando dataset processado...")
    processed_dir = Path("data/processed")
    if (processed_dir / "features.npy").exists() and (processed_dir / "labels.npy").exists():
        print_step(3, "Verificando dataset processado", "[OK] Dataset processado encontrado")
        return True
    print_step(3, "Verificando dataset processado", "[WARN] Dataset não encontrado")
    return False


def train_model() -> bool:
    """Executa script de treinamento se necessário"""
    print_step(4, "Treinando modelo (se necessário)...")
    try:
        result = subprocess.run([sys.executable, "training/train_model.py"], capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            print(f"   [ERROR] Erro no treinamento: {result.stderr}")
            return False
        print_step(4, "Treinando modelo", "[OK] Concluído")
        return True
    except subprocess.TimeoutExpired:
        print_step(4, "Treinando modelo", "[WAIT] Timeout - treinamento demorando")
        return True
    except Exception as e:
        print_step(4, "Treinando modelo", f"[ERROR] Erro: {e}")
        return False


def start_streamlit():
    """Inicia a interface Streamlit"""
    print_step(5, "Iniciando interface web...")
    try:
        print(f"{GREEN}Abrindo Streamlit...{ENDC}")
        print(f"{BLUE}Acesse: http://localhost:8501{ENDC}")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "localhost"])
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interface parada pelo usuário{ENDC}")


def main():
    """Função principal do script orquestrador"""
    print_header()
    if not check_python_version():
        sys.exit(1)
    if not install_requirements():
        sys.exit(1)
    if not check_dataset():
        print(f"{YELLOW}[WARN] Execute 'python training/preprocess_data.py' para gerar o dataset processado.{ENDC}")
    # Verificar se há modelo treinado
    models_dir = Path("data/models")
    model_exists = any((models_dir.glob("*.joblib")))
    if not model_exists:
        print(f"{YELLOW}[WARN] Nenhum modelo encontrado. Iniciando treinamento...{ENDC}")
        if not train_model():
            sys.exit(1)
    print(f"{GREEN}Tudo pronto! Iniciando aplicação...{ENDC}")
    start_streamlit()


if __name__ == "__main__":
    main()
