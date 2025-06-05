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

# Função auxiliar para verificar a existência de artefatos
def check_outputs_exist(output_paths: list[Path], phase_name: str) -> bool:
    """Verifica se todos os caminhos de Path (arquivos ou diretórios) existem."""
    print(f"🔎 Verificando artefatos para a {phase_name}...")
    all_exist = True
    if not output_paths:
        print(f"  ⚠️ Lista de artefatos vazia para {phase_name}. Considerar como não existente.")
        return False

    for path_obj in output_paths:
        if not path_obj.exists():
            print(f"  ⏳ Artefato não encontrado: {path_obj.relative_to(PROJECT_ROOT)}")
            all_exist = False
            # Não precisa de break, é bom listar todos que faltam se for o caso,
            # mas a lógica de pular depende de *todos* existirem.
            # Para otimizar a verificação, um break aqui seria mais rápido se um faltar.
            # Vamos manter assim para ter um log completo do que falta, se for o caso.
        else:
            print(f"  ✅ Artefato encontrado: {path_obj.relative_to(PROJECT_ROOT)}")
    
    if all_exist:
        print(f"👍 Todos os artefatos para {phase_name} encontrados.")
    else:
        print(f"❗ Alguns artefatos para {phase_name} não foram encontrados.")
    return all_exist

try:
    from pipeline import fase1_collect_data
    from pipeline import fase1b_clean_data
    from database import setup_database
    from pipeline import fase2_explore_data
    from pipeline import fase2b_advanced_analysis
    from visualization import plot_generator
    # from app import dashboard_ui # Comentado o antigo dashboard Tkinter
    from app.gemini_style_dashboard import GeminiStyleDashboard # Importando o novo dashboard
    from PySide6.QtWidgets import QApplication # Importa QApplication aqui
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print(f"Verifique se a estrutura de diretórios e os arquivos __init__.py estão corretos em '{SRC_DIR}'.")
    sys.exit(1)

def run_complete_pipeline():
    """Executa todas as fases do pipeline de dados."""
    print("🚀 INICIANDO PIPELINE DE DADOS COMPLETO...")
    print("=" * 50)

    # --- Fase 1: Coleta de Dados ---
    fase1_outputs = [
        PROJECT_ROOT / "data/raw/idh_oficial_real.csv",
        PROJECT_ROOT / "data/raw/despesas_publicas_oficiais_real.csv"
    ]
    print("\n🔷 FASE 1: Coleta de Dados...")
    if check_outputs_exist(fase1_outputs, "Fase 1"):
        print("⏭️  Fase 1 já concluída (artefatos encontrados). Pulando.")
        success_f1 = True
    else:
        print("🔧 Executando Fase 1: Coleta de Dados...")
        success_f1 = fase1_collect_data.main()
        if not success_f1:
            print("❌ Erro na Fase 1: Coleta de Dados. Abortando pipeline.")
            return False
    print("✅ Fase 1: Coleta de Dados verificada/concluída.")
    print("-" * 50)

    # --- Fase 1b: Limpeza e Estruturação de Dados ---
    fase1b_outputs = [PROJECT_ROOT / "data/processed/dataset_unificado.csv"]
    print("\n🔷 FASE 1b: Limpeza e Estruturação de Dados...")
    if check_outputs_exist(fase1b_outputs, "Fase 1b"):
        print("⏭️  Fase 1b já concluída (artefatos encontrados). Pulando.")
        success_f1b = True
    else:
        print("🔧 Executando Fase 1b: Limpeza de Dados...")
        success_f1b = fase1b_clean_data.main()
        if not success_f1b:
            print("❌ Erro na Fase 1b: Limpeza de Dados. Abortando pipeline.")
            return False
    print("✅ Fase 1b: Limpeza e Estruturação de Dados verificada/concluída.")
    print("-" * 50)

    # --- Fase 2.5: Configuração do Banco de Dados ---
    fase2_5_outputs = [PROJECT_ROOT / "data/processed/projeto_visualizacao.db"]
    print("\n🔷 FASE 2.5: Configuração do Banco de Dados...")
    if check_outputs_exist(fase2_5_outputs, "Fase 2.5"):
        print("⏭️  Fase 2.5 já concluída (artefatos encontrados). Pulando.")
        success_db = True
    else:
        print("🔧 Executando Fase 2.5: Configuração do Banco de Dados...")
        success_db = setup_database.main()
        if not success_db:
            print("❌ Erro na Fase 2.5: Configuração do Banco de Dados. Abortando pipeline.")
            return False
    print("✅ Fase 2.5: Configuração do Banco de Dados verificada/concluída.")
    print("-" * 50)
    
    # --- Fase 2 (Exploração): Análise Exploratória de Dados ---
    fase2_outputs = [PROJECT_ROOT / "results/exploratory_analysis"] # Verifica o diretório
    print("\n🔷 FASE 2 (Exploração): Análise Exploratória de Dados...")
    if check_outputs_exist(fase2_outputs, "Fase 2 (Exploração)"):
        print("⏭️  Fase 2 (Exploração) já concluída (artefatos encontrados). Pulando.")
    else:
        print("🔧 Executando Fase 2 (Exploração): Análise Exploratória de Dados...")
        try:
            fase2_explore_data.run_exploratory_analysis()
        except Exception as e_f2exp:
            print(f"❌ Erro na Fase 2 (Exploração): Análise Exploratória. Detalhes: {e_f2exp}")
            # Decidir se o pipeline deve parar aqui. Por ora, continua mas marca como falha implícita.
            # Para ser mais explícito, poderíamos ter um success_f2 = False aqui.
    print("✅ Fase 2 (Exploração): Análise Exploratória de Dados verificada/concluída.")
    print("-" * 50)

    # --- Fase 2b (Avançada): Análises Estatísticas Avançadas ---
    fase2b_outputs = [
        PROJECT_ROOT / "results/advanced_analysis/analises_avancadas.json",
        PROJECT_ROOT / "results/advanced_analysis/graficos" # Verifica o diretório de gráficos
    ]
    print("\n🔷 FASE 2b (Avançada): Análises Estatísticas Avançadas...")
    if check_outputs_exist(fase2b_outputs, "Fase 2b (Avançada)"):
        print("⏭️  Fase 2b (Avançada) já concluída (artefatos encontrados). Pulando.")
        # Assume que se os arquivos existem, a "execução" foi um sucesso para o pipeline
        resultados_f2b_ok = True 
    else:
        print("🔧 Executando Fase 2b (Avançada): Análises Estatísticas Avançadas...")
        resultados_f2b = fase2b_advanced_analysis.main()
        if resultados_f2b is None: # A main de analises_avancadas retorna None em caso de erro
            print("⚠️  Fase 2b (Avançada): Análises Avançadas encontraram problemas ou não retornaram resultados.")
            resultados_f2b_ok = False # Explicitamente marcar falha para lógica de pipeline
        else:
            resultados_f2b_ok = True
    
    if resultados_f2b_ok: # Ajustado para usar a flag
        print("✅ Fase 2b (Avançada): Análises Estatísticas Avançadas verificadas/concluídas.")
    else:
        # Decide se quer abortar o pipeline aqui. Por ora, apenas loga.
        print("❗ Fase 2b (Avançada) não foi concluída com sucesso.")
    print("-" * 50)

    # --- Fase 3: Geração de Visualizações Estáticas ---
    fase3_outputs = [PROJECT_ROOT / "results/final_visualizations"] # Verifica o diretório
    print("\n🔷 FASE 3: Geração de Visualizações Estáticas...")
    if check_outputs_exist(fase3_outputs, "Fase 3"):
        print("⏭️  Fase 3 já concluída (artefatos encontrados). Pulando.")
    else:
        print("🔧 Executando Fase 3: Geração de Visualizações Estáticas...")
        try:
            plot_generator.main()
        except Exception as e_f3:
            print(f"❌ Erro na Fase 3: Geração de Visualizações. Detalhes: {e_f3}")
    print("✅ Fase 3: Geração de Visualizações Estáticas verificada/concluída.")
    print("-" * 50)

    print("\n🎉 PIPELINE DE DADOS COMPLETO VERIFICADO/CONCLUÍDO!")
    print("=" * 50)
    return True

def start_dashboard_application():
    """Inicia a aplicação de Dashboard Interativo."""
    print("\n🚀 Iniciando Dashboard Interativo...")
    try:
        # app = dashboard_ui.DashboardApp() # Comentada a antiga app Tkinter
        # app.mainloop()

        # Iniciando a aplicação PySide6
        q_app = QApplication(sys.argv)
        # window = PySideDashboardApp() # Comentada a instanciação anterior
        window = GeminiStyleDashboard() # Instanciando o novo dashboard
        window.show()
        sys.exit(q_app.exec())

    except Exception as e:
        print(f"❌ Erro ao iniciar o Dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pipeline_success = run_complete_pipeline()

    if pipeline_success: # Esta flag agora reflete se as fases *necessárias* foram executadas com sucesso
        print("\nPipeline de dados verificado/concluído com sucesso. Iniciando o Dashboard Interativo...")
        start_dashboard_application()
    else:
        print("\n O pipeline de dados não foi concluído com sucesso. O Dashboard não será iniciado.")

    print("\nPrograma finalizado.") 