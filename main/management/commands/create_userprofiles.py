# yourapp/management/commands/create_userprofiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for users without one'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.username}'))
