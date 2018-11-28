># psql -U pgsql -d template1 -c "CREATE DATABASE syslogng"
CREATE USER logwriter  WITH password '';
ALTER USER logwriter WITH PASSWORD syslogng;
GRANT ALL privileges ON DATABASE syslogng TO logwriter;
ALTER DATABASE syslogng OWNER TO logwriter;

CREATE TABLE message_levels (id SERIAL PRIMARY KEY, name VARCHAR(10) NOT NULL)
CREATE TABLE comments ( id SERIAL PRIMARY KEY, name VARCHAR(80) NOT NULL, comment VARCHAR(80) NOT NULL, type INT NOT NULL);
CREATE TABLE aliases  ( id SERIAL PRIMARY KEY, name VARCHAR(80) NOT NULL, alias   VARCHAR(80) NOT NULL, type INT NOT NULL);
CREATE OR REPLACE FUNCTION addAlias(_name varchar(80), _alias varchar(80), _type INT)
RETURNS integer AS
$$
BEGIN
    LOCK TABLE aliases IN SHARE ROW EXCLUSIVE MODE;
    IF EXISTS(SELECT aliases.name FROM aliases WHERE aliases.name=_name AND aliases.type=_type) THEN
        IF _name = _alias THEN
            DELETE FROM aliases WHERE name=_name AND type=_type;
            RETURN -1;
        ELSE
            UPDATE aliases SET alias=_alias WHERE aliases.name=_name AND aliases.type=_type;
            RETURN 1;
        END IF;
    ELSE
        IF _name != _alias THEN
            INSERT INTO aliases (name, alias, type) VALUES (_name, _alias, _type);
        END IF;
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;



DROP FUNCTION NewLogAdd()
CREATE OR REPLACE FUNCTION NewLogAdd()
RETURNS trigger AS
$$
DECLARE
    dt varchar;
    host varchar;
    program varchar;
BEGIN
    dt      := * from split_part(NEW.table_name, '_', 2);
    IF char_length(dt) = 6
    THEN
        host    := * from split_part(NEW.table_name, '_'||dt||'_', 2);
        program := * from split_part(NEW.table_name, '_'||dt||'_', 3);
        IF char_length(host) > 0 AND char_length(program) > 0
        THEN
            insert into b values(0,host,'new');
        END IF;
    END IF;
    return NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER NewLogAdd AFTER INSERT ON information_schema.tables FOR EACH ROW EXECUTE PROCEDURE NewLogAdd();

#
# host, program - 'black%', 'kernel%' OR 'black%', '' OR '', ''
#
DROP FUNCTION gettables(host varchar, program varchar, fdate varchar);
CREATE OR REPLACE FUNCTION gettables(host varchar, program varchar, fdate varchar)
RETURNS table(name varchar, last_value TIMESTAMPTZ) AS
$$
DECLARE
    tb record;
BEGIN
    FOR tb IN SELECT table_name FROM information_schema.tables
              WHERE table_type = 'BASE TABLE'
              AND table_schema = 'public'
              AND table_name LIKE 'log%' || host || program || fdate
              ORDER BY table_type, table_name
    LOOP
        RETURN QUERY EXECUTE 'SELECT CAST(''' || tb.table_name || ''' as varchar) AS name, TB.datetime AS last_value 
        FROM ' || tb.table_name || ' AS TB, ' || tb.table_name || '_id_seq AS  IDSEQ WHERE TB.id = IDSEQ.last_value';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

#
# With last update column AND count of error levels messages
#
DROP FUNCTION gettables_lup_counts(host varchar, program varchar, fdate varchar);
CREATE OR REPLACE FUNCTION gettables_lup_counts(host varchar, program varchar, fdate varchar)
RETURNS table(name varchar, last_value TIMESTAMPTZ, err bigint, warning bigint) AS
$$
DECLARE
    tb record;
BEGIN
    FOR tb IN SELECT table_name FROM information_schema.tables
              WHERE table_type = 'BASE TABLE'
              AND table_schema = 'public'
              AND table_name LIKE 'log%' || host || program || fdate
              ORDER BY table_type, table_name
    LOOP
        RETURN QUERY EXECUTE 'WITH temp AS (select level_num from ' || tb.table_name || ' )
            SELECT * FROM
                ( SELECT CAST(''' || tb.table_name || ''' as varchar) AS name, TB.datetime AS last_value FROM ' || tb.table_name || ' AS TB, ' || tb.table_name || '_id_seq AS  IDSEQ 
                  WHERE TB.id = IDSEQ.last_value ) AS T3
              , ( SELECT COUNT(level_num) err     FROM temp  WHERE level_num=''0'' OR level_num=''1'' OR level_num=''2'' OR level_num=''3'' ) AS T1
              , ( SELECT COUNT(level_num) warning FROM temp  WHERE level_num=''4'') AS T2';
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getlogcontent(logname varchar, start_id bigint, limit_id bigint, order_by varchar, filter varchar)
RETURNS table(datetime timestamptz, host varchar, program varchar, level varchar, pid varchar, message text ) AS
$$
BEGIN
    RETURN QUERY EXECUTE('SELECT T.datetime, T.host, T.program, T.level, T.pid, T.message FROM (
        SELECT ROW_NUMBER() OVER(ORDER BY ' || order_by || ' ) AS id, log.datetime, log.host, log.program, lvls.level, log.pid, log.message
        FROM ' || logname  || ' log
        INNER JOIN message_levels lvls ON log.level_num=lvls.id ' || filter || '
    ) T
    WHERE T.id>=' || start_id || ' LIMIT ' || limit_id);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getlogcontent(logname varchar, filter varchar)
RETURNS table(datetime timestamptz, host varchar, program varchar, level varchar, pid varchar, message text ) AS
$$
BEGIN
    RETURN QUERY EXECUTE('SELECT log.datetime, log.host, log.program, log.level, log.pid, log.message
        FROM ' || logname  || ' log
        INNER JOIN message_levels lvls ON log.level_num=lvls.id ' || filter
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION GetLogContentCounts(logname varchar, start_id bigint, limit_id bigint, order_by varchar)
RETURNS recordsTotal bigint, recordsFiltered bigint AS
$$
    DECLARE
        recordsTotal := 0;
        recordsFiltered := 0;
    BEGIN
        recordsTotal 
        recordsFiltered

'SELECT COUNT(T.id) FROM ' || logname  || ' log ' || filter

