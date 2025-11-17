"""Agente WalletManager - Gerencia saldo, liquidez e limites da carteira"""
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.portfolio import Carteira, Transacao, TipoOperacao
from models.market import Alerta
from agents.base_agent import BaseAgent
from services.message_bus import Message, MessageType
from services.logger import wallet_logger
import os
from dotenv import load_dotenv

load_dotenv()

MIN_LIQUIDITY_THRESHOLD = float(os.getenv("MIN_LIQUIDITY_THRESHOLD", "1000.0"))


class WalletManager(BaseAgent):
    """Agente responsável por gerenciar o saldo, liquidez e limites da carteira"""

    def __init__(self):
        super().__init__("WalletManager")
        self.saldo_atual = 0.0
        self.limite_operacional = 0.0
        self.fluxo_caixa = []
        self.alertas_enviados = set()

    async def perceive(self):
        """Observa o saldo, transações e recebe relatórios"""
        db = SessionLocal()
        try:
            # Observa saldo atual
            carteira = db.query(Carteira).first()
            if carteira:
                self.saldo_atual = carteira.saldo_disponivel
                wallet_logger.debug(f"Saldo atual observado: R$ {self.saldo_atual:.2f}")

            # Observa transações recentes
            transacoes_recentes = db.query(Transacao).order_by(
                Transacao.timestamp.desc()
            ).limit(10).all()
            
            for transacao in transacoes_recentes:
                wallet_logger.debug(
                    f"Transação observada: {transacao.tipo.value} de "
                    f"{transacao.quantidade} unidades por R$ {transacao.preco_unitario:.2f}"
                )

        except Exception as e:
            wallet_logger.error(f"Erro na percepção: {e}")
        finally:
            db.close()

    async def act(self):
        """Ações reativas baseadas nas percepções"""
        # Verifica liquidez
        await self._verificar_liquidez()
        
        # Atualiza fluxo de caixa
        await self._atualizar_fluxo_caixa()

    async def handle_message(self, message: Message):
        """Processa mensagens recebidas de outros agentes"""
        wallet_logger.debug(f"Mensagem recebida: {message.message_type.value}")

        if message.message_type == MessageType.RELATORIO_PORTFOLIO:
            # Recebe relatório do PortfolioManager sobre alocação atual
            await self._processar_relatorio_portfolio(message.payload)

        elif message.message_type == MessageType.RELATORIO_MERCADO:
            # Recebe relatório do MarketAnalyst sobre condições de mercado
            await self._processar_relatorio_mercado(message.payload)

        elif message.message_type == MessageType.SOLICITACAO_AUTORIZACAO:
            # Processa solicitação de autorização do PortfolioManager
            await self._processar_solicitacao_autorizacao(message)

    async def calcular_saldo_atual(self) -> float:
        """Calcula o saldo atual da carteira"""
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if carteira:
                self.saldo_atual = carteira.saldo_disponivel
                return self.saldo_atual
            return 0.0
        finally:
            db.close()

    async def definir_limite_operacional(self, limite: float):
        """Define o limite operacional para compras"""
        self.limite_operacional = limite
        wallet_logger.info(f"Limite operacional definido: R$ {limite:.2f}")
        
        await self.message_bus.publish(
            Message(
                message_type=MessageType.LIMITE_DEFINIDO,
                sender=self.name,
                payload={"limite": limite}
            )
        )

    async def atualizar_fluxo_caixa(self):
        """Atualiza o fluxo de caixa com entradas e saídas"""
        db = SessionLocal()
        try:
            transacoes = db.query(Transacao).order_by(
                Transacao.timestamp.desc()
            ).limit(50).all()
            
            self.fluxo_caixa = [
                {
                    "tipo": t.tipo.value,
                    "valor": t.valor_total,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in transacoes
            ]
            
            wallet_logger.debug(f"Fluxo de caixa atualizado com {len(self.fluxo_caixa)} transações")
        finally:
            db.close()

    async def gerar_relatorio_financeiro(self) -> dict:
        """Gera relatório financeiro completo"""
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            saldo = carteira.saldo_disponivel if carteira else 0.0
            
            # Calcula entradas e saídas do período
            transacoes = db.query(Transacao).all()
            entradas = sum(
                t.valor_total for t in transacoes 
                if t.tipo == TipoOperacao.VENDA
            )
            saidas = sum(
                t.valor_total for t in transacoes 
                if t.tipo == TipoOperacao.COMPRA
            )
            
            relatorio = {
                "saldo_atual": saldo,
                "limite_operacional": self.limite_operacional,
                "entradas_periodo": entradas,
                "saidas_periodo": saidas,
                "saldo_liquido": entradas - saidas,
                "liquidez_suficiente": saldo >= MIN_LIQUIDITY_THRESHOLD
            }
            
            wallet_logger.info("Relatório financeiro gerado")
            return relatorio
        finally:
            db.close()

    async def enviar_autorizacao_operacao(
        self, 
        operacao_tipo: str, 
        valor: float, 
        receiver: str,
        dados_originais: dict = None
    ) -> bool:
        """Envia autorização de operação para PortfolioManager"""
        # SEMPRE consulta o banco de dados para obter o saldo atual mais recente
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if not carteira:
                wallet_logger.error("Carteira não encontrada ao autorizar operação")
                return False
            
            saldo_atual_db = carteira.saldo_disponivel
            # Atualiza também a variável de instância para manter sincronizado
            self.saldo_atual = saldo_atual_db
            
            if operacao_tipo == "compra":
                if valor > saldo_atual_db:
                    wallet_logger.warning(
                        f"Operação de compra negada: saldo insuficiente "
                        f"(solicitado: R$ {valor:.2f}, disponível: R$ {saldo_atual_db:.2f})"
                    )
                    payload_negado = {"autorizado": False, "motivo": "saldo_insuficiente"}
                    if dados_originais:
                        payload_negado.update(dados_originais)
                    
                    await self.message_bus.send(
                        Message(
                            message_type=MessageType.AUTORIZACAO_COMPRA,
                            sender=self.name,
                            receiver=receiver,
                            payload=payload_negado
                        )
                    )
                    return False
                
                # Compra autorizada
                wallet_logger.info(
                    f"Operação de compra autorizada: R$ {valor:.2f} "
                    f"(saldo disponível: R$ {saldo_atual_db:.2f})"
                )
                payload_autorizado = {"autorizado": True, "valor": valor}
                if dados_originais:
                    payload_autorizado.update(dados_originais)
                
                await self.message_bus.send(
                    Message(
                        message_type=MessageType.AUTORIZACAO_COMPRA,
                        sender=self.name,
                        receiver=receiver,
                        payload=payload_autorizado
                    )
                )
                return True
            
            elif operacao_tipo == "venda":
                # Venda sempre autorizada (não precisa de saldo)
                wallet_logger.info(
                    f"Operação de venda autorizada: R$ {valor:.2f}"
                )
                payload_autorizado = {"autorizado": True, "valor": valor}
                if dados_originais:
                    payload_autorizado.update(dados_originais)
                
                await self.message_bus.send(
                    Message(
                        message_type=MessageType.AUTORIZACAO_VENDA,
                        sender=self.name,
                        receiver=receiver,
                        payload=payload_autorizado
                    )
                )
                return True
            
            return False
        finally:
            db.close()

    async def _verificar_liquidez(self):
        """Verifica se a liquidez está abaixo do limite"""
        if self.saldo_atual < MIN_LIQUIDITY_THRESHOLD:
            alerta_id = f"liquidez_baixa_{int(self.saldo_atual)}"
            
            if alerta_id not in self.alertas_enviados:
                wallet_logger.warning(
                    f"Liquidez baixa detectada: R$ {self.saldo_atual:.2f} "
                    f"(mínimo: R$ {MIN_LIQUIDITY_THRESHOLD:.2f})"
                )
                
                # Cria alerta no banco
                db = SessionLocal()
                try:
                    alerta = Alerta(
                        agente_origem=self.name,
                        tipo="liquidez_baixa",
                        mensagem=f"Saldo disponível abaixo do mínimo: R$ {self.saldo_atual:.2f}",
                        severidade="warning"
                    )
                    db.add(alerta)
                    db.commit()
                finally:
                    db.close()
                
                # Envia mensagem de alerta
                await self.message_bus.broadcast(
                    Message(
                        message_type=MessageType.ALERTA_LIQUIDEZ,
                        sender=self.name,
                        payload={
                            "saldo_atual": self.saldo_atual,
                            "limite_minimo": MIN_LIQUIDITY_THRESHOLD
                        }
                    )
                )
                
                self.alertas_enviados.add(alerta_id)
        else:
            # Remove alertas antigos se liquidez melhorou
            self.alertas_enviados.discard(f"liquidez_baixa_{int(self.saldo_atual)}")

    async def _atualizar_fluxo_caixa(self):
        """Atualiza o fluxo de caixa"""
        await self.atualizar_fluxo_caixa()

    async def _processar_relatorio_portfolio(self, payload: dict):
        """Processa relatório do PortfolioManager"""
        wallet_logger.debug(f"Relatório de portfolio recebido: {payload}")

    async def _processar_relatorio_mercado(self, payload: dict):
        """Processa relatório do MarketAnalyst"""
        wallet_logger.debug(f"Relatório de mercado recebido: {payload}")

    async def _processar_solicitacao_autorizacao(self, message: Message):
        """Processa solicitação de autorização do PortfolioManager"""
        payload = message.payload
        operacao_tipo = payload.get("tipo", "compra")
        valor = payload.get("valor", 0.0)
        
        # Inclui todos os dados originais na resposta de autorização
        autorizado = await self.enviar_autorizacao_operacao(
            operacao_tipo, 
            valor, 
            message.sender,
            dados_originais=payload  # Passa os dados originais
        )

