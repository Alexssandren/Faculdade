"""Agente PortfolioManager - Gerencia composição e diversificação da carteira"""
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.portfolio import (
    Carteira, Ativo, Posicao, Transacao, TipoOperacao, 
    TipoAtivo, ConfiguracaoDiversificacao
)
from models.market import Alerta
from agents.base_agent import BaseAgent
from services.message_bus import Message, MessageType
from services.logger import portfolio_logger
from datetime import datetime


class PortfolioManager(BaseAgent):
    """Agente responsável por decidir composição e diversificação da carteira"""

    def __init__(self):
        super().__init__("PortfolioManager")
        self.distribuicao_atual = {}
        self.configuracao_alvo = {}
        self.operacoes_pendentes = []
        self.autorizacoes_recebidas = {}
        self.ultima_operacao_por_ativo = {}  # Controle de cooldown
        self.cooldown_segundos = 30  # Tempo mínimo entre operações no mesmo ativo

    async def start(self):
        """Inicia o agente e atualiza valor total da carteira"""
        await super().start()
        # Garante que o valor total da carteira está correto na inicialização
        await self._atualizar_valor_total_carteira()
        
        # Verifica se precisa começar a investir (carteira vazia com saldo)
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            posicoes_count = db.query(Posicao).count()
            
            if carteira and carteira.saldo_disponivel > 0 and posicoes_count == 0:
                portfolio_logger.info(
                    f"Carteira vazia detectada com saldo de R$ {carteira.saldo_disponivel:.2f}. "
                    f"Iniciando distribuição automática do capital..."
                )
                # Força uma avaliação imediata para começar a investir
                await self._avaliar_diversificacao()
        finally:
            db.close()
        
        portfolio_logger.info("PortfolioManager iniciado e valor total da carteira atualizado")

    async def perceive(self):
        """Observa ativos, limites, análises e distribuição atual"""
        db = SessionLocal()
        try:
            # Observa distribuição atual da carteira
            await self._observar_distribuicao_atual(db)
            
            # Observa configuração alvo de diversificação
            configs = db.query(ConfiguracaoDiversificacao).all()
            for config in configs:
                self.configuracao_alvo[config.tipo_ativo] = {
                    "porcentagem_alvo": config.porcentagem_alvo,
                    "tolerancia": config.tolerancia
                }
            
            # Observa ativos disponíveis
            ativos = db.query(Ativo).all()
            portfolio_logger.debug(f"Observados {len(ativos)} ativos disponíveis")

        except Exception as e:
            portfolio_logger.error(f"Erro na percepção: {e}")
        finally:
            db.close()

    async def act(self):
        """Ações reativas: avalia diversificação e executa ajustes"""
        # Atualiza valor total da carteira periodicamente (preços mudam)
        await self._atualizar_valor_total_carteira()
        await self._avaliar_diversificacao()
        await self._processar_operacoes_autorizadas()

    async def handle_message(self, message: Message):
        """Processa mensagens recebidas"""
        portfolio_logger.debug(f"Mensagem recebida: {message.message_type.value}")

        if message.message_type == MessageType.AUTORIZACAO_COMPRA:
            await self._processar_autorizacao_compra(message)
        
        elif message.message_type == MessageType.AUTORIZACAO_VENDA:
            await self._processar_autorizacao_venda(message)
        
        elif message.message_type == MessageType.SINAL_COMPRA:
            await self._processar_sinal_compra(message)
        
        elif message.message_type == MessageType.SINAL_VENDA:
            await self._processar_sinal_venda(message)
        
        elif message.message_type == MessageType.ANALISE_TENDENCIA:
            await self._processar_analise_tendencia(message)
        
        elif message.message_type == MessageType.ALERTA_LIQUIDEZ:
            await self._processar_alerta_liquidez(message)

    async def avaliar_distribuicao_carteira(self) -> dict:
        """Avalia a distribuição atual da carteira"""
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if not carteira:
                return {}
            
            # Calcula distribuição por tipo de ativo usando valor ATUAL de mercado
            posicoes = db.query(Posicao).join(Ativo).all()
            
            # Valor total sempre é: valor das posições + saldo disponível
            valor_posicoes = sum(p.quantidade * p.ativo.preco_atual for p in posicoes)
            valor_total = valor_posicoes + carteira.saldo_disponivel
            
            # Se não há valor total, retorna vazio
            if valor_total == 0:
                return {}
            
            distribuicao = {}
            
            for tipo in TipoAtivo:
                # Usa quantidade * preco_atual para obter valor de mercado atual
                valor_tipo = sum(
                    p.quantidade * p.ativo.preco_atual for p in posicoes 
                    if p.ativo.tipo == tipo
                )
                porcentagem = (valor_tipo / valor_total) * 100 if valor_total > 0 else 0
                distribuicao[tipo.value] = {
                    "valor": valor_tipo,
                    "porcentagem": porcentagem
                }
            
            portfolio_logger.info(f"Distribuição avaliada: {distribuicao}")
            return distribuicao
        finally:
            db.close()

    async def decidir_compra_venda(self) -> list:
        """Decide quais operações realizar para balancear a carteira"""
        distribuicao_atual = await self.avaliar_distribuicao_carteira()
        operacoes = []
        
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if not carteira:
                return operacoes
            
            # Para calcular quanto investir em cada tipo, sempre usa o valor total da carteira
            # como base (posições + saldo), mas limita as compras ao saldo disponível
            posicoes_count = db.query(Posicao).count()
            if posicoes_count == 0:
                # Carteira vazia: usa apenas o saldo disponível
                valor_base = carteira.saldo_disponivel
            else:
                # Carteira com posições: usa valor total para calcular porcentagens,
                # mas as compras serão limitadas ao saldo disponível
                valor_base = carteira.valor_total_carteira
                # Se valor_total ainda não foi atualizado, calcula: posições + saldo
                if valor_base == 0 or valor_base < carteira.saldo_disponivel:
                    posicoes = db.query(Posicao).join(Ativo).all()
                    valor_posicoes = sum(p.quantidade * p.ativo.preco_atual for p in posicoes)
                    valor_base = valor_posicoes + carteira.saldo_disponivel
            
            for tipo_ativo, config_alvo in self.configuracao_alvo.items():
                porcentagem_alvo = config_alvo["porcentagem_alvo"]
                tolerancia = config_alvo.get("tolerancia", 5.0)
                
                porcentagem_atual = distribuicao_atual.get(
                    tipo_ativo.value, {}
                ).get("porcentagem", 0.0)
                
                diferenca = porcentagem_atual - porcentagem_alvo
                
                # Se está fora da tolerância, precisa ajustar
                if abs(diferenca) > tolerancia:
                    portfolio_logger.info(
                        f"Desequilíbrio detectado em {tipo_ativo.value}: "
                        f"atual={porcentagem_atual:.2f}%, "
                        f"alvo={porcentagem_alvo:.2f}%, "
                        f"diferença={diferenca:.2f}%"
                    )
                    
                    # Se está abaixo do alvo, precisa comprar
                    if diferenca < -tolerancia:
                        # Busca ativos deste tipo para comprar
                        ativos_tipo = db.query(Ativo).filter(
                            Ativo.tipo == tipo_ativo
                        ).all()
                        
                        if ativos_tipo:
                            # Escolhe o primeiro disponível (pode melhorar a lógica)
                            ativo = ativos_tipo[0]
                            
                            # Calcula quanto seria necessário para atingir a porcentagem alvo
                            valor_necessario_teorico = abs(diferenca) / 100 * valor_base
                            
                            # IMPORTANTE: Limita ao saldo disponível REAL
                            # Não podemos comprar mais do que temos em caixa
                            valor_necessario = min(valor_necessario_teorico, carteira.saldo_disponivel)
                            
                            # Só adiciona se houver saldo suficiente e valor for significativo
                            if valor_necessario > 100 and carteira.saldo_disponivel >= valor_necessario:
                                operacoes.append({
                                    "tipo": "compra",
                                    "ativo_codigo": ativo.codigo,
                                    "valor": valor_necessario,
                                    "motivo": f"Ajuste de diversificação: {tipo_ativo.value}"
                                })
                                portfolio_logger.debug(
                                    f"Operação de compra planejada para {ativo.codigo}: "
                                    f"R$ {valor_necessario:.2f} (teórico: R$ {valor_necessario_teorico:.2f}, "
                                    f"saldo disponível: R$ {carteira.saldo_disponivel:.2f})"
                                )
                            else:
                                portfolio_logger.debug(
                                    f"Não adicionando operação de compra para {ativo.codigo}: "
                                    f"valor necessário R$ {valor_necessario:.2f} (teórico: R$ {valor_necessario_teorico:.2f}), "
                                    f"saldo disponível R$ {carteira.saldo_disponivel:.2f}"
                                )
                    
                    # Se está acima do alvo, pode considerar vender
                    elif diferenca > tolerancia:
                        # Busca posições deste tipo para vender
                        posicoes_tipo = db.query(Posicao).join(Ativo).filter(
                            Ativo.tipo == tipo_ativo
                        ).all()
                        
                        if posicoes_tipo:
                            posicao = posicoes_tipo[0]
                            # Verifica se a posição ainda existe e tem quantidade suficiente
                            if posicao and posicao.quantidade > 0:
                                valor_venda = abs(diferenca) / 100 * valor_base
                                quantidade_calculada = valor_venda / posicao.ativo.preco_atual
                                
                                # Garante que não tenta vender mais do que tem
                                quantidade_venda = min(posicao.quantidade, quantidade_calculada)
                                
                                # Só adiciona se a quantidade for significativa (mínimo R$ 100)
                                if quantidade_venda * posicao.ativo.preco_atual >= 100:
                                    operacoes.append({
                                        "tipo": "venda",
                                        "ativo_codigo": posicao.ativo.codigo,
                                        "quantidade": quantidade_venda,
                                        "motivo": f"Ajuste de diversificação: {tipo_ativo.value}"
                                    })
            
            return operacoes
        finally:
            db.close()

    async def executar_operacao(
        self, 
        tipo: str, 
        ativo_codigo: str, 
        quantidade: float = None, 
        valor: float = None
    ) -> bool:
        """Executa uma operação de compra ou venda"""
        from datetime import datetime
        
        # Atualiza timestamp da última operação
        self.ultima_operacao_por_ativo[ativo_codigo] = datetime.utcnow()
        
        db = SessionLocal()
        try:
            ativo = db.query(Ativo).filter(Ativo.codigo == ativo_codigo).first()
            if not ativo:
                portfolio_logger.error(f"Ativo {ativo_codigo} não encontrado")
                return False
            
            carteira = db.query(Carteira).first()
            if not carteira:
                portfolio_logger.error("Carteira não encontrada")
                return False
            
            if tipo == "compra":
                if not valor:
                    portfolio_logger.error("Valor não especificado para compra")
                    return False
                
                quantidade = valor / ativo.preco_atual
                
                # Verifica saldo
                if valor > carteira.saldo_disponivel:
                    portfolio_logger.warning(
                        f"Saldo insuficiente para compra: "
                        f"solicitado R$ {valor:.2f}, "
                        f"disponível R$ {carteira.saldo_disponivel:.2f}"
                    )
                    return False
                
                # Cria transação
                transacao = Transacao(
                    ativo_id=ativo.id,
                    tipo=TipoOperacao.COMPRA,
                    quantidade=quantidade,
                    preco_unitario=ativo.preco_atual,
                    valor_total=valor
                )
                db.add(transacao)
                
                # Atualiza posição
                posicao = db.query(Posicao).filter(Posicao.ativo_id == ativo.id).first()
                if posicao:
                    novo_valor_total = posicao.valor_total + valor
                    nova_quantidade = posicao.quantidade + quantidade
                    posicao.preco_medio = novo_valor_total / nova_quantidade
                    posicao.quantidade = nova_quantidade
                    posicao.valor_total = novo_valor_total
                else:
                    posicao = Posicao(
                        ativo_id=ativo.id,
                        quantidade=quantidade,
                        preco_medio=ativo.preco_atual,
                        valor_total=valor
                    )
                    db.add(posicao)
                
                # Atualiza saldo
                carteira.saldo_disponivel -= valor
                
                portfolio_logger.info(
                    f"Compra executada: {quantidade:.4f} {ativo_codigo} "
                    f"por R$ {valor:.2f}"
                )
            
            elif tipo == "venda":
                if not quantidade:
                    portfolio_logger.error("Quantidade não especificada para venda")
                    return False
                
                if quantidade <= 0:
                    portfolio_logger.error(f"Quantidade inválida para venda: {quantidade:.4f}")
                    return False
                
                posicao = db.query(Posicao).filter(Posicao.ativo_id == ativo.id).first()
                if not posicao:
                    portfolio_logger.warning(
                        f"Posição não encontrada para venda: {ativo_codigo}"
                    )
                    return False
                
                if posicao.quantidade <= 0:
                    portfolio_logger.warning(
                        f"Posição sem quantidade disponível para venda: {ativo_codigo}"
                    )
                    return False
                
                # Ajusta quantidade se solicitada for maior que disponível
                if quantidade > posicao.quantidade:
                    portfolio_logger.warning(
                        f"Ajustando quantidade de venda: solicitado {quantidade:.4f}, "
                        f"disponível {posicao.quantidade:.4f}"
                    )
                    quantidade = posicao.quantidade
                
                valor = quantidade * ativo.preco_atual
                
                # Cria transação
                transacao = Transacao(
                    ativo_id=ativo.id,
                    tipo=TipoOperacao.VENDA,
                    quantidade=quantidade,
                    preco_unitario=ativo.preco_atual,
                    valor_total=valor
                )
                db.add(transacao)
                
                # Atualiza posição
                posicao.quantidade -= quantidade
                posicao.valor_total = posicao.quantidade * posicao.preco_medio
                
                # Remove posição se quantidade zerar
                if posicao.quantidade <= 0:
                    db.delete(posicao)
                
                # Atualiza saldo
                carteira.saldo_disponivel += valor
                
                portfolio_logger.info(
                    f"Venda executada: {quantidade:.4f} {ativo_codigo} "
                    f"por R$ {valor:.2f}"
                )
            
            # Atualiza valor total da carteira
            await self._atualizar_valor_total_carteira(db)
            
            db.commit()
            
            # Notifica operação
            await self.notificar_operacoes(transacao)
            
            return True
            
        except Exception as e:
            db.rollback()
            portfolio_logger.error(f"Erro ao executar operação: {e}")
            return False
        finally:
            db.close()

    async def atualizar_portfolio(self):
        """Atualiza informações do portfólio"""
        await self._atualizar_valor_total_carteira()
        distribuicao = await self.avaliar_distribuicao_carteira()
        
        await self.message_bus.publish(
            Message(
                message_type=MessageType.DISTRIBUICAO_CARTEIRA,
                sender=self.name,
                payload={"distribuicao": distribuicao}
            )
        )

    async def notificar_operacoes(self, transacao: Transacao):
        """Notifica outras partes sobre operações realizadas"""
        await self.message_bus.publish(
            Message(
                message_type=MessageType.OPERACAO_EXECUTADA,
                sender=self.name,
                payload={
                    "transacao_id": transacao.id,
                    "tipo": transacao.tipo.value,
                    "ativo_id": transacao.ativo_id,
                    "valor": transacao.valor_total
                }
            )
        )

    async def _observar_distribuicao_atual(self, db: Session):
        """Observa distribuição atual da carteira"""
        self.distribuicao_atual = await self.avaliar_distribuicao_carteira()

    async def _avaliar_diversificacao(self):
        """Avalia se a diversificação está balanceada"""
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # Verifica se a carteira está vazia (sem posições)
            posicoes_count = db.query(Posicao).count()
            carteira = db.query(Carteira).first()
            
            # Se não há posições mas há saldo, precisa começar a investir
            if posicoes_count == 0 and carteira and carteira.saldo_disponivel > 0:
                portfolio_logger.info(
                    f"Carteira vazia com saldo de R$ {carteira.saldo_disponivel:.2f}. "
                    f"Iniciando distribuição inicial do capital..."
                )
                # Força distribuição inicial sem cooldown
                operacoes = await self.decidir_compra_venda()
                if operacoes:
                    # Executa múltiplas operações para distribuir rapidamente
                    max_operacoes = min(5, len(operacoes))  # Executa até 5 operações por ciclo inicial
                    for i in range(max_operacoes):
                        if i < len(operacoes):
                            await self._solicitar_autorizacao(operacoes[i])
                    portfolio_logger.info(f"Iniciando distribuição: {max_operacoes} operações planejadas")
                return
        finally:
            db.close()
        
        distribuicao = await self.avaliar_distribuicao_carteira()
        
        # Verifica se pode rebalancear (cooldown global)
        pode_rebalancear = True
        agora = datetime.utcnow()
        
        # Verifica se houve alguma operação recente
        if self.ultima_operacao_por_ativo:
            tempo_minimo = min(
                (agora - ultima_op).total_seconds() 
                for ultima_op in self.ultima_operacao_por_ativo.values()
                if isinstance(ultima_op, datetime)
            )
            if tempo_minimo < self.cooldown_segundos:
                pode_rebalancear = False
                portfolio_logger.debug(
                    f"Rebalanceamento adiado: última operação há {tempo_minimo:.1f}s "
                    f"(cooldown: {self.cooldown_segundos}s)"
                )
        
        for tipo_ativo, config in self.configuracao_alvo.items():
            porcentagem_alvo = config["porcentagem_alvo"]
            tolerancia = config.get("tolerancia", 5.0)
            
            porcentagem_atual = distribuicao.get(
                tipo_ativo.value, {}
            ).get("porcentagem", 0.0)
            
            diferenca = abs(porcentagem_atual - porcentagem_alvo)
            
            if diferenca > tolerancia:
                # Cria alerta apenas uma vez por tipo (evita spam)
                db = SessionLocal()
                try:
                    # Verifica se já existe alerta recente para este tipo
                    alerta_existente = db.query(Alerta).filter(
                        Alerta.agente_origem == self.name,
                        Alerta.tipo == "diversificacao_desbalanceada",
                        Alerta.mensagem.like(f"%{tipo_ativo.value}%")
                    ).order_by(Alerta.timestamp.desc()).first()
                    
                    # Só cria novo alerta se não houver um recente (últimos 60 segundos)
                    criar_alerta = True
                    if alerta_existente and alerta_existente.timestamp:
                        tempo_alerta = (agora - alerta_existente.timestamp).total_seconds()
                        if tempo_alerta < 60:
                            criar_alerta = False
                    
                    if criar_alerta:
                        alerta = Alerta(
                            agente_origem=self.name,
                            tipo="diversificacao_desbalanceada",
                            mensagem=(
                                f"Diversificação desbalanceada em {tipo_ativo.value}: "
                                f"atual {porcentagem_atual:.2f}%, "
                                f"alvo {porcentagem_alvo:.2f}%"
                            ),
                            severidade="warning"
                        )
                        db.add(alerta)
                        db.commit()
                finally:
                    db.close()
                
                # Só tenta rebalancear se não houver operações recentes
                if pode_rebalancear:
                    operacoes = await self.decidir_compra_venda()
                    if operacoes:
                        # Se a carteira está muito desbalanceada (muitas operações necessárias),
                        # executa mais operações por ciclo para acelerar o investimento inicial
                        db_temp = SessionLocal()
                        try:
                            carteira_temp = db_temp.query(Carteira).first()
                            posicoes_temp = db_temp.query(Posicao).count()
                            
                            # Se não há posições ou há muito dinheiro em caixa, executa mais operações
                            saldo_percentual = (carteira_temp.saldo_disponivel / carteira_temp.valor_total_carteira * 100) if carteira_temp.valor_total_carteira > 0 else 100
                            
                            if posicoes_temp == 0 or saldo_percentual > 80:
                                # Carteira vazia ou muito dinheiro em caixa: executa até 3 operações por ciclo
                                max_operacoes = min(3, len(operacoes))
                            else:
                                # Carteira já tem posições: mantém limite de 1 operação
                                max_operacoes = 1
                        finally:
                            db_temp.close()
                        
                        portfolio_logger.info(
                            f"Iniciando rebalanceamento: {len(operacoes)} operações planejadas, "
                            f"executando {max_operacoes}"
                        )
                        
                        # Executa múltiplas operações se necessário
                        for i in range(max_operacoes):
                            if i < len(operacoes):
                                await self._solicitar_autorizacao(operacoes[i])
                        
                        # Marca que houve tentativa de rebalanceamento
                        self.ultima_operacao_por_ativo["_rebalanceamento"] = agora

    async def _solicitar_autorizacao(self, operacao: dict):
        """Solicita autorização ao WalletManager"""
        # Verifica saldo atual antes de solicitar autorização
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if not carteira:
                portfolio_logger.error("Carteira não encontrada ao solicitar autorização")
                return
            
            # Se for compra, verifica se ainda há saldo suficiente
            if operacao.get("tipo") == "compra":
                valor_solicitado = operacao.get("valor", 0)
                saldo_atual = carteira.saldo_disponivel
                
                # GARANTE que o valor não excede o saldo disponível
                if valor_solicitado > saldo_atual:
                    portfolio_logger.warning(
                        f"[SOLICITAÇÃO] Valor solicitado (R$ {valor_solicitado:.2f}) "
                        f"excede saldo disponível (R$ {saldo_atual:.2f}). "
                        f"Ajustando valor..."
                    )
                    # Ajusta para o máximo disponível se ainda for significativo
                    if saldo_atual > 100:
                        operacao["valor"] = saldo_atual
                        portfolio_logger.info(
                            f"[SOLICITAÇÃO] Valor ajustado para R$ {saldo_atual:.2f} "
                            f"(saldo disponível)"
                        )
                    else:
                        portfolio_logger.debug(
                            f"[SOLICITAÇÃO] Saldo muito baixo (R$ {saldo_atual:.2f}), "
                            f"não solicitando compra de R$ {valor_solicitado:.2f}"
                        )
                        return
                else:
                    portfolio_logger.debug(
                        f"[SOLICITAÇÃO] Solicitando autorização: {operacao.get('ativo_codigo')} "
                        f"por R$ {valor_solicitado:.2f} (saldo: R$ {saldo_atual:.2f})"
                    )
        finally:
            db.close()
        
        # Envia solicitação com o valor (possivelmente ajustado)
        valor_final = operacao.get("valor", 0)
        await self.message_bus.send(
            Message(
                message_type=MessageType.SOLICITACAO_AUTORIZACAO,
                sender=self.name,
                receiver="WalletManager",
                payload={
                    "tipo": operacao["tipo"],
                    "valor": valor_final,
                    "ativo_codigo": operacao["ativo_codigo"],
                    "quantidade": operacao.get("quantidade"),
                    "motivo": operacao.get("motivo")
                }
            )
        )

    async def _processar_autorizacao_compra(self, message: Message):
        """Processa autorização de compra recebida"""
        payload = message.payload
        
        # Só adiciona à lista se foi autorizada
        if payload.get("autorizado"):
            operacao_id = f"compra_{payload.get('ativo_codigo', '')}_{payload.get('valor', 0)}"
            self.autorizacoes_recebidas[operacao_id] = payload
            self.operacoes_pendentes.append({
                "tipo": "compra",
                "ativo_codigo": payload.get("ativo_codigo"),
                "valor": payload.get("valor"),
                "motivo": payload.get("motivo", "Ajuste de diversificação")
            })
            portfolio_logger.info(
                f"Autorização de compra recebida: {payload.get('ativo_codigo')} "
                f"por R$ {payload.get('valor', 0):.2f}"
            )
        else:
            # Log quando autorização é negada
            portfolio_logger.warning(
                f"Autorização de compra negada: {payload.get('ativo_codigo', 'N/A')} "
                f"por R$ {payload.get('valor', 0):.2f}. "
                f"Motivo: {payload.get('motivo', 'desconhecido')}"
            )

    async def _processar_autorizacao_venda(self, message: Message):
        """Processa autorização de venda recebida"""
        if message.payload.get("autorizado"):
            payload = message.payload
            operacao_id = f"venda_{payload.get('ativo_codigo', '')}_{payload.get('valor', 0)}"
            self.autorizacoes_recebidas[operacao_id] = payload
            self.operacoes_pendentes.append({
                "tipo": "venda",
                "ativo_codigo": payload.get("ativo_codigo"),
                "quantidade": payload.get("quantidade"),
                "motivo": payload.get("motivo", "Ajuste de diversificação")
            })
            portfolio_logger.info(
                f"Autorização de venda recebida: {payload.get('ativo_codigo')} "
                f"quantidade: {payload.get('quantidade', 0):.4f}"
            )

    async def _processar_operacoes_autorizadas(self):
        """Processa operações que receberam autorização"""
        operacoes_executadas = []
        
        for op in self.operacoes_pendentes[:]:
            try:
                if op["tipo"] == "compra":
                    ativo_codigo = op.get("ativo_codigo")
                    valor = op.get("valor")
                    
                    if ativo_codigo and valor:
                        # Verifica saldo novamente antes de executar (pode ter mudado)
                        db = SessionLocal()
                        try:
                            carteira = db.query(Carteira).first()
                            if not carteira:
                                portfolio_logger.error("Carteira não encontrada ao processar operação autorizada")
                                continue
                            
                            # Se o saldo mudou e não é mais suficiente, ajusta ou pula
                            if valor > carteira.saldo_disponivel:
                                portfolio_logger.warning(
                                    f"Saldo insuficiente ao executar operação autorizada: "
                                    f"solicitado R$ {valor:.2f}, disponível R$ {carteira.saldo_disponivel:.2f}. "
                                    f"Ajustando valor..."
                                )
                                # Ajusta para o máximo disponível se ainda for significativo
                                if carteira.saldo_disponivel > 100:
                                    valor = carteira.saldo_disponivel
                                    op["valor"] = valor
                                    portfolio_logger.info(
                                        f"Valor ajustado para R$ {valor:.2f} (saldo disponível)"
                                    )
                                else:
                                    portfolio_logger.debug(
                                        f"Saldo muito baixo (R$ {carteira.saldo_disponivel:.2f}), "
                                        f"pulando operação"
                                    )
                                    continue
                        finally:
                            db.close()
                        
                        sucesso = await self.executar_operacao(
                            tipo="compra",
                            ativo_codigo=ativo_codigo,
                            valor=valor
                        )
                        if sucesso:
                            operacoes_executadas.append(op)
                            portfolio_logger.info(
                                f"Operação de compra executada: {ativo_codigo} "
                                f"por R$ {valor:.2f}"
                            )
                        else:
                            portfolio_logger.warning(
                                f"Operação de compra não executada: {ativo_codigo} "
                                f"por R$ {valor:.2f} (falha na execução)"
                            )
                
                elif op["tipo"] == "venda":
                    ativo_codigo = op.get("ativo_codigo")
                    quantidade = op.get("quantidade")
                    
                    if ativo_codigo and quantidade:
                        sucesso = await self.executar_operacao(
                            tipo="venda",
                            ativo_codigo=ativo_codigo,
                            quantidade=quantidade
                        )
                        if sucesso:
                            operacoes_executadas.append(op)
                            portfolio_logger.info(
                                f"Operação de venda executada: {ativo_codigo} "
                                f"quantidade: {quantidade:.4f}"
                            )
            except Exception as e:
                portfolio_logger.error(
                    f"Erro ao processar operação autorizada: {e}. "
                    f"Operação: {op}"
                )
        
        # Remove apenas as operações executadas com sucesso
        for op_executada in operacoes_executadas:
            if op_executada in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(op_executada)
        
        # Limpa operações pendentes antigas (mais de 10 itens)
        if len(self.operacoes_pendentes) > 10:
            self.operacoes_pendentes = self.operacoes_pendentes[-10:]

    async def _processar_sinal_compra(self, message: Message):
        """Processa sinal de compra do MarketAnalyst"""
        from datetime import datetime
        
        sinais = message.payload.get("sinais", {})
        for codigo, sinal in sinais.items():
            if sinal["acao"] == "compra":
                # Verifica cooldown
                ultima_op = self.ultima_operacao_por_ativo.get(codigo)
                if ultima_op:
                    tempo_decorrido = (datetime.utcnow() - ultima_op).total_seconds()
                    if tempo_decorrido < self.cooldown_segundos:
                        portfolio_logger.debug(
                            f"Cooldown ativo para {codigo}: "
                            f"{self.cooldown_segundos - tempo_decorrido:.1f}s restantes"
                        )
                        continue
                
                # Só compra se houver saldo suficiente e não estiver tentando rebalancear ao mesmo tempo
                db = SessionLocal()
                try:
                    carteira = db.query(Carteira).first()
                    if carteira and carteira.saldo_disponivel > 1000:
                        await self._solicitar_autorizacao({
                            "tipo": "compra",
                            "ativo_codigo": codigo,
                            "valor": min(1000.0, carteira.saldo_disponivel * 0.1),  # Máximo 10% do saldo
                            "motivo": sinal.get("motivo", "Sinal de compra")
                        })
                        self.ultima_operacao_por_ativo[codigo] = datetime.utcnow()
                finally:
                    db.close()

    async def _processar_sinal_venda(self, message: Message):
        """Processa sinal de venda do MarketAnalyst"""
        from datetime import datetime, timedelta
        
        sinais = message.payload.get("sinais", {})
        for codigo, sinal in sinais.items():
            if sinal["acao"] == "venda":
                # Verifica cooldown
                ultima_op = self.ultima_operacao_por_ativo.get(codigo)
                if ultima_op:
                    tempo_decorrido = (datetime.utcnow() - ultima_op).total_seconds()
                    if tempo_decorrido < self.cooldown_segundos:
                        portfolio_logger.debug(
                            f"Cooldown ativo para {codigo}: "
                            f"{self.cooldown_segundos - tempo_decorrido:.1f}s restantes"
                        )
                        continue
                
                db = SessionLocal()
                try:
                    posicao = db.query(Posicao).join(Ativo).filter(
                        Ativo.codigo == codigo
                    ).first()
                    
                    if posicao and posicao.quantidade > 0:
                        # Vende apenas 5% em vez de 10% para ser menos agressivo
                        quantidade_venda = posicao.quantidade * 0.05
                        
                        # Garante que não tenta vender mais do que tem
                        quantidade_venda = min(quantidade_venda, posicao.quantidade)
                        
                        # Só vende se a quantidade for significativa (mínimo R$ 100)
                        valor_venda = quantidade_venda * posicao.ativo.preco_atual
                        if valor_venda >= 100 and quantidade_venda > 0:
                            await self._solicitar_autorizacao({
                                "tipo": "venda",
                                "ativo_codigo": codigo,
                                "quantidade": quantidade_venda,
                                "motivo": sinal.get("motivo", "Sinal de venda")
                            })
                            self.ultima_operacao_por_ativo[codigo] = datetime.utcnow()
                        else:
                            portfolio_logger.debug(
                                f"Não vendendo {codigo}: quantidade muito pequena "
                                f"({quantidade_venda:.4f} = R$ {valor_venda:.2f})"
                            )
                finally:
                    db.close()

    async def _processar_analise_tendencia(self, message: Message):
        """Processa análise de tendência do MarketAnalyst"""
        portfolio_logger.debug(f"Análise recebida: {message.payload}")

    async def _processar_alerta_liquidez(self, message: Message):
        """Processa alerta de liquidez baixa"""
        portfolio_logger.warning(
            f"Alerta de liquidez: {message.payload.get('mensagem')}"
        )

    async def _calcular_valor_total_carteira(self) -> float:
        """Calcula valor total da carteira"""
        db = SessionLocal()
        try:
            carteira = db.query(Carteira).first()
            if carteira:
                return carteira.valor_total_carteira
            return 0.0
        finally:
            db.close()

    async def _atualizar_valor_total_carteira(self, db: Session = None):
        """Atualiza valor total da carteira baseado no valor atual de mercado"""
        if db is None:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            carteira = db.query(Carteira).first()
            if carteira:
                # Busca posições com seus ativos (precisa fazer join para pegar preco_atual)
                posicoes = db.query(Posicao).join(Ativo).all()
                
                # Calcula valor total usando preço ATUAL de mercado, não o custo médio
                valor_posicoes = sum(p.quantidade * p.ativo.preco_atual for p in posicoes)
                
                # Se não há posições, valor total = saldo disponível
                # Se há posições, valor total = valor das posições + saldo disponível
                valor_total = valor_posicoes + carteira.saldo_disponivel
                
                # Garante que o valor total nunca seja menor que o saldo disponível
                # (isso pode acontecer se os preços caírem muito, mas é um limite de segurança)
                if valor_total < carteira.saldo_disponivel:
                    portfolio_logger.warning(
                        f"Valor total ({valor_total:.2f}) menor que saldo disponível "
                        f"({carteira.saldo_disponivel:.2f}). Isso indica perdas significativas."
                    )
                
                # Log detalhado para debug
                valor_anterior = carteira.valor_total_carteira
                diferenca = valor_total - valor_anterior
                
                portfolio_logger.info(
                    f"[VALOR TOTAL] Anterior: R$ {valor_anterior:.2f} | "
                    f"Novo: R$ {valor_total:.2f} | "
                    f"Diferença: R$ {diferenca:+.2f} | "
                    f"Posições: R$ {valor_posicoes:.2f} ({len(posicoes)} pos) | "
                    f"Saldo: R$ {carteira.saldo_disponivel:.2f}"
                )
                
                # Log detalhado de cada posição se houver
                if posicoes:
                    for p in posicoes:
                        valor_atual_mercado = p.quantidade * p.ativo.preco_atual
                        valor_investido = p.valor_total
                        ganho_perda = valor_atual_mercado - valor_investido
                        portfolio_logger.debug(
                            f"  Posição {p.ativo.codigo}: "
                            f"Qtd={p.quantidade:.4f}, "
                            f"Preço={p.ativo.preco_atual:.2f}, "
                            f"Investido=R$ {valor_investido:.2f}, "
                            f"Atual=R$ {valor_atual_mercado:.2f}, "
                            f"G/P=R$ {ganho_perda:+.2f}"
                        )
                
                carteira.valor_total_carteira = valor_total
                if should_close:
                    db.commit()
        finally:
            if should_close:
                db.close()

