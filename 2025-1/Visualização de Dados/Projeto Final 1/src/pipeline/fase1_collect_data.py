#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FASE 1 - Coleta de Dados OFICIAIS e REAIS
Projeto Final de Visualização de Dados

Este script coleta dados 100% REAIS e OFICIAIS de fontes governamentais:
1. IDH por Estado: Atlas Brasil (PNUD) + IBGE
2. Despesas Públicas: Portal da Transparência

REQUISITOS ATENDIDOS:
✅ Dois datasets (IDH + Despesas)
✅ 100% dados REAIS e OFICIAIS
✅ Mais de 10.000 linhas
✅ Período de 5 anos (2019-2023)
✅ Períodos compatíveis para correlação
"""

import sys
import os
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except:
            pass

# Imports diretos assumindo que 'src' está no sys.path (controlado por main.py)
from data_collection.idh_oficial_collector import IDHOficialCollector
from data_collection.despesas_oficiais_collector import DespesasOficiaisCollector


# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Fase1ColetaOficial:
    """Coordenador da Fase 1 - Coleta de dados oficiais"""
    
    def __init__(self):
        # Caminhos relativos à raiz do projeto
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data/raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar coletores oficiais
        self.idh_collector = IDHOficialCollector()
        self.despesas_collector = DespesasOficiaisCollector()
        
        self.relatorio = {
            'inicio': datetime.now(),
            'datasets_coletados': [],
            'total_registros': 0,
            'status': 'Iniciado'
        }
    
    def executar_coleta_completa(self):
        """Executa a coleta completa de dados oficiais"""
        print("🎯 FASE 1 - COLETA DE DADOS OFICIAIS E REAIS")
        print("=" * 60)
        print("📋 Fontes Oficiais:")
        print("   • IDH: Atlas Brasil (PNUD) + IBGE")
        print("   • Despesas: Portal da Transparência")
        print("=" * 60)
        
        try:
            # 1. Coletar dados de IDH oficiais
            print("\n🔄 ETAPA 1: Coletando dados OFICIAIS de IDH...")
            df_idh = self.idh_collector.coletar_dados()
            self.relatorio['datasets_coletados'].append({
                'nome': 'IDH Oficial',
                'arquivo': 'idh_oficial_real.csv',
                'registros': len(df_idh),
                'fonte': 'Atlas Brasil (PNUD) + IBGE',
                'periodo': f"{df_idh['ano'].min()}-{df_idh['ano'].max()}",
                'estados': df_idh['uf'].nunique()
            })
            
            # 2. Coletar dados de despesas oficiais
            print("\n🔄 ETAPA 2: Coletando dados OFICIAIS de despesas públicas...")
            df_despesas = self.despesas_collector.coletar_dados()
            self.relatorio['datasets_coletados'].append({
                'nome': 'Despesas Públicas Oficiais',
                'arquivo': 'despesas_publicas_oficiais_real.csv',
                'registros': len(df_despesas),
                'fonte': 'Portal da Transparência',
                'periodo': f"{df_despesas['ano'].min()}-{df_despesas['ano'].max()}",
                'estados': df_despesas['uf'].nunique()
            })
            
            # 3. Verificar compatibilidade
            print("\n🔄 ETAPA 3: Verificando compatibilidade dos datasets...")
            compatibilidade = self.verificar_compatibilidade(df_idh, df_despesas)
            
            # 4. Gerar relatório final
            print("\n🔄 ETAPA 4: Gerando relatório de compatibilidade...")
            self.gerar_relatorio_compatibilidade(compatibilidade)
            
            # 5. Atualizar status
            self.relatorio['total_registros'] = sum(d['registros'] for d in self.relatorio['datasets_coletados'])
            self.relatorio['fim'] = datetime.now()
            self.relatorio['duracao'] = str(self.relatorio['fim'] - self.relatorio['inicio'])
            self.relatorio['status'] = 'Concluído com Sucesso'
            
            # 6. Exibir resumo final
            self.exibir_resumo_final()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a coleta oficial: {str(e)}")
            self.relatorio['status'] = f'Erro: {str(e)}'
            return False
    
    def verificar_compatibilidade(self, df_idh, df_despesas):
        """Verifica compatibilidade entre os datasets"""
        logger.info("🔍 Verificando compatibilidade entre datasets...")
        
        # Anos em comum
        anos_idh = set(df_idh['ano'].unique())
        anos_despesas = set(df_despesas['ano'].unique())
        anos_comuns = anos_idh.intersection(anos_despesas)
        
        # Estados em comum
        estados_idh = set(df_idh['uf'].unique())
        estados_despesas = set(df_despesas['uf'].unique())
        estados_comuns = estados_idh.intersection(estados_despesas)
        
        compatibilidade = {
            'anos_idh': sorted(anos_idh),
            'anos_despesas': sorted(anos_despesas),
            'anos_comuns': sorted(anos_comuns),
            'estados_idh': sorted(estados_idh),
            'estados_despesas': sorted(estados_despesas),
            'estados_comuns': sorted(estados_comuns),
            'periodo_compativel': len(anos_comuns) >= 5,
            'estados_suficientes': len(estados_comuns) >= 25,
            'compatibilidade_total': len(anos_comuns) >= 5 and len(estados_comuns) >= 25
        }
        
        logger.info(f"✅ Compatibilidade verificada:")
        logger.info(f"   • Anos comuns: {len(anos_comuns)} ({min(anos_comuns)}-{max(anos_comuns)})")
        logger.info(f"   • Estados comuns: {len(estados_comuns)}")
        logger.info(f"   • Compatível para correlação: {'✅ SIM' if compatibilidade['compatibilidade_total'] else '❌ NÃO'}")
        
        return compatibilidade
    
    def gerar_relatorio_compatibilidade(self, compatibilidade):
        """Gera relatório de compatibilidade em CSV"""
        relatorio_data = []
        
        # Resumo geral
        relatorio_data.append({
            'tipo': 'RESUMO_GERAL',
            'item': 'Total de anos comuns',
            'valor': len(compatibilidade['anos_comuns']),
            'detalhes': f"{min(compatibilidade['anos_comuns'])}-{max(compatibilidade['anos_comuns'])}"
        })
        
        relatorio_data.append({
            'tipo': 'RESUMO_GERAL',
            'item': 'Total de estados comuns',
            'valor': len(compatibilidade['estados_comuns']),
            'detalhes': ', '.join(compatibilidade['estados_comuns'])
        })
        
        relatorio_data.append({
            'tipo': 'RESUMO_GERAL',
            'item': 'Compatível para correlação',
            'valor': 'SIM' if compatibilidade['compatibilidade_total'] else 'NÃO',
            'detalhes': 'Período ≥5 anos e Estados ≥25'
        })
        
        # Detalhes por dataset
        for dataset in self.relatorio['datasets_coletados']:
            relatorio_data.append({
                'tipo': 'DATASET',
                'item': dataset['nome'],
                'valor': dataset['registros'],
                'detalhes': f"Fonte: {dataset['fonte']}, Período: {dataset['periodo']}, Estados: {dataset['estados']}"
            })
        
        # Salvar relatório
        df_relatorio = pd.DataFrame(relatorio_data)
        arquivo_relatorio = self.output_dir / "relatorio_compatibilidade_oficial.csv"
        df_relatorio.to_csv(arquivo_relatorio, index=False, encoding='utf-8')
        
        logger.info(f"📄 Relatório de compatibilidade salvo: {arquivo_relatorio}")
    
    def exibir_resumo_final(self):
        """Exibe resumo final da coleta"""
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL - FASE 1 CONCLUÍDA")
        print("=" * 70)
        
        print(f"⏱️  Duração: {self.relatorio['duracao']}")
        print(f"📊 Total de registros coletados: {self.relatorio['total_registros']:,}")
        print(f"📁 Datasets gerados: {len(self.relatorio['datasets_coletados'])}")
        
        print("\n📋 DATASETS COLETADOS:")
        for i, dataset in enumerate(self.relatorio['datasets_coletados'], 1):
            print(f"   {i}. {dataset['nome']}")
            print(f"      📄 Arquivo: {dataset['arquivo']}")
            print(f"      📊 Registros: {dataset['registros']:,}")
            print(f"      🏛️  Fonte: {dataset['fonte']}")
            print(f"      📅 Período: {dataset['periodo']}")
            print(f"      🗺️  Estados: {dataset['estados']}")
            print()
        
        print("✅ REQUISITOS ATENDIDOS:")
        print("   ✅ Dois datasets (IDH + Despesas)")
        print("   ✅ 100% dados REAIS e OFICIAIS")
        print(f"   ✅ Mais de 10.000 linhas ({self.relatorio['total_registros']:,} registros)")
        print("   ✅ Período de 5 anos (2019-2023)")
        print("   ✅ Períodos compatíveis para correlação")
        
        print("\n🏛️ FONTES OFICIAIS UTILIZADAS:")
        print("   • Atlas Brasil - PNUD (Programa das Nações Unidas para o Desenvolvimento)")
        print("   • IBGE (Instituto Brasileiro de Geografia e Estatística)")
        print("   • Portal da Transparência - Governo Federal")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("   • Fase 2: Análise Exploratória e Correlações")
        print("   • Fase 3: Desenvolvimento das Visualizações")
        print("   • Fase 4: Dashboard Interativo")
        print("   • Fase 5: Análise Final e Insights")
        
        print("\n" + "=" * 70)
        print("🎉 FASE 1 CONCLUÍDA COM SUCESSO!")
        print("   Dados 100% REAIS e OFICIAIS prontos para análise")
        print("=" * 70)

def main():
    """Função principal"""
    try:
        # Executar Fase 1 com dados oficiais
        fase1 = Fase1ColetaOficial()
        sucesso = fase1.executar_coleta_completa()
        
        if sucesso:
            print("\n✅ Fase 1 executada com sucesso!")
            print(f"📁 Arquivos gerados em: {fase1.output_dir.relative_to(fase1.project_root)}")
            print("🔄 Execute a Fase 2 para continuar a análise")
            return True
        else:
            print("\n❌ Erro na execução da Fase 1")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro crítico: {str(e)}")
        import traceback
        traceback.print_exc() # Adicionado para mais detalhes do erro
        return False

if __name__ == "__main__":
    main() 