import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    django.setup()
except Exception as e:
    print(f"Failed to setup Django. Error: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
User = get_user_model()

def setup_cxos():
    cxo_data = [
        {"email": "arvohra87@gmail.com", "role": "cxo_citi", "name": "Citi CXO (A. Vohra)"},
        {"email": "prashantchaurasiy01@gmail.com", "role": "cxo_emb", "name": "Embassy CXO (P. Chaurasiya)"}
    ]

    print("--- Setting up CXO Accounts ---")
    
    for data in cxo_data:
        # Check if user already exists
        user = User.objects.filter(email__iexact=data["email"]).first()
        
        if user:
            print(f"Found existing user {user.email}. Updating role from '{user.role}' to '{data['role']}'.")
            user.role = data['role']
            user.name = data['name']
            user.is_active = True
            user.save()
        else:
            print(f"Creating new user {data['email']} with role '{data['role']}'.")
            user = User.objects.create_user(
                email=data['email'],
                password="Password123!", # Default password
                role=data['role']
            )
            if hasattr(user, 'name'):
                user.name = data['name']
                user.save()
            print(f" -> Password set to: Password123!")

    print("\nDone! The workflow engine will now automatically route CXO approvals to these exact email addresses.")

if __name__ == "__main__":
    setup_cxos()
