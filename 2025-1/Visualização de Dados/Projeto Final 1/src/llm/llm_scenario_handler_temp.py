import pandas as pd
import re
from typing import Tuple, Dict, Optional, List

# Funções auxiliares
def _extract_year_from_query(
    query_ano_str: Optional[str], 
    prev_response_content: Optional[str] = None, 
    df: Optional[pd.DataFrame] = None, 
    uf_context: Optional[str] = None
) -> Optional[int]:
    """
    Extrai o ano de forma robusta.
    1. Do query_ano_str atual (se válido).
    2. Do prev_response_content (se aplicável e encontrável).
    3. Do ano mais recente no df para um uf_context (se fornecido).
    4. Do ano mais recente geral no df.
    """

    # 1. Tentar com query_ano_str (se fornecido e válido)
    if query_ano_str:
        try:
            year_val = int(query_ano_str) # Tenta converter para int
            if 1900 <= year_val <= 2100: # Validação básica de um ano razoável
                return year_val
        except ValueError:
            pass # Não é um inteiro, tentar outras formas

    # 2. Tentar extrair do prev_response_content usando regex
    if prev_response_content and isinstance(prev_response_content, str):
        # Regex para encontrar um ano de 4 dígitos (ex: em 2020, ano de 2019)
        # Prioriza anos próximos a palavras como "ano", "em", "de"
        year_patterns = [
            r'(?:ano de|em|no ano de|o ano é|foi em)\s*(\d{4})',
            r'\b(\d{4})\b' # Um número de 4 dígitos como fallback
        ]
        for pattern in year_patterns:
            match = re.search(pattern, prev_response_content, re.IGNORECASE)
            if match:
                try:
                    year_val = int(match.group(1))
                    if 1900 <= year_val <= 2100:
                        return year_val
                except ValueError:
                    continue # Encontrou algo mas não é um ano válido
    
    # 3. Se df e uf_context são fornecidos, buscar o ano mais recente para essa UF
    if df is not None and not df.empty and 'ano' in df.columns and uf_context and 'uf' in df.columns:
        uf_data = df[df['uf'].str.upper() == uf_context.upper()]
        if not uf_data.empty and pd.notna(uf_data['ano'].max()):
            try:
                latest_year_uf = int(uf_data['ano'].max())
                return latest_year_uf
            except ValueError:
                pass

    # 4. Se df é fornecido (sem uf_context específico ou se o passo 3 falhou), buscar o ano mais recente geral
    if df is not None and not df.empty and 'ano' in df.columns:
        if pd.notna(df['ano'].max()):
            try:
                latest_year_general = int(df['ano'].max())
                return latest_year_general
            except ValueError:
                pass 

    return None

def _extract_uf_from_query(
    query_uf_str: Optional[str], 
    prev_response_content: Optional[str] = None, 
    df: Optional[pd.DataFrame] = None, 
    uf_context: Optional[str] = None
) -> Optional[str]:
    """
    Extrai a UF de forma robusta.
    1. Do query_uf_str atual (se válida).
    2. Do prev_response_content (buscando nome completo ou sigla).
    Retorna a sigla da UF em maiúsculas ou None.
    """
    
    if df is None or df.empty:
        # Tentar apenas com query_uf_str se for uma sigla de 2 letras
        if query_uf_str and isinstance(query_uf_str, str) and len(query_uf_str) == 2 and query_uf_str.isalpha():
            return query_uf_str.upper()
        return None

    map_estado_uf = {}
    known_ufs_set = set()
    if 'estado' in df.columns and 'uf' in df.columns:
        df_estados_ufs = df[['estado', 'uf']].dropna().drop_duplicates()
        map_estado_uf = {str(row['estado']).strip().lower(): str(row['uf']).strip().upper() for _, row in df_estados_ufs.iterrows()}
        known_ufs_set = {str(uf).strip().upper() for uf in df['uf'].dropna().unique()}
    elif 'uf' in df.columns: # Caso não tenha a coluna 'estado' mas tenha 'uf'
        known_ufs_set = {str(uf).strip().upper() for uf in df['uf'].dropna().unique()}
    else:
        # Fallback para query_uf_str como acima, se df não tem as colunas necessárias
        if query_uf_str and isinstance(query_uf_str, str) and len(query_uf_str) == 2 and query_uf_str.isalpha():
            return query_uf_str.upper()
        return None

    # 1. Tentar com query_uf_str (se fornecido e válido)
    if query_uf_str and isinstance(query_uf_str, str):
        uf_upper = query_uf_str.strip().upper()
        if uf_upper in known_ufs_set:
            return uf_upper
        # Verificar se é nome completo
        if map_estado_uf and query_uf_str.strip().lower() in map_estado_uf:
            found_uf = map_estado_uf[query_uf_str.strip().lower()]
            return found_uf

    # 2. Tentar extrair do prev_response_content
    if prev_response_content and isinstance(prev_response_content, str):
        prev_response_lower = prev_response_content.lower()
        prev_response_upper = prev_response_content.upper() # Para siglas

        # Procurar por nomes completos primeiro (mais longos, mais específicos)
        if map_estado_uf:
            # Ordenar por comprimento para evitar substrings (ex: "para" em "paraná")
            sorted_estados = sorted(map_estado_uf.keys(), key=len, reverse=True)
            for nome_estado_lower in sorted_estados:
                # Usar \b para garantir que estamos pegando a palavra inteira
                if re.search(r'\b' + re.escape(nome_estado_lower) + r'\b', prev_response_lower):
                    found_uf = map_estado_uf[nome_estado_lower]
                    return found_uf
        
        # Procurar por siglas de UF (2 letras)
        if known_ufs_set:
            # Usar regex para encontrar UFs como palavras isoladas
            # Ajuste no regex para garantir que UFs como 'SP' não sejam pegas em palavras como 'disponível'
            # Isso pode ser complexo. Uma abordagem é procurar por " UF " ou no início/fim de frases.
            # Por simplicidade, vamos procurar a sigla exata com word boundaries.
            for uf_sigla in known_ufs_set:
                if re.search(r'\b' + re.escape(uf_sigla) + r'\b', prev_response_upper):
                    return uf_sigla

    return None

# --- Funções Auxiliares para Cenários de Gastos ---
def _get_relevant_expense_columns(
    data_df: pd.DataFrame,
    categoria_despesa_query: Optional[str] = None
) -> Tuple[List[str], bool, Optional[str]]:
    """
    Identifica as colunas de despesa relevantes e se é um gasto total.
    Retorna (lista_colunas_despesa, is_total_geral, nome_coluna_categoria_usada).
    """
    available_df_columns = data_df.columns.tolist()
    base_expense_cols = {
        "saude": "despesa_saude",
        "educacao": "despesa_educacao",
        "educação": "despesa_educacao", # Alias
        "infraestrutura": "despesa_infraestrutura",
        "assistencia social": "despesa_assistencia_social",
        "assistência social": "despesa_assistencia_social" # Alias
    }
    
    # Colunas de despesa individuais realmente presentes no DataFrame
    valid_individual_expense_cols_in_df = [col for col_map in base_expense_cols.values() for col in [col_map] if col in available_df_columns]
    valid_individual_expense_cols_in_df = sorted(list(set(valid_individual_expense_cols_in_df))) # Remover duplicatas e ordenar

    is_total_geral = False
    colunas_a_somar_ou_usar = []
    nome_coluna_categoria_usada: Optional[str] = None

    if categoria_despesa_query:
        categoria_lower = categoria_despesa_query.lower()
        if any(term in categoria_lower for term in ["total", "geral", "todas", "combinado"]):
            is_total_geral = True
            nome_coluna_categoria_usada = "Total"
        else:
            for key, col_name in base_expense_cols.items():
                if key in categoria_lower:
                    if col_name in available_df_columns:
                        colunas_a_somar_ou_usar = [col_name]
                        nome_coluna_categoria_usada = key.title() # ex: "Saude"
                        break
                    else:
                        return [], False, None # Categoria especificada mas coluna não existe
            if not colunas_a_somar_ou_usar: # Categoria especificada mas não mapeada
                return [], False, None
    
    # Lógica para gasto total geral ou falta de categoria específica
    if is_total_geral or not categoria_despesa_query:
        # Verificar se há coluna despesa_total_milhoes
        if "despesa_total_milhoes" in available_df_columns:
            colunas_a_somar_ou_usar = ["despesa_total_milhoes"]
        elif valid_individual_expense_cols_in_df:
            # Somar todas as colunas individuais disponíveis
            colunas_a_somar_ou_usar = valid_individual_expense_cols_in_df
        else:
            return [], False, None

    if not colunas_a_somar_ou_usar:
        return [], False, None

    return colunas_a_somar_ou_usar, is_total_geral, nome_coluna_categoria_usada

# --- Funções de Cenário Específicas ---
def _handle_idh_especifico(
    data_df: pd.DataFrame,
    uf: str,
    ano: int
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Busca o IDH para uma UF e ano específicos.
    Retorna (text_part, scenario_filters) ou (None, None).
    """
    if not uf or not ano:
        return None, None

    try:
        filtered_data = data_df[
            (data_df['uf'].str.upper() == uf.upper()) &
            (data_df['ano'] == ano)
        ]

        if not filtered_data.empty and 'idh' in filtered_data.columns and pd.notna(filtered_data['idh'].iloc[0]):
            valor_idh = filtered_data['idh'].iloc[0]
            text_part = f"O IDH de {uf.upper()} em {ano} foi {valor_idh:.3f}."
            scenario_filters = {
                "tipo_cenario_factual": "idh_especifico",
                "uf_cenario": uf.upper(),
                "ano_cenario": ano,
                "valor_cenario": valor_idh
            }
            return text_part, scenario_filters
        else:
            text_part = f"Não encontrei dados de IDH para {uf.upper()} em {ano} nos meus registros."
            # Mesmo se não encontrar, podemos retornar o filtro que tentamos, mas sem valor
            scenario_filters = {
                "tipo_cenario_factual": "idh_especifico_nao_encontrado",
                "uf_cenario": uf.upper(),
                "ano_cenario": ano
            }
            return text_part, scenario_filters # Retorna a mensagem de não encontrado

    except Exception as e:
        return f"Ocorreu um erro ao buscar o IDH específico para {uf.upper()} em {ano}.", None

def _handle_idh_maior_brasil(
    data_df: pd.DataFrame,
    ano: Optional[int] # Ano pode ser None, para buscar no mais recente
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o maior IDH no Brasil para um ano específico ou o mais recente.
    """
    if data_df.empty or 'idh' not in data_df.columns or 'uf' not in data_df.columns or 'ano' not in data_df.columns:
        return "Não consigo processar essa informação no momento devido a dados ausentes.", None

    temp_df = data_df.copy()
    ano_usado = ano
    mensagem_ano = f"em {ano}" if ano else "no ano mais recente disponível"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados de IDH para o ano {ano} para determinar o maior.", {"tipo_cenario_factual": "idh_maior_brasil_sem_dados_ano", "ano_cenario": ano}
    else: # Se ano não foi fornecido, usa o mais recente
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano = f"no ano mais recente ({ano_usado})"
        else:
            return "Não foi possível determinar o ano mais recente para a análise de maior IDH.", {"tipo_cenario_factual": "idh_maior_brasil_sem_ano_recente"}

    temp_df = temp_df.dropna(subset=['idh'])
    if temp_df.empty:
        return f"Não há dados de IDH válidos {mensagem_ano} para determinar o maior.", {"tipo_cenario_factual": "idh_maior_brasil_sem_dados_validos", "ano_cenario": ano_usado}

    try:
        estado_maior_idh = temp_df.loc[temp_df['idh'].idxmax()]
        uf_maior = estado_maior_idh['uf']
        valor_idh = estado_maior_idh['idh']
        text_part = f"O estado com o maior IDH no Brasil {mensagem_ano} é {uf_maior}, com um valor de {valor_idh:.3f}."
        scenario_filters = {
            "tipo_cenario_factual": "idh_maior_brasil",
            "ano_cenario": ano_usado,
            "uf_cenario_resultado": uf_maior,
            "valor_cenario": valor_idh
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o maior IDH {mensagem_ano}.", None

def _handle_idh_menor_brasil(
    data_df: pd.DataFrame,
    ano: Optional[int] # Ano pode ser None, para buscar no mais recente
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o menor IDH no Brasil para um ano específico ou o mais recente.
    """
    if data_df.empty or 'idh' not in data_df.columns or 'uf' not in data_df.columns or 'ano' not in data_df.columns:
        return "Não consigo processar essa informação no momento devido a dados ausentes.", None

    temp_df = data_df.copy()
    ano_usado = ano
    mensagem_ano = f"em {ano}" if ano else "no ano mais recente disponível"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados de IDH para o ano {ano} para determinar o menor.", {"tipo_cenario_factual": "idh_menor_brasil_sem_dados_ano", "ano_cenario": ano}
    else: # Se ano não foi fornecido, usa o mais recente
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano = f"no ano mais recente ({ano_usado})"
        else:
            return "Não foi possível determinar o ano mais recente para a análise de menor IDH.", {"tipo_cenario_factual": "idh_menor_brasil_sem_ano_recente"}

    temp_df = temp_df.dropna(subset=['idh'])
    if temp_df.empty:
        return f"Não há dados de IDH válidos {mensagem_ano} para determinar o menor.", {"tipo_cenario_factual": "idh_menor_brasil_sem_dados_validos", "ano_cenario": ano_usado}

    try:
        estado_menor_idh = temp_df.loc[temp_df['idh'].idxmin()]
        uf_menor = estado_menor_idh['uf']
        valor_idh = estado_menor_idh['idh']
        text_part = f"O estado com o menor IDH (ou pior IDH) no Brasil {mensagem_ano} é {uf_menor}, com um valor de {valor_idh:.3f}."
        scenario_filters = {
            "tipo_cenario_factual": "idh_menor_brasil",
            "ano_cenario": ano_usado,
            "uf_cenario_resultado": uf_menor,
            "valor_cenario": valor_idh
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o menor IDH {mensagem_ano}.", None

def _handle_idh_maior_regiao(
    data_df: pd.DataFrame,
    regiao: str,
    ano: Optional[int]
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o maior IDH em uma região específica, para um ano ou o mais recente.
    """
    if not regiao:
        return "A região não foi especificada para a busca do maior IDH.", None
    if (data_df.empty or 'idh' not in data_df.columns or 'uf' not in data_df.columns or
        'ano' not in data_df.columns or 'regiao' not in data_df.columns):
        return "Não consigo processar essa informação no momento devido a dados ausentes.", None

    temp_df = data_df[data_df['regiao'].str.lower() == regiao.lower()].copy()
    if temp_df.empty:
        return f"Não foram encontrados dados para a região '{regiao.title()}'.", {"tipo_cenario_factual": "idh_maior_regiao_sem_dados_regiao", "regiao_cenario": regiao}

    ano_usado = ano
    mensagem_ano = f"em {ano}" if ano else "no ano mais recente disponível na região"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados de IDH para a região '{regiao.title()}' no ano {ano}.", {"tipo_cenario_factual": "idh_maior_regiao_sem_dados_ano", "regiao_cenario": regiao, "ano_cenario": ano}
    else:
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano = f"no ano mais recente ({ano_usado}) na região"
        else:
            return f"Não foi possível determinar o ano mais recente para a análise de maior IDH na região '{regiao.title()}'.", {"tipo_cenario_factual": "idh_maior_regiao_sem_ano_recente", "regiao_cenario": regiao}
    
    temp_df = temp_df.dropna(subset=['idh'])
    if temp_df.empty:
        return f"Não há dados de IDH válidos para a região '{regiao.title()}' {mensagem_ano.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_maior_regiao_sem_dados_validos", "regiao_cenario": regiao, "ano_cenario": ano_usado}

    try:
        estado_maior_idh = temp_df.loc[temp_df['idh'].idxmax()]
        uf_maior = estado_maior_idh['uf']
        valor_idh = estado_maior_idh['idh']
        text_part = f"Na região {regiao.title()}, o estado com o maior IDH {mensagem_ano.replace(' na região', '')} é {uf_maior}, com um valor de {valor_idh:.3f}."
        scenario_filters = {
            "tipo_cenario_factual": "idh_maior_regiao",
            "regiao_cenario": regiao,
            "ano_cenario": ano_usado,
            "uf_cenario_resultado": uf_maior,
            "valor_cenario": valor_idh
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o maior IDH na região {regiao.title()} {mensagem_ano.replace(' na região', '')}.", None

def _handle_idh_menor_regiao(
    data_df: pd.DataFrame,
    regiao: str,
    ano: Optional[int]
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o menor IDH em uma região específica, para um ano ou o mais recente.
    """
    if not regiao:
        return "A região não foi especificada para a busca do menor IDH.", None
    if (data_df.empty or 'idh' not in data_df.columns or 'uf' not in data_df.columns or
        'ano' not in data_df.columns or 'regiao' not in data_df.columns):
        return "Não consigo processar essa informação no momento devido a dados ausentes.", None

    temp_df = data_df[data_df['regiao'].str.lower() == regiao.lower()].copy()
    if temp_df.empty:
        return f"Não foram encontrados dados para a região '{regiao.title()}'.", {"tipo_cenario_factual": "idh_menor_regiao_sem_dados_regiao", "regiao_cenario": regiao}

    ano_usado = ano
    mensagem_ano = f"em {ano}" if ano else "no ano mais recente disponível na região"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados para a região '{regiao.title()}' no ano {ano}.", {"tipo_cenario_factual": "idh_menor_regiao_sem_dados_ano", "regiao_cenario": regiao, "ano_cenario": ano}
    else:
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano = f"no ano mais recente ({ano_usado}) na região"
        else:
            return f"Não foi possível determinar o ano mais recente para a análise de menor IDH na região '{regiao.title()}'.", {"tipo_cenario_factual": "idh_menor_regiao_sem_ano_recente", "regiao_cenario": regiao}
    
    temp_df = temp_df.dropna(subset=['idh'])
    if temp_df.empty:
        return f"Não há dados de IDH válidos para a região '{regiao.title()}' {mensagem_ano.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_menor_regiao_sem_dados_validos", "regiao_cenario": regiao, "ano_cenario": ano_usado}

    try:
        estado_menor_idh = temp_df.loc[temp_df['idh'].idxmin()]
        uf_menor = estado_menor_idh['uf']
        valor_idh = estado_menor_idh['idh']
        text_part = f"Na região {regiao.title()}, o estado com o menor IDH (ou pior IDH) {mensagem_ano.replace(' na região', '')} é {uf_menor}, com um valor de {valor_idh:.3f}."
        scenario_filters = {
            "tipo_cenario_factual": "idh_menor_regiao",
            "regiao_cenario": regiao,
            "ano_cenario": ano_usado,
            "uf_cenario_resultado": uf_menor,
            "valor_cenario": valor_idh
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o menor IDH na região {regiao.title()} {mensagem_ano.replace(' na região', '')}.", None

def _handle_idh_medio_brasil(
    data_df: pd.DataFrame,
    ano: Optional[int] # Ano pode ser None, para buscar no mais recente
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Calcula o IDH médio no Brasil para um ano específico ou o mais recente.
    """
    if data_df.empty or 'idh' not in data_df.columns or 'ano' not in data_df.columns:
        return "Não consigo calcular o IDH médio no momento devido a dados ausentes.", None

    temp_df = data_df.copy()
    ano_usado = ano
    mensagem_ano_contexto = f"em {ano}" if ano else "no ano mais recente disponível"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados de IDH para o ano {ano} para calcular a média.", {"tipo_cenario_factual": "idh_medio_brasil_sem_dados_ano", "ano_cenario": ano}
    else: # Se ano não foi fornecido, usa o mais recente
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano_contexto = f"no ano mais recente ({ano_usado})"
        else:
            return "Não foi possível determinar o ano mais recente para o cálculo do IDH médio.", {"tipo_cenario_factual": "idh_medio_brasil_sem_ano_recente"}

    temp_df = temp_df.dropna(subset=['idh'])
    if temp_df.empty:
        return f"Não há dados de IDH válidos {mensagem_ano_contexto} para calcular a média.", {"tipo_cenario_factual": "idh_medio_brasil_sem_dados_validos", "ano_cenario": ano_usado}

    try:
        media_idh = temp_df['idh'].mean()
        text_part = f"O IDH médio no Brasil {mensagem_ano_contexto} foi de {media_idh:.3f}."
        scenario_filters = {
            "tipo_cenario_factual": "idh_medio_brasil",
            "ano_cenario": ano_usado,
            "valor_cenario": media_idh
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar calcular o IDH médio {mensagem_ano_contexto}.", None

# --- Cenários de Gastos ---
def _handle_gasto_especifico_uf_ano(
    data_df: pd.DataFrame,
    uf: str,
    ano: int,
    categoria_despesa: Optional[str] = None # Ex: "Saúde", "Educação", ou None para total
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Busca um gasto específico (categoria ou total) para uma UF e ano.
    """
    if not uf or not ano:
        return "UF ou Ano não fornecidos para a busca de gasto específico.", None

    relevant_cols, is_total, cat_usada_nome = _get_relevant_expense_columns(data_df, categoria_despesa)

    if not relevant_cols:
        msg = f"Não foi possível identificar as colunas de despesa para a categoria '{categoria_despesa if categoria_despesa else 'Total'}'."
        return msg, {"tipo_cenario_factual": "gasto_especifico_col_nao_encontrada", "uf_cenario": uf, "ano_cenario": ano, "categoria_tentada": categoria_despesa}

    try:
        filtered_data = data_df[
            (data_df['uf'].str.upper() == uf.upper()) &
            (data_df['ano'] == ano)
        ].copy() # Usar .copy() para evitar SettingWithCopyWarning se formos adicionar coluna

        if filtered_data.empty:
            return f"Não encontrei dados para {uf.upper()} em {ano}.", {"tipo_cenario_factual": "gasto_especifico_sem_dados_uf_ano", "uf_cenario": uf, "ano_cenario": ano, "categoria_usada": cat_usada_nome}
        
        # Garantir que todas as colunas relevantes são numéricas
        for col in relevant_cols:
            if col not in filtered_data.columns:
                 return f"A coluna de despesa '{col}' não foi encontrada para {uf.upper()} em {ano}.", None
            filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

        # Calcular o valor do gasto
        if len(relevant_cols) == 1:
            valor_gasto = filtered_data[relevant_cols[0]].iloc[0]
        else: # Múltiplas colunas para somar (caso de total calculado)
            valor_gasto = filtered_data[relevant_cols].sum(axis=1).iloc[0]

        if pd.notna(valor_gasto):
            nome_exibicao_categoria = cat_usada_nome if cat_usada_nome else ("Total" if is_total else "Desconhecida")
            if nome_exibicao_categoria == "Total":
                text_part = f"O gasto público total de {uf.upper()} em {ano} foi de R$ {valor_gasto:.2f} milhões."
            else:
                text_part = f"O gasto público em {nome_exibicao_categoria} para {uf.upper()} em {ano} foi de R$ {valor_gasto:.2f} milhões."
            
            scenario_filters = {
                "tipo_cenario_factual": "gasto_especifico",
                "uf_cenario": uf.upper(),
                "ano_cenario": ano,
                "categoria_cenario": nome_exibicao_categoria,
                "valor_cenario": valor_gasto
            }
            return text_part, scenario_filters
        else:
            nome_exibicao_categoria = cat_usada_nome if cat_usada_nome else ("Total" if is_total else "Desconhecida")
            msg = f"O valor do gasto em {nome_exibicao_categoria} para {uf.upper()} em {ano} não está disponível ou é inválido."
            return msg, {"tipo_cenario_factual": "gasto_especifico_valor_nan", "uf_cenario": uf, "ano_cenario": ano, "categoria_usada": nome_exibicao_categoria}

    except Exception as e:
        return f"Ocorreu um erro ao buscar o gasto específico.", None

def _handle_gasto_maior_brasil(
    data_df: pd.DataFrame,
    ano: Optional[int],
    categoria_despesa: Optional[str] = None
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o maior gasto (total ou por categoria) no Brasil.
    """
    if ano:
        ano_usado = ano
        mensagem_ano_contexto = f"em {ano}"
    else:
        if pd.notna(data_df['ano'].max()):
            ano_usado = int(data_df['ano'].max())
            temp_df = data_df[data_df['ano'] == ano_usado]
            mensagem_ano_contexto = f"no ano mais recente ({ano_usado})"
        else:
            return "Não foi possível determinar o ano mais recente para a análise.", {"tipo_cenario_factual": "gasto_maior_brasil_sem_ano_recente"}

    relevant_cols, is_total, cat_usada_nome = _get_relevant_expense_columns(data_df, categoria_despesa)
    if not relevant_cols:
        msg = f"Não foi possível identificar colunas de despesa para '{categoria_despesa if categoria_despesa else 'Total'}' para encontrar o maior gasto."
        return msg, {"tipo_cenario_factual": "gasto_maior_brasil_col_nao_encontrada", "categoria_tentada": categoria_despesa}

    temp_df = data_df.copy()
    # Garantir que as colunas de despesa são numéricas e tratar NaNs como 0 para soma/comparação
    for col in relevant_cols:
        if col not in temp_df.columns:
            return f"Coluna de despesa '{col}' não encontrada no DataFrame.", None
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce').fillna(0)

    # Criar coluna de gasto consolidado se necessário (soma de várias ou uso de uma específica)
    col_gasto_final = "__gasto_calculado_temp"
    if len(relevant_cols) == 1:
        temp_df[col_gasto_final] = temp_df[relevant_cols[0]]
    else: # Soma de múltiplas colunas (geralmente para total)
        temp_df[col_gasto_final] = temp_df[relevant_cols].sum(axis=1)

    if temp_df.empty or temp_df[col_gasto_final].isnull().all():
        return f"Não há dados de gasto válidos {mensagem_ano_contexto} para a categoria '{cat_usada_nome if cat_usada_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_maior_brasil_sem_dados_validos", "ano_cenario": ano_usado, "categoria_usada": cat_usada_nome}

    try:
        estado_maior_gasto = temp_df.loc[temp_df[col_gasto_final].idxmax()]
        uf_maior = estado_maior_gasto['uf']
        valor_gasto = estado_maior_gasto[col_gasto_final]
        
        nome_exib_cat = cat_usada_nome if cat_usada_nome and cat_usada_nome != "Total" else "público total"
        if cat_usada_nome == "Total": nome_exib_cat = "público total"
        else: nome_exib_cat = f"em {cat_usada_nome.lower() if cat_usada_nome else 'gastos'}"

        text_part = f"O estado com o maior gasto {nome_exib_cat} no Brasil {mensagem_ano_contexto} é {uf_maior}, com R$ {valor_gasto:.2f} milhões."
        scenario_filters = {
            "tipo_cenario_factual": "gasto_maior_brasil",
            "ano_cenario": ano_usado,
            "categoria_cenario": cat_usada_nome if cat_usada_nome else "Total",
            "uf_cenario_resultado": uf_maior,
            "valor_cenario": valor_gasto
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o maior gasto.", None

def _handle_gasto_menor_brasil(
    data_df: pd.DataFrame,
    ano: Optional[int],
    categoria_despesa: Optional[str] = None
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o menor gasto (total ou por categoria) no Brasil.
    """
    if ano:
        ano_usado = ano
        mensagem_ano_contexto = f"em {ano}"
    else:
        if pd.notna(data_df['ano'].max()):
            ano_usado = int(data_df['ano'].max())
            temp_df = data_df[data_df['ano'] == ano_usado]
            mensagem_ano_contexto = f"no ano mais recente ({ano_usado})"
        else:
            return "Não foi possível determinar o ano mais recente para a análise.", {"tipo_cenario_factual": "gasto_menor_brasil_sem_ano_recente", "categoria_usada": categoria_despesa}

    relevant_cols, is_total, cat_usada_nome = _get_relevant_expense_columns(data_df, categoria_despesa)
    if not relevant_cols:
        msg = f"Não foi possível identificar colunas de despesa para '{categoria_despesa if categoria_despesa else 'Total'}' para encontrar o menor gasto."
        return msg, {"tipo_cenario_factual": "gasto_menor_brasil_col_nao_encontrada", "categoria_tentada": categoria_despesa}

    temp_df = data_df.copy()
    for col in relevant_cols:
        if col not in temp_df.columns:
            return f"Coluna de despesa '{col}' não encontrada no DataFrame.", None
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce').fillna(float('inf')) # fillna com inf para min

    col_gasto_final = "__gasto_calculado_temp"
    if len(relevant_cols) == 1:
        temp_df[col_gasto_final] = temp_df[relevant_cols[0]]
    else:
        temp_df[col_gasto_final] = temp_df[relevant_cols].sum(axis=1)
    
    # Assegurar que após a soma, infs (de linhas onde todas as colunas eram NaN) não causem problemas
    # Se a soma resultar em inf (porque todas as colunas somadas eram inf), essa linha não é válida para min.
    temp_df = temp_df[temp_df[col_gasto_final] != float('inf')]

    if temp_df.empty or temp_df[col_gasto_final].isnull().all():
        return f"Não há dados de gasto válidos {mensagem_ano_contexto} para a categoria '{cat_usada_nome if cat_usada_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_menor_brasil_sem_dados_validos", "ano_cenario": ano_usado, "categoria_usada": cat_usada_nome}

    try:
        estado_menor_gasto = temp_df.loc[temp_df[col_gasto_final].idxmin()] # MUDANÇA AQUI
        uf_menor = estado_menor_gasto['uf']
        valor_gasto = estado_menor_gasto[col_gasto_final]
        
        nome_exib_cat = cat_usada_nome if cat_usada_nome and cat_usada_nome != "Total" else "público total"
        if cat_usada_nome == "Total": nome_exib_cat = "público total"
        else: nome_exib_cat = f"em {cat_usada_nome.lower() if cat_usada_nome else 'gastos'}"

        text_part = f"O estado com o menor gasto {nome_exib_cat} no Brasil {mensagem_ano_contexto} é {uf_menor}, com R$ {valor_gasto:.2f} milhões."
        scenario_filters = {
            "tipo_cenario_factual": "gasto_menor_brasil",
            "ano_cenario": ano_usado,
            "categoria_cenario": cat_usada_nome if cat_usada_nome else "Total",
            "uf_cenario_resultado": uf_menor,
            "valor_cenario": valor_gasto
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o menor gasto.", None

def _handle_gasto_maior_regiao(
    data_df: pd.DataFrame,
    regiao: str,
    ano: Optional[int],
    categoria_despesa: Optional[str] = None
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o maior gasto (total ou por categoria) em uma REGIAO específica.
    """
    if not regiao:
        return "A região não foi especificada para a busca do maior gasto.", None

    relevant_cols, is_total, cat_usada_nome = _get_relevant_expense_columns(data_df, categoria_despesa)
    if not relevant_cols:
        msg = f"Não foi possível identificar colunas de despesa para '{categoria_despesa if categoria_despesa else 'Total'}' na região '{regiao.title()}'."
        return msg, {"tipo_cenario_factual": "gasto_maior_regiao_col_nao_encontrada", "regiao_cenario":regiao, "categoria_tentada": categoria_despesa}

    temp_df = data_df[data_df['regiao'].str.lower() == regiao.lower()].copy()
    if temp_df.empty:
        return f"Não foram encontrados dados para a região '{regiao.title()}'.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_dados_regiao", "regiao_cenario": regiao}

    for col in relevant_cols:
        if col not in temp_df.columns:
            return f"Coluna de despesa '{col}' não encontrada para a região '{regiao.title()}'.", None
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce').fillna(0)

    col_gasto_final = "__gasto_calculado_temp"
    if len(relevant_cols) == 1:
        temp_df[col_gasto_final] = temp_df[relevant_cols[0]]
    else:
        temp_df[col_gasto_final] = temp_df[relevant_cols].sum(axis=1)

    ano_usado = ano
    mensagem_ano_contexto = f"em {ano}" if ano else "no ano mais recente disponível na região"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados para a região '{regiao.title()}' no ano {ano} para determinar o maior gasto.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_dados_ano", "regiao_cenario": regiao, "ano_cenario": ano, "categoria_usada": cat_usada_nome}
    else:
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano_contexto = f"no ano mais recente ({ano_usado}) na região"
        else:
            return f"Não foi possível determinar o ano mais recente para a análise na região '{regiao.title()}'.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_ano_recente", "regiao_cenario": regiao, "categoria_usada": cat_usada_nome}

    if temp_df.empty or temp_df[col_gasto_final].isnull().all():
        return f"Não há dados de gasto válidos para '{cat_usada_nome if cat_usada_nome else 'Total'}' na região '{regiao.title()}' {mensagem_ano_contexto.replace(' na região', '')}.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_dados_validos", "regiao_cenario":regiao, "ano_cenario": ano_usado, "categoria_usada": cat_usada_nome}

    try:
        estado_maior_gasto = temp_df.loc[temp_df[col_gasto_final].idxmax()]
        uf_maior = estado_maior_gasto['uf']
        valor_gasto = estado_maior_gasto[col_gasto_final]
        
        nome_exib_cat = cat_usada_nome if cat_usada_nome and cat_usada_nome != "Total" else "público total"
        if cat_usada_nome == "Total": nome_exib_cat = "público total"
        else: nome_exib_cat = f"em {cat_usada_nome.lower() if cat_usada_nome else 'gastos'}"
        
        text_part = f"Na região {regiao.title()}, o estado com o maior gasto {nome_exib_cat} {mensagem_ano_contexto.replace(' na região', '')} é {uf_maior}, com R$ {valor_gasto:.2f} milhões."
        scenario_filters = {
            "tipo_cenario_factual": "gasto_maior_regiao",
            "regiao_cenario": regiao,
            "ano_cenario": ano_usado,
            "categoria_cenario": cat_usada_nome if cat_usada_nome else "Total",
            "uf_cenario_resultado": uf_maior,
            "valor_cenario": valor_gasto
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o maior gasto na região '{regiao.title()}'.", None

def _handle_gasto_menor_regiao(
    data_df: pd.DataFrame,
    regiao: str,
    ano: Optional[int],
    categoria_despesa: Optional[str] = None
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Encontra o estado com o menor gasto (total ou por categoria) em uma REGIAO específica.
    """
    if not regiao:
        return "A região não foi especificada para a busca do menor gasto.", None

    relevant_cols, is_total, cat_usada_nome = _get_relevant_expense_columns(data_df, categoria_despesa)
    if not relevant_cols:
        msg = f"Não foi possível identificar colunas de despesa para '{categoria_despesa if categoria_despesa else 'Total'}' na região '{regiao.title()}'."
        return msg, {"tipo_cenario_factual": "gasto_menor_regiao_col_nao_encontrada", "regiao_cenario":regiao, "categoria_tentada": categoria_despesa}

    temp_df = data_df[data_df['regiao'].str.lower() == regiao.lower()].copy()
    if temp_df.empty:
        return f"Não foram encontrados dados para a região '{regiao.title()}'.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_dados_regiao", "regiao_cenario": regiao}

    for col in relevant_cols:
        if col not in temp_df.columns:
            return f"Coluna de despesa '{col}' não encontrada para a região '{regiao.title()}'.", None
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce').fillna(float('inf')) # Fill com inf para min

    col_gasto_final = "__gasto_calculado_temp"
    if len(relevant_cols) == 1:
        temp_df[col_gasto_final] = temp_df[relevant_cols[0]]
    else:
        temp_df[col_gasto_final] = temp_df[relevant_cols].sum(axis=1)
    
    temp_df = temp_df[temp_df[col_gasto_final] != float('inf')]

    ano_usado = ano
    mensagem_ano_contexto = f"em {ano}" if ano else "no ano mais recente disponível na região"

    if ano:
        temp_df = temp_df[temp_df['ano'] == ano]
        if temp_df.empty:
            return f"Não há dados para a região '{regiao.title()}' no ano {ano} para determinar o menor gasto.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_dados_ano", "regiao_cenario": regiao, "ano_cenario": ano, "categoria_usada": cat_usada_nome}
    else:
        if pd.notna(temp_df['ano'].max()):
            ano_usado = int(temp_df['ano'].max())
            temp_df = temp_df[temp_df['ano'] == ano_usado]
            mensagem_ano_contexto = f"no ano mais recente ({ano_usado}) na região"
        else:
            return f"Não foi possível determinar o ano mais recente para a análise na região '{regiao.title()}'.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_ano_recente", "regiao_cenario": regiao, "categoria_usada": cat_usada_nome}

    if temp_df.empty or temp_df[col_gasto_final].isnull().all():
        return f"Não há dados de gasto válidos para '{cat_usada_nome if cat_usada_nome else 'Total'}' na região '{regiao.title()}' {mensagem_ano_contexto.replace(' na região', '')}.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_dados_validos", "regiao_cenario":regiao, "ano_cenario": ano_usado, "categoria_usada": cat_usada_nome}

    try:
        estado_menor_gasto = temp_df.loc[temp_df[col_gasto_final].idxmin()] # MUDANÇA AQUI
        uf_menor = estado_menor_gasto['uf']
        valor_gasto = estado_menor_gasto[col_gasto_final]
        
        nome_exib_cat = cat_usada_nome if cat_usada_nome and cat_usada_nome != "Total" else "público total"
        if cat_usada_nome == "Total": nome_exib_cat = "público total"
        else: nome_exib_cat = f"em {cat_usada_nome.lower() if cat_usada_nome else 'gastos'}"
        
        text_part = f"Na região {regiao.title()}, o estado com o menor gasto {nome_exib_cat} {mensagem_ano_contexto.replace(' na região', '')} é {uf_menor}, com R$ {valor_gasto:.2f} milhões."
        scenario_filters = {
            "tipo_cenario_factual": "gasto_menor_regiao",
            "regiao_cenario": regiao,
            "ano_cenario": ano_usado,
            "categoria_cenario": cat_usada_nome if cat_usada_nome else "Total",
            "uf_cenario_resultado": uf_menor,
            "valor_cenario": valor_gasto
        }
        return text_part, scenario_filters
    except Exception as e:
        return f"Ocorreu um erro ao tentar encontrar o menor gasto na região '{regiao.title()}'.", None

# Função Principal de Orquestração
def handle_factual_scenarios(
    user_query_lower: str,
    final_intent_for_scenarios: Optional[str],
    filters_from_llm: Dict,
    data_df: pd.DataFrame,
    conversation_history: List[Dict]
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Tenta lidar com a consulta do usuário por meio de cenários factuais predefinidos.
    Retorna (text_part, updated_filters) se um cenário for acionado e bem-sucedido.
    Retorna (None, None) se nenhum cenário factual for aplicável.
    """
    text_part: Optional[str] = None
    updated_filters: Dict = filters_from_llm.copy()
    scenario_filters: Optional[Dict] = None 

    prev_response_content: Optional[str] = None
    if len(conversation_history) >= 2 and conversation_history[-2]["role"] == "assistant":
        prev_response_content = conversation_history[-2]["content"]

    # Extração de entidades ANTES da árvore de decisão
    extracted_uf = _extract_uf_from_query(filters_from_llm.get('uf'), prev_response_content, data_df)
    extracted_ano = _extract_year_from_query(filters_from_llm.get('ano'), prev_response_content, data_df, uf_context=extracted_uf)
    extracted_regiao = filters_from_llm.get('regiao') # Região geralmente vem bem do LLM
    extracted_categoria_gasto = filters_from_llm.get('categoria_despesa') # Categoria de despesa do LLM

    # Atualizar os filtros que serão retornados com o que foi extraído aqui, se forem mais precisos
    if extracted_uf: updated_filters['uf'] = extracted_uf
    if extracted_ano: updated_filters['ano'] = extracted_ano
    if extracted_regiao: updated_filters['regiao'] = extracted_regiao # Mantém se extraído do LLM
    if extracted_categoria_gasto: updated_filters['categoria_despesa'] = extracted_categoria_gasto # Mantém se extraído do LLM

    # --- Árvore de Decisão para Cenários --- #
    if final_intent_for_scenarios == "idh_especifico" and extracted_uf and extracted_ano:
        text_part, scenario_filters = _handle_idh_especifico(data_df, extracted_uf, extracted_ano)
    
    elif final_intent_for_scenarios == "idh_maior_brasil" and not extracted_uf and not extracted_regiao:
        text_part, scenario_filters = _handle_idh_maior_brasil(data_df, extracted_ano)

    elif final_intent_for_scenarios == "idh_menor_brasil" and not extracted_uf and not extracted_regiao:
        text_part, scenario_filters = _handle_idh_menor_brasil(data_df, extracted_ano)

    elif final_intent_for_scenarios == "idh_maior_regiao" and extracted_regiao and not extracted_uf:
        text_part, scenario_filters = _handle_idh_maior_regiao(data_df, extracted_regiao, extracted_ano)

    elif final_intent_for_scenarios == "idh_menor_regiao" and extracted_regiao and not extracted_uf:
        text_part, scenario_filters = _handle_idh_menor_regiao(data_df, extracted_regiao, extracted_ano)

    elif final_intent_for_scenarios == "idh_medio_brasil" and not extracted_uf and not extracted_regiao:
        text_part, scenario_filters = _handle_idh_medio_brasil(data_df, extracted_ano)
    
    # Novo cenário de gasto específico
    elif final_intent_for_scenarios == "gasto_especifico" and extracted_uf and extracted_ano:
        # A categoria pode ser None (para total) ou uma string específica
        text_part, scenario_filters = _handle_gasto_especifico_uf_ano(data_df, extracted_uf, extracted_ano, extracted_categoria_gasto)

    elif final_intent_for_scenarios == "gasto_maior_brasil" and not extracted_uf and not extracted_regiao:
        text_part, scenario_filters = _handle_gasto_maior_brasil(data_df, extracted_ano, extracted_categoria_gasto)

    elif final_intent_for_scenarios == "gasto_menor_brasil" and not extracted_uf and not extracted_regiao:
        text_part, scenario_filters = _handle_gasto_menor_brasil(data_df, extracted_ano, extracted_categoria_gasto)

    elif final_intent_for_scenarios == "gasto_maior_regiao" and extracted_regiao and not extracted_uf:
        text_part, scenario_filters = _handle_gasto_maior_regiao(data_df, extracted_regiao, extracted_ano, extracted_categoria_gasto)

    elif final_intent_for_scenarios == "gasto_menor_regiao" and extracted_regiao and not extracted_uf:
        text_part, scenario_filters = _handle_gasto_menor_regiao(data_df, extracted_regiao, extracted_ano, extracted_categoria_gasto)

    # Outros cenários de gastos serão adicionados aqui com elif

    if text_part and scenario_filters:
        updated_filters.update(scenario_filters) 
        return text_part, updated_filters

    return None, None 