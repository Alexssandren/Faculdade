"""Modelos relacionados à carteira de investimentos"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from models.database import Base


class TipoAtivo(enum.Enum):
    """Tipos de ativos disponíveis"""
    ACAO = "Ação"
    RENDA_FIXA = "Renda Fixa"
    CRIPTO = "Criptomoeda"
    FUNDO = "Fundo de Investimento"


class TipoOperacao(enum.Enum):
    """Tipos de operações"""
    COMPRA = "Compra"
    VENDA = "Venda"


class Ativo(Base):
    """Modelo de ativo financeiro"""
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(Enum(TipoAtivo), nullable=False)
    preco_atual = Column(Float, nullable=False, default=0.0)
    preco_anterior = Column(Float, nullable=False, default=0.0)
    variacao_percentual = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    posicoes = relationship("Posicao", back_populates="ativo")
    transacoes = relationship("Transacao", back_populates="ativo")

    def __repr__(self):
        return f"<Ativo(codigo={self.codigo}, tipo={self.tipo.value}, preco={self.preco_atual})>"


class Posicao(Base):
    """Modelo de posição na carteira"""
    __tablename__ = "posicoes"

    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    quantidade = Column(Float, nullable=False, default=0.0)
    preco_medio = Column(Float, nullable=False, default=0.0)
    valor_total = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    ativo = relationship("Ativo", back_populates="posicoes")

    def __repr__(self):
        return f"<Posicao(ativo_id={self.ativo_id}, quantidade={self.quantidade}, valor={self.valor_total})>"


class Transacao(Base):
    """Modelo de transação realizada"""
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    tipo = Column(Enum(TipoOperacao), nullable=False)
    quantidade = Column(Float, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    ativo = relationship("Ativo", back_populates="transacoes")

    def __repr__(self):
        return f"<Transacao(tipo={self.tipo.value}, ativo_id={self.ativo_id}, valor={self.valor_total})>"


class Carteira(Base):
    """Modelo de carteira de investimentos"""
    __tablename__ = "carteira"

    id = Column(Integer, primary_key=True, index=True)
    saldo_disponivel = Column(Float, nullable=False, default=0.0)
    valor_total_carteira = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Carteira(saldo={self.saldo_disponivel}, valor_total={self.valor_total_carteira})>"


class ConfiguracaoDiversificacao(Base):
    """Configuração de diversificação desejada por tipo de ativo"""
    __tablename__ = "configuracao_diversificacao"

    id = Column(Integer, primary_key=True, index=True)
    tipo_ativo = Column(Enum(TipoAtivo), unique=True, nullable=False)
    porcentagem_alvo = Column(Float, nullable=False)  # 0.0 a 100.0
    tolerancia = Column(Float, default=5.0)  # Tolerância em porcentagem
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ConfiguracaoDiversificacao(tipo={self.tipo_ativo.value}, alvo={self.porcentagem_alvo}%)>"

