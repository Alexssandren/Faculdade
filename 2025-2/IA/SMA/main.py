"""Ponto de entrada principal do sistema multiagente"""
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from agents.wallet_manager import WalletManager
from agents.market_analyst import MarketAnalyst
from agents.portfolio_manager import PortfolioManager
from services.market_simulator import MarketSimulator
from services.logger import system_logger
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models.database import get_db
from models.portfolio import Carteira, Ativo, Posicao, Transacao, ConfiguracaoDiversificacao
from models.market import Alerta, IndicadorMercado
from api.routes import portfolio, market, alerts
import json
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))


# Instâncias globais dos agentes
wallet_manager = None
market_analyst = None
portfolio_manager = None
market_simulator = None


async def start_agents():
    """Inicia todos os agentes do sistema"""
    global wallet_manager, market_analyst, portfolio_manager, market_simulator
    
    system_logger.info("Iniciando agentes do sistema...")
    
    # Cria instâncias dos agentes
    wallet_manager = WalletManager()
    market_analyst = MarketAnalyst()
    portfolio_manager = PortfolioManager()
    market_simulator = MarketSimulator(update_interval=UPDATE_INTERVAL)
    
    # Inicia os agentes
    await wallet_manager.start()
    await market_analyst.start()
    await portfolio_manager.start()
    await market_simulator.start()
    
    # Inicia loops de execução dos agentes
    asyncio.create_task(wallet_manager.run_cycle())
    asyncio.create_task(market_analyst.run_cycle())
    asyncio.create_task(portfolio_manager.run_cycle())
    
    system_logger.info("Todos os agentes iniciados com sucesso!")


async def stop_agents():
    """Para todos os agentes do sistema"""
    global wallet_manager, market_analyst, portfolio_manager, market_simulator
    
    system_logger.info("Parando agentes do sistema...")
    
    if wallet_manager:
        await wallet_manager.stop()
    if market_analyst:
        await market_analyst.stop()
    if portfolio_manager:
        await portfolio_manager.stop()
    if market_simulator:
        await market_simulator.stop()
    
    system_logger.info("Todos os agentes parados.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    await start_agents()
    yield
    # Shutdown
    await stop_agents()


# Cria aplicação FastAPI com lifespan
app = FastAPI(title="SMA Portfolio Management System", lifespan=lifespan)

# Monta rotas estáticas
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
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
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web", "templates", "index.html")
    
    if not os.path.exists(file_path):
        return HTMLResponse(
            content=f"<h1>Erro</h1><p>Arquivo não encontrado: {file_path}</p>",
            status_code=404
        )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Erro</h1><p>Erro ao ler arquivo: {str(e)}</p>",
            status_code=500
        )


# Inclui rotas da API (depois da rota raiz para não conflitar)
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])


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


def main():
    """Função principal"""
    system_logger.info("Iniciando Sistema Multiagente de Gestão de Carteira...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

