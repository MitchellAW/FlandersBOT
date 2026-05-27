#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
BACKUP_DIR="$SCRIPT_DIR/../backups"
DB_CONTAINER_NAME="flandersdb"
APP_CONTAINER_NAME="flanders"

source "$SCRIPT_DIR/../.env"


# Check for backup file
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

# Bring app down but leave db running
echo "Ensure only $DB_CONTAINER_NAME is running..."
docker compose down
docker compose up $DB_CONTAINER_NAME -d

# Wait for db to be ready
echo "Waiting for database to be ready..."
until docker compose exec $DB_CONTAINER_NAME pg_isready -U $POSTGRES_USER; do
    sleep 1
done

# Backup a pre restore backup file before restoring to the given file
echo "Taking backup before restore..."
docker exec $DB_CONTAINER_NAME pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$BACKUP_DIR/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql"

# Drop and recreate databases
echo "Recreating database..."
docker exec $DB_CONTAINER_NAME psql -U $POSTGRES_USER -d postgres -c "DROP DATABASE $POSTGRES_DB;"
docker exec $DB_CONTAINER_NAME psql -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $POSTGRES_DB;"

# Restore
echo "Restoring data..."
docker exec -i $DB_CONTAINER_NAME psql -U $POSTGRES_USER $POSTGRES_DB < $1

# Bring flanders container back up
echo "Start $APP_CONTAINER_NAME app back up"
docker compose up $APP_CONTAINER_NAME -d

echo "Restore complete. Pre-restore backup saved as pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql"
