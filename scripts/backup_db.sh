#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
BACKUP_DIR="$SCRIPT_DIR/../backups"
DB_CONTAINER_NAME="flandersdb"

mkdir -p "$BACKUP_DIR"
source "$SCRIPT_DIR/../.env"

# Use provided filename or default to timestamped backup
BACKUP_FILE="${1:-$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql}"

echo "Backing up database to $BACKUP_FILE..."
docker exec $DB_CONTAINER_NAME pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup complete: $BACKUP_FILE"
else
    echo "Backup failed."
    exit 1
fi
