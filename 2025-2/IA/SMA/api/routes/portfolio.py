"""Rotas relacionadas ao portfólio"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.portfolio import Carteira, Posicao, Transacao, Ativo, ConfiguracaoDiversificacao
from typing import List
from pydantic import BaseModel

router = APIRouter()


class DistribuicaoResponse(BaseModel):
    tipo_ativo: str
    valor: float
    porcentagem: float


@router.get("/carteira")
async def get_carteira(db: Session = Depends(get_db)):
    """Retorna informações da carteira"""
    carteira = db.query(Carteira).first()
    if not carteira:
        return {"saldo_disponivel": 0.0, "valor_total": 0.0}
    
    return {
        "saldo_disponivel": carteira.saldo_disponivel,
        "valor_total": carteira.valor_total_carteira,
        "updated_at": carteira.updated_at.isoformat() if carteira.updated_at else None
    }


@router.get("/distribuicao")
async def get_distribuicao(db: Session = Depends(get_db)):
    """Retorna distribuição atual da carteira por tipo de ativo"""
    carteira = db.query(Carteira).first()
    if not carteira:
        return {"distribuicao": []}
    
    posicoes = db.query(Posicao).join(Ativo).all()
    
    # Usa valor_total_carteira, ou saldo_disponivel se valor_total for 0 (carteira vazia)
    valor_total = carteira.valor_total_carteira
    if valor_total == 0:
        valor_total = carteira.saldo_disponivel
    
    # Se ainda não há valor, retorna vazio
    if valor_total == 0:
        return {"distribuicao": []}
    
    distribuicao = {}
    for posicao in posicoes:
        tipo = posicao.ativo.tipo.value
        if tipo not in distribuicao:
            distribuicao[tipo] = {"valor": 0.0, "porcentagem": 0.0}
        # Usa valor atual de mercado (quantidade * preco_atual), não o custo médio
        valor_atual = posicao.quantidade * posicao.ativo.preco_atual
        distribuicao[tipo]["valor"] += valor_atual
    
    # Calcula porcentagens
    resultado = []
    for tipo, dados in distribuicao.items():
        dados["porcentagem"] = (dados["valor"] / valor_total) * 100 if valor_total > 0 else 0
        resultado.append({
            "tipo_ativo": tipo,
            "valor": dados["valor"],
            "porcentagem": dados["porcentagem"]
        })
    
    return {"distribuicao": resultado}


@router.get("/posicoes")
async def get_posicoes(db: Session = Depends(get_db)):
    """Retorna todas as posições da carteira"""
    posicoes = db.query(Posicao).join(Ativo).all()
    
    resultado = []
    for posicao in posicoes:
        resultado.append({
            "id": posicao.id,
            "ativo_codigo": posicao.ativo.codigo,
            "ativo_nome": posicao.ativo.nome,
            "tipo": posicao.ativo.tipo.value,
            "quantidade": posicao.quantidade,
            "preco_medio": posicao.preco_medio,
            "preco_atual": posicao.ativo.preco_atual,
            "valor_total": posicao.valor_total,
            "variacao_percentual": posicao.ativo.variacao_percentual
        })
    
    return {"posicoes": resultado}


@router.get("/transacoes")
async def get_transacoes(limit: int = 50, db: Session = Depends(get_db)):
    """Retorna histórico de transações"""
    transacoes = db.query(Transacao).join(Ativo).order_by(
        Transacao.timestamp.desc()
    ).limit(limit).all()
    
    resultado = []
    for transacao in transacoes:
        resultado.append({
            "id": transacao.id,
            "ativo_codigo": transacao.ativo.codigo,
            "ativo_nome": transacao.ativo.nome,
            "tipo": transacao.tipo.value,
            "quantidade": transacao.quantidade,
            "preco_unitario": transacao.preco_unitario,
            "valor_total": transacao.valor_total,
            "timestamp": transacao.timestamp.isoformat()
        })
    
    return {"transacoes": resultado}


@router.get("/configuracao-diversificacao")
async def get_configuracao_diversificacao(db: Session = Depends(get_db)):
    """Retorna configuração de diversificação alvo"""
    configs = db.query(ConfiguracaoDiversificacao).all()
    
    resultado = []
    for config in configs:
        resultado.append({
            "tipo_ativo": config.tipo_ativo.value,
            "porcentagem_alvo": config.porcentagem_alvo,
            "tolerancia": config.tolerancia
        })
    
    return {"configuracao": resultado}

