#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para coletar dados de despesas públicas federais por estado.
Fonte: Portal da Transparência (ou similar).
"""

import pandas as pd
import requests
import logging
import unicodedata
from io import StringIO

logger = logging.getLogger(__name__)

class DespesasOficiaisCollector:
    """
    Coleta e processa dados de despesas públicas federais por estado.
    """
    def __init__(self, anos_referencia=None):
        if anos_referencia is None:
            self.anos_referencia = [2019, 2020, 2021, 2022, 2023]
        else:
            self.anos_referencia = anos_referencia

        # A URL base para a API do Portal da Transparência ou link para download direto
        # Exemplo: "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao"
        self.base_url_portal = "https://portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao" # Placeholder para API
        # A coleta real pode envolver múltiplas chamadas de API ou download e processamento de CSVs/ZIPs grandes.

        self.uf_map = {
            'RO': 'Rondônia', 'AC': 'Acre', 'AM': 'Amazonas', 'RR': 'Roraima', 'PA': 'Pará',
            'AP': 'Amapá', 'TO': 'Tocantins', 'MA': 'Maranhão', 'PI': 'Piauí',
            'CE': 'Ceará', 'RN': 'Rio Grande do Norte', 'PB': 'Paraíba', 'PE': 'Pernambuco',
            'AL': 'Alagoas', 'SE': 'Sergipe', 'BA': 'Bahia', 'MG': 'Minas Gerais',
            'ES': 'Espírito Santo', 'RJ': 'Rio de Janeiro', 'SP': 'São Paulo',
            'PR': 'Paraná', 'SC': 'Santa Catarina', 'RS': 'Rio Grande do Sul',
            'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso', 'GO': 'Goiás', 'DF': 'Distrito Federal'
        }
        self.categorias_interesse = [
            'Educação', 'Saúde', 'Assistência Social', 'Infraestrutura', 'Segurança Pública', 'Outras'
        ]

    def _normalizar_texto(self, texto):
        if texto is None:
            return None
        nfkd_form = unicodedata.normalize('NFKD', str(texto).lower())
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def _get_despesas_data_simulado(self):
        """
        Simula a obtenção de dados de despesas.
        A implementação real buscaria do Portal da Transparência via API ou download de arquivos.
        """
        logger.warning("Usando dados de DESPESAS SIMULADOS. Substitua pela lógica de coleta real.")
        data = []
        
        for ano in self.anos_referencia:
            for uf_sigla, estado_nome in self.uf_map.items():
                for categoria in self.categorias_interesse:
                    # Simular valores de despesas
                    base_valor = (hash(uf_sigla + categoria) % 1000000) * (1 + (len(self.uf_map) - list(self.uf_map.keys()).index(uf_sigla)) * 0.1)
                    valor_pago_simulado = round(base_valor * (1 + (ano - 2019) * 0.02 + (hash(str(ano)+categoria) % 100 / 1000)), 2)
                    data.append({
                        'ano': ano,
                        'uf': uf_sigla,
                        'estado': estado_nome,
                        'categoria': categoria,
                        'valor_pago': valor_pago_simulado,
                        'fonte_despesa': 'Portal da Transparência - Dados Simulados para Exemplo'
                    })
        
        df_despesas = pd.DataFrame(data)
        df_despesas['ano'] = df_despesas['ano'].astype(int)
        df_despesas['valor_pago'] = df_despesas['valor_pago'].astype(float)
        return df_despesas[['ano', 'uf', 'estado', 'categoria', 'valor_pago', 'fonte_despesa']]

    def coletar_dados(self):
        """
        Orquestra a coleta e processamento de dados de despesas.
        Retorna um DataFrame.
        """
        logger.info("Iniciando coleta de dados de Despesas Públicas...")

        # --- Coleta de Despesas ---
        # Na implementação original, aqui ocorreria a chamada à API do Portal da Transparência
        # ou o download/processamento de arquivos CSV/ZIP.
        # A COLETA OFICIAL REAL deveria substituir _get_despesas_data_simulado()
        try:
            df_despesas = self._get_despesas_data_simulado()
            logger.info(f"Dados de Despesas (simulados) processados: {len(df_despesas)} registros.")
            
            if df_despesas.empty:
                logger.warning("Nenhum dado de despesa foi coletado (simulação retornou vazio).")
                # Retornar colunas esperadas para consistência
                return pd.DataFrame(columns=['ano', 'uf', 'estado', 'categoria', 'valor_pago', 'fonte_despesa'])

            # Garantir que todas as colunas necessárias existem
            colunas_esperadas = ['ano', 'uf', 'estado', 'categoria', 'valor_pago', 'fonte_despesa']
            for col in colunas_esperadas:
                if col not in df_despesas.columns:
                    df_despesas[col] = None # Ou valor padrão apropriado
            df_despesas = df_despesas[colunas_esperadas]

            logger.info(f"Coleta de Despesas Públicas concluída. Total de {len(df_despesas)} registros.")
            return df_despesas

        except Exception as e:
            logger.error(f"Erro ao coletar/processar dados de Despesas: {e}")
            return pd.DataFrame(columns=['ano', 'uf', 'estado', 'categoria', 'valor_pago', 'fonte_despesa'])


if __name__ == '__main__':
    # Teste rápido do coletor
    logging.basicConfig(level=logging.INFO)
    coletor_despesas = DespesasOficiaisCollector(anos_referencia=[2020, 2021])
    df_resultado_despesas = coletor_despesas.coletar_dados()

    if not df_resultado_despesas.empty:
        print("\n--- AMOSTRA DOS DADOS COLETADOS (Despesas Oficiais Collector) ---")
        print(df_resultado_despesas.head())
        print(f"\nTotal de registros: {len(df_resultado_despesas)}")
        print(f"Colunas: {df_resultado_despesas.columns.tolist()}")
        print(f"Anos: {sorted(df_resultado_despesas['ano'].unique())}")
        print(f"UFs: {df_resultado_despesas['uf'].nunique()}")
        print(f"Categorias: {df_resultado_despesas['categoria'].nunique()}")
    else:
        print("\n❌ Falha ao coletar dados de Despesas.") 