# GitHub Repository Setup Instructions

## Option 1: Using GitHub CLI (Recommended)

If you have GitHub CLI installed:

```bash
# Create GitHub repository
gh repo create davislegacysoccer/reservation-system --public --description "Django field reservation system for Davis Legacy Soccer Club - 42 teams, automated backups, secure authentication"

# Add GitHub as remote and push
git remote add origin https://github.com/davislegacysoccer/reservation-system.git
git branch -M main
git push -u origin main
```

## Option 2: Using GitHub Web Interface

1. **Go to GitHub.com** and sign in to your account

2. **Create New Repository**:
   - Click the "+" icon → "New repository"
   - Repository name: `reservation-system`
   - Description: `Django field reservation system for Davis Legacy Soccer Club - 42 teams, automated backups, secure authentication`
   - Choose: Public (or Private if preferred)
   - **DO NOT** initialize with README (we already have one)
   - Click "Create repository"

3. **Connect Local Repository**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/reservation-system.git
   git branch -M main
   git push -u origin main
   ```

## Repository Details

**Repository Name**: `reservation-system`  
**Description**: Django field reservation system for Davis Legacy Soccer Club - 42 teams, automated backups, secure authentication

**Topics/Tags** (add these in GitHub settings):
- `django`
- `soccer`
- `reservation-system`
- `docker`
- `postgresql`
- `backup-automation`
- `sports-management`

## Security Notes

- The `.env` file is excluded from the repository (contains secrets)
- Database backups are excluded (contain sensitive data)
- Use the `.env.example` file as a template for deployment

## After Repository Creation

1. **Update README.md** with actual GitHub URL
2. **Add repository URL** to your deployment documentation
3. **Set up GitHub Actions** (optional) for automated testing/deployment
4. **Configure branch protection** (optional) for main branch

## Clone Command for Others

Once the repository is created, others can clone it with:

```bash
git clone https://github.com/YOUR_USERNAME/reservation-system.git
cd reservation-system
cp .env.example .env
# Edit .env with proper values
docker-compose up -d
```