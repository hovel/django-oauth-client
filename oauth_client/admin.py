from django.contrib import admin

from oauth_client.models import Provider, Integration


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'preset']


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'admin', 'install_start', 'install_finish',
                    'is_enabled']
    raw_id_fields = ['admin']
    search_fields = ['id', 'endpoint']
