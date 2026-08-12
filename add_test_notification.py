import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from core.models import Notification
from users.models import User

# Get the first admin user
user = User.objects.filter(role__iexact='site_keeper').first()

if user:
    notif = Notification.objects.create(
        user=user,
        title="Test Dynamic Notification",
        message="This is your newly wired real-time notification!",
        link_url="/dashboard",
        is_read=False
    )
    print(f"Successfully created a test notification for {user.email}")
else:
    print("No site_keeper user found. Try creating one from the system setup menu.")
