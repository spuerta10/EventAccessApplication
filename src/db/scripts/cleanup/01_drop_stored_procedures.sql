\if :{?DB_NAME}
    \c :DB_NAME
\else
    \c event_access;
\endif

-- Drop procedure sp_register_ticket_to_user
DROP PROCEDURE IF EXISTS sp_register_ticket_to_user(UUID, UUID) CASCADE;

-- Drop function fn_mark_ticket_as_used
DROP FUNCTION IF EXISTS fn_mark_ticket_as_used(UUID) CASCADE;