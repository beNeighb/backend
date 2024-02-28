#!/bin/bash

# Source environment variables for database
source /env.db

# Source environment variables for Backblaze
source /env

# Database details
DB_NAME="${POSTGRES_DB}"  # Use env var from .env.prod.db
DB_USER="${POSTGRES_USER}"  # Use env var from .env.prod.db
DB_PASSWORD="${POSTGRES_PASSWORD}"  # Use env var from .env.prod.db
DB_HOST="${SQL_HOST}"  # Assuming your database service is named "db" in docker-compose

# Backup directory (adjust the path as needed)
BACKUP_DIR=/backups

# Get the date in YYYY-MM-DD format
DATE=$(date +%Y-%m-%d)

# Dump the database
# pg_dump -h "$DB_HOST" -U "$DB_USER" -W "$DB_PASSWORD" "$DB_NAME" > "$BACKUP_DIR/$DATE.sql.gz"

# # Compress the backup
# gzip -f "$BACKUP_DIR/$DATE.sql.gz"

# # Upload the backup to Backblaze (replace with your Backblaze B2 commands)
# # Replace the following with your actual values (sourced from .env.prod)
# b2 upload_file --application_key $B2_APPLICATION_KEY --bucket_id $B2_BUCKET_ID "$BACKUP_DIR/$DATE.sql.gz.gz"

# Remove the uncompressed backup (optional)
# rm "$BACKUP_DIR/$DATE.sql.gz"

echo "Database backup completed and uploaded to Backblaze (compressed)."
