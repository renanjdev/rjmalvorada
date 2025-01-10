-- Criação da Tabela Jovens (deve ser criada antes porque outras tabelas dependem dela)
CREATE TABLE IF NOT EXISTS jovens (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    whatsapp TEXT NOT NULL,
    endereco TEXT,
    pais TEXT,
    grupo_recitativo TEXT NOT NULL,
    batizado TEXT NOT NULL,
    data_batismo DATE,
    observacoes TEXT
);

-- Criação da Tabela Auxiliares
CREATE TABLE IF NOT EXISTS auxiliares (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    grupo_responsavel TEXT NOT NULL,
    data_batismo TEXT DEFAULT '',
    data_apresentacao TEXT DEFAULT '',
    whatsapp TEXT,
    data_nascimento TEXT
);

-- Criação da Tabela Frequência
CREATE TABLE IF NOT EXISTS frequencia (
    id SERIAL PRIMARY KEY,
    pessoa_id INTEGER NOT NULL,
    data DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('presente', 'ausente')),
    FOREIGN KEY (pessoa_id) REFERENCES jovens (id)
);

-- Inserção de Dados na Tabela Jovens
INSERT INTO jovens (id, nome, data_nascimento, whatsapp, endereco, pais, grupo_recitativo, batizado, data_batismo, observacoes) VALUES
(3, 'João Miguel', '2018-10-17', '(14) 99626-2040', 'José Homero Moreira, 155 - Jardim Imperial', 'Joyce e Renan', 'Meninos 0 a 6 anos', 'nao', NULL, NULL),
(7, 'Andrey', '2005-06-10', '(14) 99889-3092', 'Não informado', 'Miriam e Marcelo', 'Moços 12+ anos', 'sim', '2020-02-29', 'Sem observações');

-- Inserção de Dados na Tabela Auxiliares
INSERT INTO auxiliares (id, nome, grupo_responsavel, data_batismo, data_apresentacao, whatsapp, data_nascimento) VALUES
(4, 'Gabriel', 'Moços 12+ anos', '2018-07-28', '2018-08-12', '14982259593', '1998-04-04'),
(5, 'Belinha', 'Moças 12+ anos', '2016-05-21', '2017-02-11', '14991332053', '2000-10-18'),
(6, 'Abner', 'Meninos 7 a 11 anos', '2017-02-18', '2018-08-12', '14991130464', '2005-06-09'),
(7, 'Letícia', 'Meninas 7 a 11 anos', '2011-11-27', '2011-11-11', '14991156269', '1998-12-16'),
(8, 'Luis Felipe', 'Meninos 0 a 6 anos', '2020-02-29', '2021-08-07', '14982117313', '2007-02-12'),
(9, 'Otávio', 'Moços 12+ anos', '', '2021-08-07', '14981377225', '2004-02-26'),
(10, 'Amauri', 'Meninos 0 a 6 anos', '2020-02-29', '2023-12-09', '14991236873', '1111-01-01'),
(11, 'Selma', 'Moças 12+ anos', '1998-08-30', '2010-04-25', '14981034367', '1980-01-14'),
(12, 'Helena', 'Meninas 7 a 11 anos', '2019-11-16', '2024-09-08', '14991962259', '2007-02-15'),
(13, 'Daniel', 'Moços 12+ anos', '2023-05-20', '2023-12-09', '14991571029', '2024-01-13');

-- Inserção de Dados na Tabela Frequência
INSERT INTO frequencia (id, pessoa_id, data, status) VALUES
(1, 7, '2024-12-29', 'presente'),
(2, 3, '2024-12-29', 'presente'),
(3, 7, '2024-12-29', 'presente'),
(4, 3, '2024-12-29', 'presente'),
(5, 7, '2025-01-05', 'presente'),
(6, 3, '2025-01-05', 'presente'),
(7, 7, '2025-01-12', 'presente'),
(8, 3, '2025-01-12', 'ausente'),
(9, 7, '2025-01-19', 'ausente'),
(10, 3, '2025-01-19', 'presente');
