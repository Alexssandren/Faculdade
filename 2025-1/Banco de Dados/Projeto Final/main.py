#!/usr/bin/env python3
"""
Projeto Final - Banco de Dados
Análise IDH vs Despesas Públicas Federais (2019-2023)

Interface gráfica moderna com:
- Dashboard interativo
- Visualizações analíticas
- Sistema CRUD completo
- Chat IA integrado

Versão: 2.0.0 (GUI)
"""

import sys
import os
import traceback
from pathlib import Path

# Suprimir avisos específicos do Qt/DPI no Windows
if sys.platform == "win32":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
    # Suprimir avisos de DPI no stderr
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="qt")

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Função principal - inicia a aplicação GUI"""
    try:
        # Importar e iniciar a aplicação GUI
        from src.gui.main_window import MainWindow
        
        print("🚀 Iniciando Projeto Final - Banco de Dados...")
        
        # Criar e executar aplicação
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        
        # Verificar se as dependências estão instaladas
        missing_deps = []
        
        try:
            import ttkbootstrap
        except ImportError:
            missing_deps.append("ttkbootstrap")
            
        try:
            import matplotlib
        except ImportError:
            missing_deps.append("matplotlib")
            
        try:
            import numpy
        except ImportError:
            missing_deps.append("numpy")
            
        if missing_deps:
            print(f"❌ Dependências ausentes: {', '.join(missing_deps)}")
            print("\n💡 Instale as dependências com:")
            print("pip install -r requirements.txt")
        else:
            print("✅ Todas as dependências estão instaladas")
            print(f"❌ Erro específico: {e}")
            
        return 1
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return 1
            
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
    