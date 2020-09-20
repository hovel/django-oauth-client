from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone
from oauthlib.oauth2 import OAuth2Token
from requests_oauthlib import OAuth2Session


class UserToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)
    scope = models.TextField()
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'provider']

    def __str__(self) -> str:
        return f'{self.user} {self.provider}'

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

    def refresh(self):
        provider = self.get_provider()

        oauth = OAuth2Session(
            client_id=provider['client_id'],
            scope=self.token.scopes,
            token=self.token)

        token = oauth.refresh_token(
            token_url=provider['token_url'],
            client_id=provider['client_id'],
            client_secret=provider['client_secret'])

        self.token = token
        self.save()

    def get_provider(self) -> dict:
        return settings.OAUTH2_PROVIDERS[self.provider]
