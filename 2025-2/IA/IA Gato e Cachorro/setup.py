"""
Script de configuração rápida do projeto
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Executa comando e mostra progresso"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em: {description}")
        print(f"Erro: {e.stderr}")
        return False


def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Versão mínima: 3.8")
        return False


def install_dependencies():
    """Instala dependências"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Instalando dependências"
    )


def setup_kaggle():
    """Configura Kaggle (se necessário)"""
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'

    if not kaggle_json.exists():
        print("⚠️  Credenciais do Kaggle não encontradas!")
        print("Para baixar o dataset automaticamente:")
        print("1. Vá para https://www.kaggle.com")
        print("2. Clique em 'Account' > 'Create New API Token'")
        print("3. Baixe o arquivo kaggle.json")
        print(f"4. Coloque em: {kaggle_dir}")
        print("5. Execute: chmod 600 ~/.kaggle/kaggle.json")

        response = input("\nDeseja continuar sem o Kaggle configurado? (y/n): ")
        return response.lower() == 'y'

    return True


def main():
    """Função principal de setup"""
    print("🚀 Configuração do Projeto IA Classificadora")
    print("=" * 50)

    # Verificar Python
    if not check_python_version():
        print("❌ Versão do Python incompatível")
        return

    # Instalar dependências
    if not install_dependencies():
        print("❌ Falha na instalação das dependências")
        return

    # Configurar Kaggle
    if not setup_kaggle():
        print("❌ Configuração do Kaggle necessária")
        return

    print("\n🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. cd training")
    print("2. python download_data.py    # Baixar dataset")
    print("3. python preprocess_data.py  # Processar imagens")
    print("4. python train_model.py     # Treinar modelo")
    print("5. cd ../app")
    print("6. streamlit run main.py     # Iniciar aplicação")


if __name__ == "__main__":
    main()
