#PG update db version

Dump all
`pg_dumpall > dump.sql`

Update postgresql
`pkg install postgresql-server`

Create new db
`mv /usr/local/pgsql/data /usr/local/pgsql/data.old`
`mkdir /usr/local/pgsql/data`
`chown pgsql:pgsql /usr/local/pgsql/data`
`sudo -U pgsql initdb /usr/local/pgsql/data -E utf8`
`service postgresql start`
`sudo -U pgsql psql template1 < dump.sql`
`sudo -U pgsql psql template1`
`vacuume analyse;`

