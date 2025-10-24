\if :{?DB_NAME}
    \c :DB_NAME
\else
    \c event_access;
\endif

-- Drop tickets table first 
DROP TABLE IF EXISTS tickets CASCADE;

-- Drop users table
DROP TABLE IF EXISTS users CASCADE;