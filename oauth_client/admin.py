from django.contrib import admin

from oauth_client.models import ProviderPart, Integration


@admin.register(ProviderPart)
class ProviderPartAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider']


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'is_installed', 'admin']
