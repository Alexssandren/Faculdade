"""Classe base para agentes do sistema"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from services.message_bus import MessageBus, Message, MessageType
from services.logger import system_logger
import asyncio


class BaseAgent(ABC):
    """Classe abstrata base para todos os agentes"""
    
    def __init__(self, name: str):
        self.name = name
        self.message_bus = MessageBus()
        self.running = False
        system_logger.info(f"Agente {self.name} inicializado")

    async def start(self):
        """Inicia o agente"""
        self.running = True
        await self.message_bus.subscribe(self.name, self.handle_message)
        await self.message_bus.start()
        system_logger.info(f"Agente {self.name} iniciado")

    async def stop(self):
        """Para o agente"""
        self.running = False
        system_logger.info(f"Agente {self.name} parado")

    @abstractmethod
    async def handle_message(self, message: Message):
        """Processa mensagens recebidas"""
        pass

    @abstractmethod
    async def perceive(self):
        """Fase de percepção do agente"""
        pass

    @abstractmethod
    async def act(self):
        """Fase de ação do agente"""
        pass

    async def run_cycle(self):
        """Executa um ciclo completo: perceber -> agir"""
        while self.running:
            try:
                await self.perceive()
                await self.act()
                await asyncio.sleep(1)  # Intervalo entre ciclos
            except Exception as e:
                system_logger.error(f"Erro no ciclo do agente {self.name}: {e}")
                await asyncio.sleep(1)

