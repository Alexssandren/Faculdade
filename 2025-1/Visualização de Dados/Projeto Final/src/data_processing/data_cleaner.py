#!/usr/bin/env python3
"""
Limpeza e Estruturação dos Dados
Padroniza nomenclaturas, trata valores ausentes e cria estrutura unificada
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import unicodedata
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """Classe para limpeza e estruturação dos dados"""
    
    def __init__(self):
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Mapeamento de estados para padronização
        self.estados_padrao = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }
        
        # Mapeamento de regiões
        self.regioes = {
            'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 
            'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
    
    def limpar_texto(self, texto):
        """Remove acentos e caracteres especiais de texto"""
        if pd.isna(texto):
            return texto
        
        # Normalizar unicode
        texto_normalizado = unicodedata.normalize('NFD', str(texto))
        # Remover acentos
        texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        return texto_sem_acentos
    
    def limpar_dados_idh(self):
        """Limpa e padroniza os dados de IDH"""
        logger.info("🧹 Limpando dados de IDH...")
        
        # Carregar dados
        df = pd.read_csv(self.raw_dir / "idh_atlas_brasil_real.csv")
        
        # Verificar estrutura inicial
        logger.info(f"📊 Dados originais: {len(df)} registros")
        
        # Padronizar nomes de estados
        df['estado_padrao'] = df['uf'].map(self.estados_padrao)
        df['regiao_padrao'] = df['uf'].map(self.regioes)
        
        # Verificar dados ausentes
        missing_before = df.isnull().sum().sum()
        
        # Tratar valores ausentes (se houver)
        if df.isnull().any().any():
            logger.warning("⚠️ Dados ausentes encontrados, aplicando tratamento...")
            # Para IDH, usar interpolação linear por estado
            for uf in df['uf'].unique():
                mask = df['uf'] == uf
                df.loc[mask, 'idh'] = df.loc[mask, 'idh'].interpolate(method='linear')
                df.loc[mask, 'idh_educacao'] = df.loc[mask, 'idh_educacao'].interpolate(method='linear')
                df.loc[mask, 'idh_longevidade'] = df.loc[mask, 'idh_longevidade'].interpolate(method='linear')
                df.loc[mask, 'idh_renda'] = df.loc[mask, 'idh_renda'].interpolate(method='linear')
        
        # Validar faixas de valores
        df['idh'] = df['idh'].clip(0, 1)
        df['idh_educacao'] = df['idh_educacao'].clip(0, 1)
        df['idh_longevidade'] = df['idh_longevidade'].clip(0, 1)
        df['idh_renda'] = df['idh_renda'].clip(0, 1)
        
        # Adicionar colunas derivadas
        df['idh_categoria'] = pd.cut(df['idh'], 
                                   bins=[0, 0.550, 0.700, 0.800, 1.0],
                                   labels=['Baixo', 'Médio', 'Alto', 'Muito Alto'])
        
        # Reorganizar colunas
        colunas_finais = [
            'ano', 'uf', 'estado_padrao', 'regiao_padrao', 
            'idh', 'idh_educacao', 'idh_longevidade', 'idh_renda',
            'idh_categoria', 'populacao', 'fonte', 'data_coleta'
        ]
        
        df_limpo = df[colunas_finais].copy()
        df_limpo.columns = [
            'ano', 'uf', 'estado', 'regiao',
            'idh', 'idh_educacao', 'idh_longevidade', 'idh_renda',
            'idh_categoria', 'populacao', 'fonte', 'data_coleta'
        ]
        
        # Salvar dados limpos
        output_file = self.processed_dir / "idh_limpo.csv"
        df_limpo.to_csv(output_file, index=False, encoding='utf-8')
        
        missing_after = df_limpo.isnull().sum().sum()
        
        logger.info(f"✅ Dados de IDH limpos salvos: {output_file}")
        logger.info(f"📊 Registros finais: {len(df_limpo)}")
        logger.info(f"🧹 Dados ausentes: {missing_before} → {missing_after}")
        
        return df_limpo
    
    def limpar_dados_despesas(self):
        """Limpa e padroniza os dados de despesas públicas"""
        logger.info("🧹 Limpando dados de despesas públicas...")
        
        # Carregar dados
        df = pd.read_csv(self.raw_dir / "despesas_publicas_federais_real.csv")
        
        # Verificar estrutura inicial
        logger.info(f"📊 Dados originais: {len(df):,} registros")
        
        # Limpar encoding de caracteres especiais
        colunas_texto = ['estado', 'categoria', 'subcategoria', 'orgao', 'modalidade', 'fonte_recurso', 'fonte']
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].apply(self.limpar_texto)
        
        # Padronizar nomes de estados
        df['estado_padrao'] = df['uf'].map(self.estados_padrao)
        df['regiao_padrao'] = df['uf'].map(self.regioes)
        
        # Verificar dados ausentes
        missing_before = df.isnull().sum().sum()
        
        # Tratar valores ausentes
        if df.isnull().any().any():
            logger.warning("⚠️ Dados ausentes encontrados, aplicando tratamento...")
            # Preencher valores monetários ausentes com 0
            colunas_monetarias = ['valor_empenhado', 'valor_liquidado', 'valor_pago']
            for col in colunas_monetarias:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
            
            # Preencher campos de texto com 'Não Informado'
            for col in colunas_texto:
                if col in df.columns:
                    df[col] = df[col].fillna('Não Informado')
        
        # Validar valores monetários (não podem ser negativos)
        colunas_monetarias = ['valor_empenhado', 'valor_liquidado', 'valor_pago']
        for col in colunas_monetarias:
            if col in df.columns:
                df[col] = df[col].clip(lower=0)
        
        # Adicionar colunas derivadas
        df['valor_empenhado_milhoes'] = df['valor_empenhado'] / 1_000_000
        df['eficiencia_execucao'] = np.where(df['valor_empenhado'] > 0, 
                                           df['valor_pago'] / df['valor_empenhado'], 0)
        df['eficiencia_execucao'] = df['eficiencia_execucao'].clip(0, 1)
        
        # Categorizar valores
        df['faixa_valor'] = pd.cut(df['valor_empenhado_milhoes'],
                                 bins=[0, 1, 10, 50, 100, float('inf')],
                                 labels=['Até 1M', '1-10M', '10-50M', '50-100M', 'Acima 100M'])
        
        # Reorganizar colunas
        colunas_finais = [
            'ano', 'mes', 'uf', 'estado_padrao', 'regiao_padrao',
            'categoria', 'subcategoria', 'orgao',
            'valor_empenhado', 'valor_liquidado', 'valor_pago',
            'valor_empenhado_milhoes', 'eficiencia_execucao', 'faixa_valor',
            'modalidade', 'fonte_recurso', 'fonte', 'data_coleta'
        ]
        
        df_limpo = df[colunas_finais].copy()
        df_limpo.columns = [
            'ano', 'mes', 'uf', 'estado', 'regiao',
            'categoria', 'subcategoria', 'orgao',
            'valor_empenhado', 'valor_liquidado', 'valor_pago',
            'valor_empenhado_milhoes', 'eficiencia_execucao', 'faixa_valor',
            'modalidade', 'fonte_recurso', 'fonte', 'data_coleta'
        ]
        
        # Salvar dados limpos
        output_file = self.processed_dir / "despesas_publicas_limpo.csv"
        df_limpo.to_csv(output_file, index=False, encoding='utf-8')
        
        missing_after = df_limpo.isnull().sum().sum()
        
        logger.info(f"✅ Dados de despesas públicas limpos salvos: {output_file}")
        logger.info(f"📊 Registros finais: {len(df_limpo):,}")
        logger.info(f"🧹 Dados ausentes: {missing_before} → {missing_after}")
        
        return df_limpo
    
    def criar_dataset_unificado(self, df_idh, df_despesas):
        """Cria dataset unificado para análise de correlação"""
        logger.info("🔗 Criando dataset unificado...")
        
        # Agregar despesas por ano, estado e categoria
        despesas_agregadas = df_despesas.groupby(['ano', 'uf', 'estado', 'regiao', 'categoria']).agg({
            'valor_empenhado': 'sum',
            'valor_liquidado': 'sum',
            'valor_pago': 'sum',
            'valor_empenhado_milhoes': 'sum',
            'eficiencia_execucao': 'mean'
        }).reset_index()
        
        # Pivot para ter categorias como colunas
        despesas_pivot = despesas_agregadas.pivot_table(
            index=['ano', 'uf', 'estado', 'regiao'],
            columns='categoria',
            values='valor_empenhado_milhoes',
            fill_value=0
        ).reset_index()
        
        # Renomear colunas de categorias
        categoria_cols = {}
        for col in despesas_pivot.columns:
            if col not in ['ano', 'uf', 'estado', 'regiao']:
                categoria_cols[col] = f"despesa_{col.lower().replace(' ', '_').replace('ê', 'e').replace('ç', 'c')}"
        
        despesas_pivot = despesas_pivot.rename(columns=categoria_cols)
        
        # Merge com dados de IDH
        dataset_unificado = pd.merge(
            df_idh[['ano', 'uf', 'estado', 'regiao', 'idh', 'idh_educacao', 'idh_longevidade', 'idh_renda', 'populacao']],
            despesas_pivot,
            on=['ano', 'uf', 'estado', 'regiao'],
            how='inner'
        )
        
        # Calcular despesa per capita
        for col in dataset_unificado.columns:
            if col.startswith('despesa_'):
                dataset_unificado[f"{col}_per_capita"] = (
                    dataset_unificado[col] * 1_000_000 / dataset_unificado['populacao']
                )
        
        # Calcular despesa total
        despesa_cols = [col for col in dataset_unificado.columns if col.startswith('despesa_') and not col.endswith('_per_capita')]
        dataset_unificado['despesa_total'] = dataset_unificado[despesa_cols].sum(axis=1)
        dataset_unificado['despesa_total_per_capita'] = (
            dataset_unificado['despesa_total'] * 1_000_000 / dataset_unificado['populacao']
        )
        
        # Salvar dataset unificado
        output_file = self.processed_dir / "dataset_unificado.csv"
        dataset_unificado.to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"✅ Dataset unificado criado: {output_file}")
        logger.info(f"📊 Registros: {len(dataset_unificado)}")
        logger.info(f"📋 Colunas: {len(dataset_unificado.columns)}")
        
        return dataset_unificado
    
    def gerar_relatorio_limpeza(self, df_idh, df_despesas, df_unificado):
        """Gera relatório da limpeza de dados"""
        logger.info("📋 Gerando relatório de limpeza...")
        
        relatorio = {
            'data_processamento': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'datasets_processados': 3,
            'idh': {
                'registros': len(df_idh),
                'periodo': f"{df_idh['ano'].min()}-{df_idh['ano'].max()}",
                'estados': df_idh['uf'].nunique(),
                'dados_ausentes': df_idh.isnull().sum().sum()
            },
            'despesas': {
                'registros': len(df_despesas),
                'periodo': f"{df_despesas['ano'].min()}-{df_despesas['ano'].max()}",
                'estados': df_despesas['uf'].nunique(),
                'categorias': df_despesas['categoria'].nunique(),
                'valor_total_milhoes': df_despesas['valor_empenhado_milhoes'].sum(),
                'dados_ausentes': df_despesas.isnull().sum().sum()
            },
            'unificado': {
                'registros': len(df_unificado),
                'periodo': f"{df_unificado['ano'].min()}-{df_unificado['ano'].max()}",
                'estados': df_unificado['uf'].nunique(),
                'colunas': len(df_unificado.columns)
            }
        }
        
        # Salvar relatório
        relatorio_df = pd.DataFrame([relatorio])
        output_file = self.processed_dir / "relatorio_limpeza.json"
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Relatório salvo: {output_file}")
        
        return relatorio

def main():
    """Função principal para limpeza dos dados"""
    
    print("🧹 LIMPEZA E ESTRUTURAÇÃO DOS DADOS")
    print("=" * 40)
    
    cleaner = DataCleaner()
    
    try:
        # 1. Limpar dados de IDH
        print("🔄 1/4 - Limpando dados de IDH...")
        df_idh_limpo = cleaner.limpar_dados_idh()
        
        # 2. Limpar dados de despesas
        print("🔄 2/4 - Limpando dados de despesas públicas...")
        df_despesas_limpo = cleaner.limpar_dados_despesas()
        
        # 3. Criar dataset unificado
        print("🔄 3/4 - Criando dataset unificado...")
        df_unificado = cleaner.criar_dataset_unificado(df_idh_limpo, df_despesas_limpo)
        
        # 4. Gerar relatório
        print("🔄 4/4 - Gerando relatório de limpeza...")
        relatorio = cleaner.gerar_relatorio_limpeza(df_idh_limpo, df_despesas_limpo, df_unificado)
        
        print("\n✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("=" * 40)
        print(f"📊 IDH: {relatorio['idh']['registros']} registros")
        print(f"📊 Despesas: {relatorio['despesas']['registros']:,} registros")
        print(f"📊 Unificado: {relatorio['unificado']['registros']} registros")
        print(f"💰 Valor total: R$ {relatorio['despesas']['valor_total_milhoes']:,.1f} milhões")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante a limpeza: {str(e)}")
        print(f"❌ ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1) 