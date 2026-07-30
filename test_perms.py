import os
import django
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    django.setup()
except Exception as e:
    print(f"Failed to setup Django. Error: {e}")
    sys.exit(1)

def test_perms():
    from users.models import User
    from users.serializers import UserSerializer
    
    # Get a site_keeper user
    user = User.objects.filter(role='site_keeper').first()
    if not user:
        print("No site_keeper user found!")
        return

    serializer = UserSerializer(user)
    print(json.dumps(serializer.data.get('permissions'), indent=2))

if __name__ == "__main__":
    test_perms()
