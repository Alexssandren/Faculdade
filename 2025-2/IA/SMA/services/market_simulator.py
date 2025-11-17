"""Simulador de mercado para gerar variações de preços em tempo real"""
import asyncio
import random
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.portfolio import Ativo
from models.market import IndicadorMercado
from services.logger import system_logger
from datetime import datetime


class MarketSimulator:
    """Simula variações de preços e indicadores de mercado"""
    
    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval
        self.running = False
        self.volatilidade_base = {
            "Ação": 0.02,  # 2% de volatilidade média
            "Renda Fixa": 0.001,  # 0.1% de volatilidade média
            "Criptomoeda": 0.05,  # 5% de volatilidade média
            "Fundo de Investimento": 0.01  # 1% de volatilidade média
        }

    async def start(self):
        """Inicia o simulador"""
        self.running = True
        system_logger.info("MarketSimulator iniciado")
        asyncio.create_task(self._simulation_loop())

    async def stop(self):
        """Para o simulador"""
        self.running = False
        system_logger.info("MarketSimulator parado")

    async def _simulation_loop(self):
        """Loop principal de simulação"""
        while self.running:
            try:
                await self._update_prices()
                await self._update_indicators()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                system_logger.error(f"Erro no simulador: {e}")
                await asyncio.sleep(self.update_interval)

    async def _update_prices(self):
        """Atualiza preços dos ativos"""
        db = SessionLocal()
        try:
            ativos = db.query(Ativo).all()
            
            for ativo in ativos:
                volatilidade = self.volatilidade_base.get(
                    ativo.tipo.value, 
                    0.01
                )
                
                # Gera variação aleatória baseada na volatilidade
                variacao = random.gauss(0, volatilidade)
                
                # Atualiza preço
                preco_anterior = ativo.preco_atual
                novo_preco = preco_anterior * (1 + variacao)
                
                # Garante que o preço não fique negativo
                if novo_preco < 0.01:
                    novo_preco = 0.01
                
                ativo.preco_anterior = preco_anterior
                ativo.preco_atual = novo_preco
                ativo.variacao_percentual = variacao * 100
                ativo.updated_at = datetime.utcnow()
            
            db.commit()
            system_logger.debug(f"Preços atualizados para {len(ativos)} ativos")
        except Exception as e:
            db.rollback()
            system_logger.error(f"Erro ao atualizar preços: {e}")
        finally:
            db.close()

    async def _update_indicators(self):
        """Atualiza indicadores macroeconômicos"""
        db = SessionLocal()
        try:
            indicadores = db.query(IndicadorMercado).all()
            
            for ind in indicadores:
                # Variação pequena para indicadores
                variacao = random.gauss(0, 0.001)
                ind.valor = ind.valor * (1 + variacao)
                ind.variacao = variacao * 100
                ind.timestamp = datetime.utcnow()
            
            db.commit()
        except Exception as e:
            db.rollback()
            system_logger.error(f"Erro ao atualizar indicadores: {e}")
        finally:
            db.close()

    @staticmethod
    def create_sample_assets(db: Session):
        """Cria ativos de exemplo"""
        from models.portfolio import TipoAtivo
        
        ativos_exemplo = [
            # Ações
            {"codigo": "PETR4", "nome": "Petrobras PN", "tipo": TipoAtivo.ACAO, "preco": 32.50},
            {"codigo": "VALE3", "nome": "Vale ON", "tipo": TipoAtivo.ACAO, "preco": 68.90},
            {"codigo": "ITUB4", "nome": "Itaú PN", "tipo": TipoAtivo.ACAO, "preco": 28.75},
            {"codigo": "BBDC4", "nome": "Bradesco PN", "tipo": TipoAtivo.ACAO, "preco": 15.20},
            {"codigo": "ABEV3", "nome": "Ambev ON", "tipo": TipoAtivo.ACAO, "preco": 12.85},
            
            # Renda Fixa
            {"codigo": "CDB001", "nome": "CDB Banco XYZ 120% CDI", "tipo": TipoAtivo.RENDA_FIXA, "preco": 1000.0},
            {"codigo": "LCI001", "nome": "LCI Banco ABC", "tipo": TipoAtivo.RENDA_FIXA, "preco": 1000.0},
            {"codigo": "TESOURO", "nome": "Tesouro IPCA+ 2029", "tipo": TipoAtivo.RENDA_FIXA, "preco": 950.0},
            
            # Criptomoedas
            {"codigo": "BTC", "nome": "Bitcoin", "tipo": TipoAtivo.CRIPTO, "preco": 250000.0},
            {"codigo": "ETH", "nome": "Ethereum", "tipo": TipoAtivo.CRIPTO, "preco": 15000.0},
            
            # Fundos
            {"codigo": "FUND001", "nome": "Fundo Multimercado XYZ", "tipo": TipoAtivo.FUNDO, "preco": 100.0},
            {"codigo": "FUND002", "nome": "Fundo de Ações ABC", "tipo": TipoAtivo.FUNDO, "preco": 150.0},
        ]
        
        for ativo_data in ativos_exemplo:
            # Verifica se já existe
            existente = db.query(Ativo).filter(
                Ativo.codigo == ativo_data["codigo"]
            ).first()
            
            if not existente:
                ativo = Ativo(
                    codigo=ativo_data["codigo"],
                    nome=ativo_data["nome"],
                    tipo=ativo_data["tipo"],
                    preco_atual=ativo_data["preco"],
                    preco_anterior=ativo_data["preco"],
                    variacao_percentual=0.0
                )
                db.add(ativo)
        
        db.commit()
        system_logger.info(f"Criados {len(ativos_exemplo)} ativos de exemplo")

    @staticmethod
    def create_sample_indicators(db: Session):
        """Cria indicadores de exemplo"""
        indicadores_exemplo = [
            {"nome": "Selic", "valor": 10.75},
            {"nome": "IPCA", "valor": 4.62},
            {"nome": "IBOVESPA", "valor": 125000.0},
            {"nome": "Dólar", "valor": 5.15},
        ]
        
        for ind_data in indicadores_exemplo:
            existente = db.query(IndicadorMercado).filter(
                IndicadorMercado.nome == ind_data["nome"]
            ).first()
            
            if not existente:
                indicador = IndicadorMercado(
                    nome=ind_data["nome"],
                    valor=ind_data["valor"],
                    variacao=0.0
                )
                db.add(indicador)
        
        db.commit()
        system_logger.info(f"Criados {len(indicadores_exemplo)} indicadores de exemplo")

