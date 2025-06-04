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
import json # Adicionado para o relatório

# Definição de caminhos relativos à raiz do projeto
SCRIPT_DIR = Path(__file__).resolve().parent # src/pipeline
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """Classe para limpeza e estruturação dos dados"""
    
    def __init__(self, project_root_path: Path):
        self.project_root = project_root_path
        self.raw_dir = self.project_root / "data" / "raw"
        self.processed_dir = self.project_root / "data" / "processed"
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
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Maranhão', 'PB': 'Nordeste', 
            'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'ES': 'Sudeste', 'MG': 'Minas Gerais', 'RJ': 'Rio de Janeiro', 'SP': 'São Paulo',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
    
    def _convert_to_native_python_types(self, data):
        if isinstance(data, dict):
            return {key: self._convert_to_native_python_types(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_native_python_types(element) for element in data]
        elif isinstance(data, (np.int_, np.intc, np.intp, np.int8,
                               np.int16, np.int32, np.int64, np.uint8,
                               np.uint16, np.uint32, np.uint64)):
            return int(data)
        elif isinstance(data, (np.float64, np.float16, np.float32)):
            return float(data)
        elif isinstance(data, (np.ndarray,)): # Se for um array numpy, converte para lista
            return data.tolist()
        elif isinstance(data, pd.Timestamp): # Se for Timestamp do pandas
            return data.isoformat()
        return data

    def limpar_texto(self, texto):
        """Remove acentos e caracteres especiais de texto"""
        if pd.isna(texto):
            return texto
        
        texto_normalizado = unicodedata.normalize('NFD', str(texto))
        texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        return texto_sem_acentos
    
    def limpar_dados_idh(self):
        """Limpa e padroniza os dados de IDH"""
        logger.info("🧹 Limpando dados de IDH...")
        input_file_idh = self.raw_dir / "idh_oficial_real.csv"
        if not input_file_idh.exists():
            logger.error(f"Arquivo de IDH não encontrado: {input_file_idh}")
            return None
        df = pd.read_csv(input_file_idh)
        logger.info(f"📊 Dados originais IDH: {len(df)} registros")

        df['estado_padrao'] = df['uf'].map(self.estados_padrao)
        df['regiao_padrao'] = df['uf'].map(self.regioes)
        
        missing_before = df.isnull().sum().sum()
        if df.isnull().any().any():
            logger.warning("⚠️ Dados ausentes encontrados no IDH, aplicando interpolação...")
            for uf_val in df['uf'].unique():
                mask = df['uf'] == uf_val
                cols_idh = ['idh', 'idh_educacao', 'idh_longevidade', 'idh_renda']
                for col_idh in cols_idh:
                    if col_idh in df.columns:
                         df.loc[mask, col_idh] = df.loc[mask, col_idh].interpolate(method='linear')
        
        for col_idh_clip in ['idh', 'idh_educacao', 'idh_longevidade', 'idh_renda']:
            if col_idh_clip in df.columns:
                df[col_idh_clip] = df[col_idh_clip].clip(0, 1)
        
        if 'idh' in df.columns:
            df['idh_categoria'] = pd.cut(df['idh'], 
                                    bins=[0, 0.550, 0.700, 0.800, 1.0],
                                    labels=['Baixo', 'Médio', 'Alto', 'Muito Alto'])
        else:
            df['idh_categoria'] = 'Indefinido'
        
        colunas_finais_idh = [
            'ano', 'uf', 'estado_padrao', 'regiao_padrao', 
            'idh', 'idh_educacao', 'idh_longevidade', 'idh_renda',
            'idh_categoria', 'populacao', 'fonte', 'data_coleta'
        ]
        # Garantir que apenas colunas existentes sejam selecionadas
        colunas_existentes_idh = [col for col in colunas_finais_idh if col in df.columns]
        df_limpo = df[colunas_existentes_idh].copy()

        # Renomear colunas
        rename_map_idh = {
            'estado_padrao': 'estado',
            'regiao_padrao': 'regiao'
        }
        df_limpo.rename(columns=rename_map_idh, inplace=True)
        
        output_file_idh_limpo = self.processed_dir / "idh_limpo.csv"
        df_limpo.to_csv(output_file_idh_limpo, index=False, encoding='utf-8')
        missing_after = df_limpo.isnull().sum().sum()
        logger.info(f"✅ Dados de IDH limpos salvos: {output_file_idh_limpo.relative_to(self.project_root)}")
        logger.info(f"📊 Registros finais IDH: {len(df_limpo)}")
        logger.info(f"🧹 Dados ausentes IDH: {missing_before} → {missing_after}")
        return df_limpo
    
    def limpar_dados_despesas(self):
        """Limpa e padroniza os dados de despesas públicas"""
        logger.info("🧹 Limpando dados de despesas públicas...")
        input_file_despesas = self.raw_dir / "despesas_publicas_oficiais_real.csv"
        if not input_file_despesas.exists():
            logger.error(f"Arquivo de despesas não encontrado: {input_file_despesas}")
            return None
        df = pd.read_csv(input_file_despesas)
        logger.info(f"📊 Dados originais despesas: {len(df):,} registros")

        colunas_texto_desp = ['estado', 'categoria', 'subcategoria', 'orgao', 'modalidade', 'fonte_recurso', 'fonte']
        for col_txt in colunas_texto_desp:
            if col_txt in df.columns:
                df[col_txt] = df[col_txt].apply(self.limpar_texto)
        
        df['estado_padrao'] = df['uf'].map(self.estados_padrao)
        df['regiao_padrao'] = df['uf'].map(self.regioes)
        
        missing_before = df.isnull().sum().sum()
        if df.isnull().any().any():
            logger.warning("⚠️ Dados ausentes encontrados nas despesas, aplicando tratamento...")
            colunas_monetarias = ['valor_empenhado', 'valor_liquidado', 'valor_pago']
            for col_mon in colunas_monetarias:
                if col_mon in df.columns:
                    df[col_mon] = df[col_mon].fillna(0)
            for col_txt_fill in colunas_texto_desp:
                if col_txt_fill in df.columns:
                    df[col_txt_fill] = df[col_txt_fill].fillna('Não Informado')
        
        colunas_monetarias_clip = ['valor_empenhado', 'valor_liquidado', 'valor_pago']
        for col_mon_clip in colunas_monetarias_clip:
            if col_mon_clip in df.columns:
                 df[col_mon_clip] = df[col_mon_clip].clip(lower=0)
        
        if 'valor_empenhado' in df.columns:
            df['valor_empenhado_milhoes'] = df['valor_empenhado'] / 1_000_000
            if 'valor_pago' in df.columns:
                df['eficiencia_execucao'] = np.where(df['valor_empenhado'] > 0, 
                                                df['valor_pago'] / df['valor_empenhado'], 0)
                df['eficiencia_execucao'] = df['eficiencia_execucao'].clip(0, 1)
            else:
                df['eficiencia_execucao'] = 0
            df['faixa_valor'] = pd.cut(df['valor_empenhado_milhoes'],
                                     bins=[0, 1, 10, 50, 100, float('inf')],
                                     labels=['Até 1M', '1-10M', '10-50M', '50-100M', 'Acima 100M'])
        else:
            df['valor_empenhado_milhoes'] = 0
            df['eficiencia_execucao'] = 0
            df['faixa_valor'] = 'N/A'

        colunas_finais_desp = [
            'ano', 'mes', 'uf', 'estado_padrao', 'regiao_padrao',
            'categoria', 'subcategoria', 'orgao',
            'valor_empenhado', 'valor_liquidado', 'valor_pago',
            'valor_empenhado_milhoes', 'eficiencia_execucao', 'faixa_valor',
            'modalidade', 'fonte_recurso', 'fonte', 'data_coleta'
        ]
        colunas_existentes_desp = [col for col in colunas_finais_desp if col in df.columns]
        df_limpo = df[colunas_existentes_desp].copy()
        rename_map_desp = {
            'estado_padrao': 'estado',
            'regiao_padrao': 'regiao'
        }
        df_limpo.rename(columns=rename_map_desp, inplace=True)
        
        output_file_desp_limpo = self.processed_dir / "despesas_publicas_limpo.csv"
        df_limpo.to_csv(output_file_desp_limpo, index=False, encoding='utf-8')
        missing_after = df_limpo.isnull().sum().sum()
        logger.info(f"✅ Dados de despesas públicas limpos salvos: {output_file_desp_limpo.relative_to(self.project_root)}")
        logger.info(f"📊 Registros finais despesas: {len(df_limpo):,}")
        logger.info(f"🧹 Dados ausentes despesas: {missing_before} → {missing_after}")
        return df_limpo
    
    def criar_dataset_unificado(self, df_idh, df_despesas):
        """Cria dataset unificado para análise de correlação"""
        if df_idh is None or df_despesas is None:
            logger.error("Datasets de IDH ou Despesas não foram carregados/limpos corretamente. Abortando unificação.")
            return None
        logger.info("🔗 Criando dataset unificado...")
        
        # Assegurar que as colunas para groupby e pivot existem
        group_cols = ['ano', 'uf', 'estado', 'regiao', 'categoria']
        if not all(col in df_despesas.columns for col in group_cols):
            logger.error(f"Colunas necessárias para agregação de despesas ({group_cols}) não encontradas. Abortando.")
            return None
        if 'valor_empenhado_milhoes' not in df_despesas.columns:
            logger.error("Coluna 'valor_empenhado_milhoes' não encontrada para pivot. Abortando.")
            return None

        despesas_agregadas = df_despesas.groupby(group_cols, as_index=False).agg({
            'valor_empenhado': 'sum',
            'valor_liquidado': 'sum',
            'valor_pago': 'sum',
            'valor_empenhado_milhoes': 'sum',
            'eficiencia_execucao': 'mean'
        })
        
        pivot_index = ['ano', 'uf', 'estado', 'regiao']
        if not all(col in despesas_agregadas.columns for col in pivot_index):
            logger.error(f"Colunas de índice para pivot ({pivot_index}) não encontradas. Abortando.")
            return None

        despesas_pivot = despesas_agregadas.pivot_table(
            index=pivot_index,
            columns='categoria',
            values='valor_empenhado_milhoes',
            fill_value=0
        ).reset_index()
        
        # Renomear colunas de categorias pivotadas para evitar conflitos e padronizar
        # Ex: Saúde -> despesa_saude
        categoria_rename_map = {}
        for col in despesas_pivot.columns:
            if col not in pivot_index:
                clean_col_name = str(col).lower().replace(' ', '_').replace('ê', 'e').replace('ç', 'c')
                clean_col_name = re.sub(r'[^a-zA-Z0-9_]', '', clean_col_name) # Remover outros caracteres especiais
                categoria_rename_map[col] = f"despesa_{clean_col_name}"
        despesas_pivot.rename(columns=categoria_rename_map, inplace=True)
        
        # Colunas para merge do IDH
        cols_idh_merge = ['ano', 'uf', 'estado', 'regiao', 'idh', 'idh_educacao', 'idh_longevidade', 'idh_renda', 'populacao']
        cols_idh_existentes = [col for col in cols_idh_merge if col in df_idh.columns]
        if not all(col in df_idh.columns for col in pivot_index):
             logger.error(f"Colunas de merge ({pivot_index}) não encontradas em df_idh. Abortando.")
             return None

        dataset_unificado = pd.merge(
            df_idh[cols_idh_existentes],
            despesas_pivot,
            on=pivot_index, # Usar as mesmas colunas de índice para o merge
            how='inner'
        )
        
        if 'populacao' in dataset_unificado.columns and dataset_unificado['populacao'].notna().all() and (dataset_unificado['populacao'] > 0).all():
            for col in dataset_unificado.columns:
                if col.startswith('despesa_') and not col.endswith('_per_capita'): # Evitar recalcular se já existir
                    dataset_unificado[f"{col}_per_capita"] = (
                        (dataset_unificado[col] * 1_000_000) / dataset_unificado['populacao']
                    ).fillna(0) # Tratar divisão por zero ou NaN na população
        else:
            logger.warning("Coluna 'populacao' ausente, com NaNs ou zeros. Despesas per capita não serão calculadas ou podem ser imprecisas.")

        despesa_cols_sum = [col for col in dataset_unificado.columns if col.startswith('despesa_') and not col.endswith('_per_capita')]
        if despesa_cols_sum:
            dataset_unificado['despesa_total_milhoes'] = dataset_unificado[despesa_cols_sum].sum(axis=1)
            if 'populacao' in dataset_unificado.columns and dataset_unificado['populacao'].notna().all() and (dataset_unificado['populacao'] > 0).all():
                dataset_unificado['despesa_total_per_capita'] = (
                    (dataset_unificado['despesa_total_milhoes'] * 1_000_000) / dataset_unificado['populacao']
                ).fillna(0)
            else:
                dataset_unificado['despesa_total_per_capita'] = 0
                logger.warning("Coluna 'populacao' ausente ou inválida. 'despesa_total_per_capita' calculada como 0.")
        else:
             dataset_unificado['despesa_total_milhoes'] = 0
             dataset_unificado['despesa_total_per_capita'] = 0
             logger.warning("Nenhuma coluna de despesa encontrada para calcular totais.")

        output_file_unificado = self.processed_dir / "dataset_unificado.csv"
        dataset_unificado.to_csv(output_file_unificado, index=False, encoding='utf-8')
        logger.info(f"✅ Dataset unificado criado: {output_file_unificado.relative_to(self.project_root)}")
        logger.info(f"📊 Registros unificados: {len(dataset_unificado)}")
        logger.info(f"📋 Colunas unificadas: {len(dataset_unificado.columns)}")
        return dataset_unificado
    
    def gerar_relatorio_limpeza(self, df_idh, df_despesas, df_unificado):
        """Gera um relatório JSON sobre o processo de limpeza."""
        logger.info("📋 Gerando relatório de limpeza...")
        relatorio = {
            "sumario": {
                "datasets_processados": 0,
                "idh": {"registros": 0, "periodo": "N/A", "estados": 0, "dados_ausentes": 0},
                "despesas": {"registros": 0, "periodo": "N/A", "estados": 0, "categorias": 0, "valor_total_milhoes": 0, "dados_ausentes": 0},
                "unificado": {"registros": 0, "periodo": "N/A", "estados": 0, "colunas": 0}
            },
            "idh": {},
            "despesas": {},
            "unificado": {}
        }

        if df_idh is not None and not df_idh.empty:
            relatorio["sumario"]["datasets_processados"] += 1
            relatorio["idh"] = {
                "registros": len(df_idh),
                "periodo": f"{df_idh['ano'].min()}-{df_idh['ano'].max()}" if 'ano' in df_idh else 'N/A',
                "estados": df_idh['uf'].nunique() if 'uf' in df_idh else 0,
                "dados_ausentes": df_idh.isnull().sum().sum()
            }
        if df_despesas is not None and not df_despesas.empty:
            relatorio["sumario"]["datasets_processados"] += 1
            relatorio["despesas"] = {
                "registros": len(df_despesas),
                "periodo": f"{df_despesas['ano'].min()}-{df_despesas['ano'].max()}" if 'ano' in df_despesas else 'N/A',
                "estados": df_despesas['uf'].nunique() if 'uf' in df_despesas else 0,
                "categorias": df_despesas['categoria'].nunique() if 'categoria' in df_despesas else 0,
                "valor_total_milhoes": df_despesas['valor_empenhado_milhoes'].sum() if 'valor_empenhado_milhoes' in df_despesas else 0,
                "dados_ausentes": df_despesas.isnull().sum().sum()
            }
        if df_unificado is not None and not df_unificado.empty:
            relatorio["sumario"]["datasets_processados"] += 1 # Se unificado foi criado, conta como 1 dataset final
            relatorio["unificado"] = {
                "registros": len(df_unificado),
                "periodo": f"{df_unificado['ano'].min()}-{df_unificado['ano'].max()}" if 'ano' in df_unificado else 'N/A',
                "estados": df_unificado['uf'].nunique() if 'uf' in df_unificado else 0,
                "colunas": len(df_unificado.columns)
            }
        
        # Converter todo o relatório para tipos nativos Python ANTES de json.dump
        relatorio_convertido = self._convert_to_native_python_types(relatorio)

        output_file_relatorio = self.processed_dir / "relatorio_limpeza.json"
        try:
            with open(output_file_relatorio, 'w', encoding='utf-8') as f:
                json.dump(relatorio_convertido, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Relatório de limpeza salvo em: {output_file_relatorio.relative_to(self.project_root)}")
        except TypeError as e:
            logger.error(f"❌ Erro ao serializar relatório para JSON: {e}")
            logger.error("Isso pode acontecer se ainda houver tipos de dados não suportados pelo JSON (ex: complexos, datas não serializadas).")
            logger.error(f"Conteúdo problemático (primeiros níveis): { {k: type(v) for k,v in relatorio_convertido.items()} }") # type: ignore
            # Para depuração mais profunda, você pode querer imprimir partes específicas do relatorio_convertido
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório de limpeza: {e}")
        
        return relatorio # Retorna o dicionário original, não o convertido, caso seja usado em memória

def main():
    """Função principal para executar o pipeline de limpeza"""
    logger.info("🧹 INICIANDO PIPELINE DE LIMPEZA E ESTRUTURAÇÃO DOS DADOS (Fase 1b)")
    logger.info("============================================================")
    
    cleaner = DataCleaner(PROJECT_ROOT)
    
    try:
        # 1. Limpar dados de IDH
        logger.info("🔄 1/4 - Limpando dados de IDH...")
        df_idh_limpo = cleaner.limpar_dados_idh()
        if df_idh_limpo is None:
            raise ValueError("Falha ao limpar dados de IDH.")

        # 2. Limpar dados de Despesas
        logger.info("🔄 2/4 - Limpando dados de despesas públicas...")
        df_despesas_limpo = cleaner.limpar_dados_despesas()
        if df_despesas_limpo is None:
            raise ValueError("Falha ao limpar dados de despesas públicas.")

        # 3. Criar dataset unificado
        logger.info("🔄 3/4 - Criando dataset unificado...")
        df_unificado = cleaner.criar_dataset_unificado(df_idh_limpo, df_despesas_limpo)
        if df_unificado is None:
            raise ValueError("Falha ao criar dataset unificado.")

        # 4. Gerar relatório de limpeza
        logger.info("🔄 4/4 - Gerando relatório de limpeza...")
        # O relatório agora é salvo dentro de gerar_relatorio_limpeza
        # Não precisamos mais de json.dump aqui fora.
        relatorio_final = cleaner.gerar_relatorio_limpeza(df_idh_limpo, df_despesas_limpo, df_unificado)
        if not relatorio_final: # Checa se o relatório foi gerado (poderia ser None em caso de falha interna)
             logger.warning("⚠️ Relatório de limpeza não foi gerado ou está vazio.")
        
        logger.info("============================================================")
        logger.info("🎉 LIMPEZA E ESTRUTURAÇÃO CONCLUÍDAS COM SUCESSO!")
        logger.info(f"📁 Arquivos processados salvos em: {cleaner.processed_dir.relative_to(PROJECT_ROOT)}")
        logger.info("============================================================")
        return True # Adicionado retorno de sucesso

    except ValueError as ve:
        logger.error(f"❌ Erro na Fase 1b: {ve}")
        logger.error("Pipeline de limpeza abortado.")
        return False # Adicionado retorno de falha
    except Exception as e:
        logger.error(f"❌ Erro fatal durante a limpeza e estruturação: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ ERRO FATAL: {e}")
        print(f"Traceback (most recent call last):\n{traceback.format_exc()}")
        logger.error("Pipeline de limpeza abortado devido a erro inesperado.")
        return False # Adicionado retorno de falha

if __name__ == '__main__':
    main() 