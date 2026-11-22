"""Check that every link goes where the database says.

Each visit runs in a transaction that is rolled back, so the check leaves no
statistics behind. Outside sites are not fetched.

    python manage.py check_links                # report
    python manage.py check_links --list-auto    # also list auto-created junk
    python manage.py check_links --delete-junk  # delete that junk
"""
import logging
from pathlib import Path
from urllib.parse import quote, unquote

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.test import Client

from redirect.models import Redirect, Statistic, TotalStats


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("--list-auto", action="store_true")
        parser.add_argument("--delete-junk", action="store_true")

    def handle(self, *args, list_auto, delete_junk, **options):
        logging.disable(logging.WARNING)  # the app logs every static redirect
        client = Client(HTTP_HOST="yint.org", HTTP_X_REAL_IP="127.0.0.1")
        root = Path(settings.STATIC_ROOT)
        links = list(Redirect.objects.order_by("source"))
        wrong, missing, folders, junk = [], [], [], []

        with transaction.atomic():
            for r in links:
                try:
                    with transaction.atomic():  # a crash undoes only this visit
                        resp = client.get(
                            "/" + quote(r.source), HTTP_REFERER=r.referer_constraint
                        )
                except Exception as exc:
                    wrong.append(f"{r.source}: crashed with {exc!r}")
                    continue

                static = not r.destination.startswith("http")
                target = "/static/" + r.destination if static else r.destination
                got = unquote(resp.get("Location", ""))
                if not r.is_active:
                    ok, expected = resp.status_code == 404, "404"
                else:
                    ok = resp.status_code == r.status_code and got == unquote(target)
                    expected = f"{r.status_code} {target}"
                if not ok:
                    wrong.append(f"{r.source}: expected {expected}, got {resp.status_code} {got}")
                elif r.is_active and static:
                    path = root / r.destination
                    if path.is_dir():
                        folders.append(r.destination)
                    elif not path.is_file():
                        (junk if r.extra_info.startswith("Auto") else missing).append(r)
            transaction.set_rollback(True)

        self.stdout.write(
            f"{len(links)} links: {len(wrong)} wrong, {len(missing)} of your links "
            f"point to a missing file, {len(folders)} point to a folder, "
            f"{len(junk)} auto-created entries point to nothing"
        )
        for line in wrong:
            self.stdout.write(f"WRONG    {line}")
        for r in missing:
            self.stdout.write(f"MISSING  {r.source} -> {r.destination}")
        for d in folders:
            self.stdout.write(f"FOLDER   {d}")
        if list_auto:
            for r in junk:
                self.stdout.write(f"AUTO     {r.source!r}")

        if delete_junk and junk:
            ids = [r.pk for r in junk]
            with transaction.atomic():
                Statistic.objects.filter(redir_id__in=ids).delete()
                TotalStats.objects.filter(redir_id__in=ids).delete()
                Redirect.objects.filter(pk__in=ids).delete()
            self.stdout.write(f"Deleted {len(ids)} auto-created entries and their statistics.")
