from datetime import timedelta

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from . import models
from .views import get_IP_address

UA = "test-agent"


class IPAddressTests(TestCase):
    def ip(self, **meta):
        return get_IP_address(RequestFactory().get("/", **meta))

    def test_prefers_x_real_ip(self):
        self.assertEqual(
            self.ip(HTTP_X_REAL_IP="1.2.3.4", REMOTE_ADDR="172.18.0.1"), "1.2.3.4"
        )

    def test_first_entry_of_forwarded_chain(self):
        # The old code stored the whole chain, which Postgres rejects.
        chain = "1.2.3.4, 162.158.0.1"
        self.assertEqual(self.ip(HTTP_X_FORWARDED_FOR=chain), "1.2.3.4")

    def test_garbage_falls_back_to_remote_addr(self):
        self.assertEqual(
            self.ip(HTTP_X_FORWARDED_FOR="unknown", REMOTE_ADDR="10.0.0.1"), "10.0.0.1"
        )


class RedirectTests(TestCase):
    def setUp(self):
        self.link = models.Redirect.objects.create(
            source="abc", destination="https://example.org/"
        )

    def get(self, path="/abc"):
        return self.client.get(path, HTTP_X_REAL_IP="1.2.3.4", HTTP_USER_AGENT=UA)

    def add_hits(self, n, age):
        for _ in range(n):
            models.Statistic.objects.create(
                redir=self.link, ip_address="1.2.3.4", user_agent=UA
            )
        # `accessed` is auto_now, so back-date it with an update.
        models.Statistic.objects.update(accessed=timezone.now() - age)

    def test_redirects_and_logs_client_ip(self):
        response = self.get()
        self.assertRedirects(
            response, "https://example.org/", fetch_redirect_response=False
        )
        self.assertEqual(models.Statistic.objects.get().ip_address, "1.2.3.4")

    def test_rapid_downloads_are_blocked(self):
        self.add_hits(5, timedelta(minutes=1))
        self.assertEqual(self.get().status_code, 503)

    def test_old_downloads_are_not_blocked(self):
        # One day and one minute ago: timedelta.seconds is 60 here, which the
        # old code read as "one minute ago" and blocked.
        self.add_hits(5, timedelta(days=1, minutes=1))
        self.assertEqual(self.get().status_code, 302)

    def test_inactive_link_gives_404(self):
        self.link.is_active = False
        self.link.save()
        self.assertEqual(self.get().status_code, 404)

    def test_unknown_link_goes_to_static_and_leaves_no_trace(self):
        response = self.get("/no-such-file.pdf")
        self.assertRedirects(
            response, "/static/no-such-file.pdf", fetch_redirect_response=False
        )
        self.assertFalse(models.Redirect.objects.filter(source="no-such-file.pdf"))

    def test_existing_static_file_is_auto_created(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as root:
            Path(root, "notes.pdf").write_bytes(b"%PDF")
            with override_settings(STATIC_ROOT=root):
                self.get("/notes.pdf")
                self.get("/../etc/passwd")
        self.assertTrue(models.Redirect.objects.filter(source="notes.pdf"))
        self.assertFalse(models.Redirect.objects.filter(source__contains="passwd"))
