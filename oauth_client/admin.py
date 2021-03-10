from django.contrib import admin

from oauth_client.models import ProviderPart, Integration


@admin.register(ProviderPart)
class ProviderPartAdmin(admin.ModelAdmin):
    pass


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    pass
