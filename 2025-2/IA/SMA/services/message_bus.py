"""Sistema de mensageria para comunicação entre agentes"""
import asyncio
from typing import Dict, List, Callable, Any
from enum import Enum
from datetime import datetime
from services.logger import system_logger


class MessageType(Enum):
    """Tipos de mensagens entre agentes"""
    # WalletManager
    SALDO_ATUALIZADO = "saldo_atualizado"
    LIMITE_DEFINIDO = "limite_definido"
    AUTORIZACAO_COMPRA = "autorizacao_compra"
    AUTORIZACAO_VENDA = "autorizacao_venda"
    ALERTA_LIQUIDEZ = "alerta_liquidez"
    
    # MarketAnalyst
    DADOS_MERCADO = "dados_mercado"
    ANALISE_TENDENCIA = "analise_tendencia"
    SINAL_COMPRA = "sinal_compra"
    SINAL_VENDA = "sinal_venda"
    ALERTA_RISCO = "alerta_risco"
    RELATORIO_MERCADO = "relatorio_mercado"
    
    # PortfolioManager
    DISTRIBUICAO_CARTEIRA = "distribuicao_carteira"
    OPERACAO_EXECUTADA = "operacao_executada"
    SOLICITACAO_AUTORIZACAO = "solicitacao_autorizacao"
    SOLICITACAO_ANALISE = "solicitacao_analise"
    RELATORIO_PORTFOLIO = "relatorio_portfolio"


class Message:
    """Classe para representar uma mensagem entre agentes"""
    def __init__(
        self,
        message_type: MessageType,
        sender: str,
        receiver: str = None,
        payload: Dict[str, Any] = None,
        timestamp: datetime = None
    ):
        self.message_type = message_type
        self.sender = sender
        self.receiver = receiver
        self.payload = payload or {}
        self.timestamp = timestamp or datetime.utcnow()

    def __repr__(self):
        return f"<Message(type={self.message_type.value}, from={self.sender}, to={self.receiver})>"


class MessageBus:
    """Barramento de mensagens para comunicação entre agentes"""
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._initialized = True
        system_logger.info("MessageBus inicializado")

    async def subscribe(self, agent_name: str, callback: Callable):
        """Inscreve um agente para receber mensagens"""
        async with self._lock:
            if agent_name not in self._subscribers:
                self._subscribers[agent_name] = []
            self._subscribers[agent_name].append(callback)
            system_logger.debug(f"Agente {agent_name} inscrito no MessageBus")

    async def unsubscribe(self, agent_name: str, callback: Callable):
        """Remove inscrição de um agente"""
        async with self._lock:
            if agent_name in self._subscribers:
                if callback in self._subscribers[agent_name]:
                    self._subscribers[agent_name].remove(callback)

    async def publish(self, message: Message):
        """Publica uma mensagem no barramento"""
        await self._message_queue.put(message)
        system_logger.debug(f"Mensagem publicada: {message}")

    async def send(self, message: Message):
        """Envia mensagem diretamente para um agente específico"""
        if message.receiver and message.receiver in self._subscribers:
            async with self._lock:
                callbacks = self._subscribers[message.receiver].copy()
            
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    system_logger.error(f"Erro ao processar mensagem em {message.receiver}: {e}")

    async def broadcast(self, message: Message):
        """Envia mensagem para todos os agentes inscritos"""
        async with self._lock:
            all_callbacks = []
            for agent_name, callbacks in self._subscribers.items():
                if agent_name != message.sender:  # Não enviar para o próprio remetente
                    all_callbacks.extend(callbacks)
        
        for callback in all_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                system_logger.error(f"Erro ao processar broadcast: {e}")

    async def _message_processor(self):
        """Processa mensagens da fila"""
        while self._running:
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                
                # Se tem receptor específico, envia apenas para ele
                if message.receiver:
                    await self.send(message)
                else:
                    # Caso contrário, faz broadcast
                    await self.broadcast(message)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                system_logger.error(f"Erro no processador de mensagens: {e}")

    async def start(self):
        """Inicia o processamento de mensagens"""
        if not self._running:
            self._running = True
            asyncio.create_task(self._message_processor())
            system_logger.info("MessageBus iniciado")

    async def stop(self):
        """Para o processamento de mensagens"""
        self._running = False
        system_logger.info("MessageBus parado")


# Instância global do MessageBus
message_bus = MessageBus()

