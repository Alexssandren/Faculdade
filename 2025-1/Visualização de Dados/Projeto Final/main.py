#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para orquestrar a execução completa do projeto de visualização de dados.
"""

import sys
from pathlib import Path

# Adicionar o diretório 'src' ao sys.path para permitir importações diretas dos módulos
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from pipeline import fase1_collect_data
    from pipeline import fase1b_clean_data
    from database import setup_database
    from pipeline import fase2_explore_data
    from pipeline import fase2b_advanced_analysis
    from visualization import plot_generator
    from app import dashboard_ui
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print(f"Verifique se a estrutura de diretórios e os arquivos __init__.py estão corretos em '{SRC_DIR}'.")
    sys.exit(1)

def run_complete_pipeline():
    """Executa todas as fases do pipeline de dados."""
    print("🚀 INICIANDO PIPELINE DE DADOS COMPLETO...")
    print("=" * 50)

    print("\n🔷 FASE 1: Coleta de Dados...")
    success_f1 = fase1_collect_data.main()
    if not success_f1:
        print("❌ Erro na Fase 1: Coleta de Dados. Abortando pipeline.")
        return False
    print("✅ Fase 1: Coleta de Dados concluída.")
    print("-" * 50)

    print("\n🔷 FASE 1b: Limpeza e Estruturação de Dados...")
    success_f1b = fase1b_clean_data.main()
    if not success_f1b:
        print("❌ Erro na Fase 1b: Limpeza de Dados. Abortando pipeline.")
        return False
    print("✅ Fase 1b: Limpeza e Estruturação de Dados concluída.")
    print("-" * 50)

    print("\n🔷 FASE 2.5: Configuração do Banco de Dados...")
    success_db = setup_database.main()
    if not success_db:
        print("❌ Erro na Fase 2.5: Configuração do Banco de Dados. Abortando pipeline.")
        return False
    print("✅ Fase 2.5: Configuração do Banco de Dados concluída.")
    print("-" * 50)
    
    print("\n🔷 FASE 2 (Exploração): Análise Exploratória de Dados...")
    # A função em fase2_explore_data é run_exploratory_analysis
    # Vamos assumir que ela retorna True em sucesso ou lida com erros internamente.
    try:
        fase2_explore_data.run_exploratory_analysis()
        print("✅ Fase 2 (Exploração): Análise Exploratória de Dados concluída.")
    except Exception as e_f2exp:
        print(f"❌ Erro na Fase 2 (Exploração): Análise Exploratória. Detalhes: {e_f2exp}")
        # Decidir se o pipeline deve parar aqui ou continuar. Por ora, vamos continuar.
    print("-" * 50)

    print("\n🔷 FASE 2b (Avançada): Análises Estatísticas Avançadas...")
    resultados_f2b = fase2b_advanced_analysis.main()
    if resultados_f2b is None: # A main de analises_avancadas retorna None em caso de erro
        print("⚠️  Fase 2b (Avançada): Análises Avançadas encontraram problemas ou não retornaram resultados.")
    else:
        print("✅ Fase 2b (Avançada): Análises Estatísticas Avançadas concluídas.")
    print("-" * 50)

    print("\n🔷 FASE 3: Geração de Visualizações Estáticas...")
    # A main de plot_generator pode não retornar um status explícito,
    # mas imprimirá logs de sucesso/erro.
    try:
        plot_generator.main()
        print("✅ Fase 3: Geração de Visualizações Estáticas concluída.")
    except Exception as e_f3:
        print(f"❌ Erro na Fase 3: Geração de Visualizações. Detalhes: {e_f3}")
    print("-" * 50)

    print("\n🎉 PIPELINE DE DADOS COMPLETO CONCLUÍDO!")
    print("=" * 50)
    return True

def start_dashboard_application():
    """Inicia a aplicação de Dashboard Interativo."""
    print("\n🚀 Iniciando Dashboard Interativo...")
    try:
        app = dashboard_ui.DashboardApp()
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro ao iniciar o Dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pipeline_success = run_complete_pipeline()

    if pipeline_success:
        print("\nPipeline de dados concluído com sucesso. Iniciando o Dashboard Interativo...")
        start_dashboard_application()
    else:
        print("\n O pipeline de dados não foi concluído com sucesso. O Dashboard não será iniciado.")

    print("\nPrograma finalizado.") 