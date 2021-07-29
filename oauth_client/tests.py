from django.test import TestCase
from django.utils import timezone

from oauth_client.models import Integration


class Test(TestCase):
    def test_integration_is_installed_annotation(self):
        i = Integration.objects.create()

        self.assertFalse(i.is_installed)
        self.assertTrue(
            Integration.objects.filter(id=i.id, is_installed=False).exists())

        i.install_finish = timezone.now()
        i.save()

        self.assertTrue(i.is_installed)
        self.assertTrue(
            Integration.objects.filter(id=i.id, is_installed=True).exists())
