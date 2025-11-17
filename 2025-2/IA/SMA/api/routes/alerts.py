"""Rotas relacionadas a alertas"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.market import Alerta

router = APIRouter()


@router.get("/")
async def get_alertas(limit: int = 20, resolvido: bool = None, db: Session = Depends(get_db)):
    """Retorna alertas do sistema"""
    query = db.query(Alerta)
    
    if resolvido is not None:
        query = query.filter(Alerta.resolvido == (1 if resolvido else 0))
    
    alertas = query.order_by(Alerta.timestamp.desc()).limit(limit).all()
    
    resultado = []
    for alerta in alertas:
        resultado.append({
            "id": alerta.id,
            "agente_origem": alerta.agente_origem,
            "tipo": alerta.tipo,
            "mensagem": alerta.mensagem,
            "severidade": alerta.severidade,
            "resolvido": bool(alerta.resolvido),
            "timestamp": alerta.timestamp.isoformat() if alerta.timestamp else None
        })
    
    return {"alertas": resultado}


@router.post("/{alerta_id}/resolver")
async def resolver_alerta(alerta_id: int, db: Session = Depends(get_db)):
    """Marca um alerta como resolvido"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        return {"error": "Alerta não encontrado"}
    
    alerta.resolvido = 1
    db.commit()
    
    return {"message": "Alerta resolvido", "alerta_id": alerta_id}

