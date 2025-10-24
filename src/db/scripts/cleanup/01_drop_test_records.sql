\if :{?DB_NAME}
    \c :DB_NAME
\else
    \c event_access;
\endif

-- ===============================================
-- Cleanup inserted users and tickets
-- ===============================================

DELETE FROM tickets
WHERE seat IN ('A12','B05','C18','D10','E20')
  AND gate IN ('G1','G2','G3');

DELETE FROM users
WHERE username IN ('spuertaf','juanperez');
