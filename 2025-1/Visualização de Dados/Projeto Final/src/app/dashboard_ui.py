import customtkinter as ctk
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from pathlib import Path
import seaborn as sns

# Adicionar import do LLMQueryHandler e ajustar sys.path se necessário para execução direta do dashboard
import sys
SCRIPT_DIR_FOR_LLM = Path(__file__).resolve().parent # src/app
SRC_DIR_FOR_LLM = SCRIPT_DIR_FOR_LLM.parent # src/
if str(SRC_DIR_FOR_LLM) not in sys.path:
    sys.path.insert(0, str(SRC_DIR_FOR_LLM))
from llm.llm_handler import LLMQueryHandler

# Definição de caminhos relativos à raiz do projeto
SCRIPT_DIR = Path(__file__).parent # src/app
SRC_DIR = SCRIPT_DIR.parent # src/
PROJECT_ROOT = SRC_DIR.parent # Raiz do projeto

# Constantes de Caminho (ajustadas)
DATABASE_URL = PROJECT_ROOT / "data" / "processed" / "projeto_visualizacao.db"
SHAPEFILE_PATH = PROJECT_ROOT / "data" / "geospatial" / "BR_UF_2024.shp"
DATASET_UNIFICADO_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_unificado.csv"

# Configurações do CustomTkinter
ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dashboard IDH e Despesas Públicas Federais no Brasil")
        self.geometry("1200x800")

        self.data_df = None
        self.geo_data_df = None
        self.merged_df = None

        # Inicializar LLM Handler
        try:
            self.llm_handler = LLMQueryHandler()
            print("✔️ LLM Handler inicializado com sucesso.")
        except Exception as e_llm_init:
            self.llm_handler = None
            print(f"❌ Erro ao inicializar LLM Handler: {e_llm_init}")
            # Opcional: Mostrar um aviso na UI se o LLM falhar na inicialização

        self.load_data()
        self.create_widgets()

    def load_data(self):
        print("🔄 Carregando dados...")
        try:
            # Carregar dados do CSV (fallback caso o BD falhe)
            if DATASET_UNIFICADO_PATH.exists():
                self.data_df = pd.read_csv(DATASET_UNIFICADO_PATH)
                print(f"✔️ Dados carregados de {DATASET_UNIFICADO_PATH}: {self.data_df.shape[0]} linhas.")
            else:
                print(f"⚠️  Arquivo {DATASET_UNIFICADO_PATH} não encontrado. Tentando carregar do banco de dados.")
                # Ajuste para chamar o método _load_data_from_db corretamente
                self.data_df = self._load_data_from_db(DATABASE_URL) # Passar DATABASE_URL explicitamente

            if self.data_df is None or self.data_df.empty:
                print("❌ ERRO FATAL: Não foi possível carregar os dados da análise unificada.")
                return

            colunas_despesas = [
                'despesa_assistencia_social', 'despesa_educacao', 
                'despesa_infraestrutura', 'despesa_saude'
            ]
            colunas_despesas_existentes = [col for col in colunas_despesas if col in self.data_df.columns]
            print(f"ℹ️ Colunas de despesas encontradas para cálculo do Gasto Total: {colunas_despesas_existentes}")

            if not colunas_despesas_existentes:
                print("⚠️ Nenhuma coluna de despesa encontrada para calcular o Gasto Total. 'Gasto Total Normalizado' não será criado.")
            elif 'populacao' not in self.data_df.columns:
                print("⚠️ Coluna 'populacao' não encontrada. Não é possível calcular 'Gasto Total Normalizado'.")
            else:
                self.data_df['Gasto Total'] = self.data_df[colunas_despesas_existentes].sum(axis=1)
                self.data_df['Gasto Total Normalizado'] = self.data_df.apply(
                    lambda row: (row['Gasto Total'] / row['populacao']) if row['populacao'] and pd.notna(row['populacao']) and row['populacao'] != 0 else 0,
                    axis=1
                )
                print(f"✔️ Coluna 'Gasto Total Normalizado' calculada dinamicamente.")
                # print(self.data_df[['uf', 'ano', 'Gasto Total', 'populacao', 'Gasto Total Normalizado']].head())

            if SHAPEFILE_PATH.exists():
                self.geo_data_df = gpd.read_file(SHAPEFILE_PATH)
                print(f"✔️ Dados geoespaciais carregados de {SHAPEFILE_PATH}: {self.geo_data_df.shape[0]} geometrias.")
                if 'SIGLA_UF' in self.geo_data_df.columns:
                    self.geo_data_df = self.geo_data_df.rename(columns={'SIGLA_UF': 'uf'})
                elif 'SIGLA' in self.geo_data_df.columns:
                     self.geo_data_df = self.geo_data_df.rename(columns={'SIGLA': 'uf'})
                else:
                    print(f"⚠️ ATENÇÃO: Coluna de sigla da UF não encontrada como 'SIGLA_UF' ou 'SIGLA' no shapefile. Verifique as colunas: {self.geo_data_df.columns}")
                    possible_uf_cols = [col for col in self.geo_data_df.columns if self.geo_data_df[col].astype(str).str.len().max() == 2 and self.geo_data_df[col].nunique() == 27]
                    if possible_uf_cols:
                        print(f"    ℹ️  Possível coluna de UF encontrada: {possible_uf_cols[0]}. Renomeando...")
                        self.geo_data_df = self.geo_data_df.rename(columns={possible_uf_cols[0]: 'uf'})
                    else:
                        print(f"❌ ERRO: Não foi possível identificar a coluna de UF no shapefile para o merge.")
                        return
            else:
                print(f"❌ ERRO FATAL: Arquivo shapefile {SHAPEFILE_PATH} não encontrado.")
                return

            if self.data_df is not None and not self.data_df.empty and self.geo_data_df is not None and not self.geo_data_df.empty:
                # Certificar que a coluna 'uf' em ambos os dataframes seja do mesmo tipo para o merge
                self.data_df['uf'] = self.data_df['uf'].astype(str).str.upper()
                self.geo_data_df['uf'] = self.geo_data_df['uf'].astype(str).str.upper()
                
                self.merged_df = self.geo_data_df.merge(self.data_df, on="uf", how="left")
                if self.merged_df.empty:
                    print("❌ ERRO: O merge entre dados geoespaciais e dados da análise não resultou em nenhum dado.")
                    # ... (logs de erro omitidos para brevidade)
                else:
                    print(f"✔️ Dados combinados (merged_df): {self.merged_df.shape[0]} linhas.")
                    # print(f"   Colunas do merged_df ANTES do dropna: {self.merged_df.columns.tolist()}")
                    # print(f"   Primeiras 5 linhas do merged_df ANTES do dropna:\n{self.merged_df.head()}")
                    # print(f"   Tipos de dados do merged_df ANTES do dropna:\n{self.merged_df.dtypes}")
                    self.merged_df.dropna(subset=['idh'], inplace=True)
                    print(f"✔️ Dados combinados após remover IDH nulo: {self.merged_df.shape[0]} linhas.")
            else:
                print("❌ ERRO: Não foi possível realizar o merge devido a dados faltantes (data_df ou geo_data_df).")

        except Exception as e:
            print(f"❌ Erro ao carregar ou processar dados: {e}")
            import traceback
            traceback.print_exc()
            self.merged_df = None

    def _load_data_from_db(self, db_path):
        print(f"🔄 Tentando carregar dados do banco de dados: {db_path}")
        if not db_path.exists():
            print(f"❌ ERRO: Arquivo do banco de dados '{db_path}' não encontrado.")
            return pd.DataFrame()
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM analise_unificada"
            df = pd.read_sql_query(query, conn)
            conn.close()
            print(f"✔️ Dados carregados do banco de dados: {df.shape[0]} linhas.")
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar dados do banco de dados: {e}")
            return pd.DataFrame()

    def create_widgets(self):
        self.filter_frame = ctk.CTkFrame(self, width=int(1180), height=int(40))
        self.filter_frame.pack(pady=10, padx=10, fill="x")

        self.year_label = ctk.CTkLabel(self.filter_frame, text="Selecionar Ano:")
        self.year_label.pack(side="left", padx=5)

        if self.data_df is not None and not self.data_df.empty and 'ano' in self.data_df.columns:
            anos_disponiveis = sorted(self.data_df['ano'].unique().astype(str))
        else:
            anos_disponiveis = ["N/A"]

        self.year_combobox = ctk.CTkComboBox(self.filter_frame, values=anos_disponiveis, command=self.update_visualizations)
        if anos_disponiveis and anos_disponiveis[0] != "N/A":
            self.year_combobox.set(anos_disponiveis[-1])
        else:
            self.year_combobox.set("N/A")
        self.year_combobox.pack(side="left", padx=5)

        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(1, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(1, weight=1)
        
        self.canvas_mapa_calor = None
        self.canvas_bolhas = None
        self.canvas_coropletico_idh = None
        self.canvas_coropletico_gasto = None

        if self.merged_df is not None and not self.merged_df.empty:
            initial_year = anos_disponiveis[-1] if anos_disponiveis and anos_disponiveis[0] != "N/A" else None
            if initial_year:
                 self.update_visualizations(initial_year)
            else:
                self.update_visualizations(None) # Chamar para limpar ou mostrar aviso
        else:
            error_label = ctk.CTkLabel(self.plot_frame, text="Erro ao carregar os dados. Verifique o console.", font=("Arial", 16))
            # Usar grid para centralizar o label de erro no plot_frame
            error_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")

        # --- Adicionar Widgets de Chat --- 
        self.chat_frame = ctk.CTkFrame(self) # Frame principal para o chat
        self.chat_frame.pack(pady=(0,10), padx=10, fill="x", side="bottom") # Colocar na parte de baixo

        self.chat_history_textbox = ctk.CTkTextbox(self.chat_frame, height=150, state="disabled", wrap="word")
        self.chat_history_textbox.pack(pady=5, padx=5, fill="x", expand=True)

        self.chat_input_entry = ctk.CTkEntry(self.chat_frame,
                                             placeholder_text="Faça uma pergunta sobre os dados...",
                                             text_color=("gray10", "gray90"), # Cor do texto (modo claro, modo escuro)
                                             placeholder_text_color=("gray50", "gray65")) # Cor do placeholder
        self.chat_input_entry.pack(side="left", pady=5, padx=(5,0), fill="x", expand=True)
        self.chat_input_entry.bind("<Return>", self._on_send_chat_message) # Bind Enter key

        self.chat_send_button = ctk.CTkButton(self.chat_frame, text="Enviar", width=70, command=self._on_send_chat_message)
        self.chat_send_button.pack(side="right", pady=5, padx=(0,5))
        # --- Fim Widgets de Chat ---

    def update_visualizations(self, selected_year_str):
        if selected_year_str is None or selected_year_str == "N/A":
            print("⚠️ Nenhum ano selecionado ou dados não disponíveis para atualização.")
            self._clear_canvas('all')
            # Remover todos os widgets do plot_frame e mostrar mensagem de erro/aviso
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            warn_text = "Selecione um ano para ver as visualizações."
            if self.merged_df is None or self.merged_df.empty:
                warn_text = "Erro ao carregar dados. Verifique o console."
            warn_label = ctk.CTkLabel(self.plot_frame, text=warn_text, font=("Arial", 16))
            warn_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
            return

        print(f"🔄 Atualizando visualizações para o ano: {selected_year_str}")
        if self.merged_df is None or self.merged_df.empty:
            print("⚠️ Dados merged_df não disponíveis para atualização.")
            return

        try:
            selected_year = int(selected_year_str)
            data_ano_selecionado = self.merged_df[self.merged_df['ano'] == selected_year].copy()

            # Limpar labels de aviso/erro anteriores do plot_frame
            for widget in self.plot_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.destroy()
            
            if data_ano_selecionado.empty:
                print(f"⚠️ Nenhum dado encontrado para o ano {selected_year} após o merge e filtro.")
                self._clear_canvas('all')
                warn_label = ctk.CTkLabel(self.plot_frame, text=f"Nenhum dado para o ano {selected_year}.", font=("Arial", 16))
                warn_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
                return

            # print(f"🔍 Conteúdo de data_ano_selecionado para o ano {selected_year}:")
            # print(f"   Colunas: {data_ano_selecionado.columns.tolist()}")
            # print(f"   Primeiras linhas:\n{data_ano_selecionado.head()}")
            # print(f"   Valores de 'Gasto Total Normalizado' (amostra):\n{data_ano_selecionado['Gasto Total Normalizado'].head()}")
            # print(f"   Valores NaN em 'Gasto Total Normalizado': {data_ano_selecionado['Gasto Total Normalizado'].isna().sum()} de {len(data_ano_selecionado)}")

            print(f"Dados para o ano {selected_year}: {data_ano_selecionado.shape[0]} linhas.")

            self._clear_canvas('mapa_calor')
            self.plot_mapa_calor(data_ano_selecionado, selected_year)

            self._clear_canvas('bolhas')
            self.plot_grafico_bolhas(data_ano_selecionado, selected_year)
            
            self._clear_canvas('coropletico_idh')
            self.plot_mapa_coropletico(data_ano_selecionado, 'idh', selected_year, "Mapa Coroplético de IDH", 0)

            self._clear_canvas('coropletico_gasto')
            self.plot_mapa_coropletico(data_ano_selecionado, 'Gasto Total Normalizado', selected_year, "Mapa Coroplético de Gasto Total Normalizado", 1)

        except Exception as e:
            print(f"❌ Erro ao atualizar visualizações: {e}")
            import traceback
            traceback.print_exc()

    def _clear_canvas(self, canvas_name_key):
        canvas_attributes = {
            'mapa_calor': 'canvas_mapa_calor',
            'bolhas': 'canvas_bolhas',
            'coropletico_idh': 'canvas_coropletico_idh',
            'coropletico_gasto': 'canvas_coropletico_gasto'
        }
        keys_to_clear = list(canvas_attributes.keys()) if canvas_name_key == 'all' else [canvas_name_key]

        for key in keys_to_clear:
            attr_name = canvas_attributes.get(key)
            if attr_name and hasattr(self, attr_name):
                canvas_widget_wrapper = getattr(self, attr_name)
                if canvas_widget_wrapper:
                    # canvas_widget_wrapper é o CTkFrame que contém o FigureCanvasTkAgg
                    for child in canvas_widget_wrapper.winfo_children():
                        child.destroy()
                    # plt.close(canvas_widget_wrapper.figure) # Comentado para evitar fechar a figura globalmente
                    setattr(self, attr_name, None) # Remover referência ao frame antigo

    def plot_mapa_calor(self, data_df, year):
        frame_canvas = ctk.CTkFrame(self.plot_frame)
        frame_canvas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.canvas_mapa_calor = frame_canvas # Salva o frame, não o canvas matplotlib diretamente

        cols_interesse = ['idh', 'despesa_saude', 'despesa_educacao', 'despesa_assistencia_social', 'despesa_infraestrutura']
        # Filtrar apenas colunas que existem no dataframe e são numéricas
        cols_plot = [col for col in cols_interesse if col in data_df.columns and pd.api.types.is_numeric_dtype(data_df[col])]
        
        if not cols_plot or data_df[cols_plot].isnull().all().all() or len(data_df[cols_plot].dropna()) < 2:
            print(f"⚠️ Dados insuficientes ou apenas NaNs para Mapa de Calor ({year}). Colunas disponíveis: {cols_plot}")
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.text(0.5, 0.5, f"Dados insuficientes para\nMapa de Calor ({year})",
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=10)
            ax.set_axis_off()
        else:
            corr_matrix = data_df[cols_plot].corr()
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, vmin=-1, vmax=1)
            ax.set_title(f"Correlações ({year})")
        
        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        # frame_canvas.figure = fig # Associar a figura ao frame para referência se necessário

    def plot_grafico_bolhas(self, data_df, year):
        frame_canvas = ctk.CTkFrame(self.plot_frame)
        frame_canvas.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.canvas_bolhas = frame_canvas

        cols_necessarias = ['Gasto Total Normalizado', 'idh', 'populacao', 'regiao']
        if not all(col in data_df.columns for col in cols_necessarias) or data_df[cols_necessarias].isnull().all().any() or len(data_df.dropna(subset=cols_necessarias)) < 1:
            print(f"⚠️ Dados insuficientes para Gráfico de Bolhas ({year}). Checar colunas: {cols_necessarias}")
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.text(0.5, 0.5, f"Dados insuficientes para\nGráfico de Bolhas ({year})",
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=10)
            ax.set_axis_off()
        else:
            data_plot = data_df.dropna(subset=cols_necessarias).copy()
            # Garantir que população seja positiva para o tamanho da bolha
            data_plot['populacao_plot'] = data_plot['populacao'].clip(lower=1)

            fig, ax = plt.subplots(figsize=(5, 4))
            sns.scatterplot(
                data=data_plot,
                x='Gasto Total Normalizado',
                y='idh',
                size='populacao_plot',
                hue='regiao',
                sizes=(50, 500),
                alpha=0.7,
                ax=ax,
                legend=True # Controlar legenda explicitamente
            )
            ax.set_title(f"IDH vs Gasto Total Normalizado ({year})")
            ax.set_xlabel("Gasto Total por População")
            ax.set_ylabel("IDH")
            # Ajustar posição da legenda
            ax.legend(title='Região', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            fig.tight_layout() # Ajustar layout para não cortar a legenda

        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        # frame_canvas.figure = fig

    def plot_mapa_coropletico(self, data_df_ano, column_to_plot, year, title, grid_col):
        frame_canvas = ctk.CTkFrame(self.plot_frame)
        frame_canvas.grid(row=1, column=grid_col, padx=5, pady=5, sticky="nsew")
        if grid_col == 0:
            self.canvas_coropletico_idh = frame_canvas
        else:
            self.canvas_coropletico_gasto = frame_canvas

        if self.geo_data_df is None or self.geo_data_df.empty:
            print(f"⚠️ Dados Geoespaciais não carregados. Não é possível plotar Mapa Coroplético para {title} ({year}).")
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.text(0.5, 0.5, f"Dados geoespaciais\nnão disponíveis",
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=10)
            ax.set_axis_off()
        elif column_to_plot not in data_df_ano.columns or data_df_ano[column_to_plot].isnull().all() or len(data_df_ano.dropna(subset=[column_to_plot])) < 1:
            print(f"⚠️ Dados insuficientes ou coluna '{column_to_plot}' ausente/vazia para {title} ({year}).")
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, f"Dados não disponíveis para\n{title} ({year})",
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=12)
            ax.set_axis_off()
        else:
            # Garantir que 'uf' em geo_data_df seja string para o merge
            geo_data_merged = self.geo_data_df.copy()
            geo_data_merged['uf'] = geo_data_merged['uf'].astype(str)
            
            # Preparar dados para plotagem (data_df_ano já filtrado por ano)
            data_to_plot = data_df_ano[['uf', column_to_plot]].copy()
            data_to_plot['uf'] = data_to_plot['uf'].astype(str)
            
            # Merge dos dados do ano com os dados geoespaciais
            map_data = geo_data_merged.merge(data_to_plot, on="uf", how="left")
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))
            map_data.plot(column=column_to_plot, ax=ax, legend=True,
                          legend_kwds={'label': column_to_plot, 'orientation': "horizontal"},
                          missing_kwds={"color": "lightgrey", "label": "Dados Ausentes"})
            ax.set_title(f"{title} ({year})")
            ax.set_axis_off()

        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        # frame_canvas.figure = fig

    # --- Métodos para o Chat LLM ---
    def _on_send_chat_message(self, event=None): # Adicionado event=None para o bind de Enter
        user_query = self.chat_input_entry.get().strip()
        if not user_query:
            return

        self._add_message_to_chat_history(f"Você: {user_query}")
        self.chat_input_entry.delete(0, "end")

        if self.llm_handler:
            # Indicar que está processando (poderia ser um label na UI)
            self._add_message_to_chat_history("Analisando...", is_processing=True)
            self.update_idletasks() # Força atualização da UI

            text_response, filters = self.llm_handler.get_response(user_query)
            
            # Remover a mensagem "Analisando..."
            self._remove_last_processing_message_from_chat_history()
            self._add_message_to_chat_history(f"Assistente: {text_response}")

            # Processar filtros
            if filters:
                print(f"🔍 Filtros identificados pelo LLM: {filters}")
                # TODO: Aplicar filtros à UI (ex: combobox de ano) e atualizar visualizações
                if "ano" in filters and filters["ano"]:
                    try:
                        ano_str = str(filters["ano"])
                        if ano_str in self.year_combobox.cget("values"):
                            self.year_combobox.set(ano_str)
                            # A chamada a update_visualizations já acontece pelo command do combobox
                            self._add_message_to_chat_history(f"(INFO: Filtro de ano atualizado para {ano_str})")
                        else:
                            self._add_message_to_chat_history(f"(AVISO: Ano {ano_str} sugerido pelo LLM não está disponível nos filtros.)")
                    except Exception as e_filter_apply:
                        print(f"Erro ao aplicar filtro de ano do LLM: {e_filter_apply}")
                        self._add_message_to_chat_history(f"(ERRO: Não foi possível aplicar o filtro de ano {filters['ano']})")
                # Adicionar lógica para outros filtros (uf, regiao, categoria_despesa) aqui se necessário
        else:
            self._add_message_to_chat_history("Assistente: Desculpe, o serviço de IA não está disponível no momento.")

    def _add_message_to_chat_history(self, message: str, is_processing: bool = False):
        self.chat_history_textbox.configure(state="normal")
        if is_processing:
            self.chat_history_textbox.insert("end", message + "\n", "processing_tag")
        else:
            self.chat_history_textbox.insert("end", message + "\n")
        self.chat_history_textbox.configure(state="disabled")
        self.chat_history_textbox.see("end") # Scroll para o final

    def _remove_last_processing_message_from_chat_history(self):
        self.chat_history_textbox.configure(state="normal")
        # Esta é uma forma simples. Pode precisar de mais robustez se houver múltiplas tags.
        # Deleta da penúltima linha (que contém "Analisando...") até o final da penúltima linha.
        # E depois deleta o newline extra que ficou.
        # Achar a posição da tag "processing_tag"
        # Este método é um pouco complexo com CTkTextbox, pode ser mais fácil reconstruir sem a msg
        # Por simplicidade, vamos apenas adicionar a resposta. O usuário verá "Analisando..." seguido da resposta.
        # Para remover de fato, seria necessário um controle mais fino do conteúdo do Textbox.
        # Alternativa: Limpar e re-adicionar o histórico sem a msg de "Analisando..."
        # Por ora, manteremos a mensagem "Analisando..." e a resposta aparecerá em sequência.
        # Se for um problema, podemos refinar depois.
        pass # Deixar a mensagem "Analisando..." e a resposta aparecer em sequência é aceitável por ora.
        self.chat_history_textbox.configure(state="disabled")

if __name__ == "__main__":
    # Adicionar src ao sys.path para execução direta do dashboard_ui.py (se necessário)
    # Esta duplicação de lógica de path não é ideal, mas garante que funcione se rodado direto.
    # Em produção, main.py cuidará do path.
    if str(SRC_DIR_FOR_LLM) not in sys.path: # Já definido no topo do arquivo
        sys.path.insert(0, str(SRC_DIR_FOR_LLM))
    
    app = DashboardApp()
    app.mainloop() 