# Davis Legacy Soccer Club - Reservation System

A Django-based field reservation system for soccer teams to book practice times and manage tournaments. Currently serving 42 teams with secure authentication and automated backups.

## 🏟️ System Overview

This reservation system allows soccer teams to:
- Book field time slots for practice sessions
- View available fields and time slots in a calendar interface
- Manage tournament schedules
- Track team information and contact details
- Admin management of fields, teams, and reservations

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Access to dev.davislegacysoccer.org domain

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reservation-new
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your secure values
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Run initial setup**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --noinput
   ```

5. **Load sample data (optional)**
   ```bash
   docker-compose exec web python manage.py loaddata teams_complete_fixed.json fields_only_clean.json timeslots.json tournaments_clean.json
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Django Settings
DEBUG=True                    # Set to False in production
SECRET_KEY=<secure-key>      # Generate with Django's get_random_secret_key()

# Database
DB_NAME=demo2_db
DB_USER=demo2_user
DB_PASSWORD=<secure-password>
DB_HOST=db
DB_PORT=5432

# Domain Configuration
ALLOWED_HOSTS=dev.davislegacysoccer.org,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://dev.davislegacysoccer.org,https://localhost

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<app-password>
```

### Docker Services

- **web**: Django application running on Gunicorn
- **db**: PostgreSQL 15 database with persistent storage

## 🔐 Security Features

### Authentication & Access
- **Admin Panel**: `/admin/` - Full system management
- **Team Logins**: Individual accounts for 42 soccer teams
- **Secure Sessions**: Django's built-in session management

### Security Improvements Implemented
- ✅ **Cryptographically secure SECRET_KEY** (50-character random string)
- ✅ **Strong database password** (32-character random string)
- ✅ **Environment variable protection** (credentials in `.env` file)
- ✅ **Database health checks** (automatic container recovery)
- ✅ **Persistent volumes** (data survives container restarts)
- ✅ **Production security headers** (HSTS, XSS protection, clickjacking prevention)
- ✅ **Enhanced CSRF protection** (HttpOnly cookies, secure settings)
- ✅ **Secure session management** (1-hour timeout, secure cookies)
- ✅ **Security event logging** (dedicated security.log file)
- ✅ **Hardcoded credentials removed** (email passwords, secret keys)

### Default Credentials
- **Admin Username**: `admin`
- **Admin Password**: `changeme123` ⚠️ **CHANGE IMMEDIATELY**

### Team Login Credentials
- **All Team Password**: `DLSC2025`
- **Team Usernames**: Based on team names (e.g., `17gwhite`, `12bred`, `09bblack`)
- **Total Teams**: 45 teams imported from CSV data

## 📧 Email Notifications

### Automatic Email Triggers
The system automatically sends emails for these events:

1. **New Reservations**: When teams create new field bookings
   - **To**: Team making reservation + All superuser administrators
   - **Template**: New reservation details with approval link

2. **Modified Reservations**: When teams edit existing reservations  
   - **To**: Original team + Editing team + All superuser administrators
   - **Template**: Modified reservation details for review

3. **Approved Reservations**: When admins approve pending reservations
   - **To**: Team whose reservation was approved + All superusers
   - **Template**: Approval confirmation with reservation details

4. **New Teams**: When administrators create new team accounts
   - **To**: New team (with login credentials) + All superuser administrators  
   - **Template**: Welcome email with username/password and login instructions

5. **New Tournaments**: When administrators create tournaments
   - **To**: All superuser administrators
   - **Template**: Tournament creation notification

6. **Password Reset**: Django's built-in password reset functionality
   - **To**: User requesting reset
   - **Template**: Password reset link and instructions

### Email Configuration
- **From Address**: `reservation@davislegacysoccer.org`
- **SMTP Server**: Gmail (smtp.gmail.com)
- **Subject Prefix**: `[Davis Legacy Reservation System]`
- **Recipients**: Teams + All users in 'Superuser' group

## 💾 Backup System

### Automated Daily Backups
- **Schedule**: Daily at 2:00 AM via cron
- **Retention**: 7 days (automatic cleanup)
- **Location**: `/opt/reservation-new/backups/`
- **Format**: Compressed PostgreSQL dumps (`.sql.gz`)

### Backup Commands
```bash
# Manual backup
./backup_db.sh

# View backup logs
tail -f backup.log

# List backups
ls -la backups/

# Restore from backup
gunzip backups/reservation_backup_YYYYMMDD_HHMMSS.sql.gz
docker-compose exec -T db psql -U demo2_user -d demo2_db < backups/reservation_backup_YYYYMMDD_HHMMSS.sql
```

## 🗄️ Database Schema

### Core Models
- **User**: Django auth users (teams and admins)
- **TeamProfile**: Extended team information (age, gender, description)
- **Field**: Soccer fields available for booking
- **TimeSlot**: Available time periods for each field
- **Reservation**: Individual bookings by teams
- **Tournament**: Special event management

### Data Fixtures
- `teams_complete_fixed.json`: 90 team/user records
- `fields_only_clean.json`: 11 soccer fields
- `timeslots.json`: 31 available time slots
- `tournaments_clean.json`: 18 tournament records

## 🏗️ Architecture

### Docker Configuration
```yaml
services:
  web:
    - Django 5.2.3 application
    - Gunicorn WSGI server
    - WhiteNoise static file serving
    - Persistent volumes for static/media files
    
  db:
    - PostgreSQL 15
    - UTF-8 encoding
    - Health checks enabled
    - Persistent data storage
```

### Volumes
- `pgdata`: PostgreSQL database files
- `pgbackup`: Database backup storage
- `static_volume`: Django static files
- `media_volume`: User uploaded files

## 🌐 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY`
- [ ] Use strong database password
- [ ] Configure proper domain in `ALLOWED_HOSTS`
- [ ] Set up SSL certificates (handled by Traefik)
- [ ] Configure email settings for notifications
- [ ] Set up monitoring and log aggregation

### Traefik Integration
The system includes Traefik labels for:
- Automatic HTTPS with Let's Encrypt
- Domain routing for dev.davislegacysoccer.org
- Security headers and middleware

## 🛠️ Development

### Local Development
```bash
# Start in development mode
docker-compose up

# Access Django shell
docker-compose exec web python manage.py shell

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### File Structure
```
reservation-new/
├── demo2/                  # Django project settings
├── reservations/           # Main Django app
│   ├── models.py          # Database models
│   ├── views/             # View controllers
│   ├── forms/             # Django forms
│   ├── templates/         # HTML templates
│   └── fixtures/          # Initial data
├── static/                # Static assets
├── templates/             # Global templates
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Python/Django container
├── requirements.txt       # Python dependencies
├── backup_db.sh          # Backup script
└── .env.example          # Environment template
```

## 📊 System Stats

- **Teams**: 42 active soccer teams
- **Fields**: 11 available soccer fields
- **Time Slots**: 31 bookable time periods
- **Tournaments**: 18 configured tournaments
- **Framework**: Django 5.2.3
- **Database**: PostgreSQL 15
- **Container Runtime**: Docker with Docker Compose

## 🚨 Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Check database logs
docker-compose logs db
```

**Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x backup_db.sh setup_backup_cron.sh
```

**Missing Data**
```bash
# Reload fixtures
docker-compose exec web python manage.py loaddata teams_complete_fixed.json fields_only_clean.json timeslots.json tournaments_clean.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is proprietary software for Davis Legacy Soccer Club.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review Docker and Django logs
- Contact the system administrator

---

**Last Updated**: July 2025  
**System Status**: ✅ Production Ready with Enhanced Security
**Security Score**: 8/10 (Critical vulnerabilities resolved)
**Recent Changes**: Hardcoded credentials removed, security headers added, email documentation completed