-- ============================================================
-- SCRIPT DDL - SISTEMA DE DADOS SOCIOECONÔMICOS DEC7588
-- Base de Dados: PostgreSQL  
-- Projeto: Sistema de Gestão de IDH e Despesas Públicas Federais
-- ============================================================

-- Configurações iniciais
SET client_encoding TO 'UTF8';
SET timezone TO 'America/Sao_Paulo';

-- ============================================================
-- ENTIDADES GEOGRÁFICAS
-- ============================================================

-- Tabela 1: Regiões Geográficas do Brasil
CREATE TABLE regiao (
    id SERIAL PRIMARY KEY,
    nome_regiao VARCHAR(50) NOT NULL UNIQUE,
    codigo_ibge VARCHAR(10) UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 2: Estados e Distrito Federal
CREATE TABLE estado (
    id SERIAL PRIMARY KEY,
    nome_estado VARCHAR(100) NOT NULL,
    sigla_uf VARCHAR(2) NOT NULL UNIQUE,
    codigo_ibge VARCHAR(10) UNIQUE,
    capital VARCHAR(100),
    populacao_estimada INTEGER,
    area_km2 DECIMAL(12,2),
    regiao_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_estado_regiao FOREIGN KEY (regiao_id) 
        REFERENCES regiao(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela 3: Municípios (para expansões futuras)
CREATE TABLE municipio (
    id SERIAL PRIMARY KEY,
    nome_municipio VARCHAR(100) NOT NULL,
    codigo_ibge VARCHAR(10) UNIQUE,
    populacao INTEGER,
    eh_capital BOOLEAN DEFAULT FALSE,
    estado_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_municipio_estado FOREIGN KEY (estado_id) 
        REFERENCES estado(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- ENTIDADES ORGANIZACIONAIS
-- ============================================================

-- Tabela 4: Órgãos Públicos
CREATE TABLE orgao_publico (
    id SERIAL PRIMARY KEY,
    nome_orgao VARCHAR(200) NOT NULL,
    sigla_orgao VARCHAR(20),
    codigo_siafi VARCHAR(10) UNIQUE,
    tipo_orgao VARCHAR(50) CHECK (tipo_orgao IN ('Federal', 'Estadual', 'Municipal')),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 5: Fontes de Recursos
CREATE TABLE fonte_recurso (
    id SERIAL PRIMARY KEY,
    nome_fonte VARCHAR(200) NOT NULL,
    codigo_fonte VARCHAR(10) UNIQUE,
    tipo_fonte VARCHAR(50),
    descricao TEXT,
    ativa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ENTIDADES FINANCEIRAS  
-- ============================================================

-- Tabela 6: Categorias de Despesas
CREATE TABLE categoria_despesa (
    id SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(100) NOT NULL UNIQUE,
    codigo_categoria VARCHAR(10) UNIQUE,
    descricao TEXT,
    cor_grafico VARCHAR(7), -- Cor hexadecimal (#RRGGBB)
    ativa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 7: Períodos Temporais
CREATE TABLE periodo (
    id SERIAL PRIMARY KEY,
    ano INTEGER NOT NULL UNIQUE,
    trimestre INTEGER CHECK (trimestre BETWEEN 1 AND 4),
    mes INTEGER CHECK (mes BETWEEN 1 AND 12),
    data_inicio DATE,
    data_fim DATE,
    descricao VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 8: Orçamentos
CREATE TABLE orcamento (
    id SERIAL PRIMARY KEY,
    valor_previsto_milhoes DECIMAL(15,2) NOT NULL CHECK (valor_previsto_milhoes >= 0),
    valor_empenhado_milhoes DECIMAL(15,2) CHECK (valor_empenhado_milhoes >= 0),
    valor_liquidado_milhoes DECIMAL(15,2) CHECK (valor_liquidado_milhoes >= 0),
    valor_pago_milhoes DECIMAL(15,2) CHECK (valor_pago_milhoes >= 0),
    observacoes TEXT,
    periodo_id INTEGER NOT NULL,
    categoria_despesa_id INTEGER NOT NULL,
    orgao_publico_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_orcamento_periodo FOREIGN KEY (periodo_id) 
        REFERENCES periodo(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orcamento_categoria FOREIGN KEY (categoria_despesa_id) 
        REFERENCES categoria_despesa(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orcamento_orgao FOREIGN KEY (orgao_publico_id) 
        REFERENCES orgao_publico(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela 9: Despesas (ENTIDADE CENTRAL)
CREATE TABLE despesa (
    id SERIAL PRIMARY KEY,
    valor_milhoes DECIMAL(15,2) NOT NULL CHECK (valor_milhoes >= 0),
    valor_per_capita DECIMAL(10,2) CHECK (valor_per_capita >= 0),
    tipo_despesa VARCHAR(50),
    numero_beneficiarios INTEGER CHECK (numero_beneficiarios >= 0),
    descricao TEXT,
    estado_id INTEGER NOT NULL,
    categoria_despesa_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL,
    orgao_publico_id INTEGER NOT NULL,
    fonte_recurso_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_despesa_estado FOREIGN KEY (estado_id) 
        REFERENCES estado(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_despesa_categoria FOREIGN KEY (categoria_despesa_id) 
        REFERENCES categoria_despesa(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_despesa_periodo FOREIGN KEY (periodo_id) 
        REFERENCES periodo(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_despesa_orgao FOREIGN KEY (orgao_publico_id) 
        REFERENCES orgao_publico(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_despesa_fonte FOREIGN KEY (fonte_recurso_id) 
        REFERENCES fonte_recurso(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- ENTIDADES DE INDICADORES
-- ============================================================

-- Tabela 10: Indicadores de IDH
CREATE TABLE indicador_idh (
    id SERIAL PRIMARY KEY,
    idh_geral DECIMAL(4,3) NOT NULL CHECK (idh_geral BETWEEN 0 AND 1),
    idh_educacao DECIMAL(4,3) CHECK (idh_educacao BETWEEN 0 AND 1),
    idh_longevidade DECIMAL(4,3) CHECK (idh_longevidade BETWEEN 0 AND 1),
    idh_renda DECIMAL(4,3) CHECK (idh_renda BETWEEN 0 AND 1),
    ranking_nacional INTEGER CHECK (ranking_nacional > 0),
    ranking_regional INTEGER CHECK (ranking_regional > 0),
    observacoes TEXT,
    estado_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_idh_estado FOREIGN KEY (estado_id) 
        REFERENCES estado(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_idh_periodo FOREIGN KEY (periodo_id) 
        REFERENCES periodo(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Constraint única para evitar duplicatas
    CONSTRAINT uk_idh_estado_periodo UNIQUE (estado_id, periodo_id)
);

-- ============================================================
-- ENTIDADES DO SISTEMA
-- ============================================================

-- Tabela 11: Usuários do Sistema
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_usuario VARCHAR(20) DEFAULT 'normal' 
        CHECK (tipo_usuario IN ('admin', 'normal', 'readonly')),
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 12: Relatórios Gerados
CREATE TABLE relatorio (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    tipo_relatorio VARCHAR(50) NOT NULL 
        CHECK (tipo_relatorio IN ('consulta1', 'consulta2', 'consulta3', 'custom')),
    descricao TEXT,
    parametros_json TEXT, -- JSON com parâmetros
    resultado_json TEXT,  -- JSON com resultados
    caminho_arquivo VARCHAR(500),
    formato_arquivo VARCHAR(10) CHECK (formato_arquivo IN ('PDF', 'CSV', 'HTML', 'JSON')),
    status VARCHAR(20) DEFAULT 'gerado' 
        CHECK (status IN ('gerado', 'erro', 'processando')),
    usuario_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_relatorio_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- ÍNDICES PARA OTIMIZAÇÃO
-- ============================================================

-- Índices para consultas frequentes
CREATE INDEX idx_estado_regiao ON estado(regiao_id);
CREATE INDEX idx_municipio_estado ON municipio(estado_id);
CREATE INDEX idx_despesa_estado ON despesa(estado_id);
CREATE INDEX idx_despesa_categoria ON despesa(categoria_despesa_id);
CREATE INDEX idx_despesa_periodo ON despesa(periodo_id);
CREATE INDEX idx_idh_estado ON indicador_idh(estado_id);
CREATE INDEX idx_relatorio_usuario ON relatorio(usuario_id);

-- Índices compostos para consultas complexas
CREATE INDEX idx_despesa_estado_periodo ON despesa(estado_id, periodo_id);
CREATE INDEX idx_idh_geral_desc ON indicador_idh(idh_geral DESC);

-- ============================================================
-- DADOS INICIAIS (SEED DATA)
-- ============================================================

-- Inserir regiões do Brasil
INSERT INTO regiao (nome_regiao, codigo_ibge, descricao) VALUES
('Norte', '1', 'Região Norte do Brasil'),
('Nordeste', '2', 'Região Nordeste do Brasil'),  
('Sudeste', '3', 'Região Sudeste do Brasil'),
('Sul', '4', 'Região Sul do Brasil'),
('Centro-Oeste', '5', 'Região Centro-Oeste do Brasil');

-- Inserir períodos (2019-2023)
INSERT INTO periodo (ano, data_inicio, data_fim, descricao) VALUES
(2019, '2019-01-01', '2019-12-31', 'Ano de 2019'),
(2020, '2020-01-01', '2020-12-31', 'Ano de 2020'),
(2021, '2021-01-01', '2021-12-31', 'Ano de 2021'),
(2022, '2022-01-01', '2022-12-31', 'Ano de 2022'),
(2023, '2023-01-01', '2023-12-31', 'Ano de 2023');

-- Inserir categorias principais de despesas
INSERT INTO categoria_despesa (nome_categoria, codigo_categoria, descricao, cor_grafico) VALUES
('Saúde', 'SA', 'Despesas com saúde pública', '#e74c3c'),
('Educação', 'ED', 'Despesas com educação', '#3498db'),
('Assistência Social', 'AS', 'Despesas com assistência social', '#9b59b6'),
('Previdência Social', 'PS', 'Despesas previdenciárias', '#f39c12'),
('Defesa Nacional', 'DN', 'Despesas com defesa nacional', '#2ecc71'),
('Segurança Pública', 'SP', 'Despesas com segurança pública', '#e67e22'),
('Trabalho', 'TR', 'Despesas relacionadas ao trabalho', '#1abc9c'),
('Outros', 'OU', 'Outras despesas governamentais', '#95a5a6');

-- Inserir usuário administrador padrão
INSERT INTO usuario (nome_usuario, email, senha_hash, tipo_usuario) VALUES
('Administrador', 'admin@sistema.gov.br', 'hash_senha_temporaria', 'admin');

COMMIT;
 