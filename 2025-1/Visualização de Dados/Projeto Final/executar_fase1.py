# -*- coding: utf-8 -*-
"""
Script de Execução da Fase 1 - Coleta de Dados Oficiais
Compatível com Windows, Linux e macOS
"""

import sys
import os
from pathlib import Path

def main():
    """Função principal de execução"""
    print("🚀 Iniciando Fase 1 - Coleta de Dados Oficiais")
    print("=" * 50)
    
    # Verificar Python
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Diretório: {Path.cwd()}")
    
    # Importar e executar o módulo principal
    try:
        # Adicionar diretório atual ao path
        current_dir = Path(__file__).parent.absolute()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Importar o módulo principal
        import fase1_coleta_oficial
        
        # Executar a função main
        resultado = fase1_coleta_oficial.main()
        
        if resultado:
            print("\n✅ Execução concluída com sucesso!")
            return True
        else:
            print("\n❌ Execução falhou!")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se todos os arquivos estão no local correto")
        return False
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        sys.exit(1) 