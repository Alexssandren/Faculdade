"""Modelos relacionados ao mercado financeiro"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from models.database import Base


class IndicadorMercado(Base):
    """Indicadores macroeconômicos simulados"""
    __tablename__ = "indicadores_mercado"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)  # Ex: "Selic", "IPCA", "IBOVESPA"
    valor = Column(Float, nullable=False)
    variacao = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IndicadorMercado(nome={self.nome}, valor={self.valor})>"


class Alerta(Base):
    """Alertas gerados pelos agentes"""
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    agente_origem = Column(String, nullable=False)  # "WalletManager", "MarketAnalyst", "PortfolioManager"
    tipo = Column(String, nullable=False)  # "liquidez_baixa", "diversificacao_desbalanceada", "oportunidade", etc.
    mensagem = Column(Text, nullable=False)
    severidade = Column(String, default="info")  # "info", "warning", "critical"
    resolvido = Column(Integer, default=0)  # 0 = não resolvido, 1 = resolvido
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alerta(agente={self.agente_origem}, tipo={self.tipo}, severidade={self.severidade})>"

