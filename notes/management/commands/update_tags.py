# notes/management/commands/update_tags.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notes.models import Tag

class Command(BaseCommand):
    help = 'Updates existing tags with null user to a default user'

    def handle(self, *args, **options):
        default_user = User.objects.first()  # Varsayılan bir kullanıcı seçin
        if not default_user:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return

        tags_updated = Tag.objects.filter(user__isnull=True).update(user=default_user)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {tags_updated} tags'))