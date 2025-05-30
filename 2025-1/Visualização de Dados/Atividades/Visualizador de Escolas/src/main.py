import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
import os

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DatabaseManager
from src.utils.graph_utils import GraphManager
from src.gui.components import SearchFrame, ResultsTable, PaginationFrame, LoadingIndicator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scripts import tratar_dataset

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AplicativoEscolas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Escolas")
        self.root.state('zoomed')
        
        # Configura protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.finalizar)
        
        # Lista de janelas abertas
        self.janelas_abertas = []
        
        # Inicializa gerenciadores
        self.db_manager = DatabaseManager()
        self.graph_manager = GraphManager()
        
        # Configuração do estilo
        self._setup_style()
        
        # Frame principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        header = ttk.Label(self.main_frame, text="Sistema de Gestão de Escolas", style="Header.TLabel")
        header.pack(pady=20)
        
        # Botões
        self.criar_botao(self.main_frame, "Consultar Escolas", self.abrir_consulta)
        self.criar_botao(self.main_frame, "Visualizar Gráficos", self.mostrar_graficos)
        
        # Inicialização do sistema
        self.verificar_e_preparar_sistema()

    def finalizar(self):
        """Finaliza a aplicação corretamente"""
        try:
            # Fecha todas as janelas abertas
            for janela in self.janelas_abertas:
                try:
                    janela.destroy()
                except:
                    pass
            
            # Limpa a lista de janelas
            self.janelas_abertas.clear()
            
            # Fecha todas as figuras do matplotlib
            plt.close('all')
            
            # Finaliza a aplicação
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Erro ao finalizar aplicação: {e}")
            sys.exit(1)

    def _criar_janela(self, titulo: str) -> tk.Toplevel:
        """Cria uma nova janela e a adiciona à lista de controle"""
        janela = tk.Toplevel(self.root)
        janela.title(titulo)
        janela.state('zoomed')
        
        # Adiciona à lista de janelas abertas
        self.janelas_abertas.append(janela)
        
        # Configura protocolo de fechamento
        janela.protocol("WM_DELETE_WINDOW", lambda: self._fechar_janela(janela))
        
        return janela
    
    def _fechar_janela(self, janela: tk.Toplevel):
        """Fecha uma janela específica"""
        try:
            # Remove da lista de janelas abertas
            if janela in self.janelas_abertas:
                self.janelas_abertas.remove(janela)
            
            # Fecha a janela
            janela.destroy()
            
        except Exception as e:
            logger.error(f"Erro ao fechar janela: {e}")

    def _setup_style(self):
        """Configura o estilo da aplicação"""
        style = ttk.Style()
        style.configure("TButton", padding=10)
        style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))

    def criar_botao(self, parent, texto, comando):
        """Cria um botão padronizado"""
        btn = ttk.Button(parent, text=texto, command=comando)
        btn.pack(pady=10, padx=20, fill=tk.X)

    def verificar_e_preparar_sistema(self):
        """Verifica e prepara o sistema para uso"""
        try:
            arquivo_csv = os.path.join('data', 'raw', 'microdados_ed_basica_2024.csv')
            arquivo_tratado = os.path.join('data', 'processed', 'microdados_ed_basica_2024_tratado.csv')
            arquivo_db = os.path.join('data', 'processed', 'escolas.db')
            
            if not os.path.exists(arquivo_csv):
                messagebox.showerror("Erro", f"O arquivo '{arquivo_csv}' não foi encontrado!\n"
                                           "Por favor, coloque o arquivo CSV na pasta data/raw/")
                self.root.quit()
                return
            
            # Trata o dataset se necessário
            if not os.path.exists(arquivo_tratado):
                if messagebox.askyesno("Preparar Dados", 
                                     "Precisamos preparar os dados antes de começar.\n"
                                     "Isso pode levar alguns segundos. Deseja continuar?"):
                    tratar_dataset.main()
                else:
                    self.root.quit()
                    return
            
            # Importa os dados se o banco não existir
            if not os.path.exists(arquivo_db):
                if messagebox.askyesno("Importar Dados",
                                     "Precisamos importar os dados para o banco.\n"
                                     "Isso pode levar alguns segundos. Deseja continuar?"):
                    os.environ['ARQUIVO_CSV'] = arquivo_tratado
                    from scripts import importar_escolas
                    importar_escolas.importar_dados(arquivo_tratado)
                else:
                    self.root.quit()
                    return
            
            messagebox.showinfo("Sucesso", "Sistema pronto para uso!")
            
        except Exception as e:
            logger.error(f"Erro ao preparar o sistema: {e}")
            messagebox.showerror("Erro", f"Erro ao preparar o sistema: {str(e)}")
            self.root.quit()

    def abrir_consulta(self):
        """Abre a janela de consulta de escolas"""
        # Cria a janela usando o método de controle
        consulta = self._criar_janela("Consultar Escolas")
        
        # Frame principal
        main_frame = ttk.Frame(consulta, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Componentes
        self.loading = LoadingIndicator(main_frame)
        self.search_frame = SearchFrame(main_frame, self._on_search)
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        colunas = ('ID', 'Nome', 'Município', 'UF', 'Região')
        self.results_table = ResultsTable(results_frame, colunas)
        self.pagination = PaginationFrame(results_frame, self._on_page_change)

    def _on_search(self, termo: str):
        """Callback de busca"""
        try:
            self.loading.start()
            
            # Reseta a paginação
            self.pagination.reset()
            
            # Conta total de resultados
            total = self.db_manager.contar_escolas(termo)
            self.pagination.update_total_items(total)
            
            if total == 0:
                messagebox.showinfo("Busca", "Nenhuma escola encontrada.")
                return
            
            # Busca resultados da primeira página
            results = self.db_manager.buscar_escolas(
                termo, 
                limit=self.pagination.items_per_page,
                offset=self.pagination.get_offset()
            )
            
            self.results_table.update_results(results)
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            messagebox.showerror("Erro", f"Erro ao realizar busca: {str(e)}")
        finally:
            self.loading.stop()
            
    def _on_page_change(self, page: int):
        """Callback de mudança de página"""
        try:
            self.loading.start()
            
            termo = self.search_frame.get_search_term()
            offset = (page - 1) * self.pagination.items_per_page
            
            # Busca resultados da página atual
            results = self.db_manager.buscar_escolas(
                termo, 
                limit=self.pagination.items_per_page,
                offset=offset
            )
            
            self.results_table.update_results(results)
            
        except Exception as e:
            logger.error(f"Erro ao mudar página: {e}")
            messagebox.showerror("Erro", f"Erro ao mudar página: {str(e)}")
        finally:
            self.loading.stop()

    def mostrar_graficos(self):
        """Mostra a janela de gráficos"""
        try:
            # Cria a janela usando o método de controle
            janela_graficos = self._criar_janela("Gráficos - Escolas por Município")
            
            # Notebook para as abas
            notebook = ttk.Notebook(janela_graficos)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Indicador de carregamento
            loading = LoadingIndicator(janela_graficos)
            loading.start()
            
            try:
                # Busca os dados uma única vez
                dados_municipio = self.db_manager.get_estatisticas_municipio()
                
                # 1. Gráfico de Barras
                fig1 = self.graph_manager.plot_municipio_barras(dados_municipio)
                if fig1:
                    tab1 = ttk.Frame(notebook)
                    notebook.add(tab1, text='Gráfico de Barras')
                    canvas1 = FigureCanvasTkAgg(fig1, tab1)
                    canvas1.draw()
                    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # 2. Gráfico de Pizza
                fig2 = self.graph_manager.plot_municipio_pizza(dados_municipio)
                if fig2:
                    tab2 = ttk.Frame(notebook)
                    notebook.add(tab2, text='Gráfico de Pizza')
                    canvas2 = FigureCanvasTkAgg(fig2, tab2)
                    canvas2.draw()
                    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # 3. Gráfico de Linha
                fig3 = self.graph_manager.plot_municipio_linha(dados_municipio)
                if fig3:
                    tab3 = ttk.Frame(notebook)
                    notebook.add(tab3, text='Gráfico de Linha')
                    canvas3 = FigureCanvasTkAgg(fig3, tab3)
                    canvas3.draw()
                    canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Para o indicador de carregamento antes de mostrar os gráficos
                loading.stop()
                
            except Exception as e:
                logger.error(f"Erro ao gerar gráficos: {e}")
                messagebox.showerror("Erro", f"Erro ao gerar gráficos: {str(e)}")
                try:
                    loading.stop()
                except:
                    pass
                self._fechar_janela(janela_graficos)
                
        except Exception as e:
            logger.error(f"Erro ao criar janela de gráficos: {e}")
            messagebox.showerror("Erro", f"Erro ao criar janela de gráficos: {str(e)}")

def verificar_dependencias():
    """Verifica e instala as dependências necessárias"""
    try:
        import matplotlib
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    except ImportError:
        logger.info("Instalando dependências necessárias...")
        try:
            import setup
            setup.instalar_dependencias()
            logger.info("Dependências instaladas com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao instalar dependências: {e}")
            messagebox.showerror("Erro", 
                "Não foi possível instalar as dependências necessárias.\n"
                "Por favor, execute 'pip install -r requirements.txt' manualmente.")
            sys.exit(1)

def main():
    verificar_dependencias()
    root = tk.Tk()
    app = AplicativoEscolas(root)
    root.mainloop()

if __name__ == '__main__':
    main() 