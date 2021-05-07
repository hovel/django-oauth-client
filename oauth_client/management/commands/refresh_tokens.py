from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from oauth_client.models import UserToken


class Command(BaseCommand):
    help = 'Refresh tokens'

    def handle(self, *args, **options):
        threshold = timezone.now() + timedelta(days=2)

        user_token_qs = UserToken.objects \
            .filter(user__is_active=True, expires_at__lt=threshold) \
            .exclude(refresh_token='')

        for user_token in user_token_qs:
            user_token.refresh()
