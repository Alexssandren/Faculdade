"""
Script principal para treinamento do modelo de classificação.
Agora delega o processo de escolha e treinamento a training/model_selection.py
"""

import warnings
import os, sys
# Garantir que diretório raiz esteja no sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Importar módulo de seleção de modelo
import training.model_selection as model_selection


def main():
    """Executa o pipeline de seleção/treino de modelo."""
    warnings.filterwarnings("ignore")
    model_selection.main()


if __name__ == "__main__":
    main()
