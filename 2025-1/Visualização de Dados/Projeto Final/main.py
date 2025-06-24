#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para orquestrar a execução completa do projeto de visualização de dados.
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Adicionar o diretório 'src' ao sys.path para permitir importações diretas dos módulos
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Função auxiliar para verificar a existência de artefatos
def check_outputs_exist(output_paths: list[Path], phase_name: str) -> bool:
    """Verifica se todos os caminhos de Path (arquivos ou diretórios) existem e, se for um diretório, se não está vazio."""
    print(f"🔎 Verificando artefatos para a {phase_name}...")
    all_exist = True
    if not output_paths:
        print(f"  ⚠️ Lista de artefatos vazia para {phase_name}. Considerar como não existente.")
        return False

    for path_obj in output_paths:
        if not path_obj.exists():
            print(f"  ⏳ Artefato não encontrado: {path_obj.relative_to(PROJECT_ROOT)}")
            all_exist = False
        else:
            # Se o artefato existe, mas é um diretório, verifica se está vazio
            if path_obj.is_dir():
                if not any(path_obj.iterdir()):
                    print(f"  ⏳ Artefato encontrado, mas o diretório está vazio: {path_obj.relative_to(PROJECT_ROOT)}")
                    all_exist = False
                else:
                    print(f"  ✅ Artefato (diretório com conteúdo) encontrado: {path_obj.relative_to(PROJECT_ROOT)}")
            else:
                 # Se for um arquivo, a existência já basta.
                 print(f"  ✅ Artefato (arquivo) encontrado: {path_obj.relative_to(PROJECT_ROOT)}")
    
    if all_exist:
        print(f"👍 Todos os artefatos para {phase_name} encontrados.")
    else:
        print(f"❗ Alguns artefatos para {phase_name} não foram encontrados. A fase será executada.")
    return all_exist

try:
    from visualization import plot_generator
    # from app import dashboard_ui # Comentado o antigo dashboard Tkinter
    from app.gemini_style_dashboard import GeminiStyleDashboard # Importando o novo dashboard
    from PySide6.QtWidgets import QApplication # Importa QApplication aqui
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print(f"Verifique se a estrutura de diretórios e os arquivos __init__.py estão corretos em '{SRC_DIR}'.")
    sys.exit(1)

def ensure_graphs_cache():
    """Garante que o cache de gráficos está atualizado antes de iniciar o dashboard."""
    print("🔍 Verificando cache de gráficos...")
    
    try:
        # Importar apenas o necessário para verificação
        data_path = PROJECT_ROOT / "data" / "processed" / "dataset_unificado.csv"
        cache_dir = PROJECT_ROOT / "results" / "visualizations" / "dashboard_cache"
        cache_info_path = cache_dir / "cache_info.json"
        
        # Verificar se dados existem
        if not data_path.exists():
            print("⚠️ Dataset não encontrado. Pule a geração de cache.")
            return
            
        # Carregar dados para verificação
        df = pd.read_csv(data_path)
        if df.empty:
            print("⚠️ Dataset vazio. Pule a geração de cache.")
            return
            
        anos_unicos = sorted(df['ano'].dropna().unique())
        data_modification_time = data_path.stat().st_mtime
        
        # Verificar se o cache existe e está atualizado
        cache_valid = False
        if cache_info_path.exists():
            try:
                with open(cache_info_path, 'r') as f:
                    cache_info = json.load(f)
                    
                if cache_info.get('data_modification_time', 0) >= data_modification_time:
                    # Verificar se todos os arquivos esperados existem
                    all_files_exist = True
                    
                    for ano in anos_unicos:
                        expected_files = [
                            f"mapa_coropletico_{ano}.html",
                            f"grafico_pizza_{ano}.html", 
                            f"grafico_bolhas_{ano}.html",
                            f"treemap_{ano}.html"
                        ]
                        
                        for filename in expected_files:
                            if not (cache_dir / filename).exists():
                                all_files_exist = False
                                break
                        
                        if not all_files_exist:
                            break
                    
                    cache_valid = all_files_exist
            except Exception as e:
                print(f"⚠️ Erro ao verificar cache: {e}")
                cache_valid = False
        
        if not cache_valid:
            print("🔄 Gerando cache de gráficos...")
            print("⏳ Este processo pode levar alguns minutos na primeira execução...")
            
            # Criar QApplication temporária para geração de cache
            from PySide6.QtWidgets import QApplication
            import sys
            
            # Verificar se já existe uma QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
                app_created = True
            else:
                app_created = False
            
            try:
                # Importar e executar geração de cache
                from app.widgets.graphs_container import GraphsContainerWidget
                
                # Criar instância temporária apenas para gerar cache
                temp_widget = GraphsContainerWidget()
                
                print(f"✅ Cache de gráficos gerado com sucesso!")
                print(f"📊 Total de gráficos: {len(anos_unicos) * 4}")
                
            finally:
                # Limpar widget temporário
                if 'temp_widget' in locals():
                    temp_widget.deleteLater()
                
                # Se criamos a aplicação, não precisamos fechá-la aqui
                # pois será reutilizada no dashboard
        else:
            print("✅ Cache de gráficos válido encontrado.")
            
    except Exception as e:
        print(f"❌ Erro ao verificar/gerar cache: {e}")
        print("⚠️ Dashboard será iniciado sem cache (pode ser mais lento)")

def run_complete_pipeline():
    """Verifica se os dados necessários existem. Pipeline simplificado."""
    print("🚀 VERIFICANDO DADOS DO SISTEMA...")
    print("=" * 50)

    # Verificar se os dados essenciais existem
    required_files = [
        PROJECT_ROOT / "data/raw/idh_oficial_real.csv",
        PROJECT_ROOT / "data/raw/despesas_publicas_oficiais_real.csv",
        PROJECT_ROOT / "data/processed/dataset_unificado.csv",
        PROJECT_ROOT / "data/processed/projeto_visualizacao.db"
    ]
    
    print("\n🔷 Verificando arquivos essenciais...")
    all_files_exist = True
    
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✅ {file_path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  ❌ {file_path.relative_to(PROJECT_ROOT)} - ARQUIVO AUSENTE")
            all_files_exist = False
    
    # Verificar diretórios de resultados
    result_dirs = [
        PROJECT_ROOT / "results/exploratory_analysis",
        PROJECT_ROOT / "results/advanced_analysis", 
        PROJECT_ROOT / "results/visualizations"
    ]
    
    print("\n🔷 Verificando diretórios de resultados...")
    for dir_path in result_dirs:
        if dir_path.exists() and any(dir_path.iterdir()):
            print(f"  ✅ {dir_path.relative_to(PROJECT_ROOT)} (com conteúdo)")
        elif dir_path.exists():
            print(f"  ⚠️ {dir_path.relative_to(PROJECT_ROOT)} (vazio)")
        else:
            print(f"  ❌ {dir_path.relative_to(PROJECT_ROOT)} - DIRETÓRIO AUSENTE")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"     ➤ Diretório criado automaticamente")

    # Executar geração de visualizações se os dados existem
    if all_files_exist:
        print("\n🔷 FASE 3: Geração de Visualizações Estáticas...")
        try:
            plot_generator.main()
            print("✅ Visualizações geradas com sucesso.")
        except Exception as e_f3:
            print(f"❌ Erro na geração de visualizações: {e_f3}")
            print("⚠️ Sistema continuará sem visualizações estáticas.")
    else:
        print("\n⚠️ Alguns arquivos essenciais estão ausentes.")
        print("   O sistema funcionará apenas com os dados disponíveis.")

    print("\n🎉 VERIFICAÇÃO DE DADOS CONCLUÍDA!")
    print("=" * 50)
    return True

def start_dashboard_application():
    """Inicia a aplicação de Dashboard Interativo."""
    print("🚀 Iniciando Dashboard Interativo...")
    try:
        # Verificar se já existe uma QApplication (criada durante cache)
        q_app = QApplication.instance()
        if q_app is None:
            q_app = QApplication(sys.argv)
        
        # Instanciar e mostrar o dashboard
        window = GeminiStyleDashboard()
        window.show()
        
        print("✅ Dashboard inicializado com sucesso!")
        print("📱 Interface disponível - você pode começar a usar o sistema.")
        
        sys.exit(q_app.exec())

    except Exception as e:
        print(f"❌ Erro ao iniciar o Dashboard: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal do sistema."""
    print("=" * 60)
    print("🚀 INICIANDO SISTEMA DE VISUALIZAÇÃO DE DADOS")
    print("=" * 60)
    
    # Verificar se os dados processados existem
    data_path = PROJECT_ROOT / "data" / "processed" / "dataset_unificado.csv"
    if not data_path.exists():
        print("Dados processados não encontrados. Executando pipeline completo...")
        pipeline_success = run_complete_pipeline()
    else:
        print("Dados processados encontrados. Verificando integridade...")
        
        # Verificar se os dados estão íntegros
        try:
            df = pd.read_csv(data_path)
            if df.empty or len(df) < 50:  # Verificação básica de integridade
                print("Dados incompletos. Executando pipeline...")
                pipeline_success = run_complete_pipeline()
            else:
                print(f"Dados válidos encontrados ({len(df)} registros).")
                pipeline_success = True
        except Exception as e:
            print(f"Erro ao verificar dados: {e}")
            print("Executando pipeline completo...")
            pipeline_success = run_complete_pipeline()

    if pipeline_success:
        print("\nPipeline de dados verificado/concluído com sucesso.")
        
        # 1. Verificar e gerar cache de gráficos ANTES da UI
        ensure_graphs_cache()
        
        print("\n🖥️ Iniciando interface do dashboard...")
        start_dashboard_application()
    else:
        print("\n❌ O pipeline de dados não foi concluído com sucesso. O Dashboard não será iniciado.")

    print("\nPrograma finalizado.")

if __name__ == "__main__":
    main() 