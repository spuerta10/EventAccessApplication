CREATE EXTENSION IF NOT EXISTS pgcrypto;

\c :DB_NAME;

INSERT INTO users (username, password_hash)
VALUES 
    ('spuertaf', 'spuertaf'),
    ('juanperez', 'juanperez');

INSERT INTO tickets (seat, gate, seed, status)
VALUES
    ('A12', 'G1', gen_random_bytes(20), 'valid'),
    ('B05', 'G2', gen_random_bytes(20), 'valid'),
    ('C18', 'G3', gen_random_bytes(20), 'valid'),
    ('D10', 'G1', gen_random_bytes(20), 'valid'),
    ('E20', 'G2', gen_random_bytes(20), 'valid');
