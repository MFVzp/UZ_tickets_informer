from django.core.management.base import BaseCommand
from django.conf import settings

from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(self, *args, **options):
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            superuser_name = settings.SUPERUSER_NAME or None
            superuser_email = settings.SUPERUSER_EMAIL or None
            superuser_password = settings.SUPERUSER_PASSWORD or None
            if superuser_name and superuser_email and superuser_password:
                user_model.objects.create_superuser(
                    username=superuser_name,
                    email=superuser_email,
                    password=superuser_password
                )
                self.stdout.write(self.style.SUCCESS('Successfully created superuser {}'.format(superuser_name)))
