"""Merge duplicate TotalStats rows, so 0003 can make `redir` unique.

Two simultaneous first visits to a link could each create a TotalStats row;
get_or_create then crashed on every later visit to that link.
"""
from django.db import migrations
from django.db.models import Count


def merge_duplicates(apps, schema_editor):
    TotalStats = apps.get_model("redirect", "TotalStats")
    dupes = (
        TotalStats.objects.values("redir")
        .annotate(n=Count("id"))
        .filter(n__gt=1)
        .values_list("redir", flat=True)
    )
    for redir_id in list(dupes):
        keep, *extra = TotalStats.objects.filter(redir_id=redir_id).order_by("id")
        # update(), not save(): save() would reset the auto_now last_access.
        TotalStats.objects.filter(pk=keep.pk).update(
            accesses=sum(row.accesses for row in [keep, *extra]),
            last_access=max(row.last_access for row in [keep, *extra]),
        )
        TotalStats.objects.filter(pk__in=[row.pk for row in extra]).delete()


class Migration(migrations.Migration):
    dependencies = [("redirect", "0001_initial")]
    operations = [migrations.RunPython(merge_duplicates, migrations.RunPython.noop)]
