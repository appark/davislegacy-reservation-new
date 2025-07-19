#!/bin/bash

# Set up daily database backup cron job
BACKUP_SCRIPT="/opt/reservation-new/backup_db.sh"

# Add cron job to run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> /opt/reservation-new/backup.log 2>&1") | crontab -

echo "Backup cron job added - will run daily at 2 AM"
echo "Logs will be written to /opt/reservation-new/backup.log"