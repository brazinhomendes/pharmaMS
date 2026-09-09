#!/bin/bash
export PATH="/usr/lib/postgresql/18/bin:$PATH"
pg_ctl -D /home/brazmendes/Desktop/pharmaMS/pgdata -l /home/brazmendes/Desktop/pharmaMS/pgdata/logfile start 2>/dev/null
echo "PostgreSQL: $(pg_isready -h localhost -p 5433 -q && echo 'online (:5433)' || echo 'offline')"
