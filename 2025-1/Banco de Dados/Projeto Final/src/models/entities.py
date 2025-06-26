"""
Entidades do Sistema de Dados Socioeconômicos - DEC7588
Modelo conceitual com 12+ entidades

Sistema para gerenciamento de dados de IDH e despesas públicas federais
por estado brasileiro, com funcionalidades CRUD completas.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ==================== ENTIDADES GEOGRÁFICAS ====================

class Regiao(Base):
    """
    Entidade 1: Regiões geográficas do Brasil
    """
    __tablename__ = 'regiao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_regiao = Column(String(50), nullable=False, unique=True)
    codigo_ibge = Column(String(10), unique=True)
    descricao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    estados = relationship("Estado", back_populates="regiao", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Regiao(id={self.id}, nome='{self.nome_regiao}')>"


class Estado(Base):
    """
    Entidade 2: Estados e Distrito Federal
    """
    __tablename__ = 'estado'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_estado = Column(String(100), nullable=False)
    sigla_uf = Column(String(2), nullable=False, unique=True)
    codigo_ibge = Column(String(10), unique=True)
    capital = Column(String(100))
    populacao_estimada = Column(Integer)
    area_km2 = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    regiao_id = Column(Integer, ForeignKey('regiao.id'), nullable=False)
    
    # Relacionamentos
    regiao = relationship("Regiao", back_populates="estados")
    municipios = relationship("Municipio", back_populates="estado", cascade="all, delete-orphan")
    despesas = relationship("Despesa", back_populates="estado")
    indicadores_idh = relationship("IndicadorIDH", back_populates="estado")
    
    def __repr__(self):
        return f"<Estado(id={self.id}, nome='{self.nome_estado}', uf='{self.sigla_uf}')>"


class Municipio(Base):
    """
    Entidade 3: Municípios por estado (para expansões futuras)
    """
    __tablename__ = 'municipio'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_municipio = Column(String(100), nullable=False)
    codigo_ibge = Column(String(10), unique=True)
    populacao = Column(Integer)
    eh_capital = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    estado_id = Column(Integer, ForeignKey('estado.id'), nullable=False)
    
    # Relacionamentos
    estado = relationship("Estado", back_populates="municipios")
    
    def __repr__(self):
        return f"<Municipio(id={self.id}, nome='{self.nome_municipio}')>"

# ==================== ENTIDADES ORGANIZACIONAIS ====================

class OrgaoPublico(Base):
    """
    Entidade 4: Órgãos públicos responsáveis pelos gastos
    """
    __tablename__ = 'orgao_publico'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_orgao = Column(String(200), nullable=False)
    sigla_orgao = Column(String(20))
    codigo_siafi = Column(String(10), unique=True)
    tipo_orgao = Column(String(50))  # Federal, Estadual, Municipal
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    despesas = relationship("Despesa", back_populates="orgao_publico")
    orcamentos = relationship("Orcamento", back_populates="orgao_publico")
    
    def __repr__(self):
        return f"<OrgaoPublico(id={self.id}, nome='{self.nome_orgao}')>"


class FonteRecurso(Base):
    """
    Entidade 5: Fontes de recursos para os gastos
    """
    __tablename__ = 'fonte_recurso'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_fonte = Column(String(200), nullable=False)
    codigo_fonte = Column(String(10), unique=True)
    tipo_fonte = Column(String(50))  # Próprio, Transferência, Empréstimo, etc.
    descricao = Column(Text)
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    despesas = relationship("Despesa", back_populates="fonte_recurso")
    
    def __repr__(self):
        return f"<FonteRecurso(id={self.id}, nome='{self.nome_fonte}')>"

# ==================== ENTIDADES FINANCEIRAS ====================

class CategoriaDespesa(Base):
    """
    Entidade 6: Categorias de despesas públicas
    """
    __tablename__ = 'categoria_despesa'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_categoria = Column(String(100), nullable=False, unique=True)
    codigo_categoria = Column(String(10), unique=True)
    descricao = Column(Text)
    cor_grafico = Column(String(7))  # Cor hexadecimal para gráficos
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    despesas = relationship("Despesa", back_populates="categoria_despesa")
    orcamentos = relationship("Orcamento", back_populates="categoria_despesa")
    
    def __repr__(self):
        return f"<CategoriaDespesa(id={self.id}, nome='{self.nome_categoria}')>"


class Periodo(Base):
    """
    Entidade 7: Períodos temporais para organização dos dados
    """
    __tablename__ = 'periodo'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False, unique=True)
    trimestre = Column(Integer)  # Para análises trimestrais futuras
    mes = Column(Integer)  # Para análises mensais futuras
    data_inicio = Column(Date)
    data_fim = Column(Date)
    descricao = Column(String(100))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    despesas = relationship("Despesa", back_populates="periodo")
    indicadores_idh = relationship("IndicadorIDH", back_populates="periodo")
    orcamentos = relationship("Orcamento", back_populates="periodo")
    
    def __repr__(self):
        return f"<Periodo(id={self.id}, ano={self.ano})>"


class Orcamento(Base):
    """
    Entidade 8: Orçamentos previstos por categoria e órgão
    """
    __tablename__ = 'orcamento'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_previsto_milhoes = Column(Numeric(15, 2), nullable=False)
    valor_empenhado_milhoes = Column(Numeric(15, 2))
    valor_liquidado_milhoes = Column(Numeric(15, 2))
    valor_pago_milhoes = Column(Numeric(15, 2))
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    periodo_id = Column(Integer, ForeignKey('periodo.id'), nullable=False)
    categoria_despesa_id = Column(Integer, ForeignKey('categoria_despesa.id'), nullable=False)
    orgao_publico_id = Column(Integer, ForeignKey('orgao_publico.id'), nullable=False)
    
    # Relacionamentos
    periodo = relationship("Periodo", back_populates="orcamentos")
    categoria_despesa = relationship("CategoriaDespesa", back_populates="orcamentos")
    orgao_publico = relationship("OrgaoPublico", back_populates="orcamentos")
    
    def __repr__(self):
        return f"<Orcamento(id={self.id}, valor_previsto={self.valor_previsto_milhoes})>"


class Despesa(Base):
    """
    Entidade 9: Despesas públicas realizadas (entidade central)
    """
    __tablename__ = 'despesa'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_milhoes = Column(Numeric(15, 2), nullable=False)
    valor_per_capita = Column(Numeric(10, 2))
    tipo_despesa = Column(String(50))  # Corrente, Capital, etc.
    numero_beneficiarios = Column(Integer)
    descricao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    estado_id = Column(Integer, ForeignKey('estado.id'), nullable=False)
    categoria_despesa_id = Column(Integer, ForeignKey('categoria_despesa.id'), nullable=False)
    periodo_id = Column(Integer, ForeignKey('periodo.id'), nullable=False)
    orgao_publico_id = Column(Integer, ForeignKey('orgao_publico.id'), nullable=False)
    fonte_recurso_id = Column(Integer, ForeignKey('fonte_recurso.id'), nullable=False)
    
    # Relacionamentos
    estado = relationship("Estado", back_populates="despesas")
    categoria_despesa = relationship("CategoriaDespesa", back_populates="despesas")
    periodo = relationship("Periodo", back_populates="despesas")
    orgao_publico = relationship("OrgaoPublico", back_populates="despesas")
    fonte_recurso = relationship("FonteRecurso", back_populates="despesas")
    
    def __repr__(self):
        return f"<Despesa(id={self.id}, valor={self.valor_milhoes}, estado_id={self.estado_id})>"

# ==================== ENTIDADES DE INDICADORES ====================

class IndicadorIDH(Base):
    """
    Entidade 10: Índices de Desenvolvimento Humano por estado e período
    """
    __tablename__ = 'indicador_idh'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idh_geral = Column(Float, nullable=False)
    idh_educacao = Column(Float)
    idh_longevidade = Column(Float)
    idh_renda = Column(Float)
    ranking_nacional = Column(Integer)
    ranking_regional = Column(Integer)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    estado_id = Column(Integer, ForeignKey('estado.id'), nullable=False)
    periodo_id = Column(Integer, ForeignKey('periodo.id'), nullable=False)
    
    # Relacionamentos
    estado = relationship("Estado", back_populates="indicadores_idh")
    periodo = relationship("Periodo", back_populates="indicadores_idh")
    
    def __repr__(self):
        return f"<IndicadorIDH(id={self.id}, idh_geral={self.idh_geral}, estado_id={self.estado_id})>"

# ==================== ENTIDADES DO SISTEMA ====================

class Usuario(Base):
    """
    Entidade 11: Usuários do sistema
    """
    __tablename__ = 'usuario'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_usuario = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), default='normal')  # admin, normal, readonly
    ativo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    relatorios = relationship("Relatorio", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome_usuario}', email='{self.email}')>"


class Relatorio(Base):
    """
    Entidade 12: Relatórios gerados pelo sistema
    """
    __tablename__ = 'relatorio'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    tipo_relatorio = Column(String(50), nullable=False)  # consulta1, consulta2, consulta3, custom
    descricao = Column(Text)
    parametros_json = Column(Text)  # JSON com parâmetros usados
    resultado_json = Column(Text)  # JSON com resultados
    caminho_arquivo = Column(String(500))  # Caminho para arquivo gerado
    formato_arquivo = Column(String(10))  # PDF, CSV, HTML, etc.
    status = Column(String(20), default='gerado')  # gerado, erro, processando
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="relatorios")
    
    def __repr__(self):
        return f"<Relatorio(id={self.id}, titulo='{self.titulo}', tipo='{self.tipo_relatorio}')>"

# ==================== CONSTRAINTS E ÍNDICES ====================

# Constraints adicionais podem ser definidas aqui
# Por exemplo, unique constraints compostas, check constraints, etc.

"""
RESUMO DO MODELO CONCEITUAL (12 ENTIDADES):

1. Regiao - Regiões geográficas (5 regiões)
2. Estado - Estados e DF (27 entidades)
3. Municipio - Municípios (para expansão futura)
4. OrgaoPublico - Órgãos responsáveis pelos gastos
5. FonteRecurso - Fontes dos recursos financeiros
6. CategoriaDespesa - Tipos de despesas (Saúde, Educação, etc.)
7. Periodo - Períodos temporais (anos, trimestres, meses)
8. Orcamento - Orçamentos previstos vs realizados
9. Despesa - Despesas realizadas (ENTIDADE CENTRAL)
10. IndicadorIDH - Índices de desenvolvimento humano
11. Usuario - Usuários do sistema
12. Relatorio - Relatórios gerados

RELACIONAMENTOS PRINCIPAIS:
- Estado N:1 Regiao
- Municipio N:1 Estado  
- Despesa N:1 Estado, CategoriaDespesa, Periodo, OrgaoPublico, FonteRecurso
- IndicadorIDH N:1 Estado, Periodo
- Orcamento N:1 Periodo, CategoriaDespesa, OrgaoPublico
- Relatorio N:1 Usuario

CARACTERÍSTICAS:
- Modelo normalizado (3NF)
- Constraints de integridade referencial
- Campos de auditoria (created_at, updated_at)
- Campos de controle (ativo, status)
- Flexibilidade para expansões futuras
""" 