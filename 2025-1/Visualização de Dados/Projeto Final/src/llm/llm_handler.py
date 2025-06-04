"""
Módulo para lidar com a interação com o Large Language Model (LLM).
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import json # Para carregar e analisar JSON da resposta do LLM

class LLMQueryHandler:
    def __init__(self, dataset_schema_description: str = None):
        """
        Inicializa o handler do LLM.

        Args:
            dataset_schema_description (str, optional): Uma descrição textual
                do esquema do dataset principal para fornecer contexto ao LLM.
        """
        load_dotenv(dotenv_path=self.find_dotenv())
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Chave da API da OpenAI não encontrada. "
                             "Verifique seu arquivo .env e a variável OPENAI_API_KEY.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini" # Modelo a ser usado
        self.conversation_history = []
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

            O esquema principal dos dados com os quais você vai trabalhar é (simplificado):
            {self.dataset_schema}

            Exemplo de resposta com filtros:
            Pergunta do usuário: Qual o IDH de São Paulo em 2021?
            Sua Resposta: O IDH de São Paulo em 2021 foi X. {{"filtros_identificados": {{"ano": 2021, "uf": "SP"}}}}

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

        Args:
            user_query (str): A pergunta do usuário.

        Returns:
            tuple[str, dict]: (resposta_textual, filtros_identificados_dict)
                              Retorna uma tupla contendo a resposta textual do LLM
                              e um dicionário com os filtros identificados.
                              O dicionário de filtros pode ser vazio se nenhum filtro for encontrado.
        """
        self.add_user_message(user_query)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=0.2, # Baixa temperatura para respostas mais factuais e menos criativas
                # max_tokens=300 # Limitar o tamanho da resposta se necessário
            )
            
            assistant_response_content = response.choices[0].message.content

            text_part = assistant_response_content
            filters_identified = {}

            # Tentativa mais robusta de extrair o JSON de filtros da resposta
            # Espera-se que o LLM coloque o JSON com a chave "filtros_identificados" no final.
            json_marker = '{"filtros_identificados":'
            marker_start_index = assistant_response_content.rfind(json_marker)

            if marker_start_index != -1:
                # Tentar pegar a substring a partir do marcador até o final
                potential_json_block = assistant_response_content[marker_start_index:]
                # O JSON deve ser um objeto, então precisa terminar com '}'
                # Precisamos encontrar o fechamento correto do objeto JSON principal
                open_braces = 0
                json_end_index = -1
                for i, char in enumerate(potential_json_block):
                    if char == '{':
                        open_braces += 1
                    elif char == '}':
                        open_braces -= 1
                        if open_braces == 0:
                            json_end_index = i + marker_start_index # índice na string original
                            break
                
                if json_end_index != -1:
                    actual_json_str = assistant_response_content[marker_start_index : json_end_index + 1]
                    try:
                        parsed_json_outer = json.loads(actual_json_str)
                        if 'filtros_identificados' in parsed_json_outer:
                            filters_identified = parsed_json_outer.get('filtros_identificados', {})
                            text_part = assistant_response_content[:marker_start_index].strip()
                        else:
                            # Marcador encontrado, mas não a chave esperada dentro do JSON
                            pass # Mantém text_part como a resposta completa
                    except json.JSONDecodeError:
                        # String não era um JSON válido após o marcador
                        pass # Mantém text_part como a resposta completa
            
            self.add_assistant_message(assistant_response_content) # Salva a resposta completa no histórico
            return text_part, filters_identified

        except Exception as e:
            print(f"❌ Erro ao chamar a API da OpenAI: {e}")
            # Em caso de erro, podemos retornar uma mensagem padrão e nenhum filtro.
            return "Desculpe, não consegui processar sua pergunta no momento.", {}

    def reset_conversation(self):
        """Limpa o histórico da conversa, mantendo a mensagem do sistema."""
        system_message = None
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_message = self.conversation_history[0]
        
        self.conversation_history = []
        if system_message:
            self.conversation_history.append(system_message)

# Exemplo de uso (para teste rápido, remover ou comentar depois)
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