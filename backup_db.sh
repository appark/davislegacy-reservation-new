#!/bin/bash

# Database backup script for Django reservation system
# Run this daily via cron

BACKUP_DIR="/opt/reservation-new/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="reservation_backup_${DATE}.sql"
CONTAINER_NAME="reservation-new-db"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
echo "Creating database backup: ${BACKUP_FILE}"
docker exec $CONTAINER_NAME pg_dump -U demo2_user -d demo2_db > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress the backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "reservation_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_FILE}.gz"
echo "Old backups (>7 days) have been cleaned up"