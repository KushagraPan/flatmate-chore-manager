from django.conf import settings
from django.test import SimpleTestCase


class SmokeTest(SimpleTestCase):
    def test_project_setup_and_runner(self):
        """Smoke test verifying that the test runner executes and core is installed."""
        self.assertTrue(True)
        self.assertIn("core", settings.INSTALLED_APPS)
