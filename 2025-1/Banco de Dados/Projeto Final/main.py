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

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Função principal - inicia a aplicação GUI"""
    try:
        # Importar e iniciar a aplicação GUI
        from src.gui.main_window import MainWindow
        
        print("🚀 Iniciando Projeto Final - Banco de Dados...")
        print("📊 Interface Gráfica Moderna")
        print("🔄 Carregando componentes...")
        
        # Criar e executar aplicação
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n🔧 Verificando dependências...")
        
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
            print("\n🔄 Ou instale manualmente:")
            for dep in missing_deps:
                print(f"pip install {dep}")
        else:
            print("✅ Todas as dependências estão instaladas")
            print(f"❌ Erro específico: {e}")
            
        # Tentar usar CLI como fallback
        print("\n🔄 Tentando usar interface CLI como fallback...")
        try:
            from main_cli import main as cli_main
            print("✅ Interface CLI disponível")
            return cli_main()
        except Exception as cli_error:
            print(f"❌ Interface CLI também falhou: {cli_error}")
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print(f"📋 Detalhes do erro:\n{traceback.format_exc()}")
        
        # Informações de debug
        print("\n🔍 Informações de Debug:")
        print(f"Python: {sys.version}")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Arquivo executado: {__file__}")
        print(f"Caminho do projeto: {project_root}")
        
        # Verificar estrutura de arquivos
        print("\n📁 Estrutura de arquivos:")
        gui_path = project_root / "src" / "gui"
        if gui_path.exists():
            print(f"✅ Diretório GUI existe: {gui_path}")
            main_window_path = gui_path / "main_window.py"
            if main_window_path.exists():
                print(f"✅ MainWindow existe: {main_window_path}")
            else:
                print(f"❌ MainWindow não encontrado: {main_window_path}")
        else:
            print(f"❌ Diretório GUI não encontrado: {gui_path}")
            
        # Tentar CLI como fallback
        print("\n🔄 Tentando usar interface CLI como fallback...")
        try:
            from main_cli import main as cli_main
            print("✅ Usando interface CLI")
            return cli_main()
        except Exception as cli_error:
            print(f"❌ Interface CLI também falhou: {cli_error}")
            return 1
            
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
    