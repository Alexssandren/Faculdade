#!/usr/bin/env python3
"""
Script para executar a limpeza dos dados
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from data_processing.data_cleaner import main

if __name__ == "__main__":
    main() 