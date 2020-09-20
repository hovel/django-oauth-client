from django import template
from oauth_client.utils import get_authorization_url

register = template.Library()


register.simple_tag(get_authorization_url)
