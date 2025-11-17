"""Agente MarketAnalyst - Monitora mercado e identifica oportunidades"""
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.portfolio import Ativo, TipoAtivo
from models.market import IndicadorMercado, Alerta
from agents.base_agent import BaseAgent
from services.message_bus import Message, MessageType
from services.logger import market_logger
import random
from datetime import datetime, timedelta


class MarketAnalyst(BaseAgent):
    """Agente responsável por monitorar o mercado e identificar oportunidades"""

    def __init__(self):
        super().__init__("MarketAnalyst")
        self.dados_mercado = {}
        self.tendencias = {}
        self.sinais_compra_venda = {}
        self.indicadores = {}
        self.ultimo_envio_sinais = {}  # Controle de frequência de envio de sinais
        self.cooldown_sinais_segundos = 60  # Envia sinais no máximo a cada 60 segundos

    async def perceive(self):
        """Observa preços, indicadores e eventos de mercado"""
        db = SessionLocal()
        try:
            # Observa preços de ativos em tempo real
            ativos = db.query(Ativo).all()
            for ativo in ativos:
                self.dados_mercado[ativo.codigo] = {
                    "preco_atual": ativo.preco_atual,
                    "preco_anterior": ativo.preco_anterior,
                    "variacao": ativo.variacao_percentual,
                    "tipo": ativo.tipo.value
                }
                market_logger.debug(
                    f"Ativo {ativo.codigo}: R$ {ativo.preco_atual:.2f} "
                    f"({ativo.variacao_percentual:+.2f}%)"
                )

            # Observa indicadores macroeconômicos
            indicadores = db.query(IndicadorMercado).all()
            for ind in indicadores:
                self.indicadores[ind.nome] = {
                    "valor": ind.valor,
                    "variacao": ind.variacao,
                    "timestamp": ind.timestamp
                }

        except Exception as e:
            market_logger.error(f"Erro na percepção: {e}")
        finally:
            db.close()

    async def act(self):
        """Ações reativas: analisa tendências e gera sinais"""
        await self._analisar_tendencias()
        await self._gerar_sinais_compra_venda()
        await self._verificar_riscos()

    async def handle_message(self, message: Message):
        """Processa mensagens recebidas"""
        market_logger.debug(f"Mensagem recebida: {message.message_type.value}")

        if message.message_type == MessageType.SOLICITACAO_ANALISE:
            # PortfolioManager solicita análise detalhada
            await self._processar_solicitacao_analise(message)

    async def coletar_dados_mercado(self) -> dict:
        """Coleta dados atualizados do mercado"""
        db = SessionLocal()
        try:
            ativos = db.query(Ativo).all()
            dados = {}
            
            for ativo in ativos:
                dados[ativo.codigo] = {
                    "codigo": ativo.codigo,
                    "nome": ativo.nome,
                    "tipo": ativo.tipo.value,
                    "preco": ativo.preco_atual,
                    "variacao": ativo.variacao_percentual
                }
            
            market_logger.info(f"Dados de mercado coletados: {len(dados)} ativos")
            return dados
        finally:
            db.close()

    async def analisar_tendencias(self) -> dict:
        """Analisa tendências de preços dos ativos"""
        tendencias = {}
        db = SessionLocal()
        try:
            ativos = db.query(Ativo).all()
            
            for ativo in ativos:
                # Análise simples baseada em variação percentual
                variacao = ativo.variacao_percentual
                
                if variacao > 2.0:
                    tendencia = "alta_forte"
                elif variacao > 0.5:
                    tendencia = "alta_suave"
                elif variacao < -2.0:
                    tendencia = "queda_forte"
                elif variacao < -0.5:
                    tendencia = "queda_suave"
                else:
                    tendencia = "lateral"
                
                tendencias[ativo.codigo] = {
                    "tendencia": tendencia,
                    "variacao": variacao,
                    "preco_atual": ativo.preco_atual
                }
            
            market_logger.info(f"Tendências analisadas para {len(tendencias)} ativos")
            return tendencias
        finally:
            db.close()

    async def gerar_sinais_compra_venda(self) -> dict:
        """Gera sinais de compra ou venda baseados em análise técnica"""
        sinais = {}
        tendencias = await self.analisar_tendencias()
        
        for codigo, dados in tendencias.items():
            tendencia = dados["tendencia"]
            variacao = dados["variacao"]
            
            # Lógica simples de sinais
            if tendencia == "queda_forte" and variacao < -3.0:
                # Oportunidade de compra (preço caiu muito)
                sinais[codigo] = {
                    "acao": "compra",
                    "forca": "forte",
                    "motivo": f"Queda significativa ({variacao:.2f}%)"
                }
            elif tendencia == "alta_forte" and variacao > 3.0:
                # Considerar venda (preço subiu muito)
                sinais[codigo] = {
                    "acao": "venda",
                    "forca": "moderada",
                    "motivo": f"Alta significativa ({variacao:.2f}%)"
                }
            elif tendencia == "lateral":
                sinais[codigo] = {
                    "acao": "manter",
                    "forca": "fraca",
                    "motivo": "Mercado lateral"
                }
        
        # Envia sinais relevantes para PortfolioManager (com controle de frequência)
        sinais_relevantes = {
            k: v for k, v in sinais.items() 
            if v["acao"] in ["compra", "venda"]
        }
        
        if sinais_relevantes:
            # Verifica se já enviou sinais recentemente
            agora = datetime.utcnow()
            pode_enviar = True
            
            for codigo in sinais_relevantes.keys():
                ultimo_envio = self.ultimo_envio_sinais.get(codigo)
                if ultimo_envio:
                    tempo_decorrido = (agora - ultimo_envio).total_seconds()
                    if tempo_decorrido < self.cooldown_sinais_segundos:
                        pode_enviar = False
                        break
            
            if pode_enviar:
                market_logger.info(f"Gerados {len(sinais_relevantes)} sinais relevantes")
                
                # Separa sinais de compra e venda
                sinais_compra = {
                    k: v for k, v in sinais_relevantes.items() 
                    if v["acao"] == "compra"
                }
                sinais_venda = {
                    k: v for k, v in sinais_relevantes.items() 
                    if v["acao"] == "venda"
                }
                
                # Envia separadamente
                if sinais_compra:
                    await self.message_bus.send(
                        Message(
                            message_type=MessageType.SINAL_COMPRA,
                            sender=self.name,
                            receiver="PortfolioManager",
                            payload={"sinais": sinais_compra}
                        )
                    )
                    # Atualiza timestamp
                    for codigo in sinais_compra.keys():
                        self.ultimo_envio_sinais[codigo] = agora
                
                if sinais_venda:
                    await self.message_bus.send(
                        Message(
                            message_type=MessageType.SINAL_VENDA,
                            sender=self.name,
                            receiver="PortfolioManager",
                            payload={"sinais": sinais_venda}
                        )
                    )
                    # Atualiza timestamp
                    for codigo in sinais_venda.keys():
                        self.ultimo_envio_sinais[codigo] = agora
            else:
                market_logger.debug("Sinais não enviados devido a cooldown")
        
        return sinais

    async def enviar_alertas_risco(self, tipo_risco: str, mensagem: str):
        """Envia alertas de risco para outros agentes"""
        db = SessionLocal()
        try:
            alerta = Alerta(
                agente_origem=self.name,
                tipo=f"risco_{tipo_risco}",
                mensagem=mensagem,
                severidade="warning"
            )
            db.add(alerta)
            db.commit()
            
            market_logger.warning(f"Alerta de risco enviado: {mensagem}")
            
            await self.message_bus.broadcast(
                Message(
                    message_type=MessageType.ALERTA_RISCO,
                    sender=self.name,
                    payload={
                        "tipo": tipo_risco,
                        "mensagem": mensagem
                    }
                )
            )
        finally:
            db.close()

    async def produzir_relatorio_mercado(self) -> dict:
        """Produz relatório completo de mercado"""
        dados = await self.coletar_dados_mercado()
        tendencias = await self.analisar_tendencias()
        sinais = await self.gerar_sinais_compra_venda()
        
        relatorio = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_ativos": len(dados),
            "dados_mercado": dados,
            "tendencias": tendencias,
            "sinais": sinais,
            "indicadores": self.indicadores
        }
        
        market_logger.info("Relatório de mercado produzido")
        
        # Envia relatório para outros agentes
        await self.message_bus.broadcast(
            Message(
                message_type=MessageType.RELATORIO_MERCADO,
                sender=self.name,
                payload=relatorio
            )
        )
        
        return relatorio

    async def _analisar_tendencias(self):
        """Método interno para análise de tendências"""
        self.tendencias = await self.analisar_tendencias()

    async def _gerar_sinais_compra_venda(self):
        """Método interno para geração de sinais"""
        self.sinais_compra_venda = await self.gerar_sinais_compra_venda()

    async def _verificar_riscos(self):
        """Verifica riscos no mercado"""
        # Verifica volatilidade alta
        for codigo, dados in self.dados_mercado.items():
            if abs(dados["variacao"]) > 5.0:
                await self.enviar_alertas_risco(
                    "volatilidade_alta",
                    f"Alta volatilidade detectada em {codigo}: {dados['variacao']:.2f}%"
                )

    async def _processar_solicitacao_analise(self, message: Message):
        """Processa solicitação de análise do PortfolioManager"""
        ativo_codigo = message.payload.get("ativo_codigo")
        if ativo_codigo and ativo_codigo in self.dados_mercado:
            analise = {
                "ativo": ativo_codigo,
                "dados": self.dados_mercado[ativo_codigo],
                "tendencia": self.tendencias.get(ativo_codigo),
                "sinal": self.sinais_compra_venda.get(ativo_codigo)
            }
            
            await self.message_bus.send(
                Message(
                    message_type=MessageType.ANALISE_TENDENCIA,
                    sender=self.name,
                    receiver=message.sender,
                    payload=analise
                )
            )

