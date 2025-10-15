"""
Importador de dados CSV para o banco de dados
Centraliza dados do dataset_unificado.csv nas tabelas do sistema
"""

import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.connection import get_database_connection
from src.models.entities import (
    Estado, Periodo, IndicadorIDH, Despesa,
    CategoriaDespesa, OrgaoPublico, FonteRecurso
)

class CSVImporter:
    """Importador de dados CSV para o banco"""
    
    def __init__(self):
        self.db_connection = get_database_connection()
        self.csv_path = Path(__file__).parent.parent.parent / "data" / "processed" / "dataset_unificado.csv"
        self.stats = {
            'estados_criados': 0,
            'periodos_criados': 0,
            'idh_criados': 0,
            'despesas_criadas': 0,
            'total_linhas': 0
        }
        
    def import_all_data(self) -> bool:
        """Importa todos os dados do CSV para o banco"""
        try:
            print("🚀 Iniciando importação do CSV para o banco...")
            
            # Verificar se arquivo existe
            if not self.csv_path.exists():
                print(f"❌ Arquivo CSV não encontrado: {self.csv_path}")
                return False
                
            # Carregar CSV
            df = pd.read_csv(self.csv_path)
            self.stats['total_linhas'] = len(df)
            print(f"📊 CSV carregado: {len(df)} registros")
            
            # Verificar conexão com banco
            if not self.db_connection._test_connection():
                print("❌ Falha na conexão com o banco")
                return False
                
            with self.db_connection.get_session() as session:
                # 1. Importar períodos únicos
                self._import_periodos(df, session)
                
                # 2. Importar estados únicos  
                self._import_estados(df, session)
                
                # 3. Criar categorias de despesa se não existirem
                self._ensure_categorias_despesa(session)
                
                # 4. Criar órgão e fonte padrão se não existirem
                self._ensure_orgao_fonte_padrao(session)
                
                # 5. Importar dados IDH
                self._import_indicadores_idh(df, session)
                
                # 6. Importar dados de despesas
                self._import_despesas(df, session)
                
                session.commit()
                
            self._print_stats()
            print("✅ Importação concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante importação: {e}")
            return False
            
    def _import_periodos(self, df: pd.DataFrame, session):
        """Importa períodos únicos do CSV"""
        anos_unicos = sorted(df['ano'].unique())
        
        for ano in anos_unicos:
            # Verificar se já existe
            periodo_existente = session.query(Periodo).filter(Periodo.ano == ano).first()
            if not periodo_existente:
                periodo = Periodo(
                    ano=ano,
                    descricao=f"Ano {ano}",
                    data_inicio=datetime(ano, 1, 1),
                    data_fim=datetime(ano, 12, 31)
                )
                session.add(periodo)
                self.stats['periodos_criados'] += 1
                print(f"  📅 Período criado: {ano}")
                
    def _import_estados(self, df: pd.DataFrame, session):
        """Importa estados únicos do CSV"""
        # Agrupar por UF para pegar dados únicos
        estados_df = df.groupby('uf').agg({
            'estado': 'first',
            'regiao': 'first',
            'populacao': 'last'  # Usar população mais recente
        }).reset_index()
        
        for _, row in estados_df.iterrows():
            # Verificar se já existe
            estado_existente = session.query(Estado).filter(Estado.sigla_uf == row['uf']).first()
            if not estado_existente:
                # Buscar região (assumindo que já existe)
                from src.models.entities import Regiao
                regiao = session.query(Regiao).filter(Regiao.nome_regiao == row['regiao']).first()
                
                if regiao:
                    estado = Estado(
                        nome_estado=row['estado'],
                        sigla_uf=row['uf'],
                        regiao_id=regiao.id,
                        capital=row['estado'],  # Simplificação
                        populacao_estimada=int(row['populacao'])
                    )
                    session.add(estado)
                    self.stats['estados_criados'] += 1
                    print(f"  🏛️ Estado criado: {row['uf']} - {row['estado']}")
                    
    def _ensure_categorias_despesa(self, session):
        """Garante que categorias de despesa existam"""
        categorias_necessarias = [
            'Assistência Social',
            'Educação', 
            'Infraestrutura',
            'Saúde'
        ]
        
        for nome_categoria in categorias_necessarias:
            categoria_existente = session.query(CategoriaDespesa).filter(
                CategoriaDespesa.nome_categoria == nome_categoria
            ).first()
            
            if not categoria_existente:
                categoria = CategoriaDespesa(
                    nome_categoria=nome_categoria,
                    descricao=f"Categoria {nome_categoria}"
                )
                session.add(categoria)
                print(f"  📂 Categoria criada: {nome_categoria}")
                
    def _ensure_orgao_fonte_padrao(self, session):
        """Garante que órgão e fonte padrão existam"""
        # Órgão padrão
        orgao_padrao = session.query(OrgaoPublico).filter(
            OrgaoPublico.nome_orgao == 'Ministério da Fazenda'
        ).first()
        
        if not orgao_padrao:
            orgao = OrgaoPublico(
                nome_orgao='Ministério da Fazenda',
                sigla_orgao='MF',
                tipo_orgao='Federal'
            )
            session.add(orgao)
            print("  🏢 Órgão padrão criado: Ministério da Fazenda")
            
        # Fonte padrão
        fonte_padrao = session.query(FonteRecurso).filter(
            FonteRecurso.nome_fonte == 'Tesouro Nacional'
        ).first()
        
        if not fonte_padrao:
            fonte = FonteRecurso(
                nome_fonte='Tesouro Nacional',
                tipo_fonte='Federal',
                descricao='Recursos do Tesouro Nacional'
            )
            session.add(fonte)
            print("  💰 Fonte padrão criada: Tesouro Nacional")
            
    def _import_indicadores_idh(self, df: pd.DataFrame, session):
        """Importa indicadores IDH do CSV"""
        for _, row in df.iterrows():
            # Buscar estado e período
            estado = session.query(Estado).filter(Estado.sigla_uf == row['uf']).first()
            periodo = session.query(Periodo).filter(Periodo.ano == row['ano']).first()
            
            if estado and periodo:
                # Verificar se já existe
                idh_existente = session.query(IndicadorIDH).filter(
                    IndicadorIDH.estado_id == estado.id,
                    IndicadorIDH.periodo_id == periodo.id
                ).first()
                
                if not idh_existente:
                    idh = IndicadorIDH(
                        estado_id=estado.id,
                        periodo_id=periodo.id,
                        idh_geral=float(row['idh']),
                        idh_educacao=float(row['idh_educacao']),
                        idh_longevidade=float(row['idh_longevidade']),
                        idh_renda=float(row['idh_renda']),
                        ranking_nacional=1  # Será calculado depois
                    )
                    session.add(idh)
                    self.stats['idh_criados'] += 1
                    
    def _import_despesas(self, df: pd.DataFrame, session):
        """Importa despesas do CSV"""
        # Buscar IDs necessários
        orgao = session.query(OrgaoPublico).filter(
            OrgaoPublico.nome_orgao == 'Ministério da Fazenda'
        ).first()
        fonte = session.query(FonteRecurso).filter(
            FonteRecurso.nome_fonte == 'Tesouro Nacional'
        ).first()
        
        categorias_map = {
            'despesa_assistencia_social': 'Assistência Social',
            'despesa_educacao': 'Educação',
            'despesa_infraestrutura': 'Infraestrutura', 
            'despesa_saude': 'Saúde'
        }
        
        for _, row in df.iterrows():
            # Buscar estado e período
            estado = session.query(Estado).filter(Estado.sigla_uf == row['uf']).first()
            periodo = session.query(Periodo).filter(Periodo.ano == row['ano']).first()
            
            if estado and periodo and orgao and fonte:
                # Criar despesa para cada categoria
                for coluna_csv, nome_categoria in categorias_map.items():
                    if coluna_csv in row and pd.notna(row[coluna_csv]):
                        # Buscar categoria
                        categoria = session.query(CategoriaDespesa).filter(
                            CategoriaDespesa.nome_categoria == nome_categoria
                        ).first()
                        
                        if categoria:
                            # Verificar se já existe
                            despesa_existente = session.query(Despesa).filter(
                                Despesa.orgao_publico_id == orgao.id,
                                Despesa.categoria_despesa_id == categoria.id,
                                Despesa.periodo_id == periodo.id,
                                Despesa.estado_id == estado.id
                            ).first()
                            
                            if not despesa_existente:
                                despesa = Despesa(
                                    orgao_publico_id=orgao.id,
                                    fonte_recurso_id=fonte.id,
                                    categoria_despesa_id=categoria.id,
                                    periodo_id=periodo.id,
                                    estado_id=estado.id,
                                    valor_milhoes=float(row[coluna_csv]),
                                    tipo_despesa='Corrente',
                                    descricao=f'{nome_categoria} - {estado.nome_estado} - {periodo.ano}'
                                )
                                session.add(despesa)
                                self.stats['despesas_criadas'] += 1
                                
    def _print_stats(self):
        """Imprime estatísticas da importação"""
        print("\n📊 ESTATÍSTICAS DA IMPORTAÇÃO:")
        print(f"  📋 Total de linhas processadas: {self.stats['total_linhas']}")
        print(f"  🏛️ Estados criados: {self.stats['estados_criados']}")
        print(f"  📅 Períodos criados: {self.stats['periodos_criados']}")
        print(f"  📈 Indicadores IDH criados: {self.stats['idh_criados']}")
        print(f"  💰 Despesas criadas: {self.stats['despesas_criadas']}")


def main():
    """Função principal para executar importação"""
    print("🔄 Iniciando importação do CSV para o banco de dados...")
    
    importer = CSVImporter()
    success = importer.import_all_data()
    
    if success:
        print("\n✅ Importação concluída com sucesso!")
        print("📊 Dados centralizados no banco de dados")
        return 0
    else:
        print("\n❌ Falha na importação")
        return 1


if __name__ == "__main__":
    exit(main()) 