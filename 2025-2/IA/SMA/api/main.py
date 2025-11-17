"""API REST principal usando FastAPI"""
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from models.database import get_db
from models.portfolio import Carteira, Ativo, Posicao, Transacao, ConfiguracaoDiversificacao
from models.market import Alerta, IndicadorMercado
from api.routes import portfolio, market, alerts
import json
from typing import List
from datetime import datetime

app = FastAPI(title="SMA Portfolio Management System")

# Monta rotas estáticas
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Inclui rotas
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])


# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve a página principal"""
    with open("web/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para atualizações em tempo real"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo para teste
            await websocket.send_json({"message": "Connected", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/status")
async def get_status(db: Session = Depends(get_db)):
    """Retorna status geral do sistema"""
    carteira = db.query(Carteira).first()
    total_ativos = db.query(Ativo).count()
    total_posicoes = db.query(Posicao).count()
    total_transacoes = db.query(Transacao).count()
    alertas_ativos = db.query(Alerta).filter(Alerta.resolvido == 0).count()
    
    return {
        "carteira": {
            "saldo_disponivel": carteira.saldo_disponivel if carteira else 0.0,
            "valor_total": carteira.valor_total_carteira if carteira else 0.0
        },
        "estatisticas": {
            "total_ativos": total_ativos,
            "total_posicoes": total_posicoes,
            "total_transacoes": total_transacoes,
            "alertas_ativos": alertas_ativos
        }
    }


# Função para broadcast de atualizações (será chamada pelos agentes)
async def broadcast_update(update_type: str, data: dict):
    """Envia atualização para todos os clientes WebSocket conectados"""
    await manager.broadcast({
        "type": update_type,
        "data": data,
        "timestamp": json.dumps(datetime.utcnow().isoformat())
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

