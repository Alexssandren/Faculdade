import re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import seaborn as sns
import pandas as pd
from collections import Counter
import numpy as np
import os
import sys

# Download necessário do NLTK
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

def encontrar_arquivo_html():
    """Encontra o arquivo HTML da história em diferentes localizações possíveis"""
    nome_arquivo = 'Alice_no_Pais_das_Maravilhas.html'
    
    # Possíveis localizações do arquivo
    caminhos_possiveis = [
        nome_arquivo,  # Diretório atual
        os.path.join('.', nome_arquivo),  # Diretório atual explícito
        os.path.join('..', nome_arquivo),  # Diretório pai
        os.path.join(os.path.dirname(__file__), nome_arquivo),  # Mesmo diretório do script
    ]
    
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            print(f"[OK] Arquivo encontrado em: {caminho}")
            return caminho
    
    # Se não encontrou, listar arquivos disponíveis
    print(f"[ERRO] Arquivo '{nome_arquivo}' não encontrado!")
    print("\nArquivos disponíveis no diretório atual:")
    try:
        for arquivo in os.listdir('.'):
            if arquivo.endswith('.html'):
                print(f"  - {arquivo}")
    except:
        pass
    
    raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado em nenhuma localização.")

def extrair_texto_html(arquivo_html):
    try:
        with open(arquivo_html, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            return soup.get_text()
    except UnicodeDecodeError:
        # Tentar com encoding alternativo
        with open(arquivo_html, 'r', encoding='latin-1') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            return soup.get_text()

def criar_nuvem_animais(texto):
    # Converter para minúsculas
    texto = texto.lower()
    
    # Lista de animais mencionados na história
    animais = ['rabbit', 'cat', 'mouse', 'mice', 'bat', 'dormouse', 'caterpillar', 'duchess', 
               'cheshire', 'hatter', 'hare', 'queen', 'king', 'knave',
               'turtle', 'gryphon', 'lobster', 'dodo', 'eaglet', 'lory', 'duck', 'dinah',
               'flamingo', 'hedgehog', 'pig', 'puppy', 'serpent', 'pigeon', 'lizard']
    
    # Tokenização e filtragem
    tokens = word_tokenize(texto)
    stop_words = set(stopwords.words('english'))
    palavras_filtradas = []
    
    for word in tokens:
        if word.lower() in animais and word.lower() not in stop_words:
            palavras_filtradas.append(word.lower())
    
    # Contar frequência
    contador = Counter(palavras_filtradas)
    
    if not palavras_filtradas:
        print("Nenhum animal encontrado no texto!")
        return
    
    # Criar nuvem de palavras
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Set3').generate_from_frequencies(contador)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nuvem de Palavras - Animais em Alice no País das Maravilhas', fontsize=16)
    plt.tight_layout()
    plt.savefig('Nuvem.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[OK] Nuvem de palavras salva como 'Nuvem.png'")

def criar_arvore_rainha_copas(texto):
    # Procurar por falas da rainha
    # Padrões mais flexíveis para capturar falas
    padroes = [
        r'"([^"]*off with.*?head[^"]*)"',
        r'"([^"]*queen[^"]*)"',
        r'"([^"]*majesty[^"]*)"',
        r'"([^"]*sentence[^"]*)"'
    ]
    
    falas = []
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        falas.extend(matches)
    
    if not falas:
        # Se não encontrar falas específicas, vamos procurar palavras relacionadas à rainha
        palavras_rainha = ['queen', 'majesty', 'sentence', 'head', 'court', 'trial', 'execution']
        tokens = word_tokenize(texto.lower())
        stop_words = set(stopwords.words('english'))
        
        palavras_filtradas = []
        for word in tokens:
            if word in palavras_rainha and word not in stop_words:
                palavras_filtradas.append(word)
        
        contador = Counter(palavras_filtradas)
    else:
        # Processar falas encontradas
        palavras = []
        for fala in falas:
            tokens = word_tokenize(fala.lower())
            stop_words = set(stopwords.words('english'))
            palavras_filtradas = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
            palavras.extend(palavras_filtradas)
        
        contador = Counter(palavras)
    
    if not contador:
        print("Nenhuma fala da rainha encontrada!")
        return
    
    # Pegar as 10 palavras mais comuns
    palavras_comuns = contador.most_common(10)
    
    # Criar gráfico de barras
    palavras, frequencias = zip(*palavras_comuns)
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(palavras, frequencias, color='crimson', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.title('Árvore de Palavras - Contexto da Rainha de Copas', fontsize=16)
    plt.xlabel('Palavras')
    plt.ylabel('Frequência')
    
    # Adicionar valores nas barras
    for bar, freq in zip(bars, frequencias):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(freq), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('arvore.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[OK] Árvore de palavras salva como 'arvore.png'")

def criar_mapa_calor_paragrafos(arquivo_html):
    try:
        with open(arquivo_html, 'r', encoding='utf-8') as file:
            conteudo = file.read()
    except UnicodeDecodeError:
        with open(arquivo_html, 'r', encoding='latin-1') as file:
            conteudo = file.read()
    
    # Encontrar capítulos usando padrão mais específico
    capitulos = re.split(r'<h3[^>]*>CHAPTER [IVX]+', conteudo)[1:]
    
    if not capitulos:
        # Tentar outro padrão
        capitulos = re.split(r'CHAPTER [IVX]+', conteudo)[1:]
    
    if not capitulos:
        print("Nenhum capítulo encontrado!")
        return
    
    # Contar parágrafos por capítulo
    paragrafos_por_capitulo = []
    nomes_capitulos = []
    
    for i, capitulo in enumerate(capitulos[:12]):  # Limitar a 12 capítulos
        paragrafos = len(re.findall(r'<p[^>]*>', capitulo))
        paragrafos_por_capitulo.append(paragrafos)
        nomes_capitulos.append(f'Cap {i+1}')
    
    if not paragrafos_por_capitulo:
        print("Nenhum parágrafo encontrado nos capítulos!")
        return
    
    # Criar DataFrame
    df = pd.DataFrame({
        'Capítulo': nomes_capitulos,
        'Parágrafos': paragrafos_por_capitulo
    })
    
    # Criar matriz para o heatmap
    matriz = np.array(paragrafos_por_capitulo).reshape(1, -1)
    
    # Criar mapa de calor
    plt.figure(figsize=(14, 3))
    sns.heatmap(matriz, 
                xticklabels=nomes_capitulos,
                yticklabels=['Parágrafos'],
                cmap='YlOrRd', 
                annot=True, 
                fmt='d',
                cbar_kws={'label': 'Número de Parágrafos'})
    plt.title('Mapa de Calor - Quantidade de Parágrafos por Capítulo', fontsize=16)
    plt.tight_layout()
    plt.savefig('Calor.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[OK] Mapa de calor salvo como 'Calor.png'")
    print(f"[DADOS] {dict(zip(nomes_capitulos, paragrafos_por_capitulo))}")

def main():
    print("GERADOR DE VISUALIZACOES - ALICE NO PAIS DAS MARAVILHAS")
    print("=" * 60)
    
    try:
        # Encontrar o arquivo HTML
        arquivo_html = encontrar_arquivo_html()
        
        # Extrair texto
        print("Extraindo texto da história...")
        texto = extrair_texto_html(arquivo_html)
        
        print("Criando nuvem de palavras com animais...")
        criar_nuvem_animais(texto)
        
        print("Criando árvore de palavras da Rainha de Copas...")
        criar_arvore_rainha_copas(texto)
        
        print("Criando mapa de calor dos parágrafos...")
        criar_mapa_calor_paragrafos(arquivo_html)
        
        print("=" * 60)
        print("TODOS OS GRAFICOS FORAM GERADOS COM SUCESSO!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"[ERRO] {e}")
        print("\nSOLUCOES:")
        print("1. Certifique-se de que o arquivo 'Alice_no_Pais_das_Maravilhas.html' está no mesmo diretório")
        print("2. Execute o script a partir do diretório 'Codigo dataset e graficos'")
        print("3. Verifique se o nome do arquivo está correto")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO INESPERADO] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 