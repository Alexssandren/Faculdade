#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para coletar dados de IDH (Índice de Desenvolvimento Humano)
e população para os estados do Brasil.
Fontes: Atlas Brasil (PNUD / IPEA / FJP) e IBGE.
"""

import pandas as pd
import requests
import io
import logging
import unicodedata

logger = logging.getLogger(__name__)

class IDHOficialCollector:
    """
    Coleta e processa dados de IDH e população dos estados brasileiros.
    """
    def __init__(self, anos_referencia=None):
        if anos_referencia is None:
            self.anos_referencia = [2019, 2020, 2021, 2022, 2023] # Ajustar conforme disponibilidade
        else:
            self.anos_referencia = anos_referencia

        # URLs (estas podem precisar de atualização ou podem ser genéricas para consulta)
        # Para IDH, o Atlas Brasil geralmente fornece dados decenais (2000, 2010).
        # Para dados anuais, precisamos de uma fonte alternativa ou uma abordagem diferente.
        # A coleta original pode ter usado dados de 2010 e replicado/ajustado, ou encontrado uma fonte anual.
        # Vamos assumir por agora que a fonte principal é o último censo (2010 para IDHM completo)
        # e que a "coleta oficial real" pode ter encontrado dados mais recentes ou projeções.
        # Esta é uma simplificação e pode precisar ser ajustada para refletir a coleta REAL que foi feita.

        # Exemplo de URL de dados de IDHM (geralmente por consulta ou download direto de arquivo)
        # A URL específica usada anteriormente para o IDH por estado e ano seria ideal.
        # Se não tivermos, usaremos um placeholder ou uma lógica para buscar.
        self.url_idh_atlas = "http://www.atlasbrasil.org.br/acervo/biblioteca" # Placeholder - local para encontrar os arquivos
        # A coleta de dados de IDH para anos recentes como 2019-2023 em nível estadual pode ser desafiadora
        # pois o IDHM completo é calculado com base nos censos.
        # Vamos simular uma estrutura de dados que seria esperada.

        # Para população, o IBGE é a fonte.
        # Exemplo: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?=&t=downloads
        # Estas URLs mudam. É melhor ter um link direto para um CSV/XLS se possível.
        self.url_populacao_ibge_estimativas = "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/estimativa_dou_2021.xls" # Exemplo, pode estar desatualizado

        self.uf_map = {
            'RO': 'Rondônia', 'AC': 'Acre', 'AM': 'Amazonas', 'RR': 'Roraima', 'PA': 'Pará',
            'AP': 'Amapá', 'TO': 'Tocantins', 'MA': 'Maranhão', 'PI': 'Piauí',
            'CE': 'Ceará', 'RN': 'Rio Grande do Norte', 'PB': 'Paraíba', 'PE': 'Pernambuco',
            'AL': 'Alagoas', 'SE': 'Sergipe', 'BA': 'Bahia', 'MG': 'Minas Gerais',
            'ES': 'Espírito Santo', 'RJ': 'Rio de Janeiro', 'SP': 'São Paulo',
            'PR': 'Paraná', 'SC': 'Santa Catarina', 'RS': 'Rio Grande do Sul',
            'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso', 'GO': 'Goiás', 'DF': 'Distrito Federal'
        }
        self.regiao_map = {
            'RO': 'Norte', 'AC': 'Norte', 'AM': 'Norte', 'RR': 'Norte', 'PA': 'Norte', 'AP': 'Norte', 'TO': 'Norte',
            'MA': 'Nordeste', 'PI': 'Nordeste', 'CE': 'Nordeste', 'RN': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'AL': 'Nordeste', 'SE': 'Nordeste', 'BA': 'Nordeste',
            'MG': 'Sudeste', 'ES': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'SC': 'Sul', 'RS': 'Sul',
            'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'DF': 'Centro-Oeste'
        }

    def _normalizar_texto(self, texto):
        if texto is None:
            return None
        # Remove acentos e converte para minúsculas
        nfkd_form = unicodedata.normalize('NFKD', str(texto).lower())
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def _get_idh_data_simulado(self):
        """
        Simula a obtenção de dados de IDH, já que a fonte anual 2019-2023 é complexa.
        A implementação real buscaria os dados de uma API ou arquivo CSV/Excel.
        """
        logger.warning("Usando dados de IDH SIMULADOS. Substitua pela lógica de coleta real.")
        data = []
        ufs = list(self.uf_map.keys())
        base_idh = {uf: 0.700 + i*0.005 for i, uf in enumerate(ufs)} # Base IDH variando por UF

        for ano in self.anos_referencia:
            for uf_sigla, estado_nome in self.uf_map.items():
                # Simular uma pequena variação anual
                idh_simulado = round(base_idh[uf_sigla] + (ano - 2019) * 0.001 + (hash(uf_sigla) % 100 / 5000), 4)
                data.append({
                    'ano': ano,
                    'uf': uf_sigla,
                    'estado': estado_nome,
                    'idh': idh_simulado,
                    'idhm_r': idh_simulado - 0.05, # Simulação subcomponente
                    'idhm_l': idh_simulado + 0.05, # Simulação subcomponente
                    'idhm_e': idh_simulado,        # Simulação subcomponente
                    'regiao': self.regiao_map[uf_sigla],
                    'fonte_idh': 'Atlas Brasil (PNUD/IPEA/FJP) - Dados Simulados para Exemplo'
                })
        df_idh = pd.DataFrame(data)
        # Garantir os tipos corretos
        df_idh['ano'] = df_idh['ano'].astype(int)
        df_idh['idh'] = df_idh['idh'].astype(float)
        df_idh['idhm_r'] = df_idh['idhm_r'].astype(float)
        df_idh['idhm_l'] = df_idh['idhm_l'].astype(float)
        df_idh['idhm_e'] = df_idh['idhm_e'].astype(float)
        return df_idh[['ano', 'uf', 'estado', 'regiao', 'idh', 'idhm_r', 'idhm_l', 'idhm_e', 'fonte_idh']]

    def _get_populacao_data_simulado(self):
        """
        Simula a obtenção de dados de população.
        A implementação real buscaria do IBGE.
        """
        logger.warning("Usando dados de POPULAÇÃO SIMULADOS. Substitua pela lógica de coleta real.")
        data = []
        base_pop = {uf: 500000 + i*1000000 for i, uf in enumerate(self.uf_map.keys())}

        for ano in self.anos_referencia:
            for uf_sigla, estado_nome in self.uf_map.items():
                # Simular um pequeno crescimento anual
                pop_simulada = int(base_pop[uf_sigla] * (1 + (ano - 2019) * 0.005 + (hash(uf_sigla) % 100 / 10000)))
                data.append({
                    'ano': ano,
                    'uf': uf_sigla,
                    'populacao': pop_simulada
                })
        df_pop = pd.DataFrame(data)
        df_pop['ano'] = df_pop['ano'].astype(int)
        df_pop['populacao'] = df_pop['populacao'].astype(int)
        return df_pop

    def coletar_dados(self):
        """
        Orquestra a coleta e processamento de dados de IDH e população.
        Retorna um DataFrame unificado.
        """
        logger.info("Iniciando coleta de dados de IDH e População...")

        # --- Coleta de IDH ---
        # Na implementação original, aqui ocorreria o download e parsing dos dados REAIS.
        # Como o acesso a dados de IDH estaduais anuais de 2019-2023 é complexo e não foi detalhado
        # anteriormente, usaremos uma função de simulação.
        # A COLETA OFICIAL REAL deveria substituir _get_idh_data_simulado()
        try:
            df_idh = self._get_idh_data_simulado()
            logger.info(f"Dados de IDH (simulados) processados: {len(df_idh)} registros.")
        except Exception as e:
            logger.error(f"Erro ao coletar/processar dados de IDH: {e}")
            # Retornar um DataFrame vazio ou levantar a exceção, dependendo da política de erro.
            # Por enquanto, vamos simular um df vazio para não quebrar o fluxo totalmente.
            df_idh = pd.DataFrame(columns=['ano', 'uf', 'estado', 'regiao', 'idh', 'idhm_r', 'idhm_l', 'idhm_e', 'fonte_idh'])


        # --- Coleta de População ---
        # Similar ao IDH, a coleta real de população do IBGE substituiria _get_populacao_data_simulado()
        try:
            df_populacao = self._get_populacao_data_simulado()
            logger.info(f"Dados de População (simulados) processados: {len(df_populacao)} registros.")
        except Exception as e:
            logger.error(f"Erro ao coletar/processar dados de População: {e}")
            df_populacao = pd.DataFrame(columns=['ano', 'uf', 'populacao'])


        # --- Unificação ---
        if df_idh.empty or df_populacao.empty:
            logger.error("Não foi possível obter dados de IDH ou População. Retornando DataFrame vazio.")
            # Se a coleta real falhar, é importante ter uma política (ex: erro, dados parciais)
            # O código original gerava um dataset com IDH mesmo se população falhasse, e vice-versa
            # para manter a modularidade, mas para a unificação, ambos são importantes.
            # Vamos retornar um df com colunas esperadas mas vazio se um deles falhar na simulação.
            final_cols = ['ano', 'uf', 'estado', 'regiao', 'idh', 'idhm_r', 'idhm_l', 'idhm_e', 'populacao', 'fonte_idh']
            return pd.DataFrame(columns=final_cols)

        try:
            logger.info("Unificando dados de IDH e População...")
            df_final = pd.merge(df_idh, df_populacao, on=['ano', 'uf'], how='left')

            # A fonte original de IDH para os anos 2010 era o Atlas Brasil.
            # Para anos mais recentes, a fonte precisa ser confirmada.
            # A coluna 'fonte_idh' já vem do _get_idh_data_simulado.
            df_final['municipio_codigo'] = None # IDH em nível estadual não tem código de município aqui
            df_final['municipio_nome'] = None   # IDH em nível estadual

            # Selecionar e ordenar colunas finais
            colunas_finais = [
                'ano', 'uf', 'estado', 'regiao', 'idh',
                'idhm_r', 'idhm_l', 'idhm_e', # Subcomponentes do IDH
                'populacao', 'municipio_codigo', 'municipio_nome', 'fonte_idh'
            ]
            df_final = df_final[colunas_finais]

            logger.info(f"Coleta de IDH e População concluída. Total de {len(df_final)} registros unificados.")
            return df_final

        except Exception as e:
            logger.error(f"Erro ao unificar dados de IDH e População: {e}")
            final_cols = ['ano', 'uf', 'estado', 'regiao', 'idh', 'idhm_r', 'idhm_l', 'idhm_e', 'populacao', 'fonte_idh']
            return pd.DataFrame(columns=final_cols)


if __name__ == '__main__':
    # Teste rápido do coletor
    logging.basicConfig(level=logging.INFO)
    coletor_idh = IDHOficialCollector(anos_referencia=[2020, 2021])
    df_resultado_idh = coletor_idh.coletar_dados()

    if not df_resultado_idh.empty:
        print("\\n--- AMOSTRA DOS DADOS COLETADOS (IDH Oficial Collector) ---")
        print(df_resultado_idh.head())
        print(f"\\nTotal de registros: {len(df_resultado_idh)}")
        print(f"Colunas: {df_resultado_idh.columns.tolist()}")
        print(f"Anos: {sorted(df_resultado_idh['ano'].unique())}")
        print(f"UFs: {df_resultado_idh['uf'].nunique()}")
    else:
        print("\\n❌ Falha ao coletar dados de IDH.") 