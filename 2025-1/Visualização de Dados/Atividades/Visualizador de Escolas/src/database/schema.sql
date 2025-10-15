-- Criação da tabela de Regiões
CREATE TABLE regiao (
    id_regiao INTEGER PRIMARY KEY,
    nome_regiao VARCHAR(20) NOT NULL,
    UNIQUE(nome_regiao)
);

-- Criação da tabela de UFs
CREATE TABLE uf (
    id_uf INTEGER PRIMARY KEY,
    nome_uf VARCHAR(50) NOT NULL,
    sigla_uf CHAR(2) NOT NULL,
    id_regiao INTEGER NOT NULL,
    FOREIGN KEY (id_regiao) REFERENCES regiao(id_regiao),
    UNIQUE(sigla_uf),
    UNIQUE(nome_uf)
);

-- Criação da tabela de Municípios
CREATE TABLE municipio (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio VARCHAR(100) NOT NULL,
    id_uf INTEGER NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES uf(id_uf)
);

-- Criação da tabela de Escolas
CREATE TABLE escola (
    id_escola INTEGER PRIMARY KEY,
    nome_escola VARCHAR(200) NOT NULL,
    endereco VARCHAR(300),
    id_municipio INTEGER NOT NULL,
    FOREIGN KEY (id_municipio) REFERENCES municipio(id_municipio)
);

-- Criação de índices para otimizar consultas
CREATE INDEX idx_uf_regiao ON uf(id_regiao);
CREATE INDEX idx_municipio_uf ON municipio(id_uf);
CREATE INDEX idx_escola_municipio ON escola(id_municipio); 