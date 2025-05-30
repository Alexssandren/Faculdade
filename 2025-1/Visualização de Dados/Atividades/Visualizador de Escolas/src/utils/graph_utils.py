import matplotlib.pyplot as plt
from typing import List, Tuple
import os
import json
from datetime import datetime, timedelta
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphManager:
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def _get_cache_path(self, graph_type: str) -> str:
        """Retorna o caminho do arquivo de cache para um tipo de gráfico"""
        return os.path.join(self.cache_dir, f'{graph_type}_cache.json')
    
    def _is_cache_valid(self, cache_path: str, max_age_minutes: int = 30) -> bool:
        """Verifica se o cache ainda é válido"""
        if not os.path.exists(cache_path):
            return False
            
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - cache_time
        return age < timedelta(minutes=max_age_minutes)
    
    def _save_cache(self, data: List[Tuple], graph_type: str):
        """Salva dados no cache"""
        cache_path = self._get_cache_path(graph_type)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def _load_cache(self, graph_type: str) -> List[Tuple]:
        """Carrega dados do cache"""
        cache_path = self._get_cache_path(graph_type)
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            return None
    
    def plot_regiao(self, data: List[Tuple], use_cache: bool = True) -> plt.Figure:
        """Gera gráfico de escolas por região"""
        graph_type = 'regiao'
        
        if use_cache and self._is_cache_valid(self._get_cache_path(graph_type)):
            data = self._load_cache(graph_type)
        elif data:
            self._save_cache(data, graph_type)
            
        if not data:
            logger.error("Dados não disponíveis para gerar gráfico")
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        regioes = [r[0] for r in data]
        totais = [r[1] for r in data]
        
        ax.bar(regioes, totais)
        ax.set_title('Número de Escolas por Região')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_uf(self, data: List[Tuple], use_cache: bool = True) -> plt.Figure:
        """Gera gráfico de escolas por UF"""
        graph_type = 'uf'
        
        if use_cache and self._is_cache_valid(self._get_cache_path(graph_type)):
            data = self._load_cache(graph_type)
        elif data:
            self._save_cache(data, graph_type)
            
        if not data:
            logger.error("Dados não disponíveis para gerar gráfico")
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        ufs = [r[0] for r in data]
        totais = [r[1] for r in data]
        
        ax.bar(ufs, totais)
        ax.set_title('Número de Escolas por UF (Top 10)')
        plt.tight_layout()
        
        return fig
    
    def plot_municipio_barras(self, data: List[Tuple], use_cache: bool = True) -> plt.Figure:
        """Gera gráfico de barras de escolas por município"""
        graph_type = 'municipio_barras'
        
        if use_cache and self._is_cache_valid(self._get_cache_path(graph_type)):
            data = self._load_cache(graph_type)
        elif data:
            self._save_cache(data, graph_type)
            
        if not data:
            logger.error("Dados não disponíveis para gerar gráfico")
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        municipios = [r[0] for r in data]
        totais = [r[1] for r in data]
        
        ax.bar(municipios, totais, color='skyblue')
        ax.set_title('Número de Escolas por Município (Top 10)')
        ax.tick_params(axis='x', rotation=45)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        
        # Adiciona valores sobre as barras
        for i, v in enumerate(totais):
            ax.text(i, v, str(v), ha='center', va='bottom')
            
        plt.tight_layout()
        return fig
    
    def plot_municipio_pizza(self, data: List[Tuple], use_cache: bool = True) -> plt.Figure:
        """Gera gráfico de pizza de escolas por município"""
        graph_type = 'municipio_pizza'
        
        if use_cache and self._is_cache_valid(self._get_cache_path(graph_type)):
            data = self._load_cache(graph_type)
        elif data:
            self._save_cache(data, graph_type)
            
        if not data:
            logger.error("Dados não disponíveis para gerar gráfico")
            return None
            
        fig, ax = plt.subplots(figsize=(10, 8))
        municipios = [r[0] for r in data]
        totais = [r[1] for r in data]
        
        # Calcula as porcentagens
        total = sum(totais)
        percentuais = [f'{(v/total)*100:.1f}%' for v in totais]
        
        # Cria o gráfico de pizza
        wedges, texts, autotexts = ax.pie(totais, labels=municipios, autopct='%1.1f%%',
                                        textprops={'fontsize': 8})
        
        # Ajusta a legenda
        ax.legend(wedges, [f'{m} ({p})' for m, p in zip(municipios, percentuais)],
                 title="Municípios",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        ax.set_title('Distribuição de Escolas por Município (Top 10)')
        plt.tight_layout()
        return fig
    
    def plot_municipio_linha(self, data: List[Tuple], use_cache: bool = True) -> plt.Figure:
        """Gera gráfico de linha de escolas por município"""
        graph_type = 'municipio_linha'
        
        if use_cache and self._is_cache_valid(self._get_cache_path(graph_type)):
            data = self._load_cache(graph_type)
        elif data:
            self._save_cache(data, graph_type)
            
        if not data:
            logger.error("Dados não disponíveis para gerar gráfico")
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        municipios = [r[0] for r in data]
        totais = [r[1] for r in data]
        
        # Cria o gráfico de linha com marcadores
        ax.plot(municipios, totais, marker='o', linestyle='-', linewidth=2, markersize=8)
        
        # Adiciona valores sobre os pontos
        for i, v in enumerate(totais):
            ax.text(i, v, str(v), ha='center', va='bottom')
        
        ax.set_title('Tendência do Número de Escolas por Município (Top 10)')
        ax.tick_params(axis='x', rotation=45)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
            
        # Adiciona grade
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig 