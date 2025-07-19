#!/usr/bin/env python
"""
Import teams from CSV file into Django reservation system.
This script will create new teams and update existing ones based on CSV data.
"""
import os
import sys
import csv
import django
from django.contrib.auth.models import User, Group
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo2.settings')
django.setup()

from reservations.models import TeamProfile

def parse_team_name(team_name):
    """Parse team name to extract age and gender info"""
    team_name = team_name.strip()
    if not team_name:
        return None, None, None
    
    # Extract age (first 2 digits)
    age_str = ''.join([c for c in team_name[:2] if c.isdigit()])
    age = int(age_str) if age_str else None
    
    # Extract gender (G for girls/female, B for boys/male)
    gender = None
    if 'G' in team_name.upper():
        gender = 'girls'
    elif 'B' in team_name.upper():
        gender = 'boys'
    
    # Create username from team name (remove spaces, lowercase)
    username = team_name.lower().replace(' ', '').replace('-', '')
    
    return username, age, gender

def create_or_update_team(row):
    """Create or update a team from CSV row"""
    first_name = row['first_name'].strip()
    last_name = row['last_name'].strip()
    email = row['email'].strip()
    team_name = row['team name'].strip()
    
    # Skip empty rows
    if not all([first_name, last_name, email, team_name]):
        return None, "Empty row skipped"
    
    username, age, gender = parse_team_name(team_name)
    if not username:
        return None, f"Could not parse team name: {team_name}"
    
    try:
        with transaction.atomic():
            # Get or create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            
            # Update user info if it already existed
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
            
            # Set default password for new users
            if created:
                user.set_password('password')  # Default password
                user.save()
            
            # Add to Teams group
            try:
                teams_group = Group.objects.get(name='Teams')
                user.groups.add(teams_group)
            except Group.DoesNotExist:
                pass
            
            # Get or create team profile
            team_profile, profile_created = TeamProfile.objects.get_or_create(
                team=user,
                defaults={
                    'age': age if age else 0,
                    'gender': gender if gender else 'boys',
                    'description': f"Manager: {first_name} {last_name}",
                }
            )
            
            # Update team profile if it already existed
            if not profile_created:
                if age:
                    team_profile.age = age
                if gender:
                    team_profile.gender = gender
                team_profile.description = f"Manager: {first_name} {last_name}"
                team_profile.save()
            
            status = "Created" if created else "Updated"
            return user, f"{status} team: {username} ({team_name}) - Manager: {first_name} {last_name} <{email}>"
            
    except Exception as e:
        return None, f"Error processing {team_name}: {str(e)}"

def main():
    """Main import function"""
    csv_file = '/opt/reservation-new/master-team-manager-reservations.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return
    
    print("Starting team import from CSV...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, 1):
            user, message = create_or_update_team(row)
            
            if user:
                print(f"✓ Row {row_num}: {message}")
                success_count += 1
            else:
                if "Empty row skipped" not in message:
                    print(f"✗ Row {row_num}: {message}")
                    error_count += 1
    
    print("=" * 60)
    print(f"Import completed!")
    print(f"✓ Successfully processed: {success_count} teams")
    print(f"✗ Errors: {error_count}")
    
    # Show final team count
    total_teams = User.objects.filter(groups__name='Teams').count()
    print(f"📊 Total teams in system: {total_teams}")

if __name__ == "__main__":
    main()