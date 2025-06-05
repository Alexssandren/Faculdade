"""
Módulo para lidar com a interação com o Large Language Model (LLM).
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import json # Para carregar e analisar JSON da resposta do LLM
import pandas as pd # Adicionado Pandas
from pathlib import Path # Já estava sendo usado em find_dotenv, garantir que está no topo
import re # Adicionar import re
from typing import Tuple, Dict, Optional, List # Adicionado typing

class LLMQueryHandler:
    def __init__(self, dataset_schema_description: str = None):
        """
        Inicializa o handler do LLM.

        Args:
            dataset_schema_description (str, optional): Uma descrição textual
                do esquema do dataset principal para fornecer contexto ao LLM.
        """
        # Encontrar e carregar .env
        dotenv_path = self.find_dotenv()
        load_dotenv(dotenv_path=dotenv_path)
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Chave da API da OpenAI não encontrada. "
                             "Verifique seu arquivo .env e a variável OPENAI_API_KEY.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini" # Modelo a ser usado
        self.conversation_history = []
        
        # Carregar o dataset
        self.data_df = None
        self._load_dataset()
        
        self.dataset_schema = dataset_schema_description or self._get_default_schema_description()

        # Adiciona a mensagem do sistema com o esquema do dataset ao histórico
        self.add_system_message(
            f"""Você é um assistente de análise de dados especializado em dados sobre IDH e Despesas Públicas Federais no Brasil.
            Seu objetivo é responder perguntas dos usuários com base nos dados fornecidos e extrair intenções de filtro.
            Quando uma pergunta implicar filtros (como ano, UF, região, ou tipo de despesa),
            você DEVE incluir um objeto JSON na sua resposta com a chave 'filtros_identificados'.
            O JSON deve conter pares chave-valor para os filtros. Chaves válidas para filtros são: 'ano' (inteiro), 'uf' (string, sigla do estado), 'regiao' (string), 'categoria_despesa' (string).
            Se nenhum filtro for identificado, o valor de 'filtros_identificados' deve ser null ou um objeto vazio.
            Responda de forma concisa e informativa.
            Para perguntas diretas que solicitam um fato específico (por exemplo, "Qual o estado com maior IDH?", "Qual o valor do gasto em X?", "Que estado é esse?"), forneça a resposta diretamente, sem introduções ou definições genéricas desnecessárias.
            Quando responder a perguntas de acompanhamento curtas (ex: 'E para SC?', 'E em 2021?', 'Qual o valor?'), se você identificar que o usuário está se referindo a uma entidade (UF, ano) e um tipo de dado (IDH, despesa) de uma pergunta anterior, tente responder factualmente.
            
            Tipos de intenção que você pode identificar para cenários factuais (a serem usados internamente pelo sistema para buscar dados):
            - idh_especifico: IDH para uma UF e ano.
            - idh_maior_brasil: Maior IDH no Brasil (pode ter filtro de ano).
            - idh_menor_brasil: Menor IDH no Brasil (pode ter filtro de ano).
            - idh_maior_regiao: Maior IDH em uma Região (pode ter filtro de ano).
            - idh_menor_regiao: Menor IDH em uma Região (pode ter filtro de ano).
            - idh_medio_brasil: IDH médio no Brasil (pode ter filtro de ano).
            - gasto_especifico: Gasto (total ou categoria) para uma UF e ano.
            - gasto_maior_brasil: Maior gasto (total ou categoria) no Brasil (pode ter filtro de ano).
            - gasto_menor_brasil: Menor gasto (total ou categoria) no Brasil (pode ter filtro de ano).
            - gasto_maior_regiao: Maior gasto (total ou categoria) em uma Região (pode ter filtro de ano).
            - gasto_menor_regiao: Menor gasto (total ou categoria) em uma Região (pode ter filtro de ano).
            
            Se você herdar claramente o tipo de consulta, como um IDH específico para uma UF, de uma pergunta anterior, adicione ao JSON de filtros: `\\"tipo_consulta_herdada\\": \\"idh_especifico\\"` (substitua `idh_especifico` pelo tipo de intenção relevante da lista acima).

            O esquema principal dos dados com os quais você vai trabalhar é (simplificado):
            {self.dataset_schema}

            Exemplo de resposta com filtros:
            Pergunta do usuário: Qual o IDH de São Paulo em 2021?
            Sua Resposta: O IDH de São Paulo em 2021 foi X. {{"filtros_identificados": {{"ano": 2021, "uf": "SP", "tipo_intenção_llm": "idh_especifico"}}}}

            Exemplo de resposta sem filtros diretos:
            Pergunta do usuário: Quais são as principais categorias de despesa?
            Sua Resposta: As principais categorias de despesa incluem Educação, Saúde, etc. {{"filtros_identificados": {{}}}}
            """
        )

    def find_dotenv(self):
        """Encontra o arquivo .env subindo na árvore de diretórios."""
        from pathlib import Path
        current_dir = Path(__file__).parent
        while current_dir != current_dir.parent: # Para no root
            dotenv_path = current_dir / "Chave.env" # Nome do arquivo .env que você criou
            if dotenv_path.exists():
                return dotenv_path
            current_dir = current_dir.parent
        # Se não encontrar subindo, tenta no diretório do projeto (onde está main.py)
        # Isso assume que llm_handler.py está em src/llm/ e main.py na raiz.
        project_root_dotenv = Path(__file__).parent.parent.parent / "Chave.env"
        if project_root_dotenv.exists():
            return project_root_dotenv
        raise FileNotFoundError("Arquivo Chave.env não encontrado na árvore de diretórios do projeto.")

    def _load_dataset(self):
        """Carrega o dataset principal (dataset_unificado.csv) em um DataFrame Pandas."""
        try:
            # Determinar o caminho para o dataset_unificado.csv
            # Assumindo que llm_handler.py está em src/llm/
            # e o dataset está em data/processed/
            # A raiz do projeto é duas pastas acima de llm_handler.py (src/llm/ -> src/ -> ProjetoFinal/)
            project_root = Path(__file__).resolve().parent.parent.parent
            dataset_path = project_root / "data" / "processed" / "dataset_unificado.csv"

            if dataset_path.exists():
                self.data_df = pd.read_csv(dataset_path)
                print(f"INFO: Dataset '{dataset_path.name}' carregado com sucesso no LLMQueryHandler. {len(self.data_df)} linhas.")
            else:
                print(f"AVISO: Dataset '{dataset_path}' não encontrado. LLMQueryHandler operará sem dados locais.")
        except Exception as e:
            print(f"ERRO ao carregar o dataset no LLMQueryHandler: {e}")
            self.data_df = None # Garante que data_df é None em caso de erro

    def _get_default_schema_description(self) -> str:
        """
        Retorna uma descrição padrão do esquema do dataset_unificado.csv.
        Idealmente, isso seria carregado dinamicamente ou de um arquivo de metadados.
        """
        # TODO: Carregar dinamicamente as colunas do dataset_unificado.csv ou de um arquivo de schema.
        # Por enquanto, vamos usar uma descrição placeholder mais detalhada.
        return """
        - ano (Integer): Ano de referência dos dados.
        - uf (String): Sigla da Unidade Federativa (Estado). Ex: SP, RJ, BA.
        - estado (String): Nome completo do estado.
        - regiao (String): Região geográfica do Brasil (Norte, Nordeste, Sul, Sudeste, Centro-Oeste).
        - idh (Float): Índice de Desenvolvimento Humano geral (0 a 1).
        - idh_educacao (Float): Componente de educação do IDH.
        - idh_longevidade (Float): Componente de longevidade (saúde) do IDH.
        - idh_renda (Float): Componente de renda do IDH.
        - populacao (Integer): População estimada para o estado e ano.
        - (diversas colunas de despesa): Valores em milhões de Reais para categorias de despesa.
          Exemplos de nomes de colunas de despesa (após limpeza e pivot):
          'despesa_educacao', 'despesa_saude', 'despesa_assistencia_social', 'despesa_infraestrutura', etc.
          (Os nomes exatos das colunas de despesa podem variar, o LLM deve ser flexível).
        - (diversas colunas de despesa per capita): Valores de despesa por pessoa.
          Exemplos: 'despesa_educacao_per_capita', 'despesa_saude_per_capita', etc.
        - despesa_total_milhoes (Float): Soma de todas as despesas em milhões.
        - despesa_total_per_capita (Float): Despesa total por pessoa.
        """

    def add_user_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        self.conversation_history.append({"role": "assistant", "content": message})

    def add_system_message(self, message: str):
        # A mensagem do sistema geralmente é a primeira. Se já houver uma, pode-se optar por substituir ou adicionar.
        # Para este caso, vamos garantir que seja a primeira ou substitua se já existir.
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = message
        else:
            self.conversation_history.insert(0, {"role": "system", "content": message})

    def get_response(self, user_query: str) -> tuple[str, dict]:
        """
        Envia a consulta para o LLM e retorna a resposta textual e os filtros identificados.
        Tenta responder factualmente usando o novo sistema de cenários se aplicável.
        """
        self.add_user_message(user_query)

        try:
            llm_api_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=0.2, # Baixa temperatura para respostas mais factuais/consistentes
            )
            
            assistant_response_content = llm_api_response.choices[0].message.content
            text_part_llm = assistant_response_content # Resposta padrão do LLM
            filters_identified_llm = {} # Filtros extraídos da resposta do LLM
            
            # Extração do JSON de filtros da resposta do LLM
            json_marker = '{"filtros_identificados":'
            marker_start_index = assistant_response_content.rfind(json_marker)
            if marker_start_index != -1:
                potential_json_block = assistant_response_content[marker_start_index:]
                open_braces = 0
                json_end_index = -1
                for i, char in enumerate(potential_json_block):
                    if char == '{': open_braces += 1
                    elif char == '}':
                        open_braces -= 1
                        if open_braces == 0:
                            json_end_index = i + marker_start_index
                            break
                if json_end_index != -1:
                    actual_json_str = assistant_response_content[marker_start_index : json_end_index + 1]
                    try:
                        parsed_json_outer = json.loads(actual_json_str)
                        if 'filtros_identificados' in parsed_json_outer:
                            filters_identified_llm = parsed_json_outer.get('filtros_identificados', {})
                            text_part_llm = assistant_response_content[:marker_start_index].strip()
                    except json.JSONDecodeError:
                        print(f"DEBUG LLM Handler: Falha ao decodificar JSON: {actual_json_str}")
                        pass # Mantém filters_identified_llm como {} e text_part_llm original
            
            print(f"DEBUG LLM Handler: User query: {user_query}")
            print(f"DEBUG LLM Handler: LLM raw response: {assistant_response_content}")
            print(f"DEBUG LLM Handler: LLM text_part (inicial): {text_part_llm}")
            print(f"DEBUG LLM Handler: LLM filters_identified (inicial): {filters_identified_llm}")

            if self.data_df is not None and not self.data_df.empty:
                print(f"DEBUG LLM Handler: DataFrame carregado, processando com lógica de cenários.")
                user_query_lower = user_query.lower()
                
                # 1. Determinar intenção herdada (determined_primary_intent_type)
                determined_primary_intent_type = None
                tipo_consulta_herdada_do_llm = filters_identified_llm.get("tipo_consulta_herdada")

                if tipo_consulta_herdada_do_llm:
                    determined_primary_intent_type = tipo_consulta_herdada_do_llm
                    print(f"DEBUG LLM Intent: Intenção primária herdada do JSON do LLM: '{determined_primary_intent_type}'")
                elif len(self.conversation_history) >= 3 and self.conversation_history[-3]["role"] == "user":
                    prev_user_query_full_content = self.conversation_history[-3]["content"].lower()
                    # Lógica para determinar intenção da pergunta anterior (simplificada)
                    if "idh" in prev_user_query_full_content:
                        if "maior" in prev_user_query_full_content: determined_primary_intent_type = "idh_maior_brasil"
                        elif "menor" in prev_user_query_full_content or "pior" in prev_user_query_full_content: determined_primary_intent_type = "idh_menor_brasil"
                        elif "médio" in prev_user_query_full_content or "media" in prev_user_query_full_content: determined_primary_intent_type = "idh_medio_brasil"
                        else: determined_primary_intent_type = "idh_especifico"
                    elif "gasto" in prev_user_query_full_content or "despesa" in prev_user_query_full_content:
                        if "maior" in prev_user_query_full_content: determined_primary_intent_type = "gasto_maior_brasil"
                        elif "menor" in prev_user_query_full_content: determined_primary_intent_type = "gasto_menor_brasil"
                        else: determined_primary_intent_type = "gasto_especifico"
                    if determined_primary_intent_type:
                         print(f"DEBUG LLM Intent: Intenção primária determinada da PENÚLTIMA query do usuário: '{determined_primary_intent_type}'")


                # 2. Determinar intenção da consulta ATUAL (current_query_intent)
                current_query_intent = None
                llm_identified_intent = filters_identified_llm.get("tipo_intenção_llm") # O LLM pode sugerir
                if llm_identified_intent:
                    current_query_intent = llm_identified_intent
                    print(f"DEBUG LLM Intent: Intenção da query ATUAL (do JSON LLM): '{current_query_intent}'")
                else: # Tenta inferir da query atual se o LLM não forneceu "tipo_intenção_llm"
                    if 'idh' in user_query_lower:
                        if 'médio' in user_query_lower or 'media' in user_query_lower:
                            current_query_intent = "idh_medio_brasil"
                        elif 'maior' in user_query_lower:
                            current_query_intent = "idh_maior_regiao" if filters_identified_llm.get('regiao') else "idh_maior_brasil"
                        elif 'menor' in user_query_lower or 'pior' in user_query_lower:
                            current_query_intent = "idh_menor_regiao" if filters_identified_llm.get('regiao') else "idh_menor_brasil"
                        elif filters_identified_llm.get('uf') and filters_identified_llm.get('ano'):
                            current_query_intent = "idh_especifico"
                    elif 'gasto' in user_query_lower or 'despesa' in user_query_lower:
                        if 'maior' in user_query_lower or 'mais gasta' in user_query_lower:
                            current_query_intent = "gasto_maior_regiao" if filters_identified_llm.get('regiao') else "gasto_maior_brasil"
                        elif 'menor' in user_query_lower or 'menos gasta' in user_query_lower:
                            current_query_intent = "gasto_menor_regiao" if filters_identified_llm.get('regiao') else "gasto_menor_brasil"
                        elif filters_identified_llm.get('uf') and filters_identified_llm.get('ano'):
                            current_query_intent = "gasto_especifico"
                    if current_query_intent:
                        print(f"DEBUG LLM Intent: Intenção da query ATUAL (inferida da query string): '{current_query_intent}'")

                # 3. Determinar intenção final para os cenários
                final_intent_for_scenarios = current_query_intent if current_query_intent else determined_primary_intent_type
                
                print(f"DEBUG LLM Intent: Herdada (determined_primary_intent_type): '{determined_primary_intent_type}'")
                print(f"DEBUG LLM Intent: Atual (current_query_intent): '{current_query_intent}'")
                print(f"DEBUG LLM Intent: Final para cenários (final_intent_for_scenarios): '{final_intent_for_scenarios}'")

                # 4. Chamar o novo handler de cenários factuais
                scenario_text_part, scenario_updated_filters = handle_factual_scenarios(
                    user_query_lower=user_query_lower,
                    final_intent_for_scenarios=final_intent_for_scenarios,
                    filters_from_llm=filters_identified_llm.copy(),
                    data_df=self.data_df,
                    conversation_history=self.conversation_history
                )

                if scenario_text_part is not None:
                    print(f"DEBUG LLM Handler: Cenário factual TRATADO pelo novo handler. Resposta: '{scenario_text_part}', Filtros: {scenario_updated_filters}")
                    text_part_llm = scenario_text_part
                    if scenario_updated_filters is not None:
                         filters_identified_llm = scenario_updated_filters
                else:
                    print(f"DEBUG LLM Handler: Nenhum cenário factual específico tratado pelo novo handler. Usando resposta original do LLM.")

            else: 
                print("DEBUG LLM Handler: DataFrame não carregado. Pulando lógica de cenários factuais.")
            
            self.add_assistant_message(assistant_response_content) 
            return text_part_llm, filters_identified_llm

        except Exception as e:
            print(f"❌ Erro ao chamar a API da OpenAI ou ao processar cenários: {e}")
            import traceback
            traceback.print_exc()
            self.add_assistant_message(f"Erro interno: {e}")
            return "Desculpe, não consegui processar sua pergunta no momento devido a um erro interno.", {}

    def reset_conversation(self):
        """Limpa o histórico da conversa, mantendo a mensagem do sistema."""
        system_message = None
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_message = self.conversation_history[0]
        
        self.conversation_history = []
        if system_message:
            self.conversation_history.append(system_message)

# Funções auxiliares e de cenário copiadas aqui

def _extract_top_n(query: str, default_n: int = 1) -> int:
    """
    Extrai um número N (quantos resultados listar) de uma string de consulta.
    Procura por dígitos e palavras-chave numéricas.
    """
    query_lower = query.lower() # Trabalhar com minúsculas para palavras

    # Padrões regex para encontrar números como dígitos
    # 1. "top N", "topN"
    # 2. "N maiores", "N menores", "N piores", "N melhores"
    # 3. "os N", "as N", "liste N", "liste os N"
    # 4. Números sozinhos (ex: "3", "mostre 5")
    digit_patterns = [
        r'\b(?:top\s*|primeiros\s*|últimos\s*)(\d+)\b',                 # top 3, primeiros 5, últimos 2
        r'\b(?:os|as|liste|mostre|me dê|apresente)\s*(\d+)\b',       # os 3, liste 2, mostre 5
        r'\b(\d+)\s*(?:maiores|menores|piores|melhores|estados|vezes|itens|resultados)', # 3 maiores, 2 menores
        r'\b(\d+)\b' # um número sozinho como último recurso
    ]

    for pattern in digit_patterns:
        digit_match = re.search(pattern, query_lower)
        if digit_match:
            try:
                # O grupo de captura pode ser o 1 ou o único grupo, dependendo do padrão
                num_str = digit_match.group(1) if digit_match.lastindex else digit_match.group(0)
                num = int(num_str)
                if 1 <= num <= 27: # Limite razoável para "top N" (não mais que o total de UFs)
                    print(f"DEBUG EXTRACT_TOP_N: Encontrado dígito '{num_str}' com padrão '{pattern}' -> {num}")
                    return num
            except ValueError:
                pass
            except IndexError: # Caso o grupo de captura não exista como esperado
                pass 

    # Mapeamento de palavras para números
    word_to_num = {
        "um": 1, "uma": 1,
        "dois": 2, "duas": 2,
        "três": 3, "tres": 3, 
        "quatro": 4,
        "cinco": 5,
        "seis": 6,
        "sete": 7,
        "oito": 8,
        "nove": 9,
        "dez": 10,
        "onze": 11,
        "doze": 12,
        "treze": 13,
        "catorze": 14, "quatorze": 14,
        "quinze": 15,
        # Adicionar mais se necessário, mas até 15 cobre muitos casos de "top N"
    }

    # Procurar por palavras-chave numéricas isoladas ou em frases comuns
    # Iterar em ordem decrescente de comprimento para evitar correspondências parciais (ex: "dois" em "doze")
    sorted_keywords = sorted(word_to_num.keys(), key=len, reverse=True)
    for word in sorted_keywords:
        # Tenta encontrar a palavra exata ou em frases como "os <palavra> primeiros"
        word_pattern = r'\b(?:os|as|liste|mostre|me dê|apresente\s+)?' + re.escape(word) + r'\b'
        if re.search(word_pattern, query_lower):
            num_from_word = word_to_num[word]
            print(f"DEBUG EXTRACT_TOP_N: Encontrada palavra-chave: '{word}' com padrão '{word_pattern}' -> {num_from_word}")
            return num_from_word
            
    print(f"DEBUG EXTRACT_TOP_N: Nenhum N específico encontrado na query '{query}', usando default: {default_n}")
    return default_n

def _extract_year_from_query(
    query_ano_str: Optional[str], 
    prev_response_content: Optional[str] = None, 
    df: Optional[pd.DataFrame] = None, 
    uf_context: Optional[str] = None
) -> Optional[int]:
    print(f"DEBUG EXTRACT_YEAR: Inputs - query_ano_str: '{query_ano_str}', prev_response: {prev_response_content is not None}, df_available: {df is not None and not df.empty}, uf_context: '{uf_context}'")
    if query_ano_str:
        try:
            year_val = int(query_ano_str)
            if 1900 <= year_val <= 2100:
                print(f"DEBUG EXTRACT_YEAR: Ano '{year_val}' extraído de query_ano_str.")
                return year_val
        except ValueError:
            pass
    if prev_response_content and isinstance(prev_response_content, str):
        year_patterns = [r'(?:ano de|em|no ano de|o ano é|foi em)\s*(\d{4})', r'\b(\d{4})\b']
        for pattern in year_patterns:
            match = re.search(pattern, prev_response_content, re.IGNORECASE)
            if match:
                try:
                    year_val = int(match.group(1))
                    if 1900 <= year_val <= 2100: 
                        print(f"DEBUG EXTRACT_YEAR: Ano '{year_val}' extraído de prev_response_content com pattern '{pattern}'.")
                        return year_val
                except ValueError: continue
    if df is not None and not df.empty and 'ano' in df.columns and uf_context and 'uf' in df.columns:
        uf_data = df[df['uf'].str.upper() == uf_context.upper()]
        if not uf_data.empty and pd.notna(uf_data['ano'].max()):
            try: 
                latest_year_uf = int(uf_data['ano'].max())
                print(f"DEBUG EXTRACT_YEAR: Ano mais recente '{latest_year_uf}' para UF '{uf_context}' extraído do DataFrame.")
                return latest_year_uf
            except ValueError: pass
    if df is not None and not df.empty and 'ano' in df.columns and pd.notna(df['ano'].max()):
        try: 
            latest_year_general = int(df['ano'].max())
            print(f"DEBUG EXTRACT_YEAR: Ano mais recente geral '{latest_year_general}' extraído do DataFrame.")
            return latest_year_general
        except ValueError: pass
    print("DEBUG EXTRACT_YEAR: Nenhuma ano pôde ser extraído.")
    return None

def _extract_uf_from_query(
    query_uf_str: Optional[str], 
    prev_response_content: Optional[str] = None, 
    df: Optional[pd.DataFrame] = None,
    uf_context: Optional[str] = None 
) -> Optional[str]:
    print(f"DEBUG EXTRACT_UF: Inputs - query_uf_str: '{query_uf_str}', prev_response: {prev_response_content is not None}, df: {df is not None}")
    if df is None or df.empty:
        if query_uf_str and isinstance(query_uf_str, str) and len(query_uf_str) == 2 and query_uf_str.isalpha(): return query_uf_str.upper()
        return None
    map_estado_uf, known_ufs_set = {}, set()
    if 'estado' in df.columns and 'uf' in df.columns:
        df_estados_ufs = df[['estado', 'uf']].dropna().drop_duplicates()
        map_estado_uf = {str(r['estado']).strip().lower(): str(r['uf']).strip().upper() for _, r in df_estados_ufs.iterrows()}
        known_ufs_set = {str(uf_val).strip().upper() for uf_val in df['uf'].dropna().unique()}
    elif 'uf' in df.columns: known_ufs_set = {str(uf_val).strip().upper() for uf_val in df['uf'].dropna().unique()}
    else: 
        if query_uf_str and isinstance(query_uf_str, str) and len(query_uf_str) == 2 and query_uf_str.isalpha(): return query_uf_str.upper()
        return None
    if query_uf_str and isinstance(query_uf_str, str):
        uf_upper = query_uf_str.strip().upper()
        if uf_upper in known_ufs_set: return uf_upper
        if map_estado_uf and query_uf_str.strip().lower() in map_estado_uf: return map_estado_uf[query_uf_str.strip().lower()]
    if prev_response_content and isinstance(prev_response_content, str):
        prev_lower, prev_upper = prev_response_content.lower(), prev_response_content.upper()
        if map_estado_uf:
            for nome_estado_lower in sorted(map_estado_uf.keys(), key=len, reverse=True):
                if re.search(r'\b' + re.escape(nome_estado_lower) + r'\b', prev_lower): return map_estado_uf[nome_estado_lower]
        if known_ufs_set:
            for uf_sigla in known_ufs_set:
                if re.search(r'\b' + re.escape(uf_sigla) + r'\b', prev_upper): return uf_sigla
    print("DEBUG EXTRACT_UF: Nenhuma UF pôde ser extraída.")
    return None

def _get_relevant_expense_columns(data_df: pd.DataFrame, categoria_despesa_query: Optional[str] = None) -> Tuple[List[str], bool, Optional[str]]:
    available_df_columns = data_df.columns.tolist()
    base_expense_cols = {"saude": "despesa_saude", "educacao": "despesa_educacao", "educação": "despesa_educacao", "infraestrutura": "despesa_infraestrutura", "assistencia social": "despesa_assistencia_social", "assistência social": "despesa_assistencia_social"}
    valid_individual_cols = sorted(list(set(col for bm in base_expense_cols.values() for col in [bm] if col in available_df_columns)))
    is_total, cols_to_use, cat_usada = False, [], None
    if categoria_despesa_query:
        cat_lower = categoria_despesa_query.lower()
        if any(t in cat_lower for t in ["total", "geral", "todas", "combinado"]):
            is_total, cat_usada = True, "Total"
        else:
            for k, v_col in base_expense_cols.items():
                if k in cat_lower:
                    if v_col in available_df_columns: cols_to_use, cat_usada = [v_col], k.title(); break
                    else: 
                        print(f"DEBUG EXPENSE_COLS: Categoria '{k}' mapeia para '{v_col}' que não existe no DF.")
                        return [], False, None # Categoria especificada mas coluna não existe
            if not cols_to_use: 
                print(f"DEBUG EXPENSE_COLS: Categoria de despesa '{categoria_despesa_query}' não reconhecida.")
                return [], False, None
    else: 
        is_total, cat_usada = True, "Total"
    if is_total:
        if 'despesa_total_milhoes' in available_df_columns: 
            cols_to_use = ['despesa_total_milhoes']
            print(f"DEBUG EXPENSE_COLS: Usando coluna 'despesa_total_milhoes' para gasto total.")
        elif valid_individual_cols: 
            cols_to_use = valid_individual_cols
            print(f"DEBUG EXPENSE_COLS: Calculando gasto total somando: {cols_to_use}")
        else: 
            print("DEBUG EXPENSE_COLS: Não é possível determinar colunas para gasto total.")
            return [], True, "Total"
    if not cols_to_use: 
        print(f"DEBUG EXPENSE_COLS: Nenhuma coluna de despesa relevante encontrada para categoria '{categoria_despesa_query}'.")
        return [], False, cat_usada
    print(f"DEBUG EXPENSE_COLS: Colunas selecionadas: {cols_to_use}, IsTotal: {is_total}, CategoriaUsada: {cat_usada}")
    return cols_to_use, is_total, cat_usada

def _handle_idh_especifico(df: pd.DataFrame, uf: str, ano: int) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_ESPECIFICO: Tentando para UF='{uf}', Ano='{ano}'")
    if not uf or not ano: return None, None
    try:
        fd = df[(df['uf'].str.upper() == uf.upper()) & (df['ano'] == ano)]
        if not fd.empty and 'idh' in fd.columns and pd.notna(fd['idh'].iloc[0]):
            v = fd['idh'].iloc[0]
            return f"O IDH de {uf.upper()} em {ano} foi {v:.3f}.", {"tipo_cenario_factual": "idh_especifico", "uf_cenario": uf.upper(), "ano_cenario": ano, "valor_cenario": v}
        return f"Não encontrei dados de IDH para {uf.upper()} em {ano}.", {"tipo_cenario_factual": "idh_especifico_nao_encontrado", "uf_cenario": uf.upper(), "ano_cenario": ano}
    except Exception as e: 
        print(f"ERRO em _handle_idh_especifico para UF '{uf}', Ano '{ano}': {e}")
        return f"Ocorreu um erro ao buscar o IDH específico para {uf.upper()} em {ano}.", None

def _handle_idh_maior_brasil(df: pd.DataFrame, ano: Optional[int], user_query_lower: str) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_MAIOR_BRASIL: Tentando para Ano='{ano if ano else 'Mais Recente'}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)
    
    if df.empty or not all(c in df.columns for c in ['idh', 'uf', 'ano']): 
        return "Dados insuficientes para determinar o maior IDH.", None
    
    tmp_df = df.copy()
    ano_usado = ano
    msg_ano = f"em {ano}" if ano else "no ano mais recente disponível"

    if not ano_usado and pd.notna(tmp_df['ano'].max()):
        ano_usado = int(tmp_df['ano'].max())
        msg_ano = f"no ano mais recente ({ano_usado})"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df['idh'].isnull().all():
        return f"Não há dados de IDH válidos {msg_ano}.", {"tipo_cenario_factual": "idh_maior_brasil_sem_dados", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nlargest(top_n, 'idh')
        
        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) maior(es) IDH(s) no Brasil {msg_ano}.", {"tipo_cenario_factual": "idh_maior_brasil_nao_encontrado", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

        if top_n == 1:
            estado_maior_idh = top_estados_df.iloc[0]
            text_part = f"O estado com o maior IDH no Brasil {msg_ano} é {estado_maior_idh['uf']}, com {estado_maior_idh['idh']:.3f}."
            scenario_filters = {
                "tipo_cenario_factual": "idh_maior_brasil", 
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": [estado_maior_idh['uf']], # Lista para consistência
                "valor_cenario": [estado_maior_idh['idh']], # Lista para consistência
                "top_n_solicitado": top_n,
                "resultados_retornados": 1
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} ({row['idh']:.3f})")
            
            if not resultados_lista: # Segurança, embora nlargest deve retornar algo se tmp_df não for vazio
                 return f"Não foi possível encontrar o(s) maior(es) IDH(s) no Brasil {msg_ano}.", {"tipo_cenario_factual": "idh_maior_brasil_nao_encontrado", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

            text_part = f"Os {len(resultados_lista)} estado(s) com maior IDH no Brasil {msg_ano} são:\\n" + "\\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "idh_maior_brasil_top_n", 
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df['idh'].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e:
        print(f"ERRO em _handle_idh_maior_brasil para Ano '{ano_usado}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) maior(es) IDH(s) {msg_ano}.", None

def _handle_idh_menor_brasil(df: pd.DataFrame, ano: Optional[int], user_query_lower: str) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_MENOR_BRASIL: Tentando para Ano='{ano if ano else 'Mais Recente'}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    if df.empty or not all(c in df.columns for c in ['idh', 'uf', 'ano']): 
        return "Dados insuficientes para determinar o menor IDH.", None

    tmp_df = df.copy()
    ano_usado = ano
    msg_ano = f"em {ano}" if ano else "no ano mais recente disponível"

    if not ano_usado and pd.notna(tmp_df['ano'].max()):
        ano_usado = int(tmp_df['ano'].max())
        msg_ano = f"no ano mais recente ({ano_usado})"

    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]

    if tmp_df.empty or tmp_df['idh'].isnull().all():
        return f"Não há dados de IDH válidos {msg_ano}.", {"tipo_cenario_factual": "idh_menor_brasil_sem_dados", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nsmallest(top_n, 'idh')

        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) menor(es) IDH(s) no Brasil {msg_ano}.", {"tipo_cenario_factual": "idh_menor_brasil_nao_encontrado", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

        if top_n == 1:
            estado_menor_idh = top_estados_df.iloc[0]
            text_part = f"O estado com o menor IDH no Brasil {msg_ano} é {estado_menor_idh['uf']}, com {estado_menor_idh['idh']:.3f}."
            scenario_filters = {
                "tipo_cenario_factual": "idh_menor_brasil",
                "ano_cenario": ano_usado,
                "uf_cenario_resultado": [estado_menor_idh['uf']],
                "valor_cenario": [estado_menor_idh['idh']],
                "top_n_solicitado": top_n,
                "resultados_retornados": 1
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} ({row['idh']:.3f})")
            
            if not resultados_lista:
                 return f"Não foi possível encontrar o(s) menor(es) IDH(s) no Brasil {msg_ano}.", {"tipo_cenario_factual": "idh_menor_brasil_nao_encontrado", "ano_cenario": ano_usado, "top_n_solicitado": top_n}

            text_part = f"Os {len(resultados_lista)} estado(s) com menor IDH no Brasil {msg_ano} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "idh_menor_brasil_top_n",
                "ano_cenario": ano_usado,
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df['idh'].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e:
        print(f"ERRO em _handle_idh_menor_brasil para Ano '{ano_usado}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) menor(es) IDH(s) {msg_ano}.", None

def _handle_idh_maior_regiao(df: pd.DataFrame, reg: str, ano: Optional[int], user_query_lower: str) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_MAIOR_REGIAO: Reg='{reg}', Ano='{ano if ano else 'Recente'}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    if not reg:
        return "A região não foi especificada para a busca do maior IDH.", None
    if df.empty or not all(c in df.columns for c in ['idh', 'uf', 'ano', 'regiao']): 
        return "Dados insuficientes para determinar o maior IDH regional.", None

    tmp_df = df[df['regiao'].str.lower() == reg.lower()].copy()
    if tmp_df.empty:
        return f"Não foram encontrados dados para a região '{reg.title()}'.", {"tipo_cenario_factual": "idh_maior_regiao_sem_dados_regiao", "regiao_cenario": reg, "top_n_solicitado": top_n}

    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente na região"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado}) na região"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df['idh'].isnull().all():
        return f"Sem dados de IDH válidos para a região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_maior_regiao_sem_dados_ano", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nlargest(top_n, 'idh')
        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) maior(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_maior_regiao_nao_encontrado", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

        if top_n == 1:
            estado_maior_idh = top_estados_df.iloc[0]
            text_part = f"Na região {reg.title()}, o estado com o maior IDH {msg_ano_ctx.replace(' na região', '')} é {estado_maior_idh['uf']} ({estado_maior_idh['idh']:.3f})."
            scenario_filters = {
                "tipo_cenario_factual": "idh_maior_regiao", 
                "regiao_cenario": reg, 
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": [estado_maior_idh['uf']], 
                "valor_cenario": [estado_maior_idh['idh']],
                "top_n_solicitado": top_n,
                "resultados_retornados": 1
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} ({row['idh']:.3f})")
            
            if not resultados_lista:
                return f"Não foi possível encontrar o(s) maior(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_maior_regiao_nao_encontrado", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

            text_part = f"Os {len(resultados_lista)} estado(s) com maior IDH na região {reg.title()} {msg_ano_ctx.replace(' na região', '')} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "idh_maior_regiao_top_n", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df['idh'].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        return text_part, scenario_filters
    except Exception as e: 
        print(f"ERRO em _handle_idh_maior_regiao para Região '{reg}', Ano '{ano_usado}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) maior(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", None

def _handle_idh_menor_regiao(df: pd.DataFrame, reg: str, ano: Optional[int], user_query_lower: str) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_MENOR_REGIAO: Reg='{reg}', Ano='{ano if ano else 'Recente'}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    if not reg: 
        return "A região não foi especificada para a busca do menor IDH.", None
    if df.empty or not all(c in df.columns for c in ['idh', 'uf', 'ano', 'regiao']): 
        return "Dados insuficientes para determinar o menor IDH regional.", None

    tmp_df = df[df['regiao'].str.lower() == reg.lower()].copy()
    if tmp_df.empty: 
        return f"Não foram encontrados dados para a região '{reg.title()}'.", {"tipo_cenario_factual": "idh_menor_regiao_sem_dados_regiao", "regiao_cenario": reg, "top_n_solicitado": top_n}

    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente na região"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado}) na região"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df['idh'].isnull().all():
        return f"Sem dados de IDH válidos para a região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_menor_regiao_sem_dados_ano", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nsmallest(top_n, 'idh')
        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) menor(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_menor_regiao_nao_encontrado", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

        if top_n == 1:
            estado_menor_idh = top_estados_df.iloc[0]
            text_part = f"Na região {reg.title()}, o estado com o menor IDH {msg_ano_ctx.replace(' na região', '')} é {estado_menor_idh['uf']} ({estado_menor_idh['idh']:.3f})."
            scenario_filters = {
                "tipo_cenario_factual": "idh_menor_regiao", 
                "regiao_cenario": reg, 
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": [estado_menor_idh['uf']], 
                "valor_cenario": [estado_menor_idh['idh']],
                "top_n_solicitado": top_n,
                "resultados_retornados": 1
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} ({row['idh']:.3f})")
            
            if not resultados_lista:
                 return f"Não foi possível encontrar o(s) menor(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "idh_menor_regiao_nao_encontrado", "regiao_cenario":reg, "ano_cenario": ano_usado, "top_n_solicitado": top_n}

            text_part = f"Os {len(resultados_lista)} estado(s) com menor IDH na região {reg.title()} {msg_ano_ctx.replace(' na região', '')} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "idh_menor_regiao_top_n", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df['idh'].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        return text_part, scenario_filters
    except Exception as e: 
        print(f"ERRO em _handle_idh_menor_regiao para Região '{reg}', Ano '{ano_usado}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) menor(es) IDH(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", None

def _handle_idh_medio_brasil(df: pd.DataFrame, ano: Optional[int]) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG IDH_MEDIO_BRASIL: Ano='{ano if ano else 'Recente'}'")
    if df.empty or not all(c in df.columns for c in ['idh', 'ano']): return "Dados insuficientes.", None
    tmp, ano_u, msg_ano_ctx = df.copy(), ano, f"em {ano}" if ano else "no ano mais recente disponível"
    if not ano and pd.notna(tmp['ano'].max()): 
        ano_u = int(tmp['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_u})"
    if ano_u: tmp = tmp[tmp['ano'] == ano_u]
    if tmp.empty or tmp['idh'].isnull().all(): return f"Não há dados de IDH válidos {msg_ano_ctx} para calcular a média.", {"tipo_cenario_factual": "idh_medio_brasil_sem_dados", "ano_cenario": ano_u}
    try:
        media = tmp['idh'].mean()
        return f"O IDH médio no Brasil {msg_ano_ctx} foi {media:.3f}.", {"tipo_cenario_factual": "idh_medio_brasil", "ano_cenario": ano_u, "valor_cenario": media}
    except Exception as e: 
        print(f"ERRO em _handle_idh_medio_brasil para Ano '{ano_u}': {e}")
        return f"Ocorreu um erro ao tentar calcular o IDH médio {msg_ano_ctx}.", None

def _handle_gasto_especifico_uf_ano(df: pd.DataFrame, uf: str, ano: int, cat_gasto: Optional[str]=None) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG GASTO_ESPECIFICO: UF='{uf}', Ano='{ano}', Categoria='{cat_gasto}'")
    if not uf or not ano: return "UF ou Ano não fornecidos.", None
    cols, _, cat_nome = _get_relevant_expense_columns(df, cat_gasto)
    if not cols: return f"Colunas de despesa não identificadas para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_especifico_col_nao_encontrada", "uf_cenario": uf, "ano_cenario": ano, "categoria_tentada": cat_gasto}
    try:
        fd = df[(df['uf'].str.upper() == uf.upper()) & (df['ano'] == ano)].copy()
        if fd.empty: return f"Não há dados para {uf.upper()} em {ano}.", {"tipo_cenario_factual": "gasto_especifico_sem_dados_uf_ano", "uf_cenario": uf, "ano_cenario": ano, "categoria_usada": cat_nome}
        for c in cols: 
            if c not in fd.columns: return f"Coluna de despesa '{c}' não encontrada para {uf.upper()} em {ano}.", None
            fd[c] = pd.to_numeric(fd[c], errors='coerce')
        val = fd[cols[0]].iloc[0] if len(cols) == 1 else fd[cols].sum(axis=1).iloc[0]
        if pd.notna(val):
            nome_exib = cat_nome if cat_nome and cat_nome != "Total" else "total"
            if cat_nome == "Total": nome_exib = "total"
            else: nome_exib = f"em {cat_nome.lower() if cat_nome else 'gastos'}"
            return f"O gasto {nome_exib} de {uf.upper()} em {ano} foi R$ {val:.2f} milhões.", {"tipo_cenario_factual": "gasto_especifico", "uf_cenario": uf.upper(), "ano_cenario": ano, "categoria_cenario": cat_nome if cat_nome else "Total", "valor_cenario": val}
        return f"Valor de gasto para {uf.upper()} em {ano} (categoria: {cat_nome if cat_nome else 'Total'}) não disponível ou inválido.", {"tipo_cenario_factual": "gasto_especifico_valor_na", "uf_cenario": uf, "ano_cenario": ano, "categoria_usada": cat_nome}
    except Exception as e: 
        print(f"ERRO em _handle_gasto_especifico_uf_ano para UF '{uf}', Ano '{ano}', Categoria '{cat_gasto}': {e}")
        return f"Ocorreu um erro ao buscar o gasto específico.", None

def _handle_gasto_maior_brasil(df: pd.DataFrame, ano: Optional[int], user_query_lower: str, cat_gasto: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG GASTO_MAIOR_BRASIL: Ano='{ano if ano else 'Recente'}', Cat='{cat_gasto}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    cols, _, cat_nome = _get_relevant_expense_columns(df, cat_gasto)
    if not cols: 
        return f"Colunas de despesa não identificadas para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_maior_brasil_col_nao_encontrada", "categoria_tentada": cat_gasto, "top_n_solicitado": top_n}
    
    tmp_df = df.copy()
    for c in cols: 
        if c not in tmp_df.columns: 
            return f"Coluna de despesa '{c}' não encontrada no DataFrame.", None
        tmp_df[c] = pd.to_numeric(tmp_df[c], errors='coerce').fillna(0) # Para nlargest, NaN vira 0
    
    g_col = "__gasto_temp_sum"
    tmp_df[g_col] = tmp_df[cols[0]] if len(cols) == 1 else tmp_df[cols].sum(axis=1)
    
    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado})"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df[g_col].isnull().all() or (tmp_df[g_col] <= 0).all(): # Maior gasto deve ser > 0
        return f"Sem dados de gasto válidos (maiores que zero) {msg_ano_ctx} para '{cat_nome if cat_nome else 'Total'}' para determinar o maior.", {"tipo_cenario_factual": "gasto_maior_brasil_sem_dados_positivo", "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nlargest(top_n, g_col)
        top_estados_df = top_estados_df[top_estados_df[g_col] > 0] # Garantir que só retornamos gastos positivos

        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) maior(es) gasto(s) (com valor positivo) no Brasil {msg_ano_ctx} para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_maior_brasil_nao_encontrado_positivo", "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

        nome_exib_gasto = cat_nome if cat_nome and cat_nome != "Total" else "público total"

        if len(top_estados_df) == 1: # Se top_n era 1, ou só 1 resultado positivo
            estado_maior_gasto = top_estados_df.iloc[0]
            text_part = f"O estado com o maior gasto {nome_exib_gasto} {msg_ano_ctx} é {estado_maior_gasto['uf']}, com R$ {estado_maior_gasto[g_col]:.2f} milhões."
            scenario_filters = {
                "tipo_cenario_factual": "gasto_maior_brasil", 
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total", 
                "uf_cenario_resultado": [estado_maior_gasto['uf']], 
                "valor_cenario": [estado_maior_gasto[g_col]],
                "top_n_solicitado": top_n,
                "resultados_retornados": len(top_estados_df)
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} (R$ {row[g_col]:.2f} milhões)")
            
            text_part = f"Os {len(resultados_lista)} estado(s) com maior gasto {nome_exib_gasto} {msg_ano_ctx} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "gasto_maior_brasil_top_n", 
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total",
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df[g_col].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e: 
        print(f"ERRO em _handle_gasto_maior_brasil para Ano '{ano_usado}', Cat '{cat_nome}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) maior(es) gasto(s) {msg_ano_ctx}.", None

def _handle_gasto_menor_brasil(df: pd.DataFrame, ano: Optional[int], user_query_lower: str, cat_gasto: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG GASTO_MENOR_BRASIL: Ano='{ano if ano else 'Recente'}', Cat='{cat_gasto}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    cols, _, cat_nome = _get_relevant_expense_columns(df, cat_gasto)
    if not cols: 
        return f"Colunas de despesa não identificadas para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_menor_brasil_col_nao_encontrada", "categoria_tentada": cat_gasto, "top_n_solicitado": top_n}
    
    tmp_df = df.copy()
    for c in cols: 
        if c not in tmp_df.columns: 
            return f"Coluna de despesa '{c}' não encontrada.", None
        tmp_df[c] = pd.to_numeric(tmp_df[c], errors='coerce') # NaNs serão propagados na soma
    
    g_col = "__gasto_temp_sum"
    if len(cols) == 1:
        tmp_df[g_col] = tmp_df[cols[0]]
    else:
        # Para a soma, se algum componente for NaN, a soma será NaN.
        tmp_df[g_col] = tmp_df[cols].sum(axis=1, min_count=1) # min_count=1 significa que se todos forem NaN, o resultado é NaN, senão soma os não-NaN.

    # Para nsmallest, NaNs devem ser tratados como "maior que tudo"
    tmp_df[g_col] = tmp_df[g_col].fillna(float('inf'))
    
    # Filtrar explicitamente os que são infinitos para não pegá-los como "menores"
    tmp_df = tmp_df[tmp_df[g_col] != float('inf')]

    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado})"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df[g_col].isnull().all() or (tmp_df[g_col] == float('inf')).all():
        return f"Sem dados de gasto válidos {msg_ano_ctx} para '{cat_nome if cat_nome else 'Total'}' para determinar o menor.", {"tipo_cenario_factual": "gasto_menor_brasil_sem_dados", "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nsmallest(top_n, g_col)

        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) menor(es) gasto(s) no Brasil {msg_ano_ctx} para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_menor_brasil_nao_encontrado", "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

        nome_exib_gasto = cat_nome if cat_nome and cat_nome != "Total" else "público total"

        if top_n == 1:
            estado_menor_gasto = top_estados_df.iloc[0]
            text_part = f"O estado com o menor gasto {nome_exib_gasto} {msg_ano_ctx} é {estado_menor_gasto['uf']}, com R$ {estado_menor_gasto[g_col]:.2f} milhões."
            scenario_filters = {
                "tipo_cenario_factual": "gasto_menor_brasil", 
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total", 
                "uf_cenario_resultado": [estado_menor_gasto['uf']], 
                "valor_cenario": [estado_menor_gasto[g_col]],
                "top_n_solicitado": top_n,
                "resultados_retornados": 1
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} (R$ {row[g_col]:.2f} milhões)")
            
            if not resultados_lista:
                 return f"Não foi possível encontrar o(s) menor(es) gasto(s) no Brasil {msg_ano_ctx} para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_menor_brasil_nao_encontrado", "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

            text_part = f"Os {len(resultados_lista)} estado(s) com menor gasto {nome_exib_gasto} {msg_ano_ctx} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "gasto_menor_brasil_top_n", 
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total",
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df[g_col].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e: 
        print(f"ERRO em _handle_gasto_menor_brasil para Ano '{ano_usado}', Categoria '{cat_nome}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) menor(es) gasto(s) {msg_ano_ctx}.", None

def _handle_gasto_maior_regiao(df: pd.DataFrame, reg: str, ano: Optional[int], user_query_lower: str, cat_gasto: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG GASTO_MAIOR_REGIAO: Reg='{reg}', Ano='{ano if ano else 'Recente'}', Cat='{cat_gasto}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    if not reg: 
        return "A região não foi especificada para a busca do maior gasto.", None
    
    cols, _, cat_nome = _get_relevant_expense_columns(df, cat_gasto)
    if not cols: 
        return f"Colunas de despesa não identificadas para '{cat_nome if cat_nome else 'Total'}' na região '{reg.title()}'.", {"tipo_cenario_factual": "gasto_maior_regiao_col_nao_encontrada", "regiao_cenario":reg, "categoria_tentada": cat_gasto, "top_n_solicitado": top_n}
    
    tmp_df = df[df['regiao'].str.lower() == reg.lower()].copy()
    if tmp_df.empty: 
        return f"Não foram encontrados dados para a região '{reg.title()}'.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_dados_regiao", "regiao_cenario": reg, "top_n_solicitado": top_n}

    for c in cols: 
        if c not in tmp_df.columns: 
            return f"Coluna de despesa '{c}' não encontrada para a região '{reg.title()}'.", None # Erro interno, não deveria acontecer se _get_relevant_expense_columns e o dataset estão ok
        tmp_df[c] = pd.to_numeric(tmp_df[c], errors='coerce').fillna(0) # Para nlargest, NaN vira 0 e não afeta a soma negativamente
    
    g_col = "__gasto_temp_sum"
    tmp_df[g_col] = tmp_df[cols[0]] if len(cols) == 1 else tmp_df[cols].sum(axis=1)
    
    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente na região"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado}) na região"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    # Verifica se, após filtros, há dados com gasto > 0 para processar
    if tmp_df.empty or tmp_df[g_col].isnull().all() or (tmp_df[g_col] <= 0).all(): 
        return f"Sem dados de gasto válidos (maiores que zero) para '{cat_nome if cat_nome else 'Total'}' na região '{reg.title()}' {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "gasto_maior_regiao_sem_dados_ano", "regiao_cenario":reg, "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nlargest(top_n, g_col)
        
        # Filtrar resultados com gasto zero ou negativo, se houver, pois não são "maiores gastos" significativos
        top_estados_df = top_estados_df[top_estados_df[g_col] > 0]

        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) maior(es) gasto(s) (com valor positivo) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')} para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_maior_regiao_nao_encontrado_positivo", "regiao_cenario":reg, "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

        nome_exib_gasto = cat_nome if cat_nome and cat_nome != "Total" else "público total"
        msg_final_ano = msg_ano_ctx.replace(' na região', '')

        if len(top_estados_df) == 1: # Se top_n era 1, ou se apenas 1 resultado positivo foi encontrado
            estado_maior_gasto = top_estados_df.iloc[0]
            text_part = f"Na região {reg.title()}, o estado com o maior gasto {nome_exib_gasto} {msg_final_ano} é {estado_maior_gasto['uf']}, com R$ {estado_maior_gasto[g_col]:.2f} milhões."
            scenario_filters = {
                "tipo_cenario_factual": "gasto_maior_regiao", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total", 
                "uf_cenario_resultado": [estado_maior_gasto['uf']], 
                "valor_cenario": [estado_maior_gasto[g_col]],
                "top_n_solicitado": top_n, # O N que o usuário pediu
                "resultados_retornados": len(top_estados_df) # Quantos realmente retornamos
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} (R$ {row[g_col]:.2f} milhões)")
            
            text_part = f"Os {len(resultados_lista)} estado(s) com maior gasto {nome_exib_gasto} na região {reg.title()} {msg_final_ano} são:\\n" + "\\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "gasto_maior_regiao_top_n", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total",
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df[g_col].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e: 
        print(f"ERRO em _handle_gasto_maior_regiao para Reg '{reg}', Ano '{ano_usado}', Cat '{cat_nome}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) maior(es) gasto(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", None

def _handle_gasto_menor_regiao(df: pd.DataFrame, reg: str, ano: Optional[int], user_query_lower: str, cat_gasto: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict]]:
    print(f"DEBUG GASTO_MENOR_REGIAO: Reg='{reg}', Ano='{ano if ano else 'Recente'}', Cat='{cat_gasto}', Query='{user_query_lower}'")
    top_n = _extract_top_n(user_query_lower, default_n=1)

    if not reg: 
        return "A região não foi especificada para a busca do menor gasto.", None

    cols, _, cat_nome = _get_relevant_expense_columns(df, cat_gasto)
    if not cols: 
        return f"Colunas de despesa não identificadas para '{cat_nome if cat_nome else 'Total'}' na região '{reg.title()}'.", {"tipo_cenario_factual": "gasto_menor_regiao_col_nao_encontrada", "regiao_cenario":reg, "categoria_tentada": cat_gasto, "top_n_solicitado": top_n}
    
    tmp_df = df[df['regiao'].str.lower() == reg.lower()].copy()
    if tmp_df.empty: 
        return f"Não foram encontrados dados para a região '{reg.title()}'.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_dados_regiao", "regiao_cenario": reg, "top_n_solicitado": top_n}

    for c in cols: 
        if c not in tmp_df.columns: 
            return f"Coluna de despesa '{c}' não encontrada para a região '{reg.title()}'.", None
        tmp_df[c] = pd.to_numeric(tmp_df[c], errors='coerce') # NaNs propagarão
    
    g_col = "__gasto_temp_sum"
    if len(cols) == 1:
        tmp_df[g_col] = tmp_df[cols[0]]
    else:
        tmp_df[g_col] = tmp_df[cols].sum(axis=1, min_count=1) # min_count=1 para permitir NaNs se nem todos os componentes são NaN

    tmp_df[g_col] = tmp_df[g_col].fillna(float('inf')) # Tratar NaNs como infinito para nsmallest
    tmp_df = tmp_df[tmp_df[g_col] != float('inf')] # Remover gastos efetivamente infinitos

    ano_usado = ano
    msg_ano_ctx = f"em {ano}" if ano else "no ano mais recente na região"
    if not ano_usado and pd.notna(tmp_df['ano'].max()): 
        ano_usado = int(tmp_df['ano'].max())
        msg_ano_ctx = f"no ano mais recente ({ano_usado}) na região"
    
    if ano_usado:
        tmp_df = tmp_df[tmp_df['ano'] == ano_usado]
    
    if tmp_df.empty or tmp_df[g_col].isnull().all() or (tmp_df[g_col] == float('inf')).all(): 
        return f"Sem dados de gasto válidos para '{cat_nome if cat_nome else 'Total'}' na região '{reg.title()}' {msg_ano_ctx.replace(' na região', '')}.", {"tipo_cenario_factual": "gasto_menor_regiao_sem_dados_ano", "regiao_cenario":reg, "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

    try:
        top_estados_df = tmp_df.nsmallest(top_n, g_col)
        
        # Para menor gasto, não filtramos por > 0, pois 0 ou negativo pode ser um menor gasto válido.
        if top_estados_df.empty:
            return f"Não foi possível encontrar o(s) menor(es) gasto(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')} para '{cat_nome if cat_nome else 'Total'}'.", {"tipo_cenario_factual": "gasto_menor_regiao_nao_encontrado", "regiao_cenario":reg, "ano_cenario": ano_usado, "categoria_usada": cat_nome, "top_n_solicitado": top_n}

        nome_exib_gasto = cat_nome if cat_nome and cat_nome != "Total" else "público total"
        msg_final_ano = msg_ano_ctx.replace(' na região', '')

        if len(top_estados_df) == 1:
            estado_menor_gasto = top_estados_df.iloc[0]
            text_part = f"Na região {reg.title()}, o estado com o menor gasto {nome_exib_gasto} {msg_final_ano} é {estado_menor_gasto['uf']}, com R$ {estado_menor_gasto[g_col]:.2f} milhões."
            scenario_filters = {
                "tipo_cenario_factual": "gasto_menor_regiao", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total", 
                "uf_cenario_resultado": [estado_menor_gasto['uf']], 
                "valor_cenario": [estado_menor_gasto[g_col]],
                "top_n_solicitado": top_n,
                "resultados_retornados": len(top_estados_df)
            }
        else:
            resultados_lista = []
            for index, row in top_estados_df.iterrows():
                resultados_lista.append(f"{len(resultados_lista) + 1}. {row['uf']} (R$ {row[g_col]:.2f} milhões)")
            
            text_part = f"Os {len(resultados_lista)} estado(s) com menor gasto {nome_exib_gasto} na região {reg.title()} {msg_final_ano} são:\n" + "\n".join(resultados_lista)
            scenario_filters = {
                "tipo_cenario_factual": "gasto_menor_regiao_top_n", 
                "regiao_cenario": reg,
                "ano_cenario": ano_usado, 
                "categoria_cenario": cat_nome if cat_nome else "Total",
                "uf_cenario_resultado": top_estados_df['uf'].tolist(),
                "valor_cenario": top_estados_df[g_col].tolist(),
                "top_n_solicitado": top_n,
                "resultados_retornados": len(resultados_lista)
            }
        
        return text_part, scenario_filters

    except Exception as e: 
        print(f"ERRO em _handle_gasto_menor_regiao para Reg '{reg}', Ano '{ano_usado}', Cat '{cat_nome}', TopN {top_n}: {e}")
        return f"Ocorreu um erro ao tentar encontrar o(s) menor(es) gasto(s) na região {reg.title()} {msg_ano_ctx.replace(' na região', '')}.", None

def handle_factual_scenarios(user_query_lower: str, final_intent_for_scenarios: Optional[str], filters_from_llm: Dict, data_df: pd.DataFrame, conversation_history: List[Dict]) -> Tuple[Optional[str], Optional[Dict]]:
    text_part: Optional[str] = None
    updated_filters: Dict = filters_from_llm.copy()
    scenario_filters: Optional[Dict] = None 
    prev_response_content: Optional[str] = None
    if len(conversation_history) >= 2 and conversation_history[-2]["role"] == "assistant":
        prev_response_content = conversation_history[-2]["content"]
    
    ex_uf = _extract_uf_from_query(filters_from_llm.get('uf'), prev_response_content, data_df)
    ex_ano = _extract_year_from_query(filters_from_llm.get('ano'), prev_response_content, data_df, uf_context=ex_uf)
    ex_reg = filters_from_llm.get('regiao') 
    ex_cat_gasto = filters_from_llm.get('categoria_despesa')

    # Usar chaves diferentes como uf_final, ano_final para evitar colisões se os filtros do LLM forem usados diretamente em outro lugar
    if ex_uf: updated_filters['uf_final'] = ex_uf
    if ex_ano: updated_filters['ano_final'] = ex_ano
    if ex_reg: updated_filters['regiao_final'] = ex_reg
    if ex_cat_gasto: updated_filters['categoria_despesa_final'] = ex_cat_gasto
    
    uf_h, ano_h, reg_h, cat_g_h = updated_filters.get('uf_final'), updated_filters.get('ano_final'), updated_filters.get('regiao_final'), updated_filters.get('categoria_despesa_final')
    
    print(f"DEBUG SCENARIO_HANDLER: Intent: '{final_intent_for_scenarios}', UF_h: '{uf_h}', Ano_h: '{ano_h}', Reg_h: '{reg_h}', CatG_h: '{cat_g_h}', Query: '{user_query_lower}'")

    intent_map = {
        "idh_especifico": (_handle_idh_especifico, [data_df, uf_h, ano_h], lambda: uf_h and ano_h),
        "idh_maior_brasil": (_handle_idh_maior_brasil, [data_df, ano_h, user_query_lower], lambda: not filters_from_llm.get('uf') and not filters_from_llm.get('regiao')),
        "idh_menor_brasil": (_handle_idh_menor_brasil, [data_df, ano_h, user_query_lower], lambda: not filters_from_llm.get('uf') and not filters_from_llm.get('regiao')),
        "idh_maior_regiao": (_handle_idh_maior_regiao, [data_df, reg_h, ano_h, user_query_lower], lambda: filters_from_llm.get('regiao') and not filters_from_llm.get('uf')),
        "idh_menor_regiao": (_handle_idh_menor_regiao, [data_df, reg_h, ano_h, user_query_lower], lambda: filters_from_llm.get('regiao') and not filters_from_llm.get('uf')),
        "idh_medio_brasil": (_handle_idh_medio_brasil, [data_df, ano_h], lambda: not filters_from_llm.get('uf') and not filters_from_llm.get('regiao')),
        "gasto_especifico": (_handle_gasto_especifico_uf_ano, [data_df, uf_h, ano_h, cat_g_h], lambda: uf_h and ano_h),
        "gasto_maior_brasil": (_handle_gasto_maior_brasil, [data_df, ano_h, user_query_lower, cat_g_h], lambda: not filters_from_llm.get('uf') and not filters_from_llm.get('regiao')),
        "gasto_menor_brasil": (_handle_gasto_menor_brasil, [data_df, ano_h, user_query_lower, cat_g_h], lambda: not filters_from_llm.get('uf') and not filters_from_llm.get('regiao')), 
        "gasto_maior_regiao": (_handle_gasto_maior_regiao, [data_df, reg_h, ano_h, user_query_lower, cat_g_h], lambda: filters_from_llm.get('regiao') and not filters_from_llm.get('uf')), 
        "gasto_menor_regiao": (_handle_gasto_menor_regiao, [data_df, reg_h, ano_h, user_query_lower, cat_g_h], lambda: filters_from_llm.get('regiao') and not filters_from_llm.get('uf')), 
    }

    if final_intent_for_scenarios in intent_map:
        handler_func, params_template, condition_func = intent_map[final_intent_for_scenarios]
        
        actual_params = list(params_template) # Cria cópia para modificar
        num_defaults = len(handler_func.__defaults__) if handler_func.__defaults__ else 0
        num_required_params = handler_func.__code__.co_argcount - num_defaults

        # Não é mais necessário remover Nones da cauda com assinaturas corretas
        # while len(actual_params) > num_required_params and actual_params[-1] is None:
        #     actual_params.pop()

        if condition_func():
            required_params_present = True
            # Verifica se todos os parâmetros *requeridos pela assinatura da função*
            # (aqueles sem valor default) estão presentes e não são None na lista de parâmetros construída.
            for i in range(num_required_params):
                if i >= len(actual_params) or actual_params[i] is None:
                    # Exceção: para handlers de IDH (não de gasto) que recebem ano como Optional[int]
                    # (sem default, mas logicamente opcional porque o handler pode usar o mais recente se None),
                    # não devemos falhar aqui se ano_h for None. O handler interno cuida disso.
                    # Esta lógica específica pode precisar de refinamento se houver mais casos assim.
                    is_idh_handler_ano_optional = "idh" in handler_func.__name__ and handler_func.__code__.co_varnames[i] == "ano"
                    if not is_idh_handler_ano_optional:
                        required_params_present = False
                        break
            
            if required_params_present:
                print(f"DEBUG SCENARIO_HANDLER: Chamando handler '{handler_func.__name__}' com params: {actual_params}")
                text_part, scenario_filters = handler_func(*actual_params)
            else:
                print(f"DEBUG SCENARIO_HANDLER: Handler '{handler_func.__name__}' skipped, nem todos os params requeridos presentes. Estado dos params: {actual_params[:num_required_params]}")
        else:
            print(f"DEBUG SCENARIO_HANDLER: Condição para '{final_intent_for_scenarios}' não atendida.")

    if text_part and scenario_filters:
        updated_filters.update(scenario_filters) 
        print(f"DEBUG SCENARIO_HANDLER: Cenário tratado! Texto: '{text_part}', Filtros atualizados: {updated_filters}")
        return text_part, updated_filters
    
    print(f"DEBUG SCENARIO_HANDLER: Nenhum cenário factual específico tratado ou handler não produziu texto.")
    return None, None
# Fim das funções copiadas

if __name__ == '__main__':
    # Adicionar o diretório 'src' ao sys.path para permitir importações relativas
    # ao executar este script diretamente para teste.
    import sys
    from pathlib import Path
    SCRIPT_DIR = Path(__file__).resolve().parent
    SRC_DIR = SCRIPT_DIR.parent # Deveria ser o diretório src/
    PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    if str(PROJECT_ROOT) not in sys.path: # Adicionar também a raiz do projeto pode ajudar
        sys.path.insert(0, str(PROJECT_ROOT))

    try:
        print("Testando LLMQueryHandler...")
        # Você pode fornecer uma descrição do schema mais detalhada se quiser
        handler = LLMQueryHandler()
        print("Handler inicializado.")

        print("\n--- Teste 1: Pergunta com filtro de ano e UF ---")
        query1 = "Qual foi o IDH do Ceará em 2020?"
        print(f"Usuário: {query1}")
        text_resp1, filters1 = handler.get_response(query1)
        print(f"LLM (texto): {text_resp1}")
        print(f"LLM (filtros): {filters1}")

        print("\n--- Teste 2: Pergunta mais geral sobre categoria ---")
        query2 = "Qual a correlação entre gastos com educação e o IDH na região nordeste?"
        print(f"Usuário: {query2}")
        text_resp2, filters2 = handler.get_response(query2)
        print(f"LLM (texto): {text_resp2}")
        print(f"LLM (filtros): {filters2}")
        
        print("\n--- Teste 3: Pergunta sem filtros claros ---")
        query3 = "Me fale sobre o IDH no Brasil."
        print(f"Usuário: {query3}")
        text_resp3, filters3 = handler.get_response(query3)
        print(f"LLM (texto): {text_resp3}")
        print(f"LLM (filtros): {filters3}")

        print("\n--- Histórico da Conversa ---")
        for entry in handler.conversation_history:
            print(f"- {entry['role']}: {entry['content']}")

    except Exception as e_test:
        print(f"Erro no teste: {e_test}")
        import traceback
        traceback.print_exc()

"""
# TODO:
# 1. Implementar uma forma mais robusta de obter o schema do dataset (ler colunas do CSV/BD).
# 2. Refinar a extração de JSON da resposta do LLM. Pode ser útil instruir o LLM
#    a colocar o JSON de filtros em uma linha separada ou com marcadores específicos.
# 3. Adicionar mais tratamento de erros e logging.
# 4. Considerar limites de tokens para o histórico da conversa para evitar custos excessivos
#    ou erros de API (context window).
""" 