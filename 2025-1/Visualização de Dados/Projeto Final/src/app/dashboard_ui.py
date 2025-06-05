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

        print("DEBUG INIT: Iniciando __init__ de DashboardApp")

        # Botão de Teste Global - Criado e empacotado PRIMEIRO
        print("DEBUG INIT: Criando Botão de Teste Global...")
        self.global_test_button = ctk.CTkButton(
            self,
            text="Clique em MIM! (Global Test)",
            command=self._global_test_command,
            fg_color="red",
            text_color="white",
            width=200, 
            height=50  
        )
        self.global_test_button.pack(pady=5, padx=10, side="top", anchor="n") # Reduzido pady para mais espaço
        print(f"DEBUG INIT: Botão de Teste Global empacotado.")
        self.update_idletasks()
        print(f"DEBUG INIT: Geometria global_test_button (após update_idletasks): w={self.global_test_button.winfo_width()}, h={self.global_test_button.winfo_height()}, x={self.global_test_button.winfo_x()}, y={self.global_test_button.winfo_y()}")

        self.data_df = None
        self.geo_data_df = None
        self.merged_df = None

        # Frames para os canvases - serão criados em create_widgets
        self.frame_mapa_calor = None
        self.frame_bolhas = None
        self.frame_coropletico_idh = None
        self.frame_coropletico_gasto = None
        self.plot_frame = None 
        self.filter_frame = None 

        # Referências aos widgets FigureCanvasTkAgg
        self.canvas_agg_mapa_calor = None
        self.canvas_agg_bolhas = None
        self.canvas_agg_coropletico_idh = None
        self.canvas_agg_coropletico_gasto = None

        if hasattr(self, '_on_send_chat_message') and callable(self._on_send_chat_message):
            print("DEBUG INIT: ✔️ Método _on_send_chat_message está definido.")
        else:
            print("DEBUG INIT: ❌ ALERTA: Método _on_send_chat_message NÃO está definido ou não é chamável!")

        try:
            self.llm_handler = LLMQueryHandler()
            print("DEBUG INIT: ✔️ LLM Handler inicializado com sucesso.")
        except Exception as e_llm_init:
            self.llm_handler = None
            print(f"DEBUG INIT: ❌ Erro ao inicializar LLM Handler: {e_llm_init}")

        print("DEBUG INIT: Chamando load_data()...")
        self.load_data() 
        print("DEBUG INIT: Chamando create_widgets()...")
        self.create_widgets() 
        
        if hasattr(self, 'chat_input_entry') and self.chat_input_entry:
            print(f"DEBUG INIT: Tentando dar foco para {self.chat_input_entry} com self.after")
            self.after(100, lambda: self.chat_input_entry.focus_set())
            self.after(200, lambda: print(f"DEBUG INIT (after delay): Foco tentado para chat_input_entry. Widget com foco atual: {self.focus_get()}"))
        else:
            print("DEBUG INIT: chat_input_entry não encontrado para dar foco.")
        
        print("DEBUG INIT: Fim do __init__ de DashboardApp")

    def load_data(self):
        print("DEBUG load_data: Iniciando carregamento de dados...")
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
        print(f"DEBUG _load_data_from_db: Tentando carregar dados do banco de dados: {db_path}")
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
        print("DEBUG create_widgets: Iniciando criação de widgets...")

        # Ordem de Pack: global_button (top), filter_frame (top), plot_frame (top, expand), chat_frame (bottom)

        self.filter_frame = ctk.CTkFrame(self, width=int(1180), height=int(40))
        self.filter_frame.pack(pady=(0,5), padx=10, fill="x", side="top") # Reduzido pady
        print("DEBUG create_widgets: filter_frame CRIADO E EMPACOTADO.")

        self.year_label = ctk.CTkLabel(self.filter_frame, text="Selecionar Ano:")
        self.year_label.pack(side="left", padx=5)
        
        anos_disponiveis = ["N/A"]
        if self.data_df is not None and not self.data_df.empty and 'ano' in self.data_df.columns:
            anos_disponiveis = sorted(self.data_df['ano'].unique().astype(str))
        
        self.year_combobox = ctk.CTkComboBox(self.filter_frame, values=anos_disponiveis, command=self.update_visualizations)
        if anos_disponiveis and anos_disponiveis[0] != "N/A":
            self.year_combobox.set(anos_disponiveis[-1])
        else:
            self.year_combobox.set("N/A")
        self.year_combobox.pack(side="left", padx=5)
        print("DEBUG create_widgets: Filtros de ano CRIADOS E EMPACOTADOS.")

        # --- REINTRODUZINDO plot_frame e gráficos ---
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(pady=5, padx=10, fill="both", expand=True, side="top") 
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(1, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(1, weight=1)
        print("DEBUG create_widgets: plot_frame CRIADO E EMPACOTADO.")
        
        self.frame_mapa_calor = ctk.CTkFrame(self.plot_frame)
        self.frame_mapa_calor.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_bolhas = ctk.CTkFrame(self.plot_frame)
        self.frame_bolhas.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.frame_coropletico_idh = ctk.CTkFrame(self.plot_frame)
        self.frame_coropletico_idh.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.frame_coropletico_gasto = ctk.CTkFrame(self.plot_frame)
        self.frame_coropletico_gasto.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        print("DEBUG create_widgets: Frames dos gráficos CRIADOS E POSICIONADOS com grid.")
        # --- FIM da reintrodução do plot_frame ---

        # --- Widgets de Chat --- 
        self.chat_frame = ctk.CTkFrame(self, height=180) # Altura fixa para o chat_frame
        self.chat_frame.pack(pady=(5,10), padx=10, fill="x", side="bottom", expand=False) 
        print(f"DEBUG create_widgets: chat_frame criado e empacotado: {self.chat_frame}")
        
        self.chat_frame.bind("<Button-1>", self._on_chat_frame_click)
        print(f"DEBUG create_widgets: Bind <Button-1> para _on_chat_frame_click em {self.chat_frame}")

        self.chat_history_textbox = ctk.CTkTextbox(self.chat_frame, height=100, state="disabled", wrap="word") # Reduzida altura
        self.chat_history_textbox.pack(pady=5, padx=5, fill="x", expand=True)
        print(f"DEBUG create_widgets: chat_history_textbox criado: {self.chat_history_textbox}")

        input_button_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        input_button_frame.pack(fill="x", padx=5, pady=(0,5))

        self.chat_input_entry = ctk.CTkEntry(input_button_frame,
                                             placeholder_text="Pressione Enter ou clique em Enviar...",
                                             text_color=("black", "white"), 
                                             placeholder_text_color=("gray50", "gray65")) 
        self.chat_input_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        print(f"DEBUG create_widgets: chat_input_entry criado: {self.chat_input_entry}")
        
        self.chat_input_entry.bind("<Return>", self._global_test_command_event_wrapper) 
        print(f"DEBUG create_widgets: Bind <Return> para _global_test_command em {self.chat_input_entry}")
        
        self.chat_input_entry.bind("<FocusIn>", self._on_chat_input_focus_in)
        print(f"DEBUG create_widgets: Bind <FocusIn> para _on_chat_input_focus_in em {self.chat_input_entry}")
        self.chat_input_entry.bind("<FocusOut>", self._on_chat_input_focus_out)
        print(f"DEBUG create_widgets: Bind <FocusOut> para _on_chat_input_focus_out em {self.chat_input_entry}")
        self.chat_input_entry.bind("<Button-1>", self._on_chat_input_click)
        print(f"DEBUG create_widgets: Bind <Button-1> para _on_chat_input_click em {self.chat_input_entry}")
            
        self.chat_send_button = ctk.CTkButton(input_button_frame, 
                                              text="Enviar",
                                              width=100, 
                                              command=self._global_test_command, 
                                              text_color=("black", "yellow") 
                                              )
        self.chat_send_button.pack(side="right")
        print(f"DEBUG create_widgets: chat_send_button criado: {self.chat_send_button} com comando: {self._global_test_command}")
        
        self.chat_send_button.bind("<Button-1>", self._on_chat_send_button_click_event)
        print(f"DEBUG create_widgets: Bind <Button-1> para _on_chat_send_button_click_event em {self.chat_send_button}")

        if self.filter_frame and hasattr(self, 'year_combobox'):
            initial_year = self.year_combobox.get()
            if initial_year and initial_year != "N/A":
                print(f"DEBUG create_widgets: Chamando update_visualizations com o ano inicial: {initial_year}")
                self.update_visualizations(initial_year)
            else:
                print("DEBUG create_widgets: Nenhum ano inicial válido para chamar update_visualizations.")

        print("DEBUG create_widgets: Fim da criação de widgets.")

    def update_visualizations(self, selected_year_str):
        print(f"DEBUG update_visualizations: CHAMADA (selected_year_str={selected_year_str}).")
        
        if self.plot_frame is None: # Verificação se o frame principal dos plots existe
            print("DEBUG update_visualizations: plot_frame não existe. Pulando lógica de atualização de gráficos.")
            if hasattr(self, 'chat_history_textbox') and self.chat_history_textbox:
                 self._add_message_to_chat_history(f"(INFO DEBUG: Ano selecionado mudou para {selected_year_str}, gráficos desabilitados)")
            return

        if selected_year_str is None or selected_year_str == "N/A":
            print(f"DEBUG update_visualizations: ⚠️ Nenhum ano selecionado. Limpando canvases. Foco: {self.focus_get()}")
            self._clear_canvas('all')
            for widget in self.plot_frame.winfo_children(): # Limpar frames dentro do plot_frame
                if isinstance(widget, ctk.CTkFrame): # Apenas os frames dos gráficos
                    for sub_widget in widget.winfo_children(): # FigureCanvasTkAgg
                        sub_widget.destroy()
            warn_label = ctk.CTkLabel(self.plot_frame, text="Selecione um ano para ver as visualizações.", font=("Arial", 16))
            warn_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
            return

        print(f"DEBUG update_visualizations: 🔄 Atualizando para o ano: {selected_year_str}. Foco: {self.focus_get()}")
        if self.merged_df is None or self.merged_df.empty:
            print("⚠️ Dados merged_df não disponíveis para atualização.")
            return

        try:
            selected_year = int(selected_year_str)
            data_ano_selecionado = self.merged_df[self.merged_df['ano'] == selected_year].copy()

            for widget in self.plot_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel): # Remover apenas labels de aviso antigas
                    widget.destroy()
            
            if data_ano_selecionado.empty:
                print(f"⚠️ Nenhum dado encontrado para o ano {selected_year}.")
                self._clear_canvas('all')
                warn_label = ctk.CTkLabel(self.plot_frame, text=f"Nenhum dado para o ano {selected_year}.", font=("Arial", 16))
                warn_label.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
                return

            print(f"Dados para o ano {selected_year}: {data_ano_selecionado.shape[0]} linhas.")

            self.plot_mapa_calor(data_ano_selecionado, selected_year)
            self.plot_grafico_bolhas(data_ano_selecionado, selected_year)
            self.plot_mapa_coropletico(data_ano_selecionado, 'idh', selected_year, "Mapa Coroplético de IDH", 0)
            self.plot_mapa_coropletico(data_ano_selecionado, 'Gasto Total Normalizado', selected_year, "Mapa Coroplético de Gasto Total Normalizado", 1)

        except Exception as e:
            print(f"❌ Erro ao atualizar visualizações: {e}")
            import traceback
            traceback.print_exc()

    def _get_or_create_canvas(self, frame_container, canvas_attr_name):
        """Obtém o FigureCanvasTkAgg existente ou cria um novo se não existir."""
        canvas_agg = getattr(self, canvas_attr_name, None)
        if canvas_agg is None or not canvas_agg.winfo_exists(): # Se não existe ou foi destruído
            print(f"DEBUG _get_or_create_canvas: Criando novo FigureCanvasTkAgg para {canvas_attr_name} em {frame_container}")
            figure = plt.figure(figsize=(5, 4)) # Tamanho padrão, pode ser ajustado
            canvas_agg = FigureCanvasTkAgg(figure, master=frame_container)
            canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
            setattr(self, canvas_attr_name, canvas_agg)
        else:
            print(f"DEBUG _get_or_create_canvas: Reutilizando FigureCanvasTkAgg existente para {canvas_attr_name}")
            canvas_agg.figure.clear() # Limpa a figura para reutilização
        return canvas_agg.figure, canvas_agg

    def _clear_canvas(self, canvas_name_key):
        # Esta função agora é menos central, pois a limpeza da figura ocorre em _get_or_create_canvas
        # Mas podemos usá-la para limpar todas as figuras de uma vez, se necessário.
        print(f"DEBUG _clear_canvas: Solicitado para '{canvas_name_key}'.")
        canvas_map = {
            'mapa_calor': (self.frame_mapa_calor, 'canvas_agg_mapa_calor'),
            'bolhas': (self.frame_bolhas, 'canvas_agg_bolhas'),
            'coropletico_idh': (self.frame_coropletico_idh, 'canvas_agg_coropletico_idh'),
            'coropletico_gasto': (self.frame_coropletico_gasto, 'canvas_agg_coropletico_gasto')
        }
        keys_to_clear = list(canvas_map.keys()) if canvas_name_key == 'all' else [canvas_name_key]

        for key in keys_to_clear:
            if key in canvas_map:
                frame, canvas_attr = canvas_map[key]
                canvas_widget = getattr(self, canvas_attr, None)
                if canvas_widget and hasattr(canvas_widget, 'figure') and canvas_widget.figure:
                    print(f"  Limpando figura para {key}")
                    canvas_widget.figure.clear()
                    canvas_widget.draw() # Redesenha o canvas vazio
                elif frame: # Se o frame existe mas o canvas não (ou não tem figura), limpa o frame
                     for child in frame.winfo_children():
                        child.destroy()
                     print(f"  Frame {frame} limpo (sem canvas widget para limpar figura)")

    def plot_mapa_calor(self, data_df, year):
        if self.plot_frame is None or self.frame_mapa_calor is None: return
        print(f"DEBUG plot_mapa_calor: Plotando para o ano {year}")
        
        fig, canvas_agg = self._get_or_create_canvas(self.frame_mapa_calor, 'canvas_agg_mapa_calor')
        ax = fig.subplots() # Cria ou obtém o Axes

        cols_interesse = ['idh', 'despesa_saude', 'despesa_educacao', 'despesa_assistencia_social', 'despesa_infraestrutura']
        cols_plot = [col for col in cols_interesse if col in data_df.columns and pd.api.types.is_numeric_dtype(data_df[col])]
        
        if not cols_plot or data_df[cols_plot].isnull().all().all() or len(data_df[cols_plot].dropna()) < 2:
            ax.text(0.5, 0.5, f"Dados insuficientes para\nMapa de Calor ({year})", ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
        else:
            corr_matrix = data_df[cols_plot].corr()
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, vmin=-1, vmax=1)
            ax.set_title(f"Correlações ({year})")
        
        canvas_agg.draw()

    def plot_grafico_bolhas(self, data_df, year):
        if self.plot_frame is None or self.frame_bolhas is None: return
        print(f"DEBUG plot_grafico_bolhas: Plotando para o ano {year}")

        fig, canvas_agg = self._get_or_create_canvas(self.frame_bolhas, 'canvas_agg_bolhas')
        ax = fig.subplots()

        cols_necessarias = ['Gasto Total Normalizado', 'idh', 'populacao', 'regiao']
        if not all(col in data_df.columns for col in cols_necessarias) or data_df[cols_necessarias].isnull().all().any() or len(data_df.dropna(subset=cols_necessarias)) < 1:
            ax.text(0.5, 0.5, f"Dados insuficientes para\nGráfico de Bolhas ({year})", ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
        else:
            data_plot = data_df.dropna(subset=cols_necessarias).copy()
            data_plot['populacao_plot'] = data_plot['populacao'].clip(lower=1)
            sns.scatterplot(
                data=data_plot, x='Gasto Total Normalizado', y='idh',
                size='populacao_plot', hue='regiao', sizes=(50, 500), alpha=0.7, ax=ax, legend=True
            )
            ax.set_title(f"IDH vs Gasto Total Normalizado ({year})")
            ax.set_xlabel("Gasto Total por População")
            ax.set_ylabel("IDH")
            ax.legend(title='Região', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            fig.tight_layout()
        canvas_agg.draw()

    def plot_mapa_coropletico(self, data_df_ano, column_to_plot, year, title, grid_col):
        target_frame = self.frame_coropletico_idh if grid_col == 0 else self.frame_coropletico_gasto
        canvas_attr_name = 'canvas_agg_coropletico_idh' if grid_col == 0 else 'canvas_agg_coropletico_gasto'
        
        if self.plot_frame is None or target_frame is None: return
        print(f"DEBUG plot_mapa_coropletico: Plotando {title} para o ano {year}")
        
        fig, canvas_agg = self._get_or_create_canvas(target_frame, canvas_attr_name)
        ax = fig.subplots()

        if self.geo_data_df is None or self.geo_data_df.empty:
            ax.text(0.5, 0.5, "Dados geoespaciais\nnão disponíveis", ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
        elif column_to_plot not in data_df_ano.columns or data_df_ano[column_to_plot].isnull().all() or len(data_df_ano.dropna(subset=[column_to_plot])) < 1:
            ax.text(0.5, 0.5, f"Dados não disponíveis para\n{title} ({year})", ha='center', va='center', transform=ax.transAxes)
            ax.set_axis_off()
        else:
            geo_data_merged = self.geo_data_df.copy()
            geo_data_merged['uf'] = geo_data_merged['uf'].astype(str)
            data_to_plot = data_df_ano[['uf', column_to_plot]].copy()
            data_to_plot['uf'] = data_to_plot['uf'].astype(str)
            map_data = geo_data_merged.merge(data_to_plot, on="uf", how="left")
            map_data.plot(column=column_to_plot, ax=ax, legend=True,
                          legend_kwds={'label': column_to_plot, 'orientation': "horizontal"},
                          missing_kwds={"color": "lightgrey", "label": "Dados Ausentes"})
            ax.set_title(f"{title} ({year})")
            ax.set_axis_off()
        canvas_agg.draw()

    # --- Métodos para o Chat LLM ---
    def _on_send_chat_message(self, event=None): 
        print("--- _on_send_chat_message CHAMADO ---") 
        user_query = self.chat_input_entry.get().strip()
        print(f"📝 Query do usuário: '{user_query}'") 
        if not user_query:
            print("Query (Enter) vazia, retornando.")
            return

        self._add_message_to_chat_history(f"Você (Enter): {user_query}")
        # self.chat_input_entry.delete(0, "end") 

        if self.llm_handler:
            self._add_message_to_chat_history("Analisando...", is_processing=True)
            self.update_idletasks() 

            text_response, filters = self.llm_handler.get_response(user_query)
            
            self._remove_last_processing_message_from_chat_history()
            self._add_message_to_chat_history(f"Assistente: {text_response}")

            if filters:
                print(f"🔍 Filtros identificados pelo LLM: {filters}")
                if "ano" in filters and filters["ano"]:
                    try:
                        ano_str = str(filters["ano"])
                        if ano_str in self.year_combobox.cget("values"):
                            self.year_combobox.set(ano_str)
                            self._add_message_to_chat_history(f"(INFO: Filtro de ano atualizado para {ano_str})")
                        else:
                            self._add_message_to_chat_history(f"(AVISO: Ano {ano_str} sugerido pelo LLM não está disponível nos filtros.)")
                    except Exception as e_filter_apply:
                        print(f"Erro ao aplicar filtro de ano do LLM: {e_filter_apply}")
                        self._add_message_to_chat_history(f"(ERRO: Não foi possível aplicar o filtro de ano {filters['ano']})")
        else:
            self._add_message_to_chat_history("Assistente: Desculpe, o serviço de IA não está disponível no momento.")

    def _add_message_to_chat_history(self, message: str, is_processing: bool = False):
        print(f"DEBUG _add_message_to_chat_history: Adicionando '{message}'")
        self.chat_history_textbox.configure(state="normal")
        if is_processing:
            self.chat_history_textbox.insert("end", message + "\n", "processing_tag")
        else:
            self.chat_history_textbox.insert("end", message + "\n")
        self.chat_history_textbox.configure(state="disabled")
        self.chat_history_textbox.see("end")

    def _remove_last_processing_message_from_chat_history(self):
        print("DEBUG _remove_last_processing_message_from_chat_history: Tentando remover 'Analisando...'")
        self.chat_history_textbox.configure(state="normal")
        # Lógica para remover a mensagem "Analisando..." pode ser complexa.
        # Por enquanto, apenas passamos para não quebrar.
        pass 
        self.chat_history_textbox.configure(state="disabled")

    def _test_chat_button_command(self):
        # Este método não está mais sendo usado diretamente pelos botões de chat nos testes atuais
        print("--- _test_chat_button_command (Legado para este teste) CLICADO! ---")

    def _global_test_command(self):
        print("--- GLOBAL TEST COMMAND EXECUTADO (via Botão Global, Botão Chat, ou Enter no Input) ---")
        # Este é o único comando que os botões e Enter deveriam chamar neste teste
        focused_widget = self.focus_get()
        print(f"    Widget atualmente com foco: {focused_widget}")
        if hasattr(self, 'chat_input_entry'):
            print(f"    Texto no chat_input_entry: '{self.chat_input_entry.get()}'")

    def _global_test_command_event_wrapper(self, event): # Precisa do argumento 'event' para binds
        print(f"--- _global_test_command_event_wrapper (CHAMADO POR EVENTO: {event}) ---")
        self._global_test_command()

    def _on_chat_input_focus_in(self, event):
        print(f"--- EVENTO: Foco ENTROU no chat_input_entry ({event.widget}) ---")

    def _on_chat_input_focus_out(self, event):
        print(f"--- EVENTO: Foco SAIU do chat_input_entry ({event.widget}) ---")
    
    def _on_chat_input_click(self, event):
        print(f"--- EVENTO: CLIQUE no chat_input_entry ({event.widget}) ---")

    def _on_chat_send_button_click_event(self, event):
        print(f"--- EVENTO: CLIQUE (via bind) no chat_send_button ({event.widget}) ---")
        # Chama o comando global para consistência de teste, embora o 'command=' já faça isso.
        # Isso ajuda a verificar se o bind <Button-1> está funcionando independentemente do 'command='.
        self._global_test_command()

    def _on_chat_frame_click(self, event):
        print(f"--- EVENTO: CLIQUE no chat_frame ({event.widget}) em x={event.x}, y={event.y} ---")

if __name__ == "__main__":
    if str(SRC_DIR_FOR_LLM) not in sys.path:
        sys.path.insert(0, str(SRC_DIR_FOR_LLM))
    
    app = DashboardApp()
    app.mainloop() 