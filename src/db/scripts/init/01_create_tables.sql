\if :{?DB_NAME}
    \c :DB_NAME
\else
    \c event_access;
\endif

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(user_id),  -- not given user until registered
    seat VARCHAR(10) NOT NULL,
    gate VARCHAR(10) NOT NULL,
    seed BYTEA NOT NULL,                          -- TOTP seed
    status VARCHAR(20) NOT NULL DEFAULT 'valid',
    created_at TIMESTAMP DEFAULT now(),
    used_at TIMESTAMP,
    CONSTRAINT uq_ticket_seat_gate UNIQUE (seat, gate)  -- unique seat + gate convination
);
