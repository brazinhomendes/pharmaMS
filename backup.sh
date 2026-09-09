#!/bin/bash
# pharmaMS - Backup automatico do PostgreSQL
# Este script roda como entrypoint de inicializacao do container

set -e

BACKUP_DIR="/backups"
DAYS_TO_KEEP=30

mkdir -p "$BACKUP_DIR"

echo "[$(date)] pharmaMS Backup configurado."
echo "Backups serao salvos em: $BACKUP_DIR"
echo "Retencao: $DAYS_TO_KEEP dias"
