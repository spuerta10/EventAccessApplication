\c event_access;

CREATE OR REPLACE PROCEDURE sp_register_ticket_to_user(
    p_ticket_id UUID,
    p_user_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE tickets
    SET user_id = p_user_id
    WHERE ticket_id = p_ticket_id
      AND user_id IS NULL;

    IF FOUND THEN
        -- éxito, se asignó
        RAISE NOTICE 'Ticket % registrado a usuario %', p_ticket_id, p_user_id;
    ELSE
        -- no encontró fila válida
        RAISE EXCEPTION 'Ticket no existe o ya está registrado';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION fn_mark_ticket_as_used(p_ticket_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    updated BOOLEAN := FALSE;
BEGIN
    UPDATE tickets
    SET status = 'used',
        used_at = now()
    WHERE ticket_id = p_ticket_id
      AND status = 'valid';

    IF FOUND THEN
        updated := TRUE;
    ELSE
        RAISE EXCEPTION 'Ticket % no existe o ya fue usado', p_ticket_id;
    END IF;

    RETURN updated;
END;
$$;


