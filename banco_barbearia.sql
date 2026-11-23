-- ==========================================================
-- SISTEMA BARBEARIA NAVALHA - SCRIPT SQL (POSTGRESQL)
-- Autor: Davi Negreiros de Macêdo Reis
-- ==========================================================

-- 1. Criação das tabelas
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    preco NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    servico_id INT REFERENCES servicos(id) ON DELETE CASCADE,
    data_agendamento DATE NOT NULL,
    horario TIME NOT NULL
);

-- 2. Inserção de dados iniciais
INSERT INTO usuarios (username, senha)
VALUES ('admin', '1234')
ON CONFLICT (username) DO NOTHING;

INSERT INTO servicos (nome, preco)
SELECT v.nome, v.preco
FROM (VALUES
    ('Corte', 35.00),
    ('Barba', 25.00),
    ('Corte + barba', 50.00),
    ('Sobrancelha', 10.00)
) AS v(nome, preco)
WHERE NOT EXISTS (SELECT 1 FROM servicos);

INSERT INTO agendamentos (cliente, telefone, servico_id, data_agendamento, horario)
SELECT
    v.cliente,
    v.telefone,
    s.id,
    v.data_agendamento::DATE,
    v.horario::TIME
FROM (VALUES
    ('Lucas Almeida', '86999991111', 'Corte', '2026-11-18', '09:00'),
    ('Rafael Costa', '86999992222', 'Corte + barba', '2026-11-18', '10:30'),
    ('Bruno Mendes', '86999993333', 'Barba', '2026-11-19', '14:00'),
    ('Matheus Lima', '86999994444', 'Sobrancelha', '2026-11-19', '15:00'),
    ('Gabriel Rocha', '86999995555', 'Corte + barba', '2026-11-20', '16:30'),
    ('Thiago Souza', '86999996666', 'Corte', '2026-11-20', '17:30'),
    ('Pedro Henrique', '86999997777', 'Corte', '2026-11-21', '11:00')
) AS v(cliente, telefone, nome_servico, data_agendamento, horario)
JOIN servicos s ON s.nome = v.nome_servico
WHERE NOT EXISTS (SELECT 1 FROM agendamentos);

-- 3. Consultas SQL utilizadas nos KPIs, gráficos e análises

-- KPIs gerais + MIN e MAX de preço dos serviços agendados (JOIN, MIN, MAX)
SELECT
    COUNT(a.id) AS total_agendamentos,
    COALESCE(SUM(s.preco), 0) AS faturamento_total,
    COALESCE(MIN(s.preco), 0) AS menor_preco_servico,
    COALESCE(MAX(s.preco), 0) AS maior_preco_servico
FROM agendamentos a
LEFT JOIN servicos s ON a.servico_id = s.id;

-- Faturamento e quantidade por serviço (JOIN + GROUP BY)
SELECT
    s.nome AS servico,
    COUNT(a.id) AS qtd_agendamentos,
    COALESCE(SUM(s.preco), 0) AS faturamento
FROM servicos s
LEFT JOIN agendamentos a ON s.id = a.servico_id
GROUP BY s.id, s.nome
ORDER BY faturamento DESC, qtd_agendamentos DESC;

-- Evolução de agendamentos por data (GROUP BY)
SELECT
    data_agendamento,
    COUNT(id) AS total_agendamentos
FROM agendamentos
GROUP BY data_agendamento
ORDER BY data_agendamento ASC;

-- Serviços com quantidade mínima de agendamentos (GROUP BY + HAVING)
SELECT
    s.nome AS servico,
    COUNT(a.id) AS qtd_agendamentos,
    SUM(s.preco) AS faturamento
FROM servicos s
JOIN agendamentos a ON s.id = a.servico_id
GROUP BY s.id, s.nome
HAVING COUNT(a.id) >= 2
ORDER BY qtd_agendamentos DESC;

-- Agendamentos com preço maior ou igual à média dos serviços agendados (SUBQUERY + JOIN)
SELECT
    a.id,
    a.cliente,
    s.nome AS servico,
    s.preco,
    a.data_agendamento,
    a.horario
FROM agendamentos a
JOIN servicos s ON a.servico_id = s.id
WHERE s.preco >= (
    SELECT AVG(s2.preco)
    FROM agendamentos a2
    JOIN servicos s2 ON a2.servico_id = s2.id
)
ORDER BY s.preco DESC, a.data_agendamento DESC;