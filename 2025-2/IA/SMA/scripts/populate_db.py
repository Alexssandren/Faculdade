"""Script para popular o banco de dados com dados iniciais"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from sqlalchemy import delete
from models.database import SessionLocal, init_db
from models.portfolio import (
    Carteira, ConfiguracaoDiversificacao, TipoAtivo,
    Ativo, Posicao, Transacao
)
from models.market import IndicadorMercado, Alerta
from services.market_simulator import MarketSimulator
from services.logger import system_logger
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CASH = float(os.getenv("DEFAULT_CASH", "50000.0"))


def populate_database():
    """Popula o banco de dados com dados iniciais"""
    system_logger.info("Iniciando população do banco de dados...")
    
    # Inicializa o banco
    init_db()
    
    db = SessionLocal()
    try:
        # ZERA TODAS AS TABELAS para garantir reset completo
        system_logger.info("Zerando todas as tabelas do banco de dados...")
        
        # Deleta todos os registros de todas as tabelas (respeitando foreign keys)
        db.execute(delete(Transacao))
        db.execute(delete(Posicao))
        db.execute(delete(Alerta))
        db.execute(delete(IndicadorMercado))
        db.execute(delete(ConfiguracaoDiversificacao))
        db.execute(delete(Ativo))
        db.execute(delete(Carteira))
        
        db.commit()
        system_logger.info("Todas as tabelas foram zeradas com sucesso!")
        
        # Cria carteira inicial com R$ 50.000,00 em saldo e 0 em valor total (sem investimentos)
        carteira = Carteira(
            saldo_disponivel=DEFAULT_CASH,
            valor_total_carteira=DEFAULT_CASH  # Começa igual ao saldo (será atualizado quando houver posições)
        )
        db.add(carteira)
        db.commit()
        system_logger.info(f"Carteira criada: saldo disponível R$ {DEFAULT_CASH:.2f}, valor total R$ {DEFAULT_CASH:.2f}")
        
        # Cria ativos de exemplo
        MarketSimulator.create_sample_assets(db)
        
        # Cria indicadores de exemplo
        MarketSimulator.create_sample_indicators(db)
        
        # Cria configurações de diversificação padrão
        configs_padrao = [
            {"tipo": TipoAtivo.ACAO, "porcentagem": 40.0, "tolerancia": 5.0},
            {"tipo": TipoAtivo.RENDA_FIXA, "porcentagem": 30.0, "tolerancia": 5.0},
            {"tipo": TipoAtivo.CRIPTO, "porcentagem": 20.0, "tolerancia": 5.0},
            {"tipo": TipoAtivo.FUNDO, "porcentagem": 10.0, "tolerancia": 5.0},
        ]
        
        for config_data in configs_padrao:
            existente = db.query(ConfiguracaoDiversificacao).filter(
                ConfiguracaoDiversificacao.tipo_ativo == config_data["tipo"]
            ).first()
            
            if not existente:
                config = ConfiguracaoDiversificacao(
                    tipo_ativo=config_data["tipo"],
                    porcentagem_alvo=config_data["porcentagem"],
                    tolerancia=config_data["tolerancia"]
                )
                db.add(config)
        
        db.commit()
        system_logger.info("Configurações de diversificação criadas")
        
        system_logger.info("Banco de dados populado com sucesso!")
        
    except Exception as e:
        db.rollback()
        system_logger.error(f"Erro ao popular banco de dados: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()

