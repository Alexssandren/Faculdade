import sqlite3
from typing import List, Tuple, Optional
import logging
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Caminho padrão relativo à raiz do projeto
            db_path = os.path.join('data', 'processed', 'escolas.db')
        self.db_path = db_path
        
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def buscar_escolas(self, termo: str, limit: int = 50, offset: int = 0) -> List[Tuple]:
        """Busca escolas com paginação"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        e.id_escola,
                        e.nome_escola,
                        m.nome_municipio,
                        u.sigla_uf,
                        r.nome_regiao
                    FROM escola e
                    JOIN municipio m ON e.id_municipio = m.id_municipio
                    JOIN uf u ON m.id_uf = u.id_uf
                    JOIN regiao r ON u.id_regiao = r.id_regiao
                    WHERE e.nome_escola LIKE ?
                    ORDER BY e.nome_escola
                    LIMIT ? OFFSET ?
                ''', (f'%{termo}%', limit, offset))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar escolas: {e}")
            raise

    def contar_escolas(self, termo: str) -> int:
        """Conta o total de escolas para uma busca"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM escola e
                    WHERE e.nome_escola LIKE ?
                ''', (f'%{termo}%',))
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Erro ao contar escolas: {e}")
            raise

    def get_estatisticas_regiao(self) -> List[Tuple]:
        """Retorna estatísticas de escolas por região"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.nome_regiao, COUNT(e.id_escola) as total
                    FROM regiao r
                    JOIN uf u ON r.id_regiao = u.id_regiao
                    JOIN municipio m ON u.id_uf = m.id_uf
                    JOIN escola e ON m.id_municipio = e.id_municipio
                    GROUP BY r.nome_regiao
                    ORDER BY total DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter estatísticas por região: {e}")
            raise

    def get_estatisticas_uf(self, limit: int = 10) -> List[Tuple]:
        """Retorna estatísticas de escolas por UF"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.sigla_uf, COUNT(e.id_escola) as total
                    FROM uf u
                    JOIN municipio m ON u.id_uf = m.id_uf
                    JOIN escola e ON m.id_municipio = e.id_municipio
                    GROUP BY u.sigla_uf
                    ORDER BY total DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter estatísticas por UF: {e}")
            raise

    def get_estatisticas_municipio(self, limit: int = 10) -> List[Tuple]:
        """Retorna estatísticas de escolas por município"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        m.nome_municipio || ' - ' || u.sigla_uf as municipio,
                        COUNT(e.id_escola) as total
                    FROM municipio m
                    JOIN uf u ON m.id_uf = u.id_uf
                    JOIN escola e ON m.id_municipio = e.id_municipio
                    GROUP BY m.id_municipio
                    ORDER BY total DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter estatísticas por município: {e}")
            raise 