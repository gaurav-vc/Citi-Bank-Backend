import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from users.models import User, UserProfile
from access_control.models import Role

def create_user_with_role(email, name, role_name):
    # Try to get or create the role
    role, _ = Role.objects.get_or_create(role_name=role_name)
    
    # Check if user already exists
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(
            email=email,
            name=name,
            password='password123',
            role=role_name
        )
        print(f"Created user {email}")
    else:
        user.role = role_name
        user.save()
        print(f"User {email} already exists")
    
    # Update profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.role_name = role_name
    profile.save()
    
    print(f"Assigned role {role_name} to {email}")

create_user_with_role('prashantchaurasiy01@gmail.com', 'Prashant', 'CXO - citi')
create_user_with_role('arvohra87@gmail.com', 'Arvohra', 'CXO EMB')

print("Done")
