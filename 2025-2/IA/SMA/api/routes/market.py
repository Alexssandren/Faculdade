"""Rotas relacionadas ao mercado"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.portfolio import Ativo
from models.market import IndicadorMercado

router = APIRouter()


@router.get("/ativos")
async def get_ativos(db: Session = Depends(get_db)):
    """Retorna todos os ativos disponíveis"""
    ativos = db.query(Ativo).all()
    
    resultado = []
    for ativo in ativos:
        resultado.append({
            "id": ativo.id,
            "codigo": ativo.codigo,
            "nome": ativo.nome,
            "tipo": ativo.tipo.value,
            "preco_atual": ativo.preco_atual,
            "preco_anterior": ativo.preco_anterior,
            "variacao_percentual": ativo.variacao_percentual,
            "updated_at": ativo.updated_at.isoformat() if ativo.updated_at else None
        })
    
    return {"ativos": resultado}


@router.get("/indicadores")
async def get_indicadores(db: Session = Depends(get_db)):
    """Retorna indicadores macroeconômicos"""
    indicadores = db.query(IndicadorMercado).all()
    
    resultado = []
    for ind in indicadores:
        resultado.append({
            "nome": ind.nome,
            "valor": ind.valor,
            "variacao": ind.variacao,
            "timestamp": ind.timestamp.isoformat() if ind.timestamp else None
        })
    
    return {"indicadores": resultado}

