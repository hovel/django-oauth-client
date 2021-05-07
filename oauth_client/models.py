from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import TextChoices
from django.utils import timezone
from oauthlib.oauth2 import OAuth2Token
from requests_oauthlib import OAuth2Session
import requests

logger = logging.getLogger(__name__)


class Preset(TextChoices):
    BX24 = 'bx24', 'Bitrix24'
    AMOCRM = 'amocrm', 'amoCRM'
    CUSTOM = 'custom', 'Custom'


class Provider(models.Model):
    Preset = Preset

    name = models.CharField(max_length=50, unique=True)
    preset = models.CharField(max_length=50, choices=Preset.choices)
    # поле предусмотрено для совместимости со старыми урлами, которых
    # провайдеры обозначались через кодовое имя или через сочетания кодового
    # имени и идентификатора, например как "bx" или "bx/1"
    slug = models.CharField(max_length=10)

    client_id = models.CharField(max_length=2048, blank=True)
    client_secret = models.CharField(max_length=2048, blank=True)
    authorization_url = models.URLField(max_length=2048, blank=True)
    token_url = models.URLField(max_length=2048, blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{self.preset}/{self.id}'
        super().save(*args, **kwargs)


class Integration(models.Model):
    endpoint = models.CharField(max_length=255, unique=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='managed_integrations', blank=True, null=True)
    is_installed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.endpoint}'


class UserToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE)
    scope = models.TextField()
    access_token = models.CharField(max_length=2048)
    refresh_token = models.CharField(max_length=2048, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    integration = models.ForeignKey(
        'oauth_client.Integration', on_delete=models.CASCADE,
        blank=True, null=True)

    class Meta:
        unique_together = [
            ['user', 'provider', 'endpoint'],
            ['user', 'provider', 'integration'],
        ]

    def __str__(self) -> str:
        return f'{self.user} {self.provider} {self.integration}'

    def save(self, *args, **kwargs):
        old_instance = self._meta.default_manager.filter(pk=self.pk).first()
        if old_instance:
            endpoint_changed = old_instance.endpoint != self.endpoint
            integration_changed = old_instance.integration != self.integration
        else:
            endpoint_changed = bool(self.endpoint)
            integration_changed = bool(self.integration)

        if endpoint_changed and integration_changed:
            endpoint = self.endpoint or ''
            integration_endpoint = getattr(self.integration, 'endpoint', '')
            if endpoint != integration_endpoint:
                raise ValidationError(f'{endpoint} != {integration_endpoint}')
        elif endpoint_changed:
            if self.endpoint:
                self.integration, _ = Integration.objects \
                    .get_or_create(endpoint=self.endpoint)
            else:
                self.integration = None
        elif integration_changed:
            if self.integration:
                self.endpoint = self.integration.endpoint
            else:
                self.endpoint = ''

        super().save(*args, **kwargs)

    @property
    def token(self):
        params = {
            'scope': self.scope or None,
            'access_token': self.access_token,
        }
        if self.refresh_token:
            params['refresh_token'] = self.refresh_token
        if self.expires_at:
            params['expires_at'] = self.expires_at.timestamp()
            params['expires_in'] = (self.expires_at - timezone.now()).seconds
        return OAuth2Token(params)

    @token.setter
    def token(self, token: OAuth2Token):
        expires_at = token.get('expires_at', None)
        if expires_at:
            expires_at = datetime.fromtimestamp(expires_at)

        self.scope = token.scope or ''  # in case of None
        self.access_token = token['access_token']
        self.refresh_token = token.get('refresh_token', '')
        self.expires_at = expires_at

    @property
    def client_id(self):
        return self.provider.client_id

    @property
    def client_secret(self):
        return self.provider.client_secret

    @property
    def is_expired(self):
        return self.expires_at < timezone.now() + timedelta(seconds=30)

    def refresh(self):
        from oauth_client.utils import get_token_url

        endpoint = self.integration.endpoint if self.integration else ''
        token_url = get_token_url(provider=self.provider, endpoint=endpoint)

        if self.provider.preset == Preset.BX24:
            requests.packages.urllib3.add_stderr_logger()
            new_token = requests.get(
                url=token_url,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                params={
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.refresh_token,
                }
            ).json()
            logger.debug(f'Token update response: {new_token}')
            if 'access_token' in new_token:
                self.access_token = new_token['access_token']
                self.refresh_token = new_token['refresh_token']
                self.expires_at = timezone.now() + timedelta(
                    seconds=new_token['expires_in'])
                self.expires_in = new_token['expires_in']
        else:
            oauth = OAuth2Session(
                client_id=self.client_id,
                scope=self.token.scope or '',
                token=self.token)
            token = oauth.refresh_token(
                token_url=token_url,
                client_id=self.client_id,
                client_secret=self.client_secret)
            self.token = token

        self.save()

    def get_session(self):
        oauth = OAuth2Session(
            client_id=self.client_id,
            scope=self.token.scope or '',
            token=self.token)
        return oauth
